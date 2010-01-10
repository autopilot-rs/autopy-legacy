#pragma once
#ifndef PYDROID_BITMAP_MODULE_H
#define PYDROID_BITMAP_MODULE_H

#include <Python.h>

/* Summary: pydroid module for working with bitmaps */
/* Description: This module defines the class `Bitmap` for accessing
                bitmaps and searching for bitmaps on-screen.

                It also defines functions for taking screenshots of the screen. */
PyMODINIT_FUNC initbitmap(void);

#endif /* PYDROID_BITMAP_MODULE_H */
