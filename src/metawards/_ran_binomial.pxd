
cimport cython
from libc.stdint cimport uintptr_t

cdef extern from "gsl/gsl_rng.h":
    ctypedef struct gsl_rng_type
    ctypedef struct gsl_rng
    cdef gsl_rng_type *gsl_rng_default

    gsl_rng *gsl_rng_alloc ( gsl_rng_type * T) nogil
    void gsl_rng_free (gsl_rng * r) nogil

    void gsl_rng_free (gsl_rng * r) nogil

    void gsl_rng_set ( gsl_rng * r, unsigned long int seed) nogil


cdef extern from "gsl/gsl_randist.h":
    unsigned int gsl_ran_binomial ( gsl_rng * r, double p, unsigned int n) nogil


cdef inline uintptr_t _construct_gsl_rng() nogil:
    """Construct and return a pointer to a new gsl random number
       generator. This will return a uintptr_t that can be handled
       in Python. You must destroy this random number generator
       when you don't want it anymore, using the _delete_gsl_rng
       function
    """
    cdef gsl_rng_type * T
    cdef gsl_rng* r
    T = gsl_rng_default
    r = gsl_rng_alloc(T)

    cdef uintptr_t p = <uintptr_t>r

    return p


cdef inline void _delete_gsl_rng(uintptr_t rng) nogil:
    """Delete the passed gsl random number generator.
       WARNING: It is not safe to use this pointer to
       generate any more random numbers!
    """
    cdef gsl_rng* r = _get_gsl_ptr(rng)
    gsl_rng_free(r)


cdef inline gsl_rng* _get_gsl_ptr(uintptr_t rng) nogil:
    """Get the underlying gsl_rng pointer from the uintptr_t"""
    cdef gsl_rng* r = <gsl_rng*>rng

    return r


cdef inline uintptr_t _seed_ran_binomial(uintptr_t rng,
                                         unsigned long seed) nogil:
    """Seed the passed random number generator"""
    cdef gsl_rng* r = _get_gsl_ptr(rng)
    gsl_rng_set(r, seed)


@cython.boundscheck(False)
@cython.wraparound(False)
cdef inline int _ran_binomial(gsl_rng *rng, double p, int n) nogil:
    """Generate a random number from the binomial distribution
       described by p and n
    """
    return gsl_ran_binomial(rng, p, n)
