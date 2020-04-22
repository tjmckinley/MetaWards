#!/bin/env/python3
#cython: linetrace=False
# MUST ALWAYS DISABLE AS WAY TOO SLOW FOR ITERATE

cimport cython
from cython.parallel import parallel, prange
cimport openmp

from libc.math cimport sqrt

from .._parameters import Parameters
from .._network import Network

from ._get_array_ptr cimport get_int_array_ptr, get_double_array_ptr

__all__ = ["add_wards_network_distance"]


def add_wards_network_distance(network: Network, nthreads: int = 1):
    """Reads the location data in network.parameters.input_files.position
       and adds those locations to all of the nodes in the passed
       network. Then it calculates all of the distances between
       the nodes for each link and puts that into the
       'distance' property of each link
    """

    # ncov build does not have WEEKEND defined, so not writing this code now
    params = network.params
    wards = network.nodes
    links = network.to_links
    plinks = network.play

    line = None

    print("Reading in the positions...")

    cdef int i1 = 0
    cdef double x = 0.0
    cdef double y = 0.0

    cdef double * wards_x = get_double_array_ptr(wards.x)
    cdef double * wards_y = get_double_array_ptr(wards.y)

    try:
        with open(params.input_files.position, "r") as FILE:
            line = FILE.readline()

            while line:
                words = line.split()
                i1 = int(words[0])
                x = float(words[1])
                y = float(words[2])

                wards.x[i1] = x
                wards.y[i1] = y

                line = FILE.readline()
    except Exception as e:
        raise ValueError(f"{params.input_files.position} is corrupted or "
                         f"unreadable? Error = {e.__class__}: {e}, "
                         f"line = {line}")

    print("Calculating distances...")

    cdef double total_distance = 0
    cdef double distance, distance2

    cdef int * links_ifrom = get_int_array_ptr(links.ifrom)
    cdef int * links_ito = get_int_array_ptr(links.ito)

    cdef int * plinks_ifrom = get_int_array_ptr(plinks.ifrom)
    cdef int * plinks_ito = get_int_array_ptr(plinks.ito)

    cdef double * links_distance = get_double_array_ptr(links.distance)
    cdef double * plinks_distance = get_double_array_ptr(plinks.distance)

    cdef double x1 = 0.0
    cdef double x2 = 0.0
    cdef double y1 = 0.0
    cdef double y2 = 0.0
    cdef double dx = 0.0
    cdef double dy = 0.0

    cdef int nnodes_plus_one = network.nnodes + 1
    cdef int nlinks_plus_one = network.nlinks + 1

    cdef int ifrom = 0
    cdef int ito = 0

    cdef int i = 0
    cdef int num_threads = nthreads

    with nogil, parallel(num_threads=num_threads):
        for i in prange(1, nlinks_plus_one, schedule="static"):
            ifrom = links_ifrom[i]
            ito = links_ito[i]

            x1 = wards_x[ifrom]
            y1 = wards_y[ifrom]

            x2 = wards_x[ito]
            y2 = wards_y[ito]

            dx = x1 - x2
            dy = y1 - y2

            distance = sqrt(dx*dx + dy*dy)
            links_distance[i] = distance
            total_distance += distance

    print(f"Total links distance equals {total_distance}")

    total_distance = 0.0

    if network.plinks > 0:
        with nogil, parallel(num_threads=num_threads):
            for i in prange(1, nnodes_plus_one, schedule="static"):
                ifrom = plinks_ifrom[i]
                ito = plinks_ito[i]

                x1 = wards_x[ifrom]
                y1 = wards_y[ifrom]

                x2 = wards_x[ito]
                y2 = wards_y[ito]

                dx = x1 - x2
                dy = y1 - y2

                distance = sqrt(dx*dx + dy*dy)
                plinks_distance[i] = distance
                total_distance += distance

        print(f"Total play links distance equals {total_distance}")

    return network
