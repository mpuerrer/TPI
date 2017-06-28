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

cdef extern from "gsl/gsl_errno.h":
    ctypedef void gsl_error_handler_t(const char *reason, const char *file, 
                                      int line, int gsl_errno);
    gsl_error_handler_t *gsl_set_error_handler(gsl_error_handler_t *new_handler) except *;


cdef void handler(const char *reason, const char *file, int line, int gsl_errno) except *:
    raise ValueError("GSL error %s in %s line %d. gsl_errno = %d\n" %(reason, file, line, gsl_errno))


cdef gsl_error_handler_t *old_handler = gsl_set_error_handler(<gsl_error_handler_t *> handler);
print "__init__.pyx: Successfully installed error handler!"
