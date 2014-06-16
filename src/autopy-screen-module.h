#pragma once
#ifndef AUTOPY_SCREEN_MODULE_H
#define AUTOPY_SCREEN_MODULE_H

#include <Python.h>

#if PY_MAJOR_VERSION >= 3
#define PYTHREE
#endif

/* Summary: autopy module for working with the screen */
/* Description: This module contains functions for obtaining attributes
                about the screen. */
PyMODINIT_FUNC initscreen(void);

#endif /* AUTOPY_SCREEN_MODULE_H */
