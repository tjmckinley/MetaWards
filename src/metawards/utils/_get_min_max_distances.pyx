
cimport cython

from .._network import Network


@cython.boundscheck(False)
@cython.wraparound(False)
def get_min_max_distances(network: Network):
    """Return the minimum and maximum distances recorded in the network"""
    links = network.to_links

    cdef double mindist = -1.0
    cdef double maxdist = -1.0

    cdef int i = 0
    cdef double dist = 0.0
    cdef double [::1] links_distance = links.distance

    for i in range(1, network.nlinks+1):
        dist = links_distance[i]

        if dist:
            if mindist < 0.0:
                mindist = dist
                maxdist = dist
            elif dist > maxdist:
                maxdist = dist
            elif dist < mindist:
                mindist = dist

    print(f"maxdist {maxdist} mindist {mindist}")

    if mindist > 0:
        print(f"The original code always gives a minimum distance of zero, "
              f"so setting {mindist} to zero... (check if this is correct)")

    mindist = 0

    return (mindist, maxdist)
