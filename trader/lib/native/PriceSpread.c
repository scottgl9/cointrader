#include "PriceSpread.h"

static void
PriceSpread_dealloc(PriceSpread* self)
{
    Py_XDECREF(self->values);
    self->ob_type->tp_free((PyObject*)self);
}

static PyObject *
PriceSpread_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PriceSpread *self;

    self = (PriceSpread *)type->tp_alloc(type, 0);
    self->window = 0;
    self->age = 0;
    self->sum = 0;
    self->sma_result = 0;
    self->values = (PyListObject*)PyList_New(0);
    self->ask_price = 0;
    self->bid_price = 0;
    self->last_ask_price = 0;
    self->last_bid_price = 0;

    return (PyObject *)self;
}

static int
PriceSpread_init(PriceSpread *self, PyObject *args, PyObject *kwds)
{
    if (! PyArg_ParseTuple(args, "i", &self->window))
        return -1;

    return 0;
}

static PyObject *
PriceSpread_update(PriceSpread* self, PyObject *args)
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
        self->sma_result = self->sum / size;
    } else {
        self->sum = 0;
        self->sma_result = value;
    }

    if (value > self->sma_result) {
        if (value != self->last_bid_price && value != self->bid_price) {
            self->last_ask_price = self->ask_price;
            self->ask_price = value;
        }
    } else if (value < self->sma_result) {
        if (value != self->last_ask_price && value != self->ask_price) {
            self->last_bid_price = self->bid_price;
            self->bid_price = value;
        }
    }

    self->age = (self->age + 1) % self->window;
    result = Py_BuildValue("d", self->sma_result);
    return result;
}

PyMODINIT_FUNC
initPriceSpread(void)
{
    PyObject* m;

    if (PyType_Ready(&PriceSpread_MyTestType) < 0)
        return;

    m = Py_InitModule3("PriceSpread", PriceSpread_methods,
                       "Simple Moving Average (PriceSpread)");

    Py_INCREF(&PriceSpread_MyTestType);
    PyModule_AddObject(m, "PriceSpread", (PyObject *)&PriceSpread_MyTestType);
}
