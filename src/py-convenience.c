#include "py-convenience.h"

int Py_AddClassToModule(PyObject *mod, PyTypeObject *classType)
{
	if (PyType_Ready(classType) < 0) return -1;

	Py_INCREF(classType);
	return PyModule_AddObject(mod, classType->tp_name, (PyObject *)classType);
}

void PyErr_SetFormatString(PyObject *type, size_t size,
                           const char *format, ...)
{
	char *str = malloc(sizeof(char) * (size + 1));
	va_list va;
	if (str == NULL) return;

	va_start(va, format);
	PyOS_vsnprintf(str, size, format, va);
	va_end(va);

	PyErr_SetString(type, str);
	free(str);
}

PyObject *Py_SetArgConvertErr(const char *expected, unsigned arg_count,
                                     PyObject *obj)
{
	PyErr_SetFormatString(PyExc_TypeError, 130,
	                      "argument %u must be %.50s, not %.50s",
	                      arg_count, expected, obj->ob_type->tp_name);
	return NULL;
}

PyObject *Py_SetConvertErr(const char *expected, PyObject *obj)
{
	PyErr_SetFormatString(PyExc_TypeError, 123,
	                      "argument must be %.50s, not %.50s",
	                      expected, obj->ob_type->tp_name);
	return NULL;
}
