# coding: utf-8

# Copyright 2017 Michael Puerrer
#
# License:  Standard 3-clause BSD; see "license.txt" for full license terms
#           and contributor agreement.


cdef extern from "gsl/gsl_errno.h":
    ctypedef void gsl_error_handler_t(const char *reason, const char *file, 
                                      int line, int gsl_errno);
    gsl_error_handler_t *gsl_set_error_handler(gsl_error_handler_t *new_handler) except *;


cdef void handler(const char *reason, const char *file, int line, int gsl_errno) except *:
    raise ValueError("GSL error %s in %s line %d. gsl_errno = %d\n" %(reason, file, line, gsl_errno))


cdef gsl_error_handler_t *old_handler = gsl_set_error_handler(<gsl_error_handler_t *> handler);
print "__init__.pyx: Successfully installed error handler!"
