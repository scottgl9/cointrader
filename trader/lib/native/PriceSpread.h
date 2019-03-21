#include <Python.h>
#include <structmember.h>

typedef struct {
    PyObject_HEAD
    /* internal data. */
    int window;
    int age;
    double sum;
    double sma_result;
    double ask_price;
    double bid_price;
    double last_ask_price;
    double last_bid_price;
    PyListObject *values;
} PriceSpread;

static void PriceSpread_dealloc(PriceSpread* self);
static PyObject *PriceSpread_new(PyTypeObject *type, PyObject *args, PyObject *kwds);
static int PriceSpread_init(PriceSpread *self, PyObject *args, PyObject *kwds);
static PyObject *PriceSpread_update(PriceSpread* self, PyObject *args);

static PyMemberDef PriceSpread_members[] = {
    {"window", T_INT, offsetof(PriceSpread, window), 0, "pricespreadobj window"},
    {"age", T_INT, offsetof(PriceSpread, age), 0, "pricespreadobj age"},
    {"sum", T_DOUBLE, offsetof(PriceSpread, sum), 0, "pricespreadobj sum"},
    {"sma_result", T_DOUBLE, offsetof(PriceSpread, sma_result), 0, "pricespreadobj sma_result"},
    {"values", T_OBJECT, offsetof(PriceSpread, values), 0, "pricespreadobj values"},
    {"ask_price", T_DOUBLE, offsetof(PriceSpread, ask_price), 0, "pricespreadobj ask_price"},
    {"bid_price", T_DOUBLE, offsetof(PriceSpread, bid_price), 0, "pricespreadobj bid_price"},
    {"last_ask_price", T_DOUBLE, offsetof(PriceSpread, last_ask_price), 0, "pricespreadobj last_ask_price"},
    {"last_bid_price", T_DOUBLE, offsetof(PriceSpread, last_bid_price), 0, "pricespreadobj last_bid_price"},
    {NULL}  /* Sentinel */
};

static PyMethodDef PriceSpread_methods[] = {
    {"update", (PyCFunction)PriceSpread_update, METH_VARARGS,
     "Update PriceSpread",
    },
    {NULL}  /* Sentinel */
};

static PyTypeObject PriceSpread_MyTestType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "PriceSpread.PriceSpread",                 /*tp_name*/
    sizeof(PriceSpread),               /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)PriceSpread_dealloc,   /*tp_dealloc*/
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
    "PriceSpread objects",             /* tp_doc */
    0,                         /* tp_traverse */
    0,                         /* tp_clear */
    0,                         /* tp_richcompare */
    0,                         /* tp_weaklistoffset */
    0,                         /* tp_iter */
    0,                         /* tp_iternext */
    PriceSpread_methods,               /* tp_methods */
    PriceSpread_members,               /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)PriceSpread_init,        /* tp_init */
    0,                         /* tp_alloc */
    PriceSpread_new,                   /* tp_new */
};

#ifndef PyMODINIT_FUNC  /* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif
