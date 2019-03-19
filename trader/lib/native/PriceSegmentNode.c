#include "PriceSegmentNode.h"

static void
PriceSegmentNode_dealloc(PriceSegmentNode* self)
{
    self->ob_type->tp_free((PyObject*)self);
}

static PyObject *
PriceSegmentNode_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PriceSegmentNode *self;

    // #define __Pyx_SetNameInClass(ns, name, value)  PyObject_SetItem(ns, name, value)

    self = (PriceSegmentNode *)type->tp_alloc(type, 0);
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
PriceSegmentNode_init(PriceSegmentNode *self, PyObject *args, PyObject *kwds)
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
        if (min_value >= value || min_value == 0)
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
        if (max_value <= value)
            index = i;
            max_value = value;
    }
    return index;
}

static PyObject *PriceSegmentNode_update_percent(PriceSegmentNode* self, PyObject *args)
{
    if (self->start_price != 0) {
        self->percent = f_round(100.0 * (self->end_price - self->start_price) / self->start_price, 2);
    }
    return Py_BuildValue("d", self->percent);
}

static PyObject *PriceSegmentNode_is_leaf(PriceSegmentNode* self, PyObject *args)
{
    if (self->_is_leaf) {
        Py_INCREF(Py_True);
        return Py_True;
    }

    Py_INCREF(Py_False);
    return Py_False;
}

static PyObject *
PriceSegmentNode_split(PriceSegmentNode* self, PyObject *args, PyObject *kwds)
{
    PyObject *prices, *timestamps, *parent=NULL;
    int n, t, size, end_index;
    static char *kwlist[] = {"prices", "timestamps", "n", "t", "parent", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "OOiiO", kwlist, &prices, &timestamps, &n, &t, &parent))
        return NULL;

    size = PyList_Size((PyObject*)prices);
    end_index = size - 1;

    //printf("split(size=%d, t=%d, n=%d)\n", size, t, n);

    self->parent = parent;
    self->depth = n;
    self->type = t;
    self->half_split = FALSE;

    self->start_price = PyFloat_AS_DOUBLE(PyList_GET_ITEM((PyObject *)prices, 0));  // prices[0]
    self->end_price = PyFloat_AS_DOUBLE(PyList_GET_ITEM((PyObject *)prices, end_index)); // prices[-1]
    self->start_ts = PyInt_AS_LONG(PyList_GET_ITEM((PyObject *)timestamps, 0)); // timestamps[0]
    self->end_ts = PyInt_AS_LONG(PyList_GET_ITEM((PyObject *)timestamps, end_index));  //timestamps[-1]

    self->max_price_index = get_max_value_index((PyListObject *)prices);
    self->max_price = PyFloat_AS_DOUBLE(PyList_GET_ITEM((PyObject *)prices, self->max_price_index));
    self->max_price_ts = PyInt_AS_LONG(PyList_GET_ITEM((PyObject *)timestamps, self->max_price_index));

    self->min_price_index = get_min_value_index((PyListObject *)prices);
    self->min_price = PyFloat_AS_DOUBLE(PyList_GET_ITEM((PyObject *)prices, self->min_price_index));
    self->min_price_ts = PyInt_AS_LONG(PyList_GET_ITEM((PyObject *)timestamps, self->min_price_index));

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
        int mid_index = size / 2;
        PyObject *argList, *res;
        PyObject *start_price_values, *start_ts_values;
        PyObject *end_price_values, *end_ts_values;

        self->mode = MODE_SPLIT2_HALF;

        argList = Py_BuildValue("dii", self->min_percent_price, self->min_segment_size, self->max_depth);
        self->seg_start = PyObject_CallObject((PyObject *) &PriceSegmentNode_MyTestType, argList);
        self->seg_mid = Py_None;
        Py_INCREF(Py_None);
        self->seg_end = PyObject_CallObject((PyObject *) &PriceSegmentNode_MyTestType, argList);
        Py_DECREF(argList);

        //start_price_values = prices[0:mid_index]
        //start_ts_values = timestamps[0:mid_index]

        parent = (PyObject *)self;

        start_price_values = PyList_GetSlice(prices, 0, mid_index);
        start_ts_values = PyList_GetSlice(timestamps, 0, mid_index);
        res = PyObject_CallMethod(self->seg_start, "split", "(OOiiO)", start_price_values, start_ts_values, n+1, 1, parent);
        if (res != NULL) Py_DECREF(res);

        end_price_values = PyList_GetSlice(prices, mid_index, end_index);
        end_ts_values = PyList_GetSlice(timestamps, mid_index, end_index);
        res = PyObject_CallMethod(self->seg_end, "split", "(OOiiO)", end_price_values, end_ts_values, n+1, 3, parent);
        if (res != NULL) Py_DECREF(res);
    } else {
        int index1, index2;
        PyObject *argList, *res;
        PyObject *start_price_values, *start_ts_values;
        PyObject *mid_price_values, *mid_ts_values;
        PyObject *end_price_values, *end_ts_values;

        // split prices and timestamps into three parts
        if (self->max_price_ts < self->min_price_ts) {
            self->mode = MODE_SPLIT3_MAXMIN;
            index1 = self->max_price_index;
            index2 = self->min_price_index;
        } else if (self->max_price_ts > self->min_price_ts) {
            self->mode = MODE_SPLIT3_MINMAX;
            index1 = self->min_price_index;
            index2 = self->max_price_index;
        } else {}
            self->_is_leaf = TRUE;
            Py_INCREF(Py_False);
            return Py_False;

        parent = (PyObject *)self;

        argList = Py_BuildValue("dii", self->min_percent_price, self->min_segment_size, self->max_depth);
        self->seg_start = PyObject_CallObject((PyObject *) &PriceSegmentNode_MyTestType, argList);
        self->seg_mid = PyObject_CallObject((PyObject *) &PriceSegmentNode_MyTestType, argList);
        self->seg_end = PyObject_CallObject((PyObject *) &PriceSegmentNode_MyTestType, argList);
        Py_DECREF(argList);

        start_price_values = PyList_GetSlice(prices, 0, index1);
        start_ts_values = PyList_GetSlice(timestamps, 0, index1);
        res = PyObject_CallMethod(self->seg_start, "split", "(OOiiO)", start_price_values, start_ts_values, n+1, 1, parent);
        if (res != NULL) Py_DECREF(res);

        mid_price_values = PyList_GetSlice(prices, index1, index2);
        mid_ts_values = PyList_GetSlice(timestamps, index1, index2);
        res = PyObject_CallMethod(self->seg_mid, "split", "(OOiiO)", mid_price_values, mid_ts_values, n+1, 2, parent);
        if (res != NULL) Py_DECREF(res);

        end_price_values = PyList_GetSlice(prices, index2, end_index);
        end_ts_values = PyList_GetSlice(timestamps, index2, end_index);
        res = PyObject_CallMethod(self->seg_end, "split", "(OOiiO)", end_price_values, end_ts_values, n+1, 3, parent);
        if (res != NULL) Py_DECREF(res);
    }

    Py_INCREF(Py_True);
    return Py_True;
}

// int PyModule_AddIntConstant(PyObject *module, const char *name, long value)

PyMODINIT_FUNC
initPriceSegmentNode(void)
{
    PyObject* m;

    if (PyType_Ready(&PriceSegmentNode_MyTestType) < 0)
        return;

    m = Py_InitModule3("PriceSegmentNode", PriceSegmentNode_methods,
                       "Builds Price Segment Node structure");

    Py_INCREF(&PriceSegmentNode_MyTestType);
    PyModule_AddIntConstant(m, "MODE_SPLIT_NONE", MODE_SPLIT_NONE);
    PyModule_AddIntConstant(m, "MODE_SPLIT3_MINMAX", MODE_SPLIT3_MINMAX);
    PyModule_AddIntConstant(m, "MODE_SPLIT3_MAXMIN", MODE_SPLIT3_MAXMIN);
    PyModule_AddIntConstant(m, "MODE_SPLIT2_MAX", MODE_SPLIT2_MAX);
    PyModule_AddIntConstant(m, "MODE_SPLIT2_MIN", MODE_SPLIT2_MIN);
    PyModule_AddIntConstant(m, "MODE_SPLIT2_HALF", MODE_SPLIT2_HALF);
    PyModule_AddObject(m, "PriceSegmentNode", (PyObject *)&PriceSegmentNode_MyTestType);
}
