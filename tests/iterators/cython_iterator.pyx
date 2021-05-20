
cimport cython
from cython.parallel import parallel, prange
from libc.stdint cimport uintptr_t

from metawards import Network
from metawards.iterators import iterate_default
from metawards.utils import Console

import random

from metawards.utils._get_array_ptr cimport get_double_array_ptr
from metawards.utils._ran_binomial cimport _ran_binomial, \
                             _construct_binomial_rng, \
                             _get_binomial_ptr, binomial_rng, \
                             _ran_uniform, _delete_binomial_rng, \
                             _seed_ran_binomial

def advance_test(network: Network, **kwargs):
    cdef double * ptr = get_double_array_ptr(network.nodes.day_foi)
    cdef uintptr_t rng = _construct_binomial_rng()
    cdef binomial_rng * rngptr = _get_binomial_ptr(rng)
    _seed_ran_binomial(rng, random.randint(1000000, 99999999)) 
    cdef double x = _ran_uniform(rngptr)
    cdef int y = _ran_binomial(rngptr, 0.5, 100)
    _delete_binomial_rng(rng)
    Console.info(f"Hello! {x} {y}")

def iterate_test(**kwargs):
    return [advance_test] + iterate_default(**kwargs)
