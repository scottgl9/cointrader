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
    double last_result;

    // SMA related
    int sma_age;
    double sma_sum;
    double sma_result;
    PyListObject *sma_values;
    int value_lag_age;
    PyListObject *value_lag_values;
} EMA;

static void EMA_dealloc(EMA* self);
static PyObject *EMA_new(PyTypeObject *type, PyObject *args, PyObject *kwds);
static int EMA_init(EMA *self, PyObject *args, PyObject *kwds);
static PyObject *EMA_update(EMA* self, PyObject *args);
static PyObject *EMA_ready(EMA* self, PyObject *args);

static PyMemberDef EMA_members[] = {
    {"window", T_INT, offsetof(EMA, window), 0, "emaobj window"},
    {"weight", T_DOUBLE, offsetof(EMA, weight), 0, "emaobj weight"},
    {"scale", T_DOUBLE, offsetof(EMA, scale), 0, "emaobj scale"},
    {"esf", T_DOUBLE, offsetof(EMA, esf), 0, "emaobj esf"},
    {"count", T_INT, offsetof(EMA, count), 0, "emaobj count"},
    {"result", T_DOUBLE, offsetof(EMA, result), 0, "emaobj result"},
    {"last_result", T_DOUBLE, offsetof(EMA, last_result), 0, "emaobj last_result"},
    {"sma_age", T_INT, offsetof(EMA, sma_age), 0, "emaobj sma_age"},
    {"sma_sum", T_DOUBLE, offsetof(EMA, sma_sum), 0, "emaobj sma_sum"},
    {"sma_result", T_DOUBLE, offsetof(EMA, sma_result), 0, "emaobj sma_result"},
    {"sma_values", T_OBJECT, offsetof(EMA, sma_values), 0, "emaobj sma_values"},
    {NULL}  /* Sentinel */
};

static PyMethodDef EMA_methods[] = {
    {"update", (PyCFunction)EMA_update, METH_VARARGS,
     "Update EMA",
    },
    {"ready", (PyCFunction)EMA_ready, METH_NOARGS,
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

#ifndef PyMODINIT_FUNC  /* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif
