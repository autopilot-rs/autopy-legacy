#pragma once
#ifndef PYCONVENIENCE_H
#define PYCONVENIENCE_H

#include <Python.h>

/* Checks class is ready and adds it to module.
 * 0 is returned on success, -1 on failure. */
int Py_AddClassToModule(PyObject *mod, PyTypeObject *classType);

/* Convenience wrapper around PyOS_snprintf() and PyErr_SetString(). */
void PyErr_SetFormatString(PyObject *type, size_t size,
                           const char *format, ...);

/* Throws a convert error just as PyArg_ParseTuple() would. */
/* Always returns NULL for convenience. */
PyObject *Py_SetArgConvertErr(const char *expected, unsigned arg_count,
                              PyObject *obj);

PyObject *Py_SetConvertErr(const char *expected, PyObject *obj);

#endif /* PYCONVENIENCE_H */
