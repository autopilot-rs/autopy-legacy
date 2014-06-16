#!/usr/bin/env python

from __future__ import print_function

import os
import platform
import sys
import textwrap

from distutils.core import setup, Extension
try:
    from subprocess import getoutput
except ImportError:
    from commands import getoutput

# Determine platform being used.
system = platform.system()
USE_MAC = USE_WINDOWS = USE_X11 = False
if system == 'Darwin':
    USE_MAC = True
elif system == 'Windows' or system == 'Microsoft':
    USE_WINDOWS = True
else: # Default to X11
    USE_X11 = True

def create_package_dir(package_name, docstring, module_names):
    """Automates creation of __init__.py and package directory."""
    dir_path = os.path.join(sys.path[0], package_name)
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)

    # File is in the format:
    # """
    # [doc-string (wrapped to 80 chars)]
    # """
    #
    # # Import all sub-modules for convenience
    # import [package-name].module_name
    # ...
    module_names = ['import ' + package_name + '.' + name
                    for name in sorted(module_names)]
    file_contents = '"""\n' + textwrap.fill(docstring, 80) + '\n"""\n' \
                    "\n# Import all sub-modules for convenience\n" + \
                    "\n".join(module_names)

    # Only write file if it has been changed.
    init_path = os.path.join(dir_path, '__init__.py')
    if not os.path.exists(init_path):
        update_file = True
    else:
        f = open(init_path, 'r')
        update_file = file_contents != f.read()
        f.close()

    if update_file:
        print('Updating __init__.py')
        f = open(init_path, 'w')
        f.write(file_contents)
        f.close()

def create_ext_modules(src_dir):
    """Returns list of ext modules to be used in distutils.setup()."""

    # Submodules of the package to be installed
    # Only a path relative to the |src_dir| is needed
    modules = {
                'mouse' : {'files' : ['autopy-mouse-module.c', 'mouse.c',
                                      'deadbeef_rand.c', 'py-convenience.c',
                                      'screen.c']},
                'bitmap' : {'files' : ['autopy-bitmap-module.c',
                                       'py-convenience.c', 'py-bitmap-class.c',
                                       'MMBitmap.c',
                                       'io.c', 'bmp_io.c',
                                       'png_io.c', 'str_io.c', 'snprintf.c',
                                       'screengrab.c', 'screen.c',
                                       'pasteboard.c', 'color_find.c',
                                       'bitmap_find.c', 'UTHashTable.c',
                                       'MMPointArray.c', 'zlib_util.c',
                                       'base64.c',
                                       ],
                            'libraries' : ['png', 'z']},
                'color' : {'files' : ['autopy-color-module.c', 'MMBitmap.c']},
                'screen' : {'files' : ['autopy-screen-module.c', 'screen.c',
                                       'screengrab.c', 'MMBitmap.c']},
                'key' : {'files' : ['autopy-key-module.c', 'keypress.c',
                                    'keycode.c', 'deadbeef_rand.c',
                                    'py-convenience.c']},
                'alert' : {'files' : ['autopy-alert-module.c', 'alert.c']}
              }

    # Global compilation/linkage flags.
    lflags = warning_flags = []
    if not USE_WINDOWS: # gcc-specific flags
        warning_flags = [
                         '-Wall',
                         '-Wparentheses',
                         # '-Wsign-compare',
                         '-Winline',
                         '-Wbad-function-cast',
                         '-Wdisabled-optimization',
                         '-Wshadow',
                        ]

        lflags = [
                  # '-std=c89',
                  # '-pedantic', # Don't use gcc extensions
                 ]

    cflags = lflags + warning_flags
    macros = [
              # Remove assert()'s.
              ('NDEBUG', 1),

              # Determine endian-ness at runtime for C pre-processor at
              # pre-compile time :).
              ('MM_LITTLE_ENDIAN' if sys.byteorder == 'little'
                                  else 'MM_BIG_ENDIAN', None),
             ]
    libdirs = [] # Library dirs
    incdirs = [] # Include dirs

    # Parse platform-specific options
    if USE_MAC:
        def add_framework(module, framework):
            """Appends lflags module for linking to the given framework."""
            module.setdefault('lflags', []).extend(['-framework', framework])

        # Add frameworks for appropriate modules
        for module in 'mouse', 'key', 'alert':
            add_framework(modules[module], 'CoreFoundation')
        for module in 'mouse', 'key', 'screen', 'bitmap':
            add_framework(modules[module], 'ApplicationServices')
        for module in 'screen', 'bitmap':
            add_framework(modules[module], 'OpenGL')

        add_framework(modules['key'], 'Carbon')

        # Add OS X-specific #define's.
        macros.append(('IS_MACOSX', None))
    elif USE_X11:
        for module in 'mouse', 'key', 'screen', 'bitmap':
            modules[module]['files'].append('xdisplay.c')
            modules[module].setdefault('libraries', []).append('X11')
        for module in 'mouse', 'key':
            modules[module].setdefault('libraries', []).append('Xtst')

        for dir in '/usr/X11/lib', '/usr/X1186/lib':
            if os.path.exists(dir):
                libdirs.append(dir)

        modules['alert']['files'].append('snprintf.c')

        # Add X11-specific #define's.
        macros.append(('USE_X11', None))
    elif USE_WINDOWS:
        def add_lib(module_dict, lib):
            """Adds both standard and MSVC flag to link to library."""
            modules[module].setdefault('libraries', []).append(lib)

            # The "libraries" option doesn't appear to cater to MSVC, so we
            # have to add this flag separately:
            modules[module].setdefault('lflags', []).append(lib + '.lib')

        for module in 'mouse', 'key', 'screen', 'bitmap', 'alert':
            add_lib(modules[module], 'user32')
        for module in 'screen', 'bitmap':
            add_lib(modules[module], 'Gdi32')

        # MSVC doesn't use same lib names as everybody else.
        for wrong_lib in 'png', 'z':
            modules['bitmap']['libraries'].remove(wrong_lib)
        for right_lib in 'libpng', 'zlib':
            add_lib(modules['bitmap'], right_lib)

        # We store Windows libraries and headers in our own custom folder.
        win_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               'windows')


        # Libraries are statically compiled for their architecture.
        win_dir = os.path.join(win_dir,
                               'win64' if platform.architecture()[0] == '64bit'
                                       else 'win32')

        if not os.path.isdir(win_dir):
            raise IOError('windows directory not found at: "%s"' % win_dir)

        libdirs.append(win_dir)
        incdirs.append(win_dir)

        # Add Windows-specific macros.
        macros.extend([
                       ('IS_WINDOWS', None),

                       # Ignore warnings for using standard C functions.
                       ('_CRT_SECURE_NO_DEPRECATE', None),
                      ])

    # Define Extensions formally for distutils
    ext_modules = []
    for key in modules:
        # Add src directory to module filenames
        attributes = modules[key]
        files = [os.path.join(src_dir, filename) for filename in
                                                     attributes['files']]

        # Get module-specific args
        extra_link_args = attributes.get('lflags', []) + lflags
        libraries = attributes.get('libraries', [])

        ext_modules.append(Extension(name=key,
                                     sources=files,
                                     define_macros=macros,
                                     include_dirs=incdirs,
                                     library_dirs=libdirs,
                                     libraries=libraries,
                                     language='c',
                                     extra_compile_args=cflags,
                                     extra_link_args=extra_link_args))
    return ext_modules

PACKAGE_NAME = 'autopy'
PACKAGE_DESCRIPTION = \
'''AutoPy is a simple, cross-platform GUI automation toolkit for Python. It
includes functions for controlling the keyboard and mouse, finding colors
and bitmaps on-screen, and displaying alerts -- all in a cross-platform,
efficient, and simple manner.'''
EXT_MODULES = create_ext_modules('src/')

# Create __init__ directory
modules_names = [ext_modules.name for ext_modules in EXT_MODULES]
create_package_dir(PACKAGE_NAME, PACKAGE_DESCRIPTION, modules_names)

setup(name=PACKAGE_NAME,
      version='0.51',
      author='Michael Sanders',
      author_email='michael+autopy [at] msanders [dot] com',
      url='http://autopy.org',
      license='MIT',
      description='A simple, cross-platform GUI automation toolkit for Python.',
      long_description=PACKAGE_DESCRIPTION,
      platforms=('Mac OS X 10.5+', 'X11 with XTest Extension', 'Windows'),
      packages=[PACKAGE_NAME],
      ext_package=PACKAGE_NAME,
      ext_modules=EXT_MODULES)
