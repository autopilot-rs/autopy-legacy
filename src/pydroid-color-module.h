#pragma once
#ifndef PYDROID_COLOR_MODULE_H
#define PYDROID_COLOR_MODULE_H

#include <Python.h>

/* Summary: pydroid module for converting color formats */
/* Description: This module provides routines for converting between the color
                format (hexadecimal) used by pydroid methods and other, more
                readable, formats (e.g., RGB tuples). */
PyMODINIT_FUNC initcolor(void);

#endif /* PYDROID_COLOR_MODULE_H */
