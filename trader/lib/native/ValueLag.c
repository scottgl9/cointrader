#include "ValueLag.h"

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
