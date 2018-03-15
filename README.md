# Introduction

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

# Installation

To install to the system python folder run

```
  python setup.py build_ext
  sudo python setup.py install
```

If you do not have admin rights you can install locally

```
  python setup.py build_ext
  python setup.py build_ext install --user
```

You can create a source distribution and then install the package with pip
```
python setup.py sdist
pip install --user
```

## Dependencies

TPI requires GSL, the GNU Scientific Library.
The project homepage is http://www.gnu.org/software/gsl/

TPI works with gsl 1.16, but not currently with gsl 2.x.
```
gsl-config --version
```


