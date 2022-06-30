# coding: utf-8

#  Copyright (C) 2017, Michael Pürrer, Jonathan Blackman.
#
#  This file is part of TPI.
#
#  TPI is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  TPI is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with TPI.  If not, see <http://www.gnu.org/licenses/>.
#

from __future__  import print_function

import numpy
from distutils.core import setup
from distutils.extension import Extension

try:
    from Cython.Build import cythonize
    print('Using Cython')
    USE_CYTHON = True
except:
    print('Not using Cython')
    USE_CYTHON = False


from distutils.command.build_ext import build_ext
def get_export_symbols_fixed(self, ext):
    pass  # return [] also does the job!

    # replace wrong version with the fixed:
    build_ext.get_export_symbols = get_export_symbols_fixed



VERSION = '1.0.0'

NUMPY_DEP = 'numpy>=1.11'

SETUP_REQUIRES = [NUMPY_DEP]


ext = '.pyx' if USE_CYTHON else '.c'

extensions=[
    Extension("TPI",
              sources=["TPI"+ext, "TensorProductInterpolation.c"],
              include_dirs = [numpy.get_include()],
              language="c",
              extra_compile_args = ["-std=c99", "-O3"],
              libraries=["gsl", "gslcblas"]
    )
]


cls_txt = \
"""
Development Status :: 5 - Production/Stable
Intended Audience :: Science/Research
License :: OSI Approved :: BSD License
Programming Language :: Cython
Programming Language :: Python
Programming Language :: Python :: Implementation :: CPython
Topic :: Scientific/Engineering
Operating System :: Unix
Operating System :: POSIX :: Linux
Operating System :: MacOS :: MacOS X
"""

short_desc = "Tensor product spline interpolation package"

long_desc = \
"""
The TPI package implements tensor spline interpolation in arbitrary dimensions.

The package provides two classes

BsplineBasis1D: 
  * Calculates the B-spline basis for a 1-dimensional knots vector.
  * Constructs the spline matrix.
  * The splines are cubic and use not-a-knot boundary conditions.

TP_Interpolant_ND:
  * Provides setup and solution of tensor product spline problems in N dimensions.
  * Sets up spline data structures for a Cartesian product grid.
  * Computes the spline coefficients given data for a scalar gridfunction.
  * Carries interpolates the griddata at a desired point in the parameter space 
    spanned by the grid.
  * Spline coefficient data can be returned or set, so that the setup and solution of 
    the interpolation problem can be separated, by writing the coefficient data to disk.
"""

if USE_CYTHON:
    from Cython.Build import cythonize
    extensions = cythonize(extensions)

setup(
    name="TPI",
    version=VERSION,
    ext_modules=extensions,
    author="Michael Pürrer, Jonathan Blackman",
    author_email="Michael.Puerrer@gmail.com",
    description=short_desc,
    long_description=long_desc,
    classifiers=[x for x in cls_txt.split("\n") if x],
    install_requires=SETUP_REQUIRES,
    url="https://github.com/mpuerrer/TPI"
)

