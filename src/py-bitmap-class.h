#pragma once
#ifndef PY_BITMAP_CLASS_H
#define PY_BITMAP_CLASS_H

#include <Python.h>
#include <structmember.h> /* For PyObject_HEAD, etc. */
#include "MMBitmap.h"

/* This file defines the class "Bitmap" for dealing with raw bitmaps. */
struct _BitmapObject {
	PyObject_HEAD
	MMBitmapRef bitmap;
	MMPoint point; /* For iterator */
};

typedef struct _BitmapObject BitmapObject;

extern PyTypeObject Bitmap_Type;

/* Returns a newly-initialized BitmapObject from the given MMBitmap.
 * The reference to |bitmap| is "stolen"; i.e., only the pointer is copied, and
 * the reponsibility for free()'ing the buffer is given to the |BitmapObject|.
 *
 * Remember to call PyType_Ready() before using this for the first time! */
PyObject *BitmapObject_FromMMBitmap(MMBitmapRef bitmap);

#endif /* PY_BITMAP_CLASS_H */
