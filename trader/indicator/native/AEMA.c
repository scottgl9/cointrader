// Auto-Scaling Exponential Moving Average (EMA) concept by Scott Glover
#include "AEMA.h"

static void
AEMA_dealloc(AEMA* self)
{
    Py_XDECREF(self->sma_values);
     Py_XDECREF(self->value_lag_values);
    self->ob_type->tp_free((PyObject*)self);
}

static PyObject *
AEMA_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    AEMA *self;

    self = (AEMA *)type->tp_alloc(type, 0);
    self->win = 0;
    self->scale_interval_secs = 0;
    self->scale = 1.0;
    self->last_scale = 1.0;
    self->esf = 0;
    self->result = 0;
    self->last_result = 0;
    self->count = 0;
    self->lag_window = 0;
    self->sma_age = 0;
    self->sma_sum = 0;
    self->sma_result = 0;
    self->auto_last_ts = 0;
    self->auto_counter = 0;
    self->sma_values = (PyListObject*)PyList_New(0);
    self->value_lag_age = 0;
    self->value_lag_values = (PyListObject*)PyList_New(0);

    return (PyObject *)self;
}

static int
AEMA_init(AEMA *self, PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = {"win", "scale_interval_secs", "lag_window", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "i|li", kwlist,
                                     &self->win, &self->scale_interval_secs, &self->lag_window, &self->lag_window))
        return -1;

    return 0;
}

// incorporate SMA into AEMA class
static double SMA_update(AEMA* self, double value)
{
    double tail;
    int size;

    size = PyList_Size((PyObject*)self->sma_values);

    if (size < self->win) {
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

    self->sma_age = (self->sma_age + 1) % self->win;
    return self->sma_result;
}

static PyObject *
AEMA_update(AEMA* self, PyObject *args,  PyObject *kwds)
{
    double value;
    long ts;
    double last_result;
    PyObject *result;

    static char *kwlist[] = {"value", "ts", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "dl", kwlist,
                                     &value, &ts))
        return NULL;

    if (self->auto_last_ts == 0) {
        self->auto_last_ts = ts;
    }

    self->auto_counter++;

    if ((ts - self->auto_last_ts) > self->scale_interval_secs * 1000) {
        self->scale = (double)self->auto_counter;
        self->auto_counter = 0;
        self->auto_last_ts = ts;
    }

    if (self->count < self->win) {
        self->result = SMA_update(self, value);
        self->count++;
        return Py_BuildValue("d", self->result);
    }

    last_result = self->result;

    if (self->esf == 0 || self->scale != self->last_scale) {
        self->esf = 2.0 / (((double)self->win) * self->scale + 1.0);
        self->last_scale = self->scale;
    }

    if (self->lag_window != 0) {
        int value_lag_size = PyList_Size((PyObject*)self->value_lag_values);

        if (value_lag_size < self->lag_window) {
            double tail = 0.0;
            PyList_Append((PyObject *)self->value_lag_values, Py_BuildValue("d", self->result));
            self->last_result = tail;
        } else {
            double tail = PyFloat_AsDouble(PyList_GetItem((PyObject *)self->value_lag_values, self->value_lag_age));
            PyList_SetItem((PyObject *)self->value_lag_values, self->value_lag_age, Py_BuildValue("d", self->result));

            self->last_result = tail;
            self->value_lag_age = (self->value_lag_age + 1) % self->lag_window;
        }
    } else {
        self->last_result = self->result;
    }

    self->result = last_result + self->esf * (value - last_result);

    result = Py_BuildValue("d", self->result);
    return result;
}

static PyObject *AEMA_ready(AEMA* self, PyObject *args)
{
    int size;
    size = PyList_Size((PyObject*)self->sma_values);
    if (size == self->win) {
        Py_INCREF(Py_True);
        return Py_True;
    }
    Py_INCREF(Py_False);
    return Py_False;
}

PyMODINIT_FUNC
initAEMA(void)
{
    PyObject* m;

    if (PyType_Ready(&AEMA_MyTestType) < 0)
        return;

    m = Py_InitModule3("AEMA", AEMA_methods,
                       "Exponential Moving Average (AEMA)");

    Py_INCREF(&AEMA_MyTestType);
    PyModule_AddObject(m, "AEMA", (PyObject *)&AEMA_MyTestType);
}
