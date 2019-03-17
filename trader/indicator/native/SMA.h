#include <Python.h>
#include <structmember.h>

typedef struct {
    PyObject_HEAD
    /* internal data. */
    int window;
    int age;
    double sum;
    double result;
    PyListObject *values;
} SMA;

static void SMA_dealloc(SMA* self);
static PyObject *SMA_new(PyTypeObject *type, PyObject *args, PyObject *kwds);
static int SMA_init(SMA *self, PyObject *args, PyObject *kwds);
static PyObject *SMA_update(SMA* self, PyObject *args);

static PyMemberDef SMA_members[] = {
    {"window", T_INT, offsetof(SMA, window), 0, "smaobj window"},
    {"age", T_INT, offsetof(SMA, age), 0, "smaobj age"},
    {"sum", T_DOUBLE, offsetof(SMA, sum), 0, "smaobj sum"},
    {"result", T_DOUBLE, offsetof(SMA, result), 0, "smaobj result"},
    {"values", T_OBJECT, offsetof(SMA, values), 0, "smaobj values"},
    {NULL}  /* Sentinel */
};

static PyMethodDef SMA_methods[] = {
    {"update", (PyCFunction)SMA_update, METH_VARARGS,
     "Update SMA",
    },
    {NULL}  /* Sentinel */
};

static PyTypeObject SMA_MyTestType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "SMA.SMA",                 /*tp_name*/
    sizeof(SMA),               /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)SMA_dealloc,   /*tp_dealloc*/
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
    "SMA objects",             /* tp_doc */
    0,                         /* tp_traverse */
    0,                         /* tp_clear */
    0,                         /* tp_richcompare */
    0,                         /* tp_weaklistoffset */
    0,                         /* tp_iter */
    0,                         /* tp_iternext */
    SMA_methods,               /* tp_methods */
    SMA_members,               /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)SMA_init,        /* tp_init */
    0,                         /* tp_alloc */
    SMA_new,                   /* tp_new */
};

#ifndef PyMODINIT_FUNC  /* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif
