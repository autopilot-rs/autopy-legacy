#pragma once
#ifndef PYDROID_MOUSE_MODULE_H
#define PYDROID_MOUSE_MODULE_H

#include <Python.h>

/* Summary: pydroid module for working with the mouse */
/* Description: This module contains functions for getting the current state of
                and controlling the mouse cursor.

		Unless otherwise stated, coordinates are those of a screen
                coordinate system, where the origin is at the top left. */
PyMODINIT_FUNC initmouse(void);

#endif /* PYDROID_MOUSE_MODULE_H */
