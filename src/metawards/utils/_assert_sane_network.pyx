#!/bin/env python3
#cython: boundscheck=False
#cython: cdivision=True
#cython: initializedcheck=False
#cython: cdivision_warnings=False
#cython: wraparound=False
#cython: binding=False
#cython: initializedcheck=False
#cython: nonecheck=False
#cython: overflowcheck=False

from .._network import Network

__all__ = ["assert_sane_network"]


cdef int * get_int_array_ptr(int_array):
    """Return the raw C pointer to the passed int array which was
       created using create_int_array
    """
    cdef int [::1] a = int_array
    return &(a[0])


def assert_sane_network(network: Network):
    """This function runs through and checks that the passed network
       is sane. If it is not, it prints some information and raises
       an AssertionError
    """
    # first check that the ith link really corresponds to the ith node.
    # This is assumed in most of the code
    """cdef int nlinks = network.nlinks
    cdef int nplay = network.plinks
    cdef int nnodes = network.nnodes

    assert nnodes <= nlinks

    links = network.to_links
    nodes = network.nodes
    plinks = network.play

    cdef int * links_ifrom = get_int_array_ptr(links.ifrom)
    cdef int * links_ito = get_int_array_ptr(links.ito)
    cdef int * nodes_label = get_int_array_ptr(nodes.label)

    cdef int i"""
    pass

    # Will add sanity checks as I get to fully understand this
    # data layout...
