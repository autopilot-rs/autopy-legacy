#pragma once
#ifndef AUTOPY_ALERT_MODULE_H
#define AUTOPY_ALERT_MODULE_H

#include <Python.h>

#if PY_MAJOR_VERSION >= 3
#define PYTHREE
#endif

/* Summary: autopy module for displaying alerts */
/* Description: This module contains functions for displaying cross-platform
                alert dialogs. */
PyMODINIT_FUNC initalert(void);

#endif /* AUTOPY_ALERT_MODULE_H */
