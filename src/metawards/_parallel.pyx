
from libc.stdlib cimport malloc, free

from array import array

from cython.parallel cimport parallel
cimport openmp

__all__ = ["get_available_num_threads",
           "create_thread_generators"]


def get_available_num_threads():
    """Return the maximum number of threads that are recommended
       for this computer (the OMP_NUM_THREADS value)
    """
    a = array('i', [0])

    cdef int [::1] a_view = a

    openmp.omp_set_dynamic(1)
    with nogil, parallel():
        with gil:
            a[0] = openmp.omp_get_num_threads()

    num_threads = a[0]

    print(f"Recommended to use nthreads = {num_threads}")
    return num_threads


def create_thread_generators(rng, nthreads):
    """Return a set of random number generators, one for each
       thread - these are seeded using the next 'nthreads'
       random numbers drawn from the passed generator

       If 'nthreads' is 1, 0 or None, then then just
       returns the passed 'rng'
    """
    rngs = []

    if nthreads is None or nthreads <= 1:
        rngs.append(rng)
    else:
        from ._ran_binomial import seed_ran_binomial, ran_int

        for i in range(0, nthreads):
            seed = ran_int(rng)
            print(f"Random seed for thread {i} equals {seed}")
            rngs.append(seed_ran_binomial(seed))

    # need to return these as an array so that they are more easily
    # accessible from the OpenMP loops - rng is a unsigned 64bit integer
    # as a uintptr_t - this best corresponds to unsigned long ("L")
    return array("L", rngs)
