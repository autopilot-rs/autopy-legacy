[![PyPI version](https://pypip.in/version/autopy/badge.svg)](https://pypi.python.org/pypi/autopy/)
[![PyPI downloads](https://pypip.in/status/autopy/badge.svg)](https://pypi.python.org/pypi/autopy/)
[![PyPI status](https://pypip.in/download/autopy/badge.svg)](https://pypi.python.org/pypi/autopy/)

AutoPy Introduction and Tutorial
=================================

by Michael Sanders

## Outline

* Introduction
	- What is AutoPy?
	- How so?
* Getting Started
	- Requirements
	- Installation
	- Hello World
* Tutorials
	- Controlling the Mouse
	- Working with Bitmaps
* Closing & API Reference
* License
	- Summary
	- MIT License
	- The FreeBSD Documentation License

<div id="autopy-intro"></div>

## Introduction

<div id="what-is-autopy"></div>

### What is AutoPy?

AutoPy is a simple, cross-platform GUI automation toolkit for Python. It includes functions for controlling the keyboard and mouse, finding colors and bitmaps on-screen, and displaying alerts -- all in a cross-platform, efficient, and simple manner.

Works on Mac OS X, Windows, and X11.

<div id="autopy-getting-started"></div>

## Getting Started

<div id="autopy-requirements"></div>

### Requirements

* Python 2.5+
* For Mac OS X:
	- zlib
	- libpng (see [here](http://ethan.tira-thompson.org/Mac_OS_X_Ports.html) for a simple installer)
	- Mac OS 10.5 or later (earlier versions may work, but they are as-of-now untested)
* For Windows:
	- libpng & zlib (included in both the installer and the source archive)
* For everything else:
	- libpng & zlib
	- X11 with the XTest extension (also known as the Xtst library)

<div id="autopy-installation"></div>

### Installation

Installers for Windows are available here: http://pypi.python.org/pypi/autopy/.

For every other OS, the simplest method is to use the `easy_install` utility:

	easy_install autopy

Another option is to compile from the latest source on the GitHub repository:

	$ git clone git://github.com/msanders/autopy.git
	$ cd autopy
	$ python setup.py build
	# python setup.py install

When building from source, make sure to `cd` out of the autopy directory before attempting to use AutoPy or else it may fail on an `ImportError` due to Python's relative imports.

<div id="autopy-helloworld"></div>

### Hello World

The following is the full source for a "hello world" script in autopy. Running this code will cause an alert dialog to appear on every major platform:

	import autopy
	def hello_there_world():
	    autopy.alert.alert("Hello, world")
	hello_there_world()

![Cross platform alerts](https://github.com/msanders/autopy/raw/gh-pages/alerts.png)

<div id="autopy-tutorials"></div>

## Tutorials

<div id="autopy-mouse-tutorial"></div>

### Controlling the Mouse

AutoPy includes a number of functions for controlling the mouse. For a full list, consult the [API Reference](http://www.autopy.org/documentation/api-reference/mouse.html). This short tutorial, however, only gives you a taste of two: `autopy.mouse.move()` and `autopy.mouse.smooth_move()`. These functions do exactly what they seem; for instance, to immediately "teleport" the mouse to the top left corner of the screen:

	>>> import autopy
	>>> autopy.mouse.move(1, 1)


Note that you are able to use the module `autopy.mouse` despite only importing `autopy`. This is because the grand `autopy` module imports all of the modules in the autopy package, so you don't have to.

To move the mouse a bit more realistically, we could use:

	>>> import autopy
	>>> autopy.mouse.smooth_move(1, 1)

Even better, we could write our own function to move the mouse across the screen as a sine wave:

	import autopy
	import math
	import time
	import random

	TWO_PI = math.pi * 2.0
	def sine_mouse_wave():
		"""
		Moves the mouse in a sine wave from the left edge of
		the screen to the right.
		"""
		width, height = autopy.screen.get_size()
		height /= 2
		height -= 10 # Stay in the screen bounds.

		for x in xrange(width):
			y = int(height * math.sin((TWO_PI * x) / width) + height)
			autopy.mouse.move(x, y)
			time.sleep(random.uniform(0.001, 0.003))

	sine_mouse_wave()

<a href="http://www.autopy.org/documentation/sine-wave"><img src="https://github.com/msanders/autopy/raw/gh-pages/sine-move-mouse-thumbnail.jpg" alt="Demonstration video"/></a>

Pretty cool, huh?

<div id="autopy-bitmap-tutorial"></div>

### Working with Bitmaps

All of autopy's bitmap routines can be found in the module `autopy.bitmap` (more specifically, most are found in the class `autopy.bitmap.Bitmap`). A useful way to explore autopy is to use Python's built-in `help()` function, for example in `help(autopy.bitmap.Bitmap)`. All of autopy's functions are documented with descriptive docstrings, so this should show a nice overview.

There are currently three ways to load a bitmap in autopy: 1.) by taking a screenshot, 2.) by loading a file, or 3.) by parsing a string. The first is probably the most obvious, so I'll start by showing that:

	>>> import autopy
	>>> autopy.bitmap.capture_screen()
	<Bitmap object at 0x12278>

This takes a screenshot of the main screen, copies it to a bitmap, displays its memory address, and then immediately destroys it. Let's do something more useful, like look at its pixel data:

	>>> import autopy
	>>> autopy.bitmap.capture_screen().get_color(1, 1)
	15921906

AutoPy uses a coordinate system with its origin starting at the top-left, so this statement should return the color of pixel at the top-left corner of the screen. The number shown looks a bit unrecognizable, though, but we can fix that:

	>>> import autopy
	>>> hex(autopy.bitmap.capture_screen().get_color(1, 1))
	'0xF2F2F2'

This is obviously an RGB hexadecimal value, identical those used in HTML and CSS. We could also have done: 

	>>> import autopy
	>>> autopy.color.hex_to_rgb(autopy.screen.get_color(1, 1))
	(242, 242, 242)

which converts that hex value to a tuple of `(r, g, b)` values. (Note that `autopy.screen.get_color()`, used here, is merely a more convenient and efficient version of `autopy.bitmap.capture_screen().get_color()`.)

To save the screen capture to a file, we can use:

	>>> import autopy
	>>> autopy.bitmap.capture_screen().save('screengrab.png')

The filetype is either parsed automatically from the filename, or given as an optional parameter. AutoPy currently only supports the BMP and PNG filetypes, though, as those are really all that are practical for its purpose.

Loading a bitmap is done essentially the same way, only from a class method:

	>>> import autopy
	>>> autopy.bitmap.Bitmap.open('i-am-a-monkey.png')
	<Bitmap object at 0x1001d5378>

Sometimes it is desirable to keep a short script free of any outside dependencies. In the case of bitmaps, this can be accomplished with the `to_string()` and `from_string()` methods:

	>>> autopy.bitmap.Bitmap.open('foo.png').to_string()
	'b2,3,eNpjYGD4f/MwBDGA2QBcMwpt'
	>>> autopy.bitmap.Bitmap.from_string('b2,3,eNpjYGD4f/'
									      'MwBDGA2QBcMwpt')
	<Bitmap object at 0x12278>

This is not recommended for large bitmaps (a screenshot, for instance, is obviously _way_ too big), but can be useful for short images used in a script you want to be very easily distributable.

Aside from analyzing a bitmap's pixel data, the main use for loading a bitmap is finding it on the screen or inside another bitmap. For example, the following prints the coordinates of the first monkey found in a barrel of monkeys (scanned from left to right, top to bottom):

	import autopy
	def where_is_the_monkey():
		"""Look for the monkey. Tell me if you found it."""
		monkey = autopy.bitmap.Bitmap.open('monkey.png')
		barrel = autopy.bitmap.Bitmap.open('barrel.png')

		pos = barrel.find_bitmap(monkey)
		if pos:
			print "We found him! He's here: %s" % str(pos)
		else:
			print "There is no monkey... what kind of barrel is this?"

	where_is_the_monkey()

As I hope you can see, these functions are enormously useful and have a number of practical values.

## Closing & API Reference

Hope you enjoy using autopy! For a more in depth overview, I've attempted to make the [API Reference](http://www.autopy.org/documentation/api-reference/) as complete and approachable as possible.

<div id="autopy-license"></div>

## License

<div id="autopy-license-summary"></div>

### Summary

AutoPy (the software) is licensed under the terms of the MIT license.

The documentation for AutoPy is licensed under the terms of the FreeBSD Documentation License.

These licenses are both very liberal and permit nearly anything, including using the code in other projects (as long as credit is given).

<div id="autopy-mit-license"></div>

### MIT License

Copyright &copy; 2010 Michael Sanders.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

<div id="autopy-freebsd-license"></div>

### The FreeBSD Documentation License

Copyright &copy; 2010 Michael Sanders. All rights reserved.

Redistribution and use in source (Markdown, plaintext, et. al.) and "compiled" forms (HTML, PDF and so forth) with or without modification, are permitted provided that the following conditions are met:

Redistributions of source code (Markdown, plaintext, et. al.) must retain the above copyright notice, this list of conditions and the following disclaimer as the first lines of this file unmodified.
Redistributions in compiled form (HTML, PDF and so on) must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

THIS DOCUMENTATION IS PROVIDED "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS DOCUMENTATION, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

[![Bitdeli Badge](https://d2weczhvl823v0.cloudfront.net/msanders/autopy/trend.png)](https://bitdeli.com/free "Bitdeli Badge")
