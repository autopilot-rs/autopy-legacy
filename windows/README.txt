This directory includes libraries and a DLL for libpng and zlib on Windows. Originally I attempted to use the GnuWin32 variants, but the libpng binaries were crash-prone so I've compiled my own here. The result is that you do not have to install GnuWin32, zlib, or libpng yourself at all -- just build with the setup.py script and it will take care of the rest.

Every file in the "data_files" directory gets copied into the site-packages/automan directory (i.e., where the package gets installed to). Currently this is only a DLL required to use zlib.
