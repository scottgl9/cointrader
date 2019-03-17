#include <Python.h>
#include <structmember.h>

#define BOOL int
#define TRUE 1
#define FALSE 0

typedef struct {
    PyObject_HEAD
    /* internal data. */
    int pre_window;
    int window;
    int pre_age;
    int age;
    int last_age;

    double values1_min_value;
    int values1_min_age;
    double values1_max_value;
    int values1_max_age;

    double values2_min_value;
    int values2_min_age;
    double values2_max_value;
    int values2_max_age;

    PyListObject *values1;
    PyListObject *values2;
    PyListObject *pre_values1;
    PyListObject *pre_values2;

    BOOL values_under;
    BOOL values_over;
    BOOL crossup;
    BOOL crossdown;
} Crossover;

static void Crossover_dealloc(Crossover* self);
static PyObject *Crossover_new(PyTypeObject *type, PyObject *args, PyObject *kwds);
static int Crossover_init(Crossover *self, PyObject *args, PyObject *kwds);
static PyObject *Crossover_update(Crossover* self, PyObject *args, PyObject *kwds);
static PyObject *Crossover_crossup_detected(Crossover* self, PyObject *args);
static PyObject *Crossover_crossdown_detected(Crossover* self, PyObject *args);

static PyMemberDef Crossover_members[] = {
    {"pre_window", T_INT, offsetof(Crossover, pre_window), 0, "crossoverobj pre_window"},
    {"window", T_INT, offsetof(Crossover, window), 0, "crossoverobj window"},
    {"age", T_INT, offsetof(Crossover, age), 0, "crossoverobj age"},
    {"last_age", T_INT, offsetof(Crossover, last_age), 0, "crossoverobj last_age"},
    {"pre_age", T_INT, offsetof(Crossover, pre_age), 0, "crossoverobj pre_age"},
    {"values_under", T_INT, offsetof(Crossover, values_under), 0, "crossoverobj values_under"},
    {"values_over", T_INT, offsetof(Crossover, values_over), 0, "crossoverobj values_over"},
    {"crossup", T_INT, offsetof(Crossover, crossup), 0, "crossoverobj crossup"},
    {"crossdown", T_INT, offsetof(Crossover, crossdown), 0, "crossoverobj crossdown"},
    {"values1", T_OBJECT_EX, offsetof(Crossover, values1), 0, "crossoverobj values1"},
    {"values2", T_OBJECT_EX, offsetof(Crossover, values2), 0, "crossoverobj values2"},
    {"pre_values1", T_OBJECT_EX, offsetof(Crossover, pre_values1), 0, "crossoverobj pre_values1"},
    {"pre_values2", T_OBJECT_EX, offsetof(Crossover, pre_values2), 0, "crossoverobj pre_values2"},
    {"values1_min_value", T_DOUBLE, offsetof(Crossover, values1_min_value), 0, "crossoverobj values1_min_value"},
    {"values1_min_age", T_INT, offsetof(Crossover, values1_min_age), 0, "crossoverobj values1_min_age"},
    {"values1_max_value", T_DOUBLE, offsetof(Crossover, values1_max_value), 0, "crossoverobj values1_max_value"},
    {"values1_max_age", T_INT, offsetof(Crossover, values1_max_age), 0, "crossoverobj values1_max_age"},
    {"values2_min_value", T_DOUBLE, offsetof(Crossover, values2_min_value), 0, "crossoverobj values2_min_value"},
    {"values2_min_age", T_INT, offsetof(Crossover, values2_min_age), 0, "crossoverobj values2_min_age"},
    {"values2_max_value", T_DOUBLE, offsetof(Crossover, values2_max_value), 0, "crossoverobj values2_max_value"},
    {"values2_max_age", T_INT, offsetof(Crossover, values2_max_age), 0, "crossoverobj values2_max_age"},
    {NULL}  /* Sentinel */
};


static PyMethodDef Crossover_methods[] = {
    {"update", (PyCFunction)Crossover_update, METH_VARARGS|METH_KEYWORDS,
     "Update Crossover",
    },
    {"crossup_detected", (PyCFunction)Crossover_crossup_detected, METH_NOARGS,
     "Crossover crossup detected",
    },
    {"crossdown_detected", (PyCFunction)Crossover_crossdown_detected, METH_NOARGS,
     "Crossover crossdown detected",
    },
    {NULL}  /* Sentinel */
};

static PyTypeObject Crossover_MyTestType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "Crossover.Crossover",                 /*tp_name*/
    sizeof(Crossover),               /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)Crossover_dealloc,   /*tp_dealloc*/
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
    "Crossover objects",             /* tp_doc */
    0,                         /* tp_traverse */
    0,                         /* tp_clear */
    0,                         /* tp_richcompare */
    0,                         /* tp_weaklistoffset */
    0,                         /* tp_iter */
    0,                         /* tp_iternext */
    Crossover_methods,               /* tp_methods */
    Crossover_members,               /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)Crossover_init,        /* tp_init */
    0,                         /* tp_alloc */
    Crossover_new,                   /* tp_new */
};

#ifndef PyMODINIT_FUNC  /* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif
