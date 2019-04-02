#include "Kline.h"

static void
Kline_dealloc(Kline* self)
{
    self->ob_type->tp_free((PyObject*)self);
}

static PyObject *
Kline_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    Kline *self;

    self = (Kline *)type->tp_alloc(type, 0);
    self->symbol = NULL;
    self->open = 0;
    self->close = 0;
    self->low = 0;
    self->high = 0;
    self->volume_base = 0;
    self->volume_quote = 0;
    self->volume = 0;
    self->ts = 0;

    return (PyObject *)self;
}

static int
Kline_init(Kline *self, PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = {"symbol", "open", "close", "low", "high", "volume_base", "volume_quote", "ts", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|Uddddddl", kwlist,
                                     &self->symbol, &self->open, &self->close, &self->low, &self->high,
                                     &self->volume_base, &self->volume_quote, &self->ts))
        return -1;

    self->volume = self->volume_quote;

    return 0;
}

static PyObject *Kline_reset(Kline *self, PyObject *args)
{
    self->open = 0;
    self->close = 0;
    self->low = 0;
    self->high = 0;
    self->volume_base = 0;
    self->volume_quote = 0;
    self->volume = 0;
    self->ts = 0;

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject* Kline_Repr(PyObject *o)
{
    Kline *self = (Kline *)o;
    PyObject *result = PyDict_New();
    Py_INCREF(result);
    PyDict_SetItemString(result, "open", Py_BuildValue("d", self->open));
    PyDict_SetItemString(result, "close", Py_BuildValue("d", self->close));
    PyDict_SetItemString(result, "volume_base", Py_BuildValue("d", self->volume_base));
    PyDict_SetItemString(result, "volume_quote", Py_BuildValue("d", self->volume_quote));
    PyDict_SetItemString(result, "ts", Py_BuildValue("l", self->ts));

    return result;
}

PyMODINIT_FUNC
initKline(void)
{
    PyObject* m;

    if (PyType_Ready(&Kline_MyTestType) < 0)
        return;

    m = Py_InitModule3("Kline", Kline_methods,
                       "Class to represent Kline");

    Py_INCREF(&Kline_MyTestType);
    PyModule_AddObject(m, "Kline", (PyObject *)&Kline_MyTestType);
}
