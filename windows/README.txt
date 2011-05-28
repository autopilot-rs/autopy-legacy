This directory contains statically compiled binaries of libpng 1.5.2 and zlib
1.2.5. They were compiled using the "visualc71" project in the libpng 1.5.2
source[1] on Microsoft Visual Studio 2008.

The following settings were used:

1.) The instructions stated in README.txt in the visual71 directory were
followed.

2.) The "Lib Release" Configuration was set for both libpng and zlib (pngtest
was not built).

3.) For both libpng and zlib, on the Property Pages dialog under Configuration
Properties > Library > General, "uuid.lib" was set under "Ignore Specific
Library" in order to avoid a linking error.

4.) In addition, under Configuration Properties > C/C++ > Optimization, "Favor
Small Code" was selected in order to produce smaller binaries.

Using this approach, no external libraries or DLLs should be required for the
user to install (outside of those already installed by Python).

[1]: (Download: http://prdownloads.sourceforge.net/libpng/lpng152.zip?download
      Path: "projects/visualc71")
