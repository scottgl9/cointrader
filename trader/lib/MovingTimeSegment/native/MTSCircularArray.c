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
    double value;
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "dl", kwlist,
                                     &value, &ts))
        return NULL;

}

static PyObject *MTSCircularArray_ready(MTSCircularArray* self, PyObject *args)
{
    Py_INCREF(Py_False);
    return Py_False;
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
