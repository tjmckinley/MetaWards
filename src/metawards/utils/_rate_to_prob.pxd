#!/bin/env/python3
#cython: boundscheck=False
#cython: cdivision=True
#cython: initializedcheck=False
#cython: cdivision_warnings=False
#cython: wraparound=False
#cython: binding=False
#cython: initializedcheck=False
#cython: nonecheck=False
#cython: overflowcheck=False

from libc.math cimport exp

cdef inline double rate_to_prob(double rate) nogil:
    """Convert the return the probability associated with the passed
       infection rate
    """
    return rate - (0.5*rate*rate) if rate < 1e-6 else 1.0 - exp(-rate)
