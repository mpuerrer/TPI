# coding: utf-8

import numpy
from distutils.core import setup
from distutils.extension import Extension

try:
    from Cython.Build import cythonize
    print 'Using Cython'
    USE_CYTHON = True
except:
    print 'Not using Cython'
    USE_CYTHON = False



VERSION = '0.1'

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
Development Status :: 3 - Alpha
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
    version = VERSION,
    ext_modules=extensions,
    author="Michael Pürrer",
    author_email="Michael.Puerrer@gmail.com",
    description = short_desc,
    long_description = long_desc,
    classifiers = [x for x in cls_txt.split("\n") if x],
    install_requires = SETUP_REQUIRES
    # url=
)

