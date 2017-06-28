/*
 * Copyright (C) 2017, Michael Pürrer, Jonathan Blackman.
 *
 *  This file is part of TPI.
 *  
 *  TPI is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 *  
 *  TPI is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *  
 *  You should have received a copy of the GNU General Public License
 *  along with TPI.  If not, see <http://www.gnu.org/licenses/>.
 */


#include "TensorProductInterpolation.h"
#include <time.h>
#include <stdio.h>


/******************************* Generic code *********************************/

void TP_Interpolation_Setup_ND(
    array *nodes,                     // Input: array of arrys containing the nodes
                                      // for each parameter space dimension
    int n,                            // Input: Dimensionality of parameter space
    gsl_bspline_workspace ***bw_out   // Output: pointer to array of pointers to
                                      // B-spline workspaces: The array of pointers
                                      // must be allocated
) {
    gsl_bspline_workspace **bw = *bw_out;

    for (int j=0; j<n; j++) {
        int nc = nodes[j].n + 2;
        // Setup cubic B-spline workspaces
        const size_t nbreak = nc-2;  // must have nbreak = n-2 for cubic splines
        bw[j] = gsl_bspline_alloc(4, nbreak);
        gsl_vector *breakpts = gsl_vector_alloc(nbreak);

        for (int i=0; i<nbreak; i++)
            gsl_vector_set(breakpts, i, nodes[j].vec[i]);

        gsl_bspline_knots(breakpts, bw[j]);
        gsl_vector_free(breakpts);
    }
}

int TP_Interpolation_ND(
    double *v,                    // Input: flattened TP spline coefficient array
    int n,                        // Input: length of TP spline coefficient array v
    double* X,                    // Input: parameter space evaluation point of length m
    int m,                        // Input: dimensionality of parameter space
    gsl_bspline_workspace **bw,   // Input: array of pointers to B-spline workspaces
    double *y                     // Output: TP spline evaluated at X
) {

#ifdef CHECK_RANGES
    for (int j=0; j<m; j++) {
        gsl_vector* knots = bw[j]->knots;
        double x_min = gsl_vector_get(knots, 0);
        double x_max = gsl_vector_get(knots, knots->size - 1);
        if (X[j] < x_min || X[j] > x_max) {
            //fprintf(stderr, "Error in TP_Interpolation_ND: X[%d] = %g is outside of knots vector [%g, %g]!\n", j, X[j], x_min, x_max);
            return TPI_FAIL;
        }
    }
#endif

    clock_t time1;
    clock_t time2;
    clock_t time3;
    time1 = clock();

    int nc[m];
    gsl_vector *B[m];
    size_t is[m]; // first non-zero spline
    size_t ie[m]; // last non-zero spline
    for (int j=0; j<m; j++) {
        // Dimensionality of coefficients for each dimension
        nc[j] = bw[j]->n;

        // Store nonzero cubic (order k=4) B-spline basis functions
        B[j] = gsl_vector_alloc(4);

        // Evaluate all potentially nonzero cubic B-spline basis functions at X
        // and store them in the array of vectors Bx[].
        // Since the B-splines are of compact support we only need to store a small
        // number of basis functions to avoid computing terms that would be zero anyway.
        gsl_bspline_eval_nonzero(X[j], B[j], &is[j], &ie[j], bw[j]);
    }

    time2 = clock();
    printf("%0.6f seconds for bspline evals\n", ((float)time2 - (float)time1)/CLOCKS_PER_SEC);

    // This will hold the value of the TP spline interpolant
    // To compute it we need to calculate an m-dimensional sum over
    // spline coefficients and non-zero B-spline bases.
    double sum = 0;

    // Start logic of dynamic nested loop of depth m
    int max = 4; // upper bound of each nested loop
    int *slots = (int *) malloc(sizeof(int) * m); // m indices in range(0, 4)

    // Store the products of the first k bsplines, and the kth partial sums of the indices.
    // Prepend the identity so we can always index with [i-1].
    double *b_prod_hierarchy = (double *) malloc(sizeof(double) * (m+1));
    int *i_sum_hierarchy = (int *) malloc(sizeof(int) * (m+1));

    // Initialize the indices and current bspline products
    int idx_sum = 0;
    double product = 1;
    b_prod_hierarchy[0] = 1;
    i_sum_hierarchy[0] = 0;
    for (int i = 0; i < m; i++) {
        slots[i] = 0;
        product *= gsl_vector_get(B[i], 0);
        b_prod_hierarchy[i+1] = product;
        idx_sum = idx_sum * nc[i] + is[i];
        i_sum_hierarchy[i+1] = idx_sum;
    }

    // Loop over last index first, loop over first index last.
    int index;

    while (true) {
        // Add the current coefficient times the product of all current bsplines
        sum += v[ i_sum_hierarchy[m] ] * b_prod_hierarchy[m];

        // Update the slots to the next valid configuration
        slots[m-1]++;
        index = m-1;
        while (slots[index] == max) {
            // Overflow, we're done
            if (index == 0)
                goto cleanup;

            slots[index--] = 0;
            slots[index]++;
        }

        // Now update the index sums and bspline products for anything that was altered
        while (index < m) {
            b_prod_hierarchy[index+1] = b_prod_hierarchy[index] * gsl_vector_get(B[index], slots[index]);
            i_sum_hierarchy[index+1] = i_sum_hierarchy[index] * nc[index] + is[index] + slots[index];
            index++;
        }
    }

    cleanup:
    time3 = clock();
    printf("%0.6f seconds for coef eval and sum\n", ((float)time3 - (float)time2)/CLOCKS_PER_SEC);

    for (int j=0; j<m; j++)
        gsl_vector_free(B[j]);
    free(slots);
    free(b_prod_hierarchy);
    free(i_sum_hierarchy);

    *y = sum;
    return TPI_SUCCESS;
}

/******************************* 1D functions *********************************/

// Initialize B-spline workspaces and knots
int Interpolation_Setup_1D(
    double *xvec,                       // Input: knots: FIXME: knots are calculate internally, so shouldn't need to do that here
    int nx,                             // Input length of knots array xvec
    gsl_bspline_workspace **bw,         // Output: Initialized B-spline workspace
    gsl_bspline_deriv_workspace **Dbw   // Output: Initialized B-spline derivative workspace
) {
    int ncx = nx + 2;

    // Setup cubic B-spline workspace
    const size_t nbreak_x = ncx-2;  // must have nbreak = n-2 for cubic splines

    if (*bw || *Dbw) {
        fprintf(stderr, "Error: Interpolation_Setup_1D(): B-spline workspace pointers should be NULL.\n");
        return TPI_FAIL;
    }
    *bw = gsl_bspline_alloc(4, nbreak_x);
    *Dbw = gsl_bspline_deriv_alloc(4);

    gsl_vector *breakpts_x = gsl_vector_alloc(nbreak_x);

    for (int i=0; i<nbreak_x; i++)
      gsl_vector_set(breakpts_x, i, xvec[i]);

    gsl_bspline_knots(breakpts_x, *bw);

    gsl_vector_free(breakpts_x);

    return (*bw)->n; // dimensions of the B-spline basis
}

// Evaluate the B-spline basis functions B_i(x) for all i at x.
// Here we specialize to cubic B-spline bases.
int Bspline_basis_1D(
    double *B_array,           // Output: the evaluated cubic B-splines
                               // B_i(x) for the knots defined in bw
    int n,                     // Input: length of Bx4_array
    gsl_bspline_workspace *bw, // Input: Initialized B-spline workspace
    double x                   // Input: evaluation point
) {
    double a = gsl_vector_get(bw->knots, 0);
    double b = gsl_vector_get(bw->knots, bw->knots->size - 1);
    if (x < a || x > b) {
        //fprintf(stderr, "Error: Bspline_basis_1D(): x: %g is outside of knots vector with bounds [%g, %g]!\n", x, a, b);
        return TPI_FAIL;
    }

    gsl_vector *B = gsl_vector_alloc(bw->n);
    gsl_bspline_eval(x, B, bw);

    for (int i=0; i<bw->n; i++)
        B_array[i] = gsl_vector_get(B, i);

    return TPI_SUCCESS;
}

// Evaluate the 3rd derivative of the B-spline basis functions B_i(x) for all i at x.
// Here we specialize to cubic B-spline bases.
int Bspline_basis_3rd_derivative_1D(
    double *D3_B_array,               // Output: the evaluated 3rd derivative of cubic
                                      // B-splines B_i(x) for the knots defined in bw
    int n,                            // Input: length of Bx4_array
    gsl_bspline_workspace *bw,        // Input: Initialized B-spline workspace
    gsl_bspline_deriv_workspace *Dbw, // Input: Initialized B-spline derivative workspace
    double x                          // Input: evaluation point
) {
    double a = gsl_vector_get(bw->knots, 0);
    double b = gsl_vector_get(bw->knots, bw->knots->size - 1);
    if (x < a || x > b) {
        //fprintf(stderr, "Error: Bspline_basis_3rd_derivative_1D(): x: %g is outside of knots vector with bounds [%g, %g]!\n", x, a, b);
        return TPI_FAIL;
    }

    size_t n_deriv = 3;
    gsl_matrix *D3_B = gsl_matrix_alloc(bw->n, n_deriv+1);
    gsl_bspline_deriv_eval(x, n_deriv, D3_B, bw, Dbw); // fine for GSL 1.16; last argument not used in new GSL versions

    for (int i=0; i<bw->n; i++)
        D3_B_array[i] = gsl_matrix_get(D3_B, i, 3); // just copy the 3rd derivative

    return TPI_SUCCESS;
}
