#include <Python.h>
#include <structmember.h>

typedef struct {
    PyObject_HEAD
    /* Your internal 'loc' data. */
    int loc;
} Test;

static void
MyTest_dealloc(Test* self)
{
    self->ob_type->tp_free((PyObject*)self);
}

static PyObject *
Test_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    Test *self;

    self = (Test *)type->tp_alloc(type, 0);
    self->loc = 0;

    return (PyObject *)self;
}

static int
Test_init(Test *self, PyObject *args, PyObject *kwds)
{
    if (! PyArg_ParseTuple(args, "i", &self->loc))
        return -1;

    return 0;
}

static PyMemberDef Test_members[] = {
    {"loc", T_INT, offsetof(Test, loc), 0, "mytestobj loc"},
    {NULL}  /* Sentinel */
};

static PyObject *
Test_foo(Test* self, PyObject *args)
{
    int data;
    PyObject *result;

    if (! PyArg_ParseTuple(args, "i", &data)) {
        return NULL;
    }

    /* We'll just return data + loc as our result. */
    result = Py_BuildValue("i", data + self->loc);

    return result;
}
static PyMethodDef Test_methods[] = {
    {"foo", (PyCFunction)Test_foo, METH_VARARGS,
     "Return input parameter added to 'loc' argument from init.",
    },
    {NULL}  /* Sentinel */
};

static PyTypeObject mytest_MyTestType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "mytest.MyTest",             /*tp_name*/
    sizeof(Test), /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)MyTest_dealloc,/*tp_dealloc*/
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
    "MyTest objects",          /* tp_doc */
    0,                         /* tp_traverse */
    0,                         /* tp_clear */
    0,                         /* tp_richcompare */
    0,                         /* tp_weaklistoffset */
    0,                         /* tp_iter */
    0,                         /* tp_iternext */
    Test_methods,      /* tp_methods */
    Test_members,      /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)Test_init,/* tp_init */
    0,                         /* tp_alloc */
    Test_new,                 /* tp_new */
};

static PyMethodDef mytest_methods[] = {
    {NULL}  /* Sentinel */
};

#ifndef PyMODINIT_FUNC  /* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif
PyMODINIT_FUNC
initmytest(void)
{
    PyObject* m;

    if (PyType_Ready(&mytest_MyTestType) < 0)
        return;

    m = Py_InitModule3("mytest", mytest_methods,
                       "Example module that creates an extension type.");

    Py_INCREF(&mytest_MyTestType);
    PyModule_AddObject(m, "Test", (PyObject *)&mytest_MyTestType);
}

