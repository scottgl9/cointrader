#include <Python.h>
#include <structmember.h>

#define BOOL int
#define TRUE 1
#define FALSE 0

typedef struct {
    PyObject_HEAD
    /* internal data. */
    long max_win_size;
    long win_secs;
    long win_secs_ts;
    BOOL minmax;
    PyListObject *values;
    PyListObject *timestamps;
    int current_size;
    int end_age;
    int start_age;
    int age;
    double min_value;
    int min_age;
    double max_value;
    int max_age;
    double sum;
    int sum_count;
} MTSCircularArray;

static void MTSCircularArray_dealloc(MTSCircularArray* self);
static PyObject *MTSCircularArray_new(PyTypeObject *type, PyObject *args, PyObject *kwds);
static int MTSCircularArray_init(MTSCircularArray *self, PyObject *args, PyObject *kwds);
static PyObject *MTSCircularArray_add(MTSCircularArray* self, PyObject *args, PyObject *kwds);
static PyObject *MTSCircularArray_values(MTSCircularArray* self, PyObject *args, PyObject *kwds);
static PyObject *MTSCircularArray_timestamps(MTSCircularArray* self, PyObject *args, PyObject *kwds);
static PyObject *MTSCircularArray_ready(MTSCircularArray* self, PyObject *args);
static PyObject *MTSCircularArray_start_index(MTSCircularArray* self, PyObject *args);
static PyObject *MTSCircularArray_last_index(MTSCircularArray* self, PyObject *args);
static PyObject *MTSCircularArray_get_value(MTSCircularArray* self, PyObject *args);
static PyObject *MTSCircularArray_set_value(MTSCircularArray* self, PyObject *args, PyObject *kwds);
static PyObject *MTSCircularArray_first_value(MTSCircularArray* self, PyObject *args);
static PyObject *MTSCircularArray_last_value(MTSCircularArray* self, PyObject *args);
static PyObject *MTSCircularArray_first_ts(MTSCircularArray* self, PyObject *args);
static PyObject *MTSCircularArray_last_ts(MTSCircularArray* self, PyObject *args);
static PyObject *MTSCircularArray_min_value(MTSCircularArray* self, PyObject *args);
static PyObject *MTSCircularArray_max_value(MTSCircularArray* self, PyObject *args);
static PyObject *MTSCircularArray_min_value_ts(MTSCircularArray* self, PyObject *args);
static PyObject *MTSCircularArray_max_value_ts(MTSCircularArray* self, PyObject *args);
static PyObject *MTSCircularArray_get_sum(MTSCircularArray* self, PyObject *args);
static PyObject *MTSCircularArray_get_sum_count(MTSCircularArray* self, PyObject *args);


static PyMemberDef MTSCircularArray_members[] = {
    {"max_win_size", T_LONG, offsetof(MTSCircularArray, max_win_size), 0, "mtscaobj max_win_size"},
    {"win_secs", T_LONG, offsetof(MTSCircularArray, win_secs), 0, "mtscaobj win_secs"},
    {"win_secs_ts", T_LONG, offsetof(MTSCircularArray, win_secs_ts), 0, "mtscaobj win_secs_ts"},
    {"_values", T_OBJECT, offsetof(MTSCircularArray, values), 0, "mtscaobj _values"},
    {"_timestamps", T_OBJECT, offsetof(MTSCircularArray, timestamps), 0, "mtscaobj _timestamps"},
    {"current_size", T_INT, offsetof(MTSCircularArray, current_size), 0, "mtscaobj current_size"},
    {"end_age", T_INT, offsetof(MTSCircularArray, end_age), 0, "mtscaobj end_age"},
    {"start_age", T_INT, offsetof(MTSCircularArray, start_age), 0, "mtscaobj start_age"},
    {"age", T_INT, offsetof(MTSCircularArray, current_size), 0, "mtscaobj age"},
    {"current_size", T_INT, offsetof(MTSCircularArray, current_size), 0, "mtscaobj current_size"},
    {"_min_value", T_DOUBLE, offsetof(MTSCircularArray, min_value), 0, "mtscaobj _min_value"},
    {"_min_age", T_INT, offsetof(MTSCircularArray, min_age), 0, "mtscaobj _min_age"},
    {"_max_value", T_DOUBLE, offsetof(MTSCircularArray, max_value), 0, "mtscaobj _max_value"},
    {"_max_age", T_INT, offsetof(MTSCircularArray, max_age), 0, "mtscaobj _max_age"},
    {"_sum", T_DOUBLE, offsetof(MTSCircularArray, sum), 0, "mtscaobj _sum"},
    {"_sum_count", T_INT, offsetof(MTSCircularArray, sum_count), 0, "mtscaobj _sum_count"},
    {NULL}  /* Sentinel */
};

static PyMethodDef MTSCircularArray_methods[] = {
    {"add", (PyCFunction)MTSCircularArray_add, METH_VARARGS|METH_KEYWORDS,
     "add MTSCircularArray",
    },
    {"values", (PyCFunction)MTSCircularArray_values, METH_VARARGS|METH_KEYWORDS,
     "values MTSCircularArray",
    },
    {"timestamps", (PyCFunction)MTSCircularArray_timestamps, METH_VARARGS|METH_KEYWORDS,
     "timestamps MTSCircularArray",
    },
    {"ready", (PyCFunction)MTSCircularArray_ready, METH_NOARGS,
     "Ready MTSCircularArray",
    },
    {"start_index", (PyCFunction)MTSCircularArray_start_index, METH_NOARGS,
    "start_index MTSCircularArray"},
    {"last_index", (PyCFunction)MTSCircularArray_last_index, METH_NOARGS,
    "last_index MTSCircularArray"},
    {"get_value", (PyCFunction)MTSCircularArray_get_value, METH_VARARGS,
    "get_value MTSCircularArray"},
    {"set_value", (PyCFunction)MTSCircularArray_set_value, METH_VARARGS|METH_KEYWORDS,
     "set_value MTSCircularArray"},
    {"first_value", (PyCFunction)MTSCircularArray_first_value, METH_NOARGS,
    "first_value MTSCircularArray"},
    {"last_value", (PyCFunction)MTSCircularArray_last_value, METH_NOARGS,
    "last_value MTSCircularArray"},
    {"first_ts", (PyCFunction)MTSCircularArray_first_ts, METH_NOARGS,
    "first_ts MTSCircularArray"},
    {"last_ts", (PyCFunction)MTSCircularArray_last_ts, METH_NOARGS,
    "last_ts MTSCircularArray"},
    {"min_value", (PyCFunction)MTSCircularArray_min_value, METH_NOARGS,
    "min_value MTSCircularArray"},
    {"max_value", (PyCFunction)MTSCircularArray_max_value, METH_NOARGS,
    "max_value MTSCircularArray"},
    {"min_value_ts", (PyCFunction)MTSCircularArray_min_value_ts, METH_NOARGS,
    "min_value_ts MTSCircularArray"},
    {"max_value_ts", (PyCFunction)MTSCircularArray_max_value_ts, METH_NOARGS,
    "max_value_ts MTSCircularArray"},
    {"get_sum", (PyCFunction)MTSCircularArray_get_sum, METH_NOARGS,
    "get_sum MTSCircularArray"},
    {"get_sum_count", (PyCFunction)MTSCircularArray_get_sum_count, METH_NOARGS,
    "get_sum_count MTSCircularArray"},
    {NULL}  /* Sentinel */
};

static PyTypeObject MTSCircularArray_MyTestType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "MTSCircularArray.MTSCircularArray",                 /*tp_name*/
    sizeof(MTSCircularArray),               /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)MTSCircularArray_dealloc,   /*tp_dealloc*/
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
    "MTSCircularArray objects",             /* tp_doc */
    0,                         /* tp_traverse */
    0,                         /* tp_clear */
    0,                         /* tp_richcompare */
    0,                         /* tp_weaklistoffset */
    0,                         /* tp_iter */
    0,                         /* tp_iternext */
    MTSCircularArray_methods,               /* tp_methods */
    MTSCircularArray_members,               /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)MTSCircularArray_init,        /* tp_init */
    0,                         /* tp_alloc */
    MTSCircularArray_new,                   /* tp_new */
};

#ifndef PyMODINIT_FUNC  /* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif
