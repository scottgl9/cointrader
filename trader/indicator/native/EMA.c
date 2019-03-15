#include <Python.h>
#include <structmember.h>

typedef struct {
    PyObject_HEAD
    /* internal data. */
    int window;
    int count;
    int lag_window;
    int slope_window;
    double weight;
    double scale;
    double esf;
    double result;

    // SMA related
    int sma_age;
    double sma_sum;
    double sma_result;
    PyListObject *sma_values;
} EMA;

static void
EMA_dealloc(EMA* self)
{
    if (self->sma_values)
        self->ob_type->tp_free(self->sma_values);

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

static PyMemberDef EMA_members[] = {
    {"window", T_INT, offsetof(EMA, window), 0, "emaobj window"},
    {"weight", T_DOUBLE, offsetof(EMA, weight), 0, "emaobj weight"},
    {"scale", T_DOUBLE, offsetof(EMA, scale), 0, "emaobj scale"},
    {"esf", T_DOUBLE, offsetof(EMA, esf), 0, "emaobj esf"},
    {"count", T_INT, offsetof(EMA, count), 0, "emaobj count"},
    {"result", T_DOUBLE, offsetof(EMA, result), 0, "emaobj result"},
    {"sma_age", T_INT, offsetof(EMA, sma_age), 0, "emaobj sma_age"},
    {"sma_sum", T_DOUBLE, offsetof(EMA, sma_sum), 0, "emaobj sma_sum"},
    {"sma_result", T_DOUBLE, offsetof(EMA, sma_result), 0, "emaobj sma_result"},
    {"sma_values", T_OBJECT, offsetof(EMA, sma_values), 0, "emaobj sma_values"},
    {NULL}  /* Sentinel */
};

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
        return Py_True;
    }
    return Py_False;
}

static PyMethodDef EMA_methods[] = {
    {"update", (PyCFunction)EMA_update, METH_VARARGS,
     "Update EMA",
    },
    {"ready", (PyCFunction)EMA_ready, METH_VARARGS,
     "Update EMA",
    },
    {NULL}  /* Sentinel */
};

static PyTypeObject EMA_MyTestType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "EMA.EMA",                 /*tp_name*/
    sizeof(EMA),               /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)EMA_dealloc,   /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,/*tp_flags*/
    "EMA objects",             /* tp_doc */
    0,                         /* tp_traverse */
    0,                         /* tp_clear */
    0,                         /* tp_richcompare */
    0,                         /* tp_weaklistoffset */
    0,                         /* tp_iter */
    0,                         /* tp_iternext */
    EMA_methods,               /* tp_methods */
    EMA_members,               /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)EMA_init,        /* tp_init */
    0,                         /* tp_alloc */
    EMA_new,                   /* tp_new */
};

//static PyMethodDef EMA_methods[] = {
//    {NULL}  /* Sentinel */
//};

#ifndef PyMODINIT_FUNC  /* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif
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
