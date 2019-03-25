#include "MTSCircularArray.h"

static void
MTSCircularArray_dealloc(MTSCircularArray* self)
{
    Py_XDECREF(self->values);
    Py_XDECREF(self->timestamps);
    self->ob_type->tp_free((PyObject*)self);
}

static PyObject *
MTSCircularArray_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    MTSCircularArray *self;

    self = (MTSCircularArray *)type->tp_alloc(type, 0);
    self->max_win_size = 0;
    self->win_secs = 0;
    self->win_secs_ts = 0;
    self->minmax = FALSE;
    self->values = NULL;
    self->timestamps = NULL;
    self->current_size = 0;
    self->end_age = 0;
    self->start_age = 0;
    self->age = 0;
    self->min_value = 0;
    self->min_age = 0;
    self->max_value = 0;
    self->max_age = 0;
    self->sum = 0;
    self->sum_count = 0;

    return (PyObject *)self;
}

static int
MTSCircularArray_init(MTSCircularArray *self, PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = {"win_secs", "max_win_size", "minmax", NULL};
    PyObject *minmax;

    int minutes=0;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "iiO", kwlist,
                                     &self->win_secs, &self->max_win_size, &minmax))
        return -1;

    self->minmax = PyObject_IsTrue(minmax);
    self->win_secs_ts = self->win_secs * 1000;
    self->values = (PyListObject*)PyList_New(self->max_win_size);
    self->timestamps = (PyListObject*)PyList_New(self->max_win_size);

    Py_XDECREF(minmax);

    return 0;
}

static PyObject *
MTSCircularArray_add(MTSCircularArray* self, PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = {"value", "ts", NULL};
    long ts;
    double value, prev_value;
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "dl", kwlist,
                                     &value, &ts))
        return NULL;

    if (self->minmax) {
        if (self->min_value == 0 || value < self->min_value) {
            self->min_value = value;
            self->min_age = 0;
        } else {
            self->min_age += 1;
        }

        if (value > self->max_value) {
            self->max_value = value;
            self->max_age = 0;
        } else {
            self->max_age += 1;
        }
    }

    if (self->current_size != 0) {
        prev_value = PyFloat_AS_DOUBLE(PyList_GetItem((PyObject *)self->values, self->age));
        self->sum -= prev_value;
        self->sum_count--;
    }

    //self._values[int(self.age)] = value;
    //self._timestamps[int(self.age)] = ts;
    self->sum += value;
    self->sum_count++;
    PyList_SetItem((PyObject *)self->values, self->age, Py_BuildValue("d", value));
    PyList_SetItem((PyObject *)self->timestamps, self->age, Py_BuildValue("l", ts));

    // if start_age back at index 0, and diff in timestamps >= win_sec_ts,
    // then resize current_size of circular array

    if (self->start_age == 0) {
        double ts0 = PyInt_AsLong(PyList_GetItem((PyObject *)self->timestamps, 0));
        if ((ts - ts0) >= self->win_secs_ts) {
            self->current_size = self->age;
        }
    }

    // index of most recent value and ts
    self->end_age = self->age;

    if (self->current_size != 0) {
        self->start_age = (self->start_age + 1) % self->current_size;
        self->age = (self->age + 1) % self->current_size;
    } else {
        self->age = (self->age + 1) % self->max_win_size;
    }

    if (self->minmax && self->current_size != 0) {
        if (self->min_age > self->current_size) {
            double cur_value = 0;
            int min_age=0;
            double min_value = 0;
            int age = self->start_age;

            for (int i=0; i<self->current_size; i++) {
                cur_value = PyFloat_AS_DOUBLE(PyList_GetItem((PyObject *)self->values, age));
                if (min_value == 0 || cur_value < min_value) {
                    min_value = cur_value;
                    min_age = age;
                }
                age = (age + 1) % self->current_size;
            }
            self->min_value = min_value;
            self->min_age = min_age;
        }

        if (self->max_age > self->current_size) {
            double cur_value = 0;
            int max_age=0;
            double max_value = 0;
            int age = self->start_age;

            for (int i=0; i<self->current_size; i++) {
                cur_value = PyFloat_AS_DOUBLE(PyList_GetItem((PyObject *)self->values, age));
                if (max_age < cur_value) {
                    max_value = cur_value;
                    max_age = age;
                }
                age = (age + 1) % self->current_size;
            }
            self->max_value = max_value;
            self->max_age = age;
        }
    }

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *MTSCircularArray_values(MTSCircularArray* self, PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = {"ordered", NULL};
    BOOL ordered;
    int age, size;
    double value;
    PyObject *result, *ordered_obj;
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O", kwlist,
                                     &ordered_obj))
        return NULL;

    ordered = PyObject_IsTrue(ordered_obj);
    Py_XDECREF(ordered_obj);

    if (!ordered) {
        if (self->current_size != 0) {
            return PyList_GetSlice((PyObject *)self->values, 0, self->current_size);
        } else {
            return PyList_GetSlice((PyObject *)self->values, 0, self->end_age);
        }
    }

    age = self->start_age;
    if (self->current_size != 0) {
        size = self->current_size;
    } else {
        size = self->age;
    }

    result = PyList_New(size);
    for (int i=0; i<size; i++) {
        value = PyFloat_AS_DOUBLE(PyList_GetItem((PyObject *)self->values, age));
        PyList_SetItem((PyObject *)self->values, i, Py_BuildValue("d", value));
        age = (age + 1) % size;
    }
    return result;
}

static PyObject *MTSCircularArray_timestamps(MTSCircularArray* self, PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = {"ordered", NULL};
    BOOL ordered;
    int age, size;
    double value;
    PyObject *result, *ordered_obj;
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O", kwlist,
                                     &ordered_obj))
        return NULL;

    ordered = PyObject_IsTrue(ordered_obj);
    Py_XDECREF(ordered_obj);

    if (!ordered) {
        if (self->current_size != 0) {
            return PyList_GetSlice((PyObject *)self->timestamps, 0, self->current_size);
        } else {
            return PyList_GetSlice((PyObject *)self->timestamps, 0, self->end_age);
        }
    }

    age = self->start_age;
    if (self->current_size != 0) {
        size = self->current_size;
    } else {
        size = self->age;
    }

    result = PyList_New(size);
    for (int i=0; i<size; i++) {
        value = PyInt_AsLong(PyList_GetItem((PyObject *)self->timestamps, age));
        PyList_SetItem((PyObject *)self->timestamps, i, Py_BuildValue("l", value));
        age = (age + 1) % size;
    }
    return result;
}

static PyObject *MTSCircularArray_ready(MTSCircularArray* self, PyObject *args)
{
    Py_INCREF(Py_False);
    return Py_False;
}

static PyObject *MTSCircularArray_start_index(MTSCircularArray* self, PyObject *args)
{
    PyObject *result = Py_BuildValue("d", self->start_age);
    return result;
}

static PyObject *MTSCircularArray_last_index(MTSCircularArray* self, PyObject *args)
{
    PyObject *result = Py_BuildValue("d", self->end_age);
    return result;
}

static PyObject *MTSCircularArray_get_value(MTSCircularArray* self, PyObject *args)
{
    int index, pos;
    if (! PyArg_ParseTuple(args, "i", &index)) {
        return NULL;
    }

    if (self->current_size != 0) {
        pos = (self->start_age + index) % self->current_size;
    } else {
        pos = index;
    }
    return PyList_GetItem((PyObject *)self->values, pos);
}

static PyObject *MTSCircularArray_set_value(MTSCircularArray* self, PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = {"index", "value", NULL};
    int index, pos;
    double value;
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "id", kwlist,
                                     &index, &value))
        return NULL;

    pos = (self->start_age + index) % self->current_size;
    //self._values[pos] = value
    PyList_SetItem((PyObject *)self->values, pos, Py_BuildValue("d", value));
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *MTSCircularArray_first_value(MTSCircularArray* self, PyObject *args)
{
    return PyList_GetItem((PyObject *)self->values, self->start_age);
}

static PyObject *MTSCircularArray_last_value(MTSCircularArray* self, PyObject *args)
{
    return PyList_GetItem((PyObject *)self->values, self->end_age);
}

static PyObject *MTSCircularArray_first_ts(MTSCircularArray* self, PyObject *args)
{
    return PyList_GetItem((PyObject *)self->timestamps, self->start_age);
}

static PyObject *MTSCircularArray_last_ts(MTSCircularArray* self, PyObject *args)
{
    return PyList_GetItem((PyObject *)self->timestamps, self->end_age);
}

static PyObject *MTSCircularArray_min_value(MTSCircularArray* self, PyObject *args)
{
    PyObject *result = Py_BuildValue("d", self->min_value);
    return result;
}

static PyObject *MTSCircularArray_max_value(MTSCircularArray* self, PyObject *args)
{
    PyObject *result = Py_BuildValue("d", self->max_value);
    return result;
}

static PyObject *MTSCircularArray_min_value_ts(MTSCircularArray* self, PyObject *args)
{
    return PyList_GetItem((PyObject *)self->timestamps, self->min_age);
}

static PyObject *MTSCircularArray_max_value_ts(MTSCircularArray* self, PyObject *args)
{
    return PyList_GetItem((PyObject *)self->timestamps, self->max_age);
}

static PyObject *MTSCircularArray_get_sum(MTSCircularArray* self, PyObject *args)
{
    PyObject *result = Py_BuildValue("d", self->sum);
    return result;
}

static PyObject *MTSCircularArray_get_sum_count(MTSCircularArray* self, PyObject *args)
{
    PyObject *result = Py_BuildValue("i", self->sum_count);
    return result;
}

PyMODINIT_FUNC
initMTSCircularArray(void)
{
    PyObject* m;

    if (PyType_Ready(&MTSCircularArray_MyTestType) < 0)
        return;

    m = Py_InitModule3("MTSCircularArray", MTSCircularArray_methods,
                       "MTS Circular Array");

    Py_INCREF(&MTSCircularArray_MyTestType);
    PyModule_AddObject(m, "MTSCircularArray", (PyObject *)&MTSCircularArray_MyTestType);
}
