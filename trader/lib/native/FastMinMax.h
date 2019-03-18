#include <Python.h>
#include <structmember.h>

typedef struct {
    PyObject_HEAD
    /* internal data. */
    int window;
    int age;
    double result;
    PyListObject *values;
} FastMinMax;

static void FastMinMax_dealloc(FastMinMax* self);
static PyObject *FastMinMax_new(PyTypeObject *type, PyObject *args, PyObject *kwds);
static int FastMinMax_init(FastMinMax *self, PyObject *args, PyObject *kwds);
static PyObject *FastMinMax_append(FastMinMax* self, PyObject *args);
static PyObject *FastMinMax_remove(FastMinMax* self, PyObject *args);
static PyObject *FastMinMax_min(FastMinMax* self, PyObject *args);
static PyObject *FastMinMax_max(FastMinMax* self, PyObject *args);

static PyMemberDef FastMinMax_members[] = {
    {"window", T_INT, offsetof(FastMinMax, window), 0, "fastminmaxobj window"},
    {"age", T_INT, offsetof(FastMinMax, age), 0, "fastminmaxobj age"},
    {"result", T_DOUBLE, offsetof(FastMinMax, result), 0, "fastminmaxobj result"},
    {"values", T_OBJECT, offsetof(FastMinMax, values), 0, "fastminmaxobj values"},
    {NULL}  /* Sentinel */
};

static PyMethodDef FastMinMax_methods[] = {
    {"append", (PyCFunction)FastMinMax_append, METH_VARARGS,
     "Append FastMinMax",
    },
    {"remove", (PyCFunction)FastMinMax_remove, METH_VARARGS,
     "Remove FastMinMax",
    },
    {"min", (PyCFunction)FastMinMax_min, METH_NOARGS,
     "FastMinMax min",
    },
    {"max", (PyCFunction)FastMinMax_max, METH_NOARGS,
     "FastMinMax max",
    },
    {NULL}  /* Sentinel */
};

static PyTypeObject FastMinMax_MyTestType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "FastMinMax.FastMinMax",                 /*tp_name*/
    sizeof(FastMinMax),               /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)FastMinMax_dealloc,   /*tp_dealloc*/
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
    "FastMinMax objects",             /* tp_doc */
    0,                         /* tp_traverse */
    0,                         /* tp_clear */
    0,                         /* tp_richcompare */
    0,                         /* tp_weaklistoffset */
    0,                         /* tp_iter */
    0,                         /* tp_iternext */
    FastMinMax_methods,               /* tp_methods */
    FastMinMax_members,               /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)FastMinMax_init,        /* tp_init */
    0,                         /* tp_alloc */
    FastMinMax_new,                   /* tp_new */
};

#ifndef PyMODINIT_FUNC  /* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif
