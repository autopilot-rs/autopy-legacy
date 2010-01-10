Pydroid Introduction and Tutorial
=================================

by Michael Sanders

## Outline

* Introduction
	- What is Pydroid?
	- Why use Pydroid?
	- What else is Pydroid?
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

<div id="pydroid-intro"></div>

## Introduction

<div id="what-is-pydroid"></div>

### What is Pydroid?

Pydroid is a simple toolkit for automating and scripting repetitive tasks, especially those involving a GUI, with Python. It includes functions for controlling the mouse and keyboard, finding colors and bitmaps on-screen, as well as displaying cross-platform alerts.

<div id="why-pydroid"></div>

### Why use Pydroid?

* Testing a GUI application for bugs and edge cases
	- You might think your app is stable, but what happens if you press that button _5000 times_?
* Automating games
	- Writing a script to beat that crappy flash game can be _so_ much more gratifying than spending hours playing it yourself.
* Freaking out friends and family
	- Well maybe this isn't really a practical use, _but_...

<div id="what-else-pydroid"></div>

### What else is Pydroid?

* Portable
	- Works on Mac OS X, Windows, and X11.
* Fast
	- Written in pure ANSI C.
* Simple
	- Pydroid is designed as a _toolkit_, not a _framework_ -- it doesn't get in your way. At the same time, convenience functions are provided where useful.
* Easy
	- Pydroid is designed to be simple and easy-to-understand, both for the end user and the implementor; that is, both the public API and the internals are straightforward and well-documented. It should be easy to pick up, and easy to modify if you need.

<div id="pydroid-getting-started"></div>

## Getting Started

<div id="pydroid-requirements"></div>

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

<div id="pydroid-installation"></div>

### Installation

#### Binary Installers

Pydroid binaries are currently available for [Leopard](http://s3.amazonaws.com/pydroid/pydroid-leopard.pkg), [Snow Leopard](http://s3.amazonaws.com/pydroid/pydroid-snowleopard.pkg), and [Windows XP](http://s3.amazonaws.com/pydroid/pydroid-setup.exe). For other platforms, you will have to compile it yourself &#8212; fortunately, this is a relatively easy task.

#### Installing from Source

Check out the latest code:

	$ git clone git://github.com/msanders/pydroid.git

Compile it:

	$ cd pydroid
	$ python setup.py build

Install it:

	# python setup.py install

<div id="pydroid-helloworld"></div>

### Hello World

The following is the full source for a "hello world" script in pydroid. Running this code will cause an alert dialog to appear on every major platform:

	import pydroid
	def hello_there_world():
	    pydroid.alert.alert("Hello, world")
	    hello_there_world()

![Cross platform alerts](http://s3.amazonaws.com/pydroid/alerts.png)

<div id="pydroid-tutorials"></div>

## Tutorials

<div id="pydroid-mouse-tutorial"></div>

### Controlling the Mouse

Pydroid includes a number of functions for controlling the mouse. For a full list, consult the [API Reference](http://msanders.com/pydroid/documentation/api-reference/mouse.html). This short tutorial, however, only gives you a taste of two: `pydroid.mouse.move()` and `pydroid.mouse.smooth_move()`. These functions do exactly what they seem; for instance, to immediately "teleport" the mouse to the top left corner of the screen:

	>>> import pydroid
	>>> pydroid.mouse.move(1, 1)


Note that you are able to use the module `pydroid.mouse` despite only importing `pydroid`. This is because the grand `pydroid` module imports all of the modules in the pydroid package, so you don't have to.

To move the mouse a bit more realistically, we could use:

	>>> import pydroid
	>>> pydroid.mouse.smooth_move(1, 1)

Even better, we could write our own function to move the mouse across the screen as a sine wave:

	import pydroid
	import math
	import time
	import random

	TWO_PI = math.pi * 2.0
	def sine_mouse_wave():
		"""
		Moves the mouse in a sine wave from the left edge of
		the screen to the right.
		"""
		width, height = pydroid.screen.get_size()
		height /= 2
		height -= 10 # Stay in the screen bounds.

		for x in xrange(width):
			y = int(height * math.sin((TWO_PI * x) / width) + height)
			pydroid.mouse.move(x, y)
			time.sleep(random.uniform(0.001, 0.003))

	sine_mouse_wave()

<a href="http://msanders.com/pydroid/sine-move-mouse.html"><img src="http://s3.amazonaws.com/pydroid/sine-move-mouse-thumbnail.jpg" alt="Demonstration video"/></a>

Pretty cool, huh?

<div id="pydroid-bitmap-tutorial"></div>

### Working with Bitmaps

All of pydroid's bitmap routines can be found in the function `pydroid.bitmap` (more specifically, most are found in the class `pydroid.bitmap.Bitmap`). A useful way to explore pydroid is to use Python's built-in `help()` function, for example in `help(pydroid.bitmap.Bitmap)`. All of pydroid's functions are documented with descriptive docstrings, so this should show a nice overview.

There are currently three ways to load a bitmap in pydroid: 1.) by taking a screenshot, 2.) by loading a file, or 3.) by parsing a string. The first is probably the most obvious, so I'll start by showing that:

	>>> import pydroid
	>>> pydroid.bitmap.capture_screen()
	<Bitmap object at 0x12278>

This takes a screenshot of the main screen, copies it to a bitmap, displays its memory address, and then immediately destroys it. Let's do something more useful, like look at its pixel data:

	>>> import pydroid
	>>> pydroid.bitmap.capture_screen().get_color(1, 1)
	15921906

Pydroid uses a coordinate system with its origin starting at the top-left, so this statement should return the color of pixel at the top-left corner of the screen. The number shown looks a bit unrecognizable, though, but we can fix that:

	>>> import pydroid
	>>> hex(pydroid.bitmap.capture_screen().get_color(1, 1))
	'0xF2F2F2'

This is obviously an RGB hexadecimal value, identical those used in HTML and CSS. We could also have done: 

	>>> import pydroid
	>>> pydroid.color.hex_to_rgb(pydroid.screen.get_color(1, 1))
	(242, 242, 242)

which converts that hex value to a tuple of `(r, g, b)` values. (Note that `pydroid.screen.get_color()`, used here, is merely a more convenient and efficient version of `pydroid.bitmap.capture_screen().get_color()`.)

To save the screen capture to a file, we can use:

	>>> import pydroid
	>>> pydroid.bitmap.capture_screen().save('screengrab.png')

The filetype is either parsed automatically from the filename, or given as an optional parameter. Pydroid currently only supports the BMP and PNG filetypes, though, as those are really all that are practical for its purpose.

Loading a bitmap is done essentially the same way, only from a class method:

	>>> import pydroid
	>>> pydroid.bitmap.Bitmap.open('i-am-a-monkey-and-i-like-it.png')
	<Bitmap object at 0x1001d5378>

Sometimes it is desirable to keep a short script free of any outside dependencies. In the case of bitmaps, this can be accomplished with the `to_string()` and `from_string()` methods:

	>>> pydroid.bitmap.Bitmap.open('foo.png').to_string()
	'b2,3,eNpjYGD4f/MwBDGA2QBcMwpt'
	>>> pydroid.bitmap.Bitmap.from_string('b2,3,eNpjYGD4f/'
									      'MwBDGA2QBcMwpt')
	<Bitmap object at 0x12278>

This is not recommended for large bitmaps (a screenshot, for instance, is obviously _way_ too big), but can be useful for short images used in a script you want to be very easily distributable.

Aside from analyzing a bitmap's pixel data, the main use for loading a bitmap is finding it on the screen or inside another bitmap. For example, the following prints the coordinates of the first monkey found in a barrel of monkeys (scanned from left to right, top to bottom):

	import pydroid
	def where_is_the_monkey_i_say():
		"""Look for the monkey. Tell me if you found it."""
		monkey = pydroid.bitmap.Bitmap.open('monkey.png')
		barrel = pydroid.bitmap.Bitmap.open('barrel.png')

		pos = barrel.find_bitmap(monkey)
		if pos:
			print "We found him! He's at %s!" % str(pos)
		else:
			print "There is no monkey... what kind of barrel is this?!"

	where_is_the_monkey_i_say()

## Closing & API Reference

As I hope you can see, these functions are enormously useful and have a number of practical values.

Hope you enjoy using pydroid! For a more in depth overview, I've attempted to make the [API Reference](http://msanders.com/pydroid/documentation/api-reference) as complete and approachable as possible.

<div id="pydroid-license"></div>

## License

<div id="pydroid-license-summary"></div>

### Summary

Pydroid (the software) is licensed under the terms of the MIT license.

The documentation for Pydroid is licensed under the terms of the FreeBSD Documentation License.

These licenses are both very liberal and permit nearly anything, including using the code in other projects (as long as credit is given).

<div id="pydroid-mit-license"></div>

### MIT License

Copyright &copy; 2010 Michael Sanders.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

<div id="pydroid-freebsd-license"></div>

### The FreeBSD Documentation License

Copyright &copy; 2010 Michael Sanders. All rights reserved.

Redistribution and use in source (Markdown, plaintext, et. al.) and "compiled" forms (HTML, PDF and so forth) with or without modification, are permitted provided that the following conditions are met:

Redistributions of source code (Markdown, plaintext, et. al.) must retain the above copyright notice, this list of conditions and the following disclaimer as the first lines of this file unmodified.
Redistributions in compiled form (HTML, PDF and so on) must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

THIS DOCUMENTATION IS PROVIDED "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS DOCUMENTATION, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
