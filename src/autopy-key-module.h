#pragma once
#ifndef AUTOPY_KEY_MODULE_H
#define AUTOPY_KEY_MODULE_H

#include <Python.h>

#if PY_MAJOR_VERSION >= 3
#define PYTHREE
#endif

/* Summary: autopy module for working with the keyboard */
/* Description: This module contains various functions for controlling the
                keyboard. */
PyMODINIT_FUNC initkey(void);

#endif /* AUTOPY_KEY_MODULE_H */
