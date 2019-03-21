#include "OBV.h"

static void
OBV_dealloc(OBV* self)
{
    self->ob_type->tp_free((PyObject*)self);
}

static PyObject *
OBV_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    OBV *self;

    self = (OBV *)type->tp_alloc(type, 0);
    self->result = 0;
    self->last_result = 0;
    self->last_close = 0;

    return (PyObject *)self;
}

static int
OBV_init(OBV *self, PyObject *args, PyObject *kwds)
{
    return 0;
}

static PyObject *
OBV_update(OBV* self, PyObject *args, PyObject *kwds)
{
    double close, volume;
    PyObject *result;

    static char *kwlist[] = {"close", "volume", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "dd", kwlist,
                                     &close, &volume))

    self->last_result = self->result;

    if (self->result == 0) {
        self->result = volume;
        self->last_close = close;
        result = Py_BuildValue("d", self->result);
        return result;
    }

    if (close > self->last_close) {
        self->result += volume;
    } else if (close < self->last_close) {
        self->result -= volume;
    }

    self->last_close = close;

    result = Py_BuildValue("d", self->result);
    return result;
}

PyMODINIT_FUNC
initOBV(void)
{
    PyObject* m;

    if (PyType_Ready(&OBV_MyTestType) < 0)
        return;

    m = Py_InitModule3("OBV", OBV_methods,
                       "On Balance Volume (OBV)");

    Py_INCREF(&OBV_MyTestType);
    PyModule_AddObject(m, "OBV", (PyObject *)&OBV_MyTestType);
}
