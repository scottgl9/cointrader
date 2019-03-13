#include <Python.h>
#include <structmember.h>

typedef struct {
    PyObject_HEAD
    /* Your internal 'loc' data. */
    int loc;
} SMA;

static void
SMA_dealloc(Test* self)
{
    self->ob_type->tp_free((PyObject*)self);
}

static PyObject *
SMA_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    SMA *self;

    self = (Test *)type->tp_alloc(type, 0);
    self->loc = 0;

    return (PyObject *)self;
}

static int
SMA_init(SMA *self, PyObject *args, PyObject *kwds)
{
    if (! PyArg_ParseTuple(args, "i", &self->loc))
        return -1;

    return 0;
}

static PyMemberDef SMA_members[] = {
    {"loc", T_INT, offsetof(SMA, loc), 0, "mysmaobj loc"},
    {NULL}  /* Sentinel */
};

static PyObject *
SMA_update(SMA* self, PyObject *args)
{
    int data;
    PyObject *result;

    if (! PyArg_ParseTuple(args, "i", &data)) {
        return NULL;
    }

    /* We'll just return data + loc as our result. */
    result = Py_BuildValue("i", data + self->loc);

    return result;
}
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
    SMA_methods,      /* tp_methods */
    SMA_members,      /* tp_members */
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

static PyMethodDef SMA_methods[] = {
    {NULL}  /* Sentinel */
};

#ifndef PyMODINIT_FUNC  /* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif
PyMODINIT_FUNC
init_SMA(void)
{
    PyObject* m;

    if (PyType_Ready(&SMA_MyTestType) < 0)
        return;

    m = Py_InitModule3("SMA", SMA_methods,
                       "Simple Moving Average (SMA)");

    Py_INCREF(&SMA_MyTestType);
    PyModule_AddObject(m, "SMA", (PyObject *)&SMA_MyTestType);
}
