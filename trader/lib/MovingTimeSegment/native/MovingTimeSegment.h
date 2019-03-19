#include <Python.h>
#include <structmember.h>

typedef struct {
    PyObject_HEAD
    /* internal data. */
    int seconds;
    long seconds_ts;
    PyListObject *values;
    PyListObject *timestamps;
    double min_value;
    int min_value_index;
    double max_value;
    int max_value_index;
    double _sum;
    int _sum_count;
} MovingTimeSegment;

static void MovingTimeSegment_dealloc(MovingTimeSegment* self);
static PyObject *MovingTimeSegment_new(PyTypeObject *type, PyObject *args, PyObject *kwds);
static int MovingTimeSegment_init(MovingTimeSegment *self, PyObject *args, PyObject *kwds);
static PyObject *MovingTimeSegment_update(MovingTimeSegment* self, PyObject *args);
static PyObject *MovingTimeSegment_ready(MovingTimeSegment* self, PyObject *args);

static PyMemberDef MovingTimeSegment_members[] = {
    {"seconds", T_INT, offsetof(MovingTimeSegment, seconds), 0, "mtsobj seconds"},
    {"seconds_ts", T_LONG, offsetof(MovingTimeSegment, seconds_ts), 0, "mtsobj seconds_ts"},
    {"values", T_OBJECT, offsetof(MovingTimeSegment, values), 0, "mtsobj values"},
    {"timestamps", T_OBJECT, offsetof(MovingTimeSegment, timestamps), 0, "mtsobj timestamps"},
    {"min_value", T_DOUBLE, offsetof(MovingTimeSegment, min_value), 0, "mtsobj min_value"},
    {"min_value_index", T_INT, offsetof(MovingTimeSegment, min_value_index), 0, "mtsobj min_value_index"},
    {"max_value", T_DOUBLE, offsetof(MovingTimeSegment, max_value), 0, "mtsobj max_value"},
    {"max_value_index", T_INT, offsetof(MovingTimeSegment, max_value_index), 0, "mtsobj max_value_index"},
    {"_sum", T_DOUBLE, offsetof(MovingTimeSegment, _sum), 0, "mtsobj _sum"},
    {"_sum_count", T_INT, offsetof(MovingTimeSegment, _sum_count), 0, "mtsobj _sum_count"},
    {NULL}  /* Sentinel */
};

static PyMethodDef MovingTimeSegment_methods[] = {
    {"update", (PyCFunction)MovingTimeSegment_update, METH_VARARGS,
     "Update MovingTimeSegment",
    },
    {"ready", (PyCFunction)MovingTimeSegment_ready, METH_VARARGS,
     "Ready MovingTimeSegment",
    },
    {NULL}  /* Sentinel */
};

static PyTypeObject MovingTimeSegment_MyTestType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "MovingTimeSegment.MovingTimeSegment",                 /*tp_name*/
    sizeof(MovingTimeSegment),               /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)MovingTimeSegment_dealloc,   /*tp_dealloc*/
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
    "MovingTimeSegment objects",             /* tp_doc */
    0,                         /* tp_traverse */
    0,                         /* tp_clear */
    0,                         /* tp_richcompare */
    0,                         /* tp_weaklistoffset */
    0,                         /* tp_iter */
    0,                         /* tp_iternext */
    MovingTimeSegment_methods,               /* tp_methods */
    MovingTimeSegment_members,               /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)MovingTimeSegment_init,        /* tp_init */
    0,                         /* tp_alloc */
    MovingTimeSegment_new,                   /* tp_new */
};

#ifndef PyMODINIT_FUNC  /* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif
