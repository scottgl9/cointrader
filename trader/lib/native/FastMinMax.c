#include "FastMinMax.h"

static void
FastMinMax_dealloc(FastMinMax* self)
{
    //if (self->values)
    //    self->ob_type->tp_free(self->values);
    Py_XDECREF(self->values);
    self->ob_type->tp_free((PyObject*)self);
}

static PyObject *
FastMinMax_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    FastMinMax *self;

    self = (FastMinMax *)type->tp_alloc(type, 0);
    self->min_value = 0;
    self->min_value_index = -1;
    self->max_value = 0;
    self->max_value_index = -1;
    self->end_index = 0;
    self->values = (PyListObject*)PyList_New(0);

    return (PyObject *)self;
}

static int
FastMinMax_init(FastMinMax *self, PyObject *args, PyObject *kwds)
{
    //if (! PyArg_ParseTuple(args, "i", &self->window))
    //    return -1;

    return 0;
}

static PyObject *
FastMinMax_append(FastMinMax* self, PyObject *args)
{
    double value;

    if (! PyArg_ParseTuple(args, "d", &value)) {
        return NULL;
    }

    if (self->min_value == 0 || self->max_value == 0) {
        self->min_value = value;
        self->min_value_index = 0;
        self->max_value = value;
        self->max_value_index = 0;
        PyList_Append((PyObject *)self->values, Py_BuildValue("d", value));

        Py_INCREF(Py_None);
        return Py_None;
    }

    if (self->min_value != 0 && value < self->min_value) {
        self->min_value = value;
        self->min_value_index = self->end_index;
    } else if (value > self->max_value) {
        self->max_value = value;
        self->max_value_index = self->end_index;
    }

    PyList_Append((PyObject *)self->values, Py_BuildValue("d", value));
    self->end_index++;

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *FastMinMax_remove(FastMinMax* self, PyObject *args)
{
    int count;
    int size;
    PyObject *result;

    if (! PyArg_ParseTuple(args, "i", &count)) {
        return NULL;
    }

    size = PyList_Size((PyObject*)self->values);

    if (size <= count) {
        Py_INCREF(Py_None);
        return Py_None;
    }

    self->min_value_index -= count;
    self->max_value_index -= count;
    self->end_index -= count;

//    self.values = self.values[count:]

//    if self.min_value_index < 0:
//        self.min_value_index = min(xrange(len(self.values)), key=self.values.__getitem__)
//
//    self.min_value = self.values[self.min_value_index]
//
//    if self.max_value_index < 0:
//        self.max_value_index = max(xrange(len(self.values)), key=self.values.__getitem__)
//
//    self.max_value = self.values[self.max_value_index]

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *FastMinMax_min(FastMinMax* self, PyObject *args)
{
    return Py_BuildValue("d", self->min_value);
}

static PyObject *FastMinMax_max(FastMinMax* self, PyObject *args)
{
    return Py_BuildValue("d", self->max_value);
}

PyMODINIT_FUNC
initFastMinMax(void)
{
    PyObject* m;

    if (PyType_Ready(&FastMinMax_MyTestType) < 0)
        return;

    m = Py_InitModule3("FastMinMax", FastMinMax_methods,
                       "For a window of size N, return value N values ago");

    Py_INCREF(&FastMinMax_MyTestType);
    PyModule_AddObject(m, "FastMinMax", (PyObject *)&FastMinMax_MyTestType);
}
