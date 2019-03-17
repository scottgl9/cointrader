#include "Crossover.h"

static void
Crossover_dealloc(Crossover* self)
{
    Py_XDECREF(self->pre_values2);
    Py_XDECREF(self->pre_values1);
    Py_XDECREF(self->values2);
    Py_XDECREF(self->values1);

    self->ob_type->tp_free((PyObject*)self);
}

static PyObject *
Crossover_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    Crossover *self;

    self = (Crossover *)type->tp_alloc(type, 0);
    self->pre_window = 0;
    self->window = 0;
    self->pre_age = 0;
    self->age = 0;
    self->last_age = 0;
    self->values1 = (PyListObject*)PyList_New(0);
    self->values2 = (PyListObject*)PyList_New(0);
    self->pre_values1 = (PyListObject*)PyList_New(0);
    self->pre_values2 = (PyListObject*)PyList_New(0);

    self->values_under = FALSE;
    self->values_over = FALSE;
    self->crossup = FALSE;
    self->crossdown = FALSE;

    self->values1_min_value = 0;
    self->values1_min_age = 0;
    self->values1_max_value = 0;
    self->values1_max_age = 0;

    self->values2_min_value = 0;
    self->values2_min_age = 0;
    self->values2_max_value = 0;
    self->values2_max_age = 0;

    return (PyObject *)self;
}

static int
Crossover_init(Crossover *self, PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = {"pre_window", "window", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "ii", kwlist,
                                     &self->pre_window, &self->window))
        return -1;

    return 0;
}

static double get_min(PyListObject *values)
{
    int size = PyList_Size((PyObject*)values);
    double value, min_value = 0;
    for (int i=0; i<size; i++) {
        value = PyFloat_AS_DOUBLE(PyList_GetItem((PyObject *)values, i));
        if (min_value > value || min_value == 0)
            min_value = value;
    }
    return min_value;
}

static double get_max(PyListObject *values)
{
    int size = PyList_Size((PyObject*)values);
    double value, max_value = 0;
    for (int i=0; i<size; i++) {
        value = PyFloat_AS_DOUBLE(PyList_GetItem((PyObject *)values, i));
        if (max_value < value)
            max_value = value;
    }
    return max_value;
}

static void get_min_and_max(PyListObject *values, double *min_value, double *max_value)
{
    int size = PyList_Size((PyObject*)values);
    double value;
    *min_value = 0;
    *max_value = 0;
    for (int i=0; i<size; i++) {
        if (*min_value > value || *min_value == 0)
            *min_value = value;
        if (*max_value < value)
            *max_value = value;

    }
}

static void update_values1_min_max(Crossover *self, double value)
{
    double min_value, max_value;
    if (self->values1_min_value == 0 || self->values1_max_value == 0) {
        //get_min_and_max(self->values1, &min_value, &max_value);
        self->values1_min_value = get_min(self->values1); //min_value; //min(self.values1)
        self->values1_max_value = get_max(self->values1); //max_value; //max(self.values1)
        self->values1_min_age = 0;
        self->values1_max_age = 0;
        return;
    }

    if (value <= self->values1_min_value) {
        self->values1_min_value = value;
        self->values1_min_age = 0;
        self->values1_max_age++;
    } else if (value >= self->values1_max_value) {
        self->values1_max_value = value;
        self->values1_max_age = 0;
        self->values1_min_age++;
    } else {
        self->values1_min_age++;
        self->values1_max_age++;
    }

    if (self->values1_min_age >= self->window - 1) {
        self->values1_min_value = get_min(self->values1); //min(self.values1)
        self->values1_min_age++;
    }

    if (self->values1_max_age >= self->window - 1) {
        self->values1_max_value = get_max(self->values1); //max(self.values1)
        self->values1_max_age++;
    }
}

static void update_values2_min_max(Crossover *self, double value)
{
    double min_value, max_value;
    if (self->values2_min_value == 0 || self->values2_max_value == 0) {
        //get_min_and_max(self->values2, &min_value, &max_value);
        self->values2_min_value = get_min(self->values2); //min_value; //min(self.values1)
        self->values2_max_value = get_max(self->values2); //max_value; //max(self.values1)
        self->values2_min_age = 0;
        self->values2_max_age = 0;
        return;
    }

    if (value <= self->values2_min_value) {
        self->values2_min_value = value;
        self->values2_min_age = 0;
        self->values2_max_age++;
    } else if (value >= self->values2_max_value) {
        self->values2_max_value = value;
        self->values2_max_age = 0;
        self->values2_min_age++;
    } else {
        self->values2_min_age++;
        self->values2_max_age++;
    }

    if (self->values2_min_age >= self->window - 1) {
        self->values2_min_value = get_min(self->values2); //min(self.values2)
        self->values2_min_age++;
    }

    if (self->values2_max_age >= self->window - 1) {
        self->values2_max_value = get_max(self->values2); //max(self.values2)
        self->values2_max_age++;
    }
}

static PyObject *
Crossover_update(Crossover* self, PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = {"value1", "value2", NULL};

    double value1, value2;
    PyObject *ovalue1, *ovalue2;
    double pre_value1, pre_value2;
    int pre_size, size1, size2;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "dd", kwlist,
                                     &value1, &value2))
        return NULL;

    size1 = PyList_Size((PyObject*)self->values1);

    if (size1 < self->window) {
        PyList_Append((PyObject *)self->values1, Py_BuildValue("d", value1));
        PyList_Append((PyObject *)self->values2, Py_BuildValue("d", value2));
    } else {
        if (self->pre_window != 0) {

            // PyFloat_AS_DOUBLE trades safety for speed
            // #define PyFloat_AS_DOUBLE(op) (((PyFloatObject *)(op))->ob_fval)
            pre_size = PyList_Size((PyObject*)self->pre_values1);
            pre_value1 = PyFloat_AS_DOUBLE(PyList_GetItem((PyObject *)self->values1, self->age));
            pre_value2 = PyFloat_AS_DOUBLE(PyList_GetItem((PyObject *)self->values2, self->age));

            if (pre_size < self->pre_window) {
                PyList_Append((PyObject *)self->pre_values1, Py_BuildValue("d", pre_value1));
                PyList_Append((PyObject *)self->pre_values2, Py_BuildValue("d", pre_value2));
            } else {
                PyList_SetItem((PyObject *)self->pre_values1, self->pre_age, Py_BuildValue("d", pre_value1));
                PyList_SetItem((PyObject *)self->pre_values2, self->pre_age, Py_BuildValue("d", pre_value2));

                self->pre_age = (self->pre_age + 1) % self->pre_window;
            }
        }

        PyList_SetItem((PyObject *)self->values1, self->age, Py_BuildValue("d", value1));
        PyList_SetItem((PyObject *)self->values2, self->age, Py_BuildValue("d", value2));
        update_values1_min_max(self, value1);
        update_values2_min_max(self, value2);

        if (self->values_under && self->values1_min_value > self->values2_max_value) {
            // values1 in window were under values2, now all values1 over values2
            self->values_under = FALSE;
            self->crossup = TRUE;
        } else if (self->values_over && self->values1_max_value < self->values2_min_value) {
            // values1 in window were over values2, now all values1 under values2
            self->values_over = FALSE;
            self->crossdown = TRUE;
        } else if (!self->values_under && !self->values_over) {
            if (self->values1_max_value < self->values2_min_value) {
                if (self->pre_window != 0) {
                    // make sure values1 in pre_window were also under values2
                    if (get_max(self->pre_values1) < get_min(self->pre_values2))
                        self->values_under = TRUE;
                } else {
                    // all of values1 under values2
                    self->values_under = TRUE;
                }
            } else if (self->values1_min_value > self->values2_max_value) {
                if (self->pre_window != 0) {
                    // make sure values1 in pre_window were also over values2
                    if (get_min(self->pre_values1) > get_max(self->pre_values2))
                        self->values_over = TRUE;
                } else {
                    // all of values1 over values2
                    self->values_over = TRUE;
                }
            }
        }
    }

    self->last_age = self->age;
    self->age = (self->age + 1) % self->window;

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *Crossover_crossup_detected(Crossover* self, PyObject *args)
{
    BOOL result = self->crossup;
    self->crossup = FALSE;
    if (result) {
        Py_INCREF(Py_True);
        return Py_True;
    }
    Py_INCREF(Py_False);
    return Py_False;
}

static PyObject *Crossover_crossdown_detected(Crossover* self, PyObject *args)
{
    BOOL result = self->crossdown;
    self->crossdown = FALSE;
    if (result) {
        Py_INCREF(Py_True);
        return Py_True;
    }
    Py_INCREF(Py_False);
    return Py_False;
}

PyMODINIT_FUNC
initCrossover(void)
{
    PyObject* m;

    if (PyType_Ready(&Crossover_MyTestType) < 0)
        return;

    m = Py_InitModule3("Crossover", Crossover_methods,
                       "For two moving values, check if a crossover has occurred");

    Py_INCREF(&Crossover_MyTestType);
    PyModule_AddObject(m, "Crossover", (PyObject *)&Crossover_MyTestType);
}
