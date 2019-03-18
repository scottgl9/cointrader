#include "PriceSegmentTree.h"

static void
PriceSegmentTree_dealloc(PriceSegmentTree* self)
{
    self->ob_type->tp_free((PyObject*)self);
}

static PyObject *
PriceSegmentTree_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PriceSegmentTree *self;

    self = (PriceSegmentTree *)type->tp_alloc(type, 0);
    self->min_percent_price = 0;
    self->min_segment_size = 0;
    self->max_depth = 0;
    self->start_price = 0;
    self->end_price = 0;
    self->start_ts = 0;
    self->end_ts = 0;
    self->min_price = 0;
    self->min_price_index = -1;
    self->min_price_ts = 0;
    self->max_price = 0;
    self->max_price_index = -1;
    self->max_price_ts = 0;
    self->seg_start = NULL;
    self->seg_mid = NULL;
    self->seg_end = NULL;

    self->percent = 0;
    self->depth = 0;
    self->type = 0;
    self->mode = 0;
    self->half_split = FALSE;
    self->_is_leaf = FALSE;

    return (PyObject *)self;
}

static int
PriceSegmentTree_init(PriceSegmentTree *self, PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = {"min_percent_price", "min_segment_size", "max_depth", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "di|i", kwlist,
                                     &self->min_percent_price, &self->min_segment_size, &self->max_depth))
        return -1;

    return 0;
}

static int get_min_value_index(PyListObject *values)
{
    int index = -1;
    int size = PyList_GET_SIZE((PyObject*)values);
    double value, min_value = 0;
    for (int i=0; i<size; i++) {
        value = PyFloat_AS_DOUBLE(PyList_GET_ITEM((PyObject *)values, i));
        if (min_value > value || min_value == 0)
            index = i;
            min_value = value;
    }
    return index;
}

static int get_max_value_index(PyListObject *values)
{
    int index = -1;
    int size = PyList_GET_SIZE((PyObject*)values);
    double value, max_value = 0;
    for (int i=0; i<size; i++) {
        value = PyFloat_AS_DOUBLE(PyList_GET_ITEM((PyObject *)values, i));
        if (max_value < value)
            index = i;
            max_value = value;
    }
    return index;
}

static PyObject *
PriceSegmentTree_split(PriceSegmentTree* self, PyObject *args, PyObject *kwds)
{
    PyObject *prices, *timestamps, *parent=NULL;
    int n, t, size;
    static char *kwlist[] = {"prices", "timestamps", "n", "t", "parent", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "OO|iiO", kwlist, &prices, &timestamps, &n, &t, &parent))
        return NULL;

    size = PyList_Size((PyObject*)prices);

    self->parent = parent;
    self->depth = n;
    self->type = t;
    self->half_split = FALSE;

    self->start_price = PyFloat_AS_DOUBLE(PyList_GET_ITEM((PyObject *)prices, 0));  // prices[0]
    self->end_price = PyFloat_AS_DOUBLE(PyList_GET_ITEM((PyObject *)prices, size)); // prices[-1]
    self->start_ts = PyInt_AS_LONG(PyList_GET_ITEM((PyObject *)timestamps, 0)); // timestamps[0]
    self->end_ts = PyInt_AS_LONG(PyList_GET_ITEM((PyObject *)timestamps, size));  //timestamps[-1]

    self->max_price_index = get_max_value_index((PyListObject *)prices);
    self->max_price = PyFloat_AS_DOUBLE(PyList_GET_ITEM((PyObject *)prices, self->max_price_index));
    self->max_price_ts = PyFloat_AS_DOUBLE(PyList_GET_ITEM((PyObject *)timestamps, self->max_price_index));

    self->min_price_index = get_min_value_index((PyListObject *)prices);
    self->min_price = PyFloat_AS_DOUBLE(PyList_GET_ITEM((PyObject *)prices, self->min_price_index));
    self->min_price_ts = PyFloat_AS_DOUBLE(PyList_GET_ITEM((PyObject *)timestamps, self->min_price_index));

    if (self->min_percent_price != 0) {
        if (100.0 * (self->max_price - self->min_price) <= self->min_percent_price * self->min_price) {
            self->_is_leaf = TRUE;
            Py_INCREF(Py_False);
            return Py_False;
        }
    }

    // Too small to split into three segments, so return
    if (size <= (3 * self->min_segment_size)) {
        self->_is_leaf = TRUE;
        Py_INCREF(Py_False);
        return Py_False;
    }

    // if mid segment size is less than min_segment_size, set half_split mode
    if (abs(self->max_price_index - self->min_price_index) < self->min_segment_size)
        self->half_split = TRUE;

    // if start or end segment size is less than min_segment_size, set half_split mode
    if (self->min_price_index < self->max_price_index) {
        if (self->min_price_index < self->min_segment_size)
            self->half_split = TRUE;
        if ((size - self->max_price_index) < self->min_segment_size)
            self->half_split = TRUE;
    } else if (self->min_price_index > self->max_price_index) {
        if (self->max_price_index < self->min_segment_size)
            self->half_split = TRUE;
        if ((size - self->min_price_index) < self->min_segment_size)
            self->half_split = TRUE;
    } else {
        self->_is_leaf = TRUE;
        Py_INCREF(Py_False);
        return Py_False;
    }

    if (self->half_split) {

    } else {
    }

    Py_INCREF(Py_True);
    return Py_True;
}

PyMODINIT_FUNC
initPriceSegmentTree(void)
{
    PyObject* m;

    if (PyType_Ready(&PriceSegmentTree_MyTestType) < 0)
        return;

    m = Py_InitModule3("PriceSegmentTree", PriceSegmentTree_methods,
                       "Builds Price Segment Tree structure");

    Py_INCREF(&PriceSegmentTree_MyTestType);
    PyModule_AddObject(m, "PriceSegmentTree", (PyObject *)&PriceSegmentTree_MyTestType);
}
