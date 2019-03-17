#include "SMA.h"

static void
SMA_dealloc(SMA* self)
{
    Py_XDECREF(self->values);
    self->ob_type->tp_free((PyObject*)self);
}

static PyObject *
SMA_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    SMA *self;

    self = (SMA *)type->tp_alloc(type, 0);
    self->window = 0;
    self->age = 0;
    self->sum = 0;
    self->result = 0;
    self->values = (PyListObject*)PyList_New(0);

    return (PyObject *)self;
}

static int
SMA_init(SMA *self, PyObject *args, PyObject *kwds)
{
    if (! PyArg_ParseTuple(args, "i", &self->window))
        return -1;

    //self->values = (PyListObject*)PyList_New(self->window);

    return 0;
}

static PyObject *
SMA_update(SMA* self, PyObject *args)
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
    } else {
        tail = PyFloat_AsDouble(PyList_GetItem((PyObject *)self->values, self->age));
        PyList_SetItem((PyObject *)self->values, self->age, Py_BuildValue("d", value));
    }

    self->sum += value - tail;
    if (size != 0)  {
        self->result = self->sum / size;
    } else {
        self->sum = 0;
        self->result = value;
    }

    self->age = (self->age + 1) % self->window;
    result = Py_BuildValue("d", self->result);
    return result;
}

PyMODINIT_FUNC
initSMA(void)
{
    PyObject* m;

    if (PyType_Ready(&SMA_MyTestType) < 0)
        return;

    m = Py_InitModule3("SMA", SMA_methods,
                       "Simple Moving Average (SMA)");

    Py_INCREF(&SMA_MyTestType);
    PyModule_AddObject(m, "SMA", (PyObject *)&SMA_MyTestType);
}
