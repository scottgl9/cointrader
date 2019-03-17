#include "EMA.h"

static void
EMA_dealloc(EMA* self)
{
    Py_XDECREF(self->sma_values);
    self->ob_type->tp_free((PyObject*)self);
}

static PyObject *
EMA_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    EMA *self;

    self = (EMA *)type->tp_alloc(type, 0);
    self->window = 0;
    self->weight = 0;
    self->scale = 1.0;
    self->esf = 0;
    self->result = 0;
    self->count = 0;
    self->sma_age = 0;
    self->sma_sum = 0;
    self->sma_result = 0;
    self->sma_values = (PyListObject*)PyList_New(0);

    return (PyObject *)self;
}

static int
EMA_init(EMA *self, PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = {"weight", "scale", "lag_window", "slope_window", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "d|dii", kwlist,
                                     &self->weight, &self->scale, &self->lag_window, &self->slope_window))
        return -1;

    self->window = (int)self->weight;

    return 0;
}

// incorporate SMA into EMA class
static double SMA_update(EMA* self, double value)
{
    double tail;
    int size;

    size = PyList_Size((PyObject*)self->sma_values);

    if (size < self->window) {
        tail = 0.0;
        PyList_Append((PyObject *)self->sma_values, Py_BuildValue("d", value));
    } else {
        tail = PyFloat_AsDouble(PyList_GetItem((PyObject *)self->sma_values, self->sma_age));
        PyList_SetItem((PyObject *)self->sma_values, self->sma_age, Py_BuildValue("d", value));
    }

    self->sma_sum += value - tail;
    if (size != 0)  {
        self->sma_result = self->sma_sum / size;
    } else {
        self->sma_sum = 0;
        self->sma_result = value;
    }

    self->sma_age = (self->sma_age + 1) % self->window;
    return self->sma_result;
}

static PyObject *
EMA_update(EMA* self, PyObject *args)
{
    double value;
    double last_result;
    PyObject *result;

    if (! PyArg_ParseTuple(args, "d", &value)) {
        return NULL;
    }

    if (self->count < self->window) {
        self->result = SMA_update(self, value);
        self->count++;
        return Py_BuildValue("d", self->result);
    }

    last_result = self->result;

    if (self->esf == 0) {
        self->esf = 2.0 / (self->weight * self->scale + 1.0);
    }

    self->result = last_result + self->esf * (value - last_result);

    result = Py_BuildValue("d", self->result);
    return result;
}

static PyObject *EMA_ready(EMA* self, PyObject *args)
{
    int size;
    size = PyList_Size((PyObject*)self->sma_values);
    if (size == self->window) {
        Py_INCREF(Py_True);
        return Py_True;
    }
    Py_INCREF(Py_False);
    return Py_False;
}

PyMODINIT_FUNC
initEMA(void)
{
    PyObject* m;

    if (PyType_Ready(&EMA_MyTestType) < 0)
        return;

    m = Py_InitModule3("EMA", EMA_methods,
                       "Exponential Moving Average (EMA)");

    Py_INCREF(&EMA_MyTestType);
    PyModule_AddObject(m, "EMA", (PyObject *)&EMA_MyTestType);
}
