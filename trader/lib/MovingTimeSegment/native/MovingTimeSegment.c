#include "MovingTimeSegment.h"

static void
MovingTimeSegment_dealloc(MovingTimeSegment* self)
{
    Py_XDECREF(self->values);
    Py_XDECREF(self->timestamps);
    self->ob_type->tp_free((PyObject*)self);
}

static PyObject *
MovingTimeSegment_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    MovingTimeSegment *self;

    self = (MovingTimeSegment *)type->tp_alloc(type, 0);
    self->seconds = 0;
    self->seconds_ts = 0;
    self->values = (PyListObject*)PyList_New(0);
    self->timestamps = (PyListObject*)PyList_New(0);
    self->min_value = 0;
    self->min_value_index = -1;
    self->max_value = 0;
    self->max_value_index = -1;
    // track moving sum of time segment values
    self->_sum = 0;
    self->_sum_count = 0;

    return (PyObject *)self;
}

static int
MovingTimeSegment_init(MovingTimeSegment *self, PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = {"seconds", "minutes", NULL};
    int minutes=0;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "ii", kwlist,
                                     &self->seconds, &minutes))
        return -1;

    if (minutes != 0)
        self->seconds += minutes * 60;

    self->seconds_ts = self->seconds * 1000;

    return 0;
}

static PyObject *
MovingTimeSegment_update(MovingTimeSegment* self, PyObject *args,  PyObject *kwds)
{
    static char *kwlist[] = {"value", "ts", NULL};
    long ts;
    double value;
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "dl", kwlist,
                                     &value, &ts))
        return NULL;

}

static PyObject *MovingTimeSegment_ready(MovingTimeSegment* self, PyObject *args)
{
    Py_INCREF(Py_False);
    return Py_False;
}


PyMODINIT_FUNC
initMovingTimeSegment(void)
{
    PyObject* m;

    if (PyType_Ready(&MovingTimeSegment_MyTestType) < 0)
        return;

    m = Py_InitModule3("MovingTimeSegment", MovingTimeSegment_methods,
                       "For a window of size N, return value N values ago");

    Py_INCREF(&MovingTimeSegment_MyTestType);
    PyModule_AddObject(m, "MovingTimeSegment", (PyObject *)&MovingTimeSegment_MyTestType);
}
