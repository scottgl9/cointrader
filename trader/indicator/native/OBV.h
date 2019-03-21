#include <Python.h>
#include <structmember.h>

typedef struct {
    PyObject_HEAD
    /* internal data. */
    double result;
    double last_result;
    double last_close;
} OBV;

static void OBV_dealloc(OBV* self);
static PyObject *OBV_new(PyTypeObject *type, PyObject *args, PyObject *kwds);
static int OBV_init(OBV *self, PyObject *args, PyObject *kwds);
static PyObject *OBV_update(OBV* self, PyObject *args, PyObject *kwds);

static PyMemberDef OBV_members[] = {
    {"result", T_DOUBLE, offsetof(OBV, result), 0, "obvobj result"},
    {"last_result", T_DOUBLE, offsetof(OBV, last_result), 0, "obvobj last_result"},
    {"last_close", T_DOUBLE, offsetof(OBV, last_close), 0, "obvobj last_close"},
    {NULL}  /* Sentinel */
};

static PyMethodDef OBV_methods[] = {
    {"update", (PyCFunction)OBV_update, METH_VARARGS|METH_KEYWORDS,
     "Update OBV",
    },
    {NULL}  /* Sentinel */
};

static PyTypeObject OBV_MyTestType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "OBV.OBV",                 /*tp_name*/
    sizeof(OBV),               /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)OBV_dealloc,   /*tp_dealloc*/
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
    "OBV objects",             /* tp_doc */
    0,                         /* tp_traverse */
    0,                         /* tp_clear */
    0,                         /* tp_richcompare */
    0,                         /* tp_weaklistoffset */
    0,                         /* tp_iter */
    0,                         /* tp_iternext */
    OBV_methods,               /* tp_methods */
    OBV_members,               /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)OBV_init,        /* tp_init */
    0,                         /* tp_alloc */
    OBV_new,                   /* tp_new */
};

#ifndef PyMODINIT_FUNC  /* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif
