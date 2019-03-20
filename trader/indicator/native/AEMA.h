#include <Python.h>
#include <structmember.h>

typedef struct {
    PyObject_HEAD
    /* internal data. */
    int win;
    long scale_interval_secs;
    int count;
    int lag_window;
    double scale;
    double last_scale;
    double esf;
    double result;
    // SMA related
    int sma_age;
    double sma_sum;
    double sma_result;
    long auto_last_ts;
    int auto_counter;
    PyListObject *sma_values;
} AEMA;

static void AEMA_dealloc(AEMA* self);
static PyObject *AEMA_new(PyTypeObject *type, PyObject *args, PyObject *kwds);
static int AEMA_init(AEMA *self, PyObject *args, PyObject *kwds);
static PyObject *AEMA_update(AEMA* self, PyObject *args,  PyObject *kwds);
static PyObject *AEMA_ready(AEMA* self, PyObject *args);

static PyMemberDef AEMA_members[] = {
    {"win", T_INT, offsetof(AEMA, win), 0, "aemaobj win"},
    {"scale_interval_secs", T_LONG, offsetof(AEMA, scale_interval_secs), 0, "aemaobj scale_interval_secs"},
    {"scale", T_DOUBLE, offsetof(AEMA, scale), 0, "aemaobj scale"},
    {"last_scale", T_DOUBLE, offsetof(AEMA, last_scale), 0, "aemaobj last_scale"},
    {"esf", T_DOUBLE, offsetof(AEMA, esf), 0, "aemaobj esf"},
    {"count", T_INT, offsetof(AEMA, count), 0, "aemaobj count"},
    {"result", T_DOUBLE, offsetof(AEMA, result), 0, "aemaobj result"},
    {"sma_age", T_INT, offsetof(AEMA, sma_age), 0, "aemaobj sma_age"},
    {"sma_sum", T_DOUBLE, offsetof(AEMA, sma_sum), 0, "aemaobj sma_sum"},
    {"sma_result", T_DOUBLE, offsetof(AEMA, sma_result), 0, "aemaobj sma_result"},
    {"sma_values", T_OBJECT, offsetof(AEMA, sma_values), 0, "aemaobj sma_values"},
    {"auto_last_ts", T_LONG, offsetof(AEMA, auto_last_ts), 0, "aemaobj auto_last_ts"},
    {"auto_counter", T_INT, offsetof(AEMA, count), 0, "aemaobj auto_counter"},
    {NULL}  /* Sentinel */
};

static PyMethodDef AEMA_methods[] = {
    {"update", (PyCFunction)AEMA_update, METH_VARARGS|METH_KEYWORDS,
     "Update AEMA",
    },
    {"ready", (PyCFunction)AEMA_ready, METH_NOARGS,
     "Update AEMA",
    },
    {NULL}  /* Sentinel */
};

static PyTypeObject AEMA_MyTestType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "AEMA.AEMA",                 /*tp_name*/
    sizeof(AEMA),               /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)AEMA_dealloc,   /*tp_dealloc*/
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
    "AEMA objects",             /* tp_doc */
    0,                         /* tp_traverse */
    0,                         /* tp_clear */
    0,                         /* tp_richcompare */
    0,                         /* tp_weaklistoffset */
    0,                         /* tp_iter */
    0,                         /* tp_iternext */
    AEMA_methods,               /* tp_methods */
    AEMA_members,               /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)AEMA_init,        /* tp_init */
    0,                         /* tp_alloc */
    AEMA_new,                   /* tp_new */
};

#ifndef PyMODINIT_FUNC  /* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif
