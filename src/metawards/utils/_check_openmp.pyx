
from cython.parallel cimport parallel
cimport openmp

__all__ = ["is_openmp_supported"]


def is_openmp_supported():
    """Return whether or not this MetaWards executable
       supports OpenMP
    """

    cdef int num_threads = 0

    # This will use our stub function if OpenMP support
    # is not compiled in - the stub returns '0'
    num_threads = openmp.omp_get_num_threads()

    return num_threads > 0
