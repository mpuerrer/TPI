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

# A py.test compliant unit test

#!/usr/bin/env python

"""
TPI.pyx

designed to be run-able with pytest

MP 02/2017
"""

import pytest
import numpy as np
import TPI

def test_BsplineBasis1D():
    x1 = np.array([1.1, 3.2, 5.1, 7.2, 9.3, 12])
    b = TPI.BsplineBasis1D(x1)
    atol = np.finfo(float).eps

    # Test B-spline basis functions at fixed x
    b_eval_Mma = np.array([0, 0.00210526315789473, 0.2988222605694564, 0.6262726488352028, 0.07279982743744609, 0, 0, 0])
    b_eval_TPI = b.EvaluateBsplines(4.7)
    assert np.array_equal(b_eval_Mma, b_eval_TPI)

    # Test 3rd derivative of B-spline basis functions at fixed x
    Db_eval_Mma = np.array([0., -0.19736842105263172, 0.4562122519413291, -0.38826574633304595, 0.1294219154443486, 0., 0., 0.])
    Db_eval_TPI = b.EvaluateBsplines3rdDerivatives(4.7)
    # print 'Db_eval_Mma - Db_eval_TPI', Db_eval_Mma - Db_eval_TPI
    assert np.allclose(Db_eval_Mma, Db_eval_TPI, atol=atol, rtol=0)


def test_BsplineBasis1D_fail():
    with pytest.raises(ValueError):
        x2 = np.array([1.1, -3.2, 5.1, 7.2, 9.3, 12])
        TPI.BsplineBasis1D(x2)

    with pytest.raises(ValueError):
        x1 = np.array([1.1, 3.2, 5.1, 7.2, 9.3, 12])
        b = TPI.BsplineBasis1D(x1)    
        b_eval_TPI = b.EvaluateBsplines(-4.7)

    with pytest.raises(ValueError):
        x1 = np.array([1.1, 3.2, 5.1, 7.2, 9.3, 12])
        b = TPI.BsplineBasis1D(x1)    
        b_eval_TPI = b.EvaluateBsplines3rdDerivatives(-4.7)

    with pytest.raises(ValueError):
        TPI.BsplineBasis1D(None)

    with pytest.raises(ValueError):
        x3 = np.array([1.1])
        TPI.BsplineBasis1D(x3)

    with pytest.raises(ValueError):
        x3 = np.array([np.nan, np.nan])
        TPI.BsplineBasis1D(x3)

    with pytest.raises(ValueError):
        x3 = np.array([1.1, np.inf, 5.1, 7.2, 9.3, 12])
        TPI.BsplineBasis1D(x3)

    with pytest.raises(ValueError):
        x2 = np.array([1.1, 3.4+2.1j, 5.1, 7.2, 9.3, 12])
        TPI.BsplineBasis1D(x2)

    with pytest.raises(ValueError):
        x2 = np.arange(12, dtype=np.float64).reshape((3,2,2))
        TPI.BsplineBasis1D(x2)

    # with pytest.raises(ValueError):
    #     x2 = np.array([1.1, "-3.4", 5.1, 7.2, 9.3, 12])
    #     TPI.BsplineBasis1D(x2)


def test_SplineMatrix():
    x1 = np.array([1.1, 3.2, 5.1, 7.2, 9.3, 12])
    b = TPI.BsplineBasis1D(x1)
    atol = np.finfo(float).eps

    # Test knots
    b_phi, b_knots = b.AssembleSplineMatrix()
    knots = np.array([1.1, 1.1, 1.1, 1.1, 3.2, 5.1, 7.2, 9.3, 12, 12, 12, 12])
    assert np.array_equal(b_knots, knots)
    
    # Test spline matrix with not-a-knot boundary conditions
    phi = np.array([[-0.647878198898607, 1.363954102944436, -1.0920157536698896, 0.505361765068409, -0.1294219154443486, 0, 0, 0],
    [1., 0., 0., 0., 0, 0, 0, 0],
    [0, 0.22562499999999996, 0.5936372950819674, 0.18073770491803284, 0., 0, 0, 0],
    [0, 0, 0.1807377049180329, 0.6713114754098362, 0.14795081967213106, 0., 0, 0],
    [0, 0, 0, 0.17213114754098363, 0.675694939415538, 0.1521739130434783, 0., 0],
    [0, 0, 0, 0, 0.22010869565217378, 0.588485054347826, 0.1914062500000001, 0.],
    [0, 0, 0, 0, 0., 0., 0., 1.],
    [0, 0, 0, -0.11152001784320278, 0.3634726507482166, -0.6438789507572575, 0.6967578984039893, -0.30483158055174536]])
  
    # print 'b_phi - phi', np.matrix(b_phi - phi)
    assert np.allclose(b_phi, phi, atol=atol, rtol=0)

def test_TP_spline_interpolation_1D():
    xi = np.array([0.1, 0.11, 0.12, 0.15, 0.2, 0.23, 0.24, 0.248, 0.249, 0.25])
    X = [xi]

    def f(x):
        return np.cos(10.0*x)

    F = f(xi)

    TPint = TPI.TP_Interpolant_ND(X)
    TPint.TPInterpolationSetupND()
    TPint.ComputeSplineCoefficientsND(F)
    
    # Check coefficients
    c_TPI = TPint.GetSplineCoefficientsND()
    assert c_TPI.shape[0] == 12
    
    # Check evaluated interpolant
    Y = np.array([0.16])
    res = TPint.TPInterpolationND(Y)
    res_Mma = -0.029174542430286686
    assert np.allclose(res, res_Mma, atol=1e-13, rtol=0)

def test_TP_spline_interpolation_2D():
    xi = np.array([0.1, 0.11, 0.12, 0.15, 0.2, 0.23, 0.24, 0.248, 0.249, 0.25])
    yi = np.array([-1, -0.8, -0.6, -0.4, -0.2, 0.0, 0.2, 0.4, 0.6, 0.8, 0.9, 0.95, 1.0])
    X = [xi, yi]

    def f(x,y):
        return np.sin(x) * np.arccos(y)

    xx, yy = np.meshgrid(xi, yi, indexing='ij')
    F = f(xx, yy)

    TPint = TPI.TP_Interpolant_ND(X)
    TPint.TPInterpolationSetupND()
    TPint.ComputeSplineCoefficientsND(F)
    
    # Check coefficients
    c_TPI = TPint.GetSplineCoefficientsND()
    assert c_TPI.shape == (12, 15)
    
    # Check evaluated interpolant
    Y = np.array([0.16, 0.28])
    res = TPint.TPInterpolationND(Y)
    res_Mma = 0.2050780890103884
    assert np.allclose(res, res_Mma, atol=1e-13, rtol=0)

    with pytest.raises(ValueError):
        res = TPint.TPInterpolationND(np.array([-0.8, 12.3]))

def test_TP_spline_interpolation_3D():
    xi = np.array([0.1, 0.11, 0.12, 0.15, 0.2, 0.23, 0.24, 0.248, 0.249, 0.25])
    yi = np.array([-1, -0.8, -0.6, -0.4, -0.2, 0.0, 0.2, 0.4, 0.6, 0.8, 0.9, 0.95, 1.0])
    zi = np.array([-1, -0.8, -0.6, -0.4, 0.0, 0.2, 0.4, 0.8, 1.0])
    X = [xi, yi, zi]

    def f(x,y,z):
        return np.sin(x) * np.arccos(y) * np.exp(z)

    xx, yy, zz = np.meshgrid(xi, yi, zi, indexing='ij')
    F = f(xx, yy, zz)

    TPint = TPI.TP_Interpolant_ND(X)
    TPint.TPInterpolationSetupND()
    TPint.ComputeSplineCoefficientsND(F)

    # Check coefficients
    c_TPI = TPint.GetSplineCoefficientsND()
    assert c_TPI.shape == (12, 15, 11)
    
    TPint.SetSplineCoefficientsND(c_TPI)

    with pytest.raises(TypeError):
        TPint2 = TPI.TP_Interpolant_ND(["aaaa"])

    with pytest.raises(ValueError):
        c = np.arange(12, dtype=np.float64).reshape((3,2,2))
        TPint.SetSplineCoefficientsND(c)

    with pytest.raises(ValueError):
        c = []
        TPint.SetSplineCoefficientsND(c)

    c_Mma = np.loadtxt("data/c_Mma_3D.dat") # grab external coefficient data exported from Mathematica
    assert len(c_TPI.flatten()) == len(c_Mma)
    assert np.allclose(c_TPI.flatten(), c_Mma, atol=1e-12, rtol=0)

    # Check evaluated interpolant
    Y = np.array([0.1692602, 0.2827312351474, -0.26624193])
    res = TPint.TPInterpolationND(Y)
    res_Mma = 0.16576975057631677
    assert np.allclose(res, res_Mma, atol=1e-13, rtol=0)

    # and its relative error compared to the function f
    rel_err = (f(*Y) - TPint.TPInterpolationND(Y)) / f(*Y)
    rel_err_Mma = -0.00008225243596719076
    assert np.allclose(rel_err, rel_err_Mma, atol=1e-13, rtol=0)

    # create a new object and set the spline coefficients directly
    TPint2 = TPI.TP_Interpolant_ND(X, coeffs=c_TPI)
    res2 = TPint2.TPInterpolationND(Y)
    assert np.allclose(res2, res_Mma, atol=1e-13, rtol=0)

    with pytest.raises(ValueError):
        Y = np.array([-1692602, 28.27312351474, -2.6624193])
        res = TPint.TPInterpolationND(Y)

def test_TP_spline_interpolation_4D():
    x1 = np.array([0.1, 0.11, 0.12, 0.15, 0.2, 0.23, 0.24, 0.248, 0.249, 0.25])
    x2 = np.array([-1, -0.8, -0.6, -0.4, -0.2, 0.0, 0.2, 0.4, 0.6, 0.8, 0.9, 0.95, 1.0])
    x3 = np.array([-1, -0.8, -0.6, -0.4, 0.0, 0.2, 0.4, 0.8, 1.0])
    x4 = np.array([-0.8, -0.6, -0.4, 0.0, 0.5, 1.0, 1.5])
    X = [x1, x2, x3, x4]

    def f(x1,x2,x3,x4):
        return np.sin(x1) * np.arccos(x2) * np.exp(x3) * np.cos(x4)

    xx1, xx2, xx3, xx4 = np.meshgrid(x1, x2, x3, x4, indexing='ij')
    F = f(xx1, xx2, xx3, xx4)

    TPint = TPI.TP_Interpolant_ND(X)
    TPint.TPInterpolationSetupND()
    TPint.ComputeSplineCoefficientsND(F)
    
    # Check coefficients
    c_TPI = TPint.GetSplineCoefficientsND()
    assert c_TPI.shape == (12, 15, 11, 9)
    
    # Check evaluated interpolant
    Y = np.array([0.16, 0.28, -0.26, 0.05])
    res = TPint.TPInterpolationND(Y)
    res_Mma = 0.15790875815398853
    assert np.allclose(res, res_Mma, atol=1e-13, rtol=0)

def test_TP_spline_interpolation_7D():
    # Randomly generated nodes data
    # def gen():
    #     n = np.random.randint(5, 12, 1).item()
    #     x = np.random.random(n) /  np.random.random(1)
    #     x.sort()
    #     return x
    #
    # X = [gen() for i in range(7)]
  
    X = [np.array([ 0.04210023,  0.08049712,  0.10439003,  0.23567061,  0.26747638,
         0.51894333,  0.87695656,  1.13424169]),
   np.array([ 0.06512773,  0.10554492,  0.30739299,  0.52934042,  0.53375456,
           0.70565296,  0.90977329,  1.0904668 ,  1.09161535]),
   np.array([ 0.17568927,  0.20990473,  0.40272389,  0.54519648,  0.62970609,
           0.65005828,  0.67672559,  1.03551716]),
   np.array([ 0.04209146,  0.18164518,  0.32001217,  0.5469396 ,  0.65685659,
           0.69706066,  0.8338755 ,  0.84175853,  1.03421552]),
   np.array([ 0.15592869,  0.24300596,  0.53102712,  0.76409654,  0.83426527]),
   np.array([ 0.09278997,  0.60858288,  0.68604479,  0.69185573,  1.05187626,
           1.25311729,  1.83783997,  2.30367353,  2.34835024,  2.5526501 ,
           2.88134666]),
   np.array([ 0.02039465,  0.84219648,  1.34410666,  1.50315468,  1.77942063,
           4.30194875,  4.81437542,  5.30694653,  6.04394163])]

    def f(x1,x2,x3,x4,x5,x6,x7):
        return np.sin(x1) * np.arccos(x2/2.) * np.exp(x3) * np.cos(x4) * np.abs(x5) + np.sin(x6)*np.exp(x7)

    xx1, xx2, xx3, xx4, xx5, xx6, xx7 = np.meshgrid(X[0], X[1], X[2], X[3], X[4], X[5], X[6], indexing='ij')
    F = f(xx1, xx2, xx3, xx4, xx5, xx6, xx7)

    TPint = TPI.TP_Interpolant_ND(X)
    TPint.TPInterpolationSetupND()
    TPint.ComputeSplineCoefficientsND(F)
    
    # Check coefficients
    c_TPI = TPint.GetSplineCoefficientsND()
    assert c_TPI.shape == (10, 11, 10, 11, 7, 13, 11)
    
    # Check evaluated interpolant
    Y = np.array([0.673, 0.2836, 0.734, 0.089, 0.619, 1.782, 4.96])
    res_expected = 140.401088491
    res = TPint.TPInterpolationND(Y)
    assert np.allclose(res, res_expected, atol=1e-7, rtol=0)

    rel_err_expected = 0.00119488601664
    rel_err = (f(*Y) - res) / f(*Y)
    assert np.allclose(rel_err, rel_err_expected, atol=1e-8, rtol=0)

    with pytest.raises(ValueError):
        Y = np.array([-16.9, 26.02, 28.2731, 23.51474, -2.6624, 193.3, 9915.1])
        res = TPint.TPInterpolationND(Y)


# Hack for running tests since pytest does not import the Cython module under python3
if __name__ == "__main__":
    test_BsplineBasis1D()
    test_BsplineBasis1D_fail()
    test_SplineMatrix()
    test_TP_spline_interpolation_1D()
    test_TP_spline_interpolation_2D()
    test_TP_spline_interpolation_3D()
    test_TP_spline_interpolation_4D()
    test_TP_spline_interpolation_7D()
    print('All tests passed successfully')
