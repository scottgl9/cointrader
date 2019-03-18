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

    if (self->min_value != 0 && value <= self->min_value) {
        self->min_value = value;
        self->min_value_index = self->end_index;
    } else if (value >= self->max_value) {
        self->max_value = value;
        self->max_value_index = self->end_index;
    }

    PyList_Append((PyObject *)self->values, Py_BuildValue("d", value));
    self->end_index+=1;

    Py_INCREF(Py_None);
    return Py_None;
}

static int get_min_value_index(PyListObject *values)
{
    int index = -1;
    int size = Py_SIZE((PyObject*)values);
    double value, min_value = 0;
    for (int i=0; i<size; i++) {
        value = PyFloat_AS_DOUBLE(PyList_GET_ITEM((PyObject *)values, i));
        if (min_value >= value || min_value == 0)
            index = i;
            min_value = value;
    }
    return index;
}

static int get_max_value_index(PyListObject *values)
{
    int index = -1;
    int size = Py_SIZE((PyObject*)values);
    double value, max_value = 0;
    for (int i=0; i<size; i++) {
        value = PyFloat_AS_DOUBLE(PyList_GET_ITEM((PyObject *)values, i));
        if (max_value <= value)
            index = i;
            max_value = value;
    }
    return index;
}

static PyObject *FastMinMax_remove(FastMinMax* self, PyObject *args)
{
    int count;
    int size;
    PyObject *values;

    if (! PyArg_ParseTuple(args, "i", &count)) {
        return NULL;
    }

    size = Py_SIZE((PyObject*)self->values);

    if (size <= count) {
        Py_INCREF(Py_None);
        return Py_None;
    }

    self->min_value_index -= count;
    self->max_value_index -= count;
    self->end_index -= count;

    // self.values = self.values[count:]
    values = PyList_GetSlice((PyObject *)self->values, count, size);
    Py_XDECREF(self->values);
    self->values = (PyListObject *)values;

    if (self->min_value_index < 0) {
        self->min_value_index = get_min_value_index(self->values);
    }

    self->min_value = PyFloat_AS_DOUBLE(PyList_GetItem((PyObject *)values, self->min_value_index));

    if (self->max_value_index < 0) {
        self->max_value_index = get_max_value_index(self->values);
    }

    self->max_value = PyFloat_AS_DOUBLE(PyList_GetItem((PyObject *)values, self->max_value_index));

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
                       "Track minimum and maximum value in a set of values");

    Py_INCREF(&FastMinMax_MyTestType);
    PyModule_AddObject(m, "FastMinMax", (PyObject *)&FastMinMax_MyTestType);
}
