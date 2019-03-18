#include <Python.h>
#include <structmember.h>

#define BOOL int
#define TRUE 1
#define FALSE 0

typedef struct {
    PyObject_HEAD
    /* internal data. */
    double min_percent_price;
    int min_segment_size;
    int max_depth;

    double start_price;
    double end_price;
    long start_ts;
    long end_ts;
    double min_price;
    int min_price_index;
    long min_price_ts;
    double max_price;
    int max_price_index;
    long max_price_ts;
    //self.half_split = False
    PyObject *parent;
    PyObject *seg_start;
    PyObject *seg_mid;
    PyObject *seg_end;
    double percent;
    int depth;
    int type;
    int mode;
    BOOL half_split;
    BOOL _is_leaf;
} PriceSegmentTree;

static void PriceSegmentTree_dealloc(PriceSegmentTree* self);
static PyObject *PriceSegmentTree_new(PyTypeObject *type, PyObject *args, PyObject *kwds);
static int PriceSegmentTree_init(PriceSegmentTree *self, PyObject *args, PyObject *kwds);
static PyObject *PriceSegmentTree_split(PriceSegmentTree* self, PyObject *args, PyObject *kwds);

static PyMemberDef PriceSegmentTree_members[] = {
    {"min_segment_size", T_INT, offsetof(PriceSegmentTree, min_segment_size), 0, "pstobj min_segment_size"},
    {"max_depth", T_INT, offsetof(PriceSegmentTree, max_depth), 0, "pstobj max_depth"},
    {"min_percent_price", T_DOUBLE, offsetof(PriceSegmentTree, min_percent_price), 0, "pstobj min_percent_price"},
    {"start_price", T_DOUBLE, offsetof(PriceSegmentTree, start_price), 0, "pstobj start_price"},
    {"end_price", T_DOUBLE, offsetof(PriceSegmentTree, end_price), 0, "pstobj end_price"},
    {"start_ts", T_LONG, offsetof(PriceSegmentTree, start_ts), 0, "pstobj start_ts"},
    {"end_ts", T_LONG, offsetof(PriceSegmentTree, end_ts), 0, "pstobj end_ts"},
    {"min_price", T_DOUBLE, offsetof(PriceSegmentTree, min_price), 0, "pstobj min_price"},
    {"min_price_index", T_INT, offsetof(PriceSegmentTree, min_price_index), 0, "pstobj min_price_index"},
    {"min_price_ts", T_LONG, offsetof(PriceSegmentTree, min_price_ts), 0, "pstobj min_price_ts"},
    {"max_price", T_DOUBLE, offsetof(PriceSegmentTree, max_price), 0, "pstobj max_price"},
    {"max_price_index", T_INT, offsetof(PriceSegmentTree, max_price_index), 0, "pstobj max_price_index"},
    {"max_price_ts", T_LONG, offsetof(PriceSegmentTree, max_price_ts), 0, "pstobj max_price_ts"},
    {"parent", T_OBJECT, offsetof(PriceSegmentTree, parent), 0, "pstobj parent"},
    {"seg_start", T_OBJECT, offsetof(PriceSegmentTree, seg_start), 0, "pstobj seg_start"},
    {"seg_mid", T_OBJECT, offsetof(PriceSegmentTree, seg_mid), 0, "pstobj seg_mid"},
    {"seg_end", T_OBJECT, offsetof(PriceSegmentTree, seg_end), 0, "pstobj seg_end"},
    {"percent", T_DOUBLE, offsetof(PriceSegmentTree, percent), 0, "pstobj percent"},
    {"depth", T_INT, offsetof(PriceSegmentTree, depth), 0, "pstobj depth"},
    {"type", T_INT, offsetof(PriceSegmentTree, type), 0, "pstobj type"},
    {"mode", T_INT, offsetof(PriceSegmentTree, mode), 0, "pstobj mode"},
    {"half_split", T_INT, offsetof(PriceSegmentTree, half_split), 0, "pstobj half_split"},
    {"_is_leaf", T_INT, offsetof(PriceSegmentTree, _is_leaf), 0, "pstobj _is_leaf"},
    {NULL}  /* Sentinel */
};

static PyMethodDef PriceSegmentTree_methods[] = {
    {"split", (PyCFunction)PriceSegmentTree_split, METH_VARARGS,
     "Split PriceSegmentTree",
    },
    {NULL}  /* Sentinel */
};

static PyTypeObject PriceSegmentTree_MyTestType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "PriceSegmentTree.PriceSegmentTree",                 /*tp_name*/
    sizeof(PriceSegmentTree),               /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)PriceSegmentTree_dealloc,   /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,/*tp_flags*/
    "PriceSegmentTree objects",             /* tp_doc */
    0,                         /* tp_traverse */
    0,                         /* tp_clear */
    0,                         /* tp_richcompare */
    0,                         /* tp_weaklistoffset */
    0,                         /* tp_iter */
    0,                         /* tp_iternext */
    PriceSegmentTree_methods,               /* tp_methods */
    PriceSegmentTree_members,               /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)PriceSegmentTree_init,        /* tp_init */
    0,                         /* tp_alloc */
    PriceSegmentTree_new,                   /* tp_new */
};

#ifndef PyMODINIT_FUNC  /* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif
