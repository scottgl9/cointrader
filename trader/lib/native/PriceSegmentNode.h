#include <Python.h>
#include <structmember.h>
#include <math.h>
#include <stdlib.h>

#define MODE_SPLIT_NONE     0
#define MODE_SPLIT3_MINMAX  1
#define MODE_SPLIT3_MAXMIN  2
#define MODE_SPLIT2_MAX     3
#define MODE_SPLIT2_MIN     4
#define MODE_SPLIT2_HALF    5

static inline double my_round(double x, unsigned int digits) {
    double fac = pow(10, digits);
    return round(x*fac)/fac;
}

static double f_round(double dval, int n)
{
    char l_fmtp[32], l_buf[64];
    char *p_str;
    sprintf (l_fmtp, "%%.%df", n);
    if (dval>=0)
            sprintf (l_buf, l_fmtp, dval);
    else
            sprintf (l_buf, l_fmtp, dval);
    return ((double)strtod(l_buf, &p_str));

}

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
} PriceSegmentNode;

static void PriceSegmentNode_dealloc(PriceSegmentNode* self);
static PyObject *PriceSegmentNode_new(PyTypeObject *type, PyObject *args, PyObject *kwds);
static int PriceSegmentNode_init(PriceSegmentNode *self, PyObject *args, PyObject *kwds);
static PyObject *PriceSegmentNode_split(PriceSegmentNode* self, PyObject *args, PyObject *kwds);
static PyObject *PriceSegmentNode_update_percent(PriceSegmentNode* self, PyObject *args);
static PyObject *PriceSegmentNode_is_leaf(PriceSegmentNode* self, PyObject *args);

static PyMemberDef PriceSegmentNode_members[] = {
    {"min_segment_size", T_INT, offsetof(PriceSegmentNode, min_segment_size), 0, "psnobj min_segment_size"},
    {"max_depth", T_INT, offsetof(PriceSegmentNode, max_depth), 0, "psnobj max_depth"},
    {"min_percent_price", T_DOUBLE, offsetof(PriceSegmentNode, min_percent_price), 0, "psnobj min_percent_price"},
    {"start_price", T_DOUBLE, offsetof(PriceSegmentNode, start_price), 0, "psnobj start_price"},
    {"end_price", T_DOUBLE, offsetof(PriceSegmentNode, end_price), 0, "psnobj end_price"},
    {"start_ts", T_LONG, offsetof(PriceSegmentNode, start_ts), 0, "psnobj start_ts"},
    {"end_ts", T_LONG, offsetof(PriceSegmentNode, end_ts), 0, "psnobj end_ts"},
    {"min_price", T_DOUBLE, offsetof(PriceSegmentNode, min_price), 0, "psnobj min_price"},
    {"min_price_index", T_INT, offsetof(PriceSegmentNode, min_price_index), 0, "psnobj min_price_index"},
    {"min_price_ts", T_LONG, offsetof(PriceSegmentNode, min_price_ts), 0, "psnobj min_price_ts"},
    {"max_price", T_DOUBLE, offsetof(PriceSegmentNode, max_price), 0, "psnobj max_price"},
    {"max_price_index", T_INT, offsetof(PriceSegmentNode, max_price_index), 0, "psnobj max_price_index"},
    {"max_price_ts", T_LONG, offsetof(PriceSegmentNode, max_price_ts), 0, "psnobj max_price_ts"},
    {"parent", T_OBJECT, offsetof(PriceSegmentNode, parent), 0, "psnobj parent"},
    {"seg_start", T_OBJECT, offsetof(PriceSegmentNode, seg_start), 0, "psnobj seg_start"},
    {"seg_mid", T_OBJECT, offsetof(PriceSegmentNode, seg_mid), 0, "psnobj seg_mid"},
    {"seg_end", T_OBJECT, offsetof(PriceSegmentNode, seg_end), 0, "psnobj seg_end"},
    {"percent", T_DOUBLE, offsetof(PriceSegmentNode, percent), 0, "psnobj percent"},
    {"depth", T_INT, offsetof(PriceSegmentNode, depth), 0, "psnobj depth"},
    {"type", T_INT, offsetof(PriceSegmentNode, type), 0, "psnobj type"},
    {"mode", T_INT, offsetof(PriceSegmentNode, mode), 0, "psnobj mode"},
    {"half_split", T_INT, offsetof(PriceSegmentNode, half_split), 0, "psnobj half_split"},
    {"_is_leaf", T_INT, offsetof(PriceSegmentNode, _is_leaf), 0, "psnobj _is_leaf"},
    {NULL}  /* Sentinel */
};

static PyMethodDef PriceSegmentNode_methods[] = {
    {"split", (PyCFunction)PriceSegmentNode_split, METH_VARARGS|METH_KEYWORDS,
     "Split PriceSegmentNode",
    },
    {"update_percent", (PyCFunction)PriceSegmentNode_update_percent, METH_NOARGS,
     "Update percent PriceSegmentNode",
    },
    {"is_leaf", (PyCFunction)PriceSegmentNode_is_leaf, METH_NOARGS,
     "Is Leaf PriceSegmentNode",
    },
    {NULL}  /* Sentinel */
};

static PyTypeObject PriceSegmentNode_MyTestType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "PriceSegmentNode.PriceSegmentNode",                 /*tp_name*/
    sizeof(PriceSegmentNode),               /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)PriceSegmentNode_dealloc,   /*tp_dealloc*/
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
    "PriceSegmentNode objects",             /* tp_doc */
    0,                         /* tp_traverse */
    0,                         /* tp_clear */
    0,                         /* tp_richcompare */
    0,                         /* tp_weaklistoffset */
    0,                         /* tp_iter */
    0,                         /* tp_iternext */
    PriceSegmentNode_methods,               /* tp_methods */
    PriceSegmentNode_members,               /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)PriceSegmentNode_init,        /* tp_init */
    0,                         /* tp_alloc */
    PriceSegmentNode_new,                   /* tp_new */
};

#ifndef PyMODINIT_FUNC  /* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif
