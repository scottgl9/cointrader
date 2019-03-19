#include <Python.h>
#include <structmember.h>

typedef struct {
    PyObject_HEAD
    /* internal data. */
    char *symbol;
    double open;
    double close;
    double low;
    double high;
    double volume_base;
    double volume_quote;
    double volume;
    long ts;
} Kline;

static void Kline_dealloc(Kline* self);
static PyObject *Kline_new(PyTypeObject *type, PyObject *args, PyObject *kwds);
static int Kline_init(Kline *self, PyObject *args, PyObject *kwds);

static PyMemberDef Kline_members[] = {
    {"symbol", T_STRING, offsetof(Kline, symbol), 0, "klineobj symbol"},
    {"open", T_DOUBLE, offsetof(Kline, open), 0, "klineobj open"},
    {"close", T_DOUBLE, offsetof(Kline, close), 0, "klineobj close"},
    {"low", T_DOUBLE, offsetof(Kline, low), 0, "klineobj low"},
    {"high", T_DOUBLE, offsetof(Kline, high), 0, "klineobj high"},
    {"volume_base", T_DOUBLE, offsetof(Kline, volume_base), 0, "klineobj volume_base"},
    {"volume_quote", T_DOUBLE, offsetof(Kline, volume_quote), 0, "klineobj volume_quote"},
    {"volume", T_DOUBLE, offsetof(Kline, volume), 0, "klineobj volume"},
    {"ts", T_LONG, offsetof(Kline, ts), 0, "klineobj ts"},
    {NULL}  /* Sentinel */
};

static PyMethodDef Kline_methods[] = {
    {NULL}  /* Sentinel */
};

static PyTypeObject Kline_MyTestType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "Kline.Kline",                 /*tp_name*/
    sizeof(Kline),               /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)Kline_dealloc,   /*tp_dealloc*/
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
    "Kline objects",             /* tp_doc */
    0,                         /* tp_traverse */
    0,                         /* tp_clear */
    0,                         /* tp_richcompare */
    0,                         /* tp_weaklistoffset */
    0,                         /* tp_iter */
    0,                         /* tp_iternext */
    Kline_methods,               /* tp_methods */
    Kline_members,               /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)Kline_init,        /* tp_init */
    0,                         /* tp_alloc */
    Kline_new,                   /* tp_new */
};

#ifndef PyMODINIT_FUNC  /* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif
