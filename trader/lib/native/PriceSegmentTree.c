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

static PyObject *
PriceSegmentTree_split(PriceSegmentTree* self, PyObject *args, PyObject *kwds)
{
    PyObject *prices, *timestamps, *parent=NULL;
    int n, t;
    static char *kwlist[] = {"prices", "timestamps", "n", "t", "parent", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "OO|iiO", kwlist, &prices, &timestamps, &n, &t, &parent))
        return NULL;
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
