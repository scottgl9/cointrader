#include <Python.h>
#include <structmember.h>

typedef struct {
    PyObject_HEAD
    /* internal data. */
    int window;
    int age;
    double result;
    PyListObject *values;
} ValueLag;

static void
ValueLag_dealloc(ValueLag* self)
{
    //if (self->values)
    //    self->ob_type->tp_free(self->values);
    Py_XDECREF(self->values);
    self->ob_type->tp_free((PyObject*)self);
}

static PyObject *
ValueLag_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    ValueLag *self;

    self = (ValueLag *)type->tp_alloc(type, 0);
    self->window = 0;
    self->age = 0;
    self->result = 0;
    self->values = (PyListObject*)PyList_New(0);

    return (PyObject *)self;
}

static int
ValueLag_init(ValueLag *self, PyObject *args, PyObject *kwds)
{
    if (! PyArg_ParseTuple(args, "i", &self->window))
        return -1;

    return 0;
}

static PyMemberDef ValueLag_members[] = {
    {"window", T_INT, offsetof(ValueLag, window), 0, "valuelagobj window"},
    {"age", T_INT, offsetof(ValueLag, age), 0, "valuelagobj age"},
    {"result", T_DOUBLE, offsetof(ValueLag, result), 0, "valuelagobj result"},
    {"values", T_OBJECT, offsetof(ValueLag, values), 0, "valuelagobj values"},
    {NULL}  /* Sentinel */
};

static PyObject *
ValueLag_update(ValueLag* self, PyObject *args)
{
    double tail;
    double value;
    int size;
    PyObject *result;

    if (! PyArg_ParseTuple(args, "d", &value)) {
        return NULL;
    }

    size = PyList_Size((PyObject*)self->values);

    if (size < self->window) {
        tail = 0.0;
        PyList_Append((PyObject *)self->values, Py_BuildValue("d", value));
        return Py_BuildValue("d", self->result);
    }

    tail = PyFloat_AsDouble(PyList_GetItem((PyObject *)self->values, self->age));
    PyList_SetItem((PyObject *)self->values, self->age, Py_BuildValue("d", value));

    self->result = tail;
    self->age = (self->age + 1) % self->window;

    result = Py_BuildValue("d", self->result);
    return result;
}

static PyObject *ValueLag_ready(ValueLag* self, PyObject *args)
{
    int size;
    size = PyList_Size((PyObject*)self->values);
    if (size == self->window) {
        return Py_True;
    }
    return Py_False;
}

static PyMethodDef ValueLag_methods[] = {
    {"update", (PyCFunction)ValueLag_update, METH_VARARGS,
     "Update ValueLag",
    },
    {"ready", (PyCFunction)ValueLag_ready, METH_VARARGS,
     "Ready ValueLag",
    },
    {NULL}  /* Sentinel */
};

static PyTypeObject ValueLag_MyTestType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "ValueLag.ValueLag",                 /*tp_name*/
    sizeof(ValueLag),               /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)ValueLag_dealloc,   /*tp_dealloc*/
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
    "ValueLag objects",             /* tp_doc */
    0,                         /* tp_traverse */
    0,                         /* tp_clear */
    0,                         /* tp_richcompare */
    0,                         /* tp_weaklistoffset */
    0,                         /* tp_iter */
    0,                         /* tp_iternext */
    ValueLag_methods,               /* tp_methods */
    ValueLag_members,               /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)ValueLag_init,        /* tp_init */
    0,                         /* tp_alloc */
    ValueLag_new,                   /* tp_new */
};

//static PyMethodDef ValueLag_methods[] = {
//    {NULL}  /* Sentinel */
//};

#ifndef PyMODINIT_FUNC  /* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif
PyMODINIT_FUNC
initValueLag(void)
{
    PyObject* m;

    if (PyType_Ready(&ValueLag_MyTestType) < 0)
        return;

    m = Py_InitModule3("ValueLag", ValueLag_methods,
                       "For a window of size N, return value N values ago");

    Py_INCREF(&ValueLag_MyTestType);
    PyModule_AddObject(m, "ValueLag", (PyObject *)&ValueLag_MyTestType);
}
