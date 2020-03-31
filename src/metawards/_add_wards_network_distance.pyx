
from libc.math cimport sqrt

from ._parameters import Parameters
from ._network import Network

__all__ = ["add_wards_network_distance"]


def add_wards_network_distance(network: Network):
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

    cdef double [:] wards_x = wards.x
    cdef double [:] wards_y = wards.y

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
    cdef int n_invalid = 0

    cdef int [:] links_ifrom = links.ifrom
    cdef int [:] links_ito = links.ito

    cdef int [:] plinks_ifrom = plinks.ifrom
    cdef int [:] plinks_ito = plinks.ito

    cdef double [:] links_distance = links.distance
    cdef double [:] plinks_distance = plinks.distance

    cdef double dx = 0.0
    cdef double dy = 0.0

    cdef int plinks_size = len(plinks.distance)

    cdef int ifrom = 0
    cdef int ito = 0
    cdef int ifrom2 = 0
    cdef int ito2 = 0

    cdef int i = 0
    cdef int ninvalid = 0

    for i in range(1, network.nlinks+1):  # shouldn't this be range(1, nlinks+1)?
                                          # the fact there is a missing link at 0
                                          # suggests this should be...
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

        # below line doesn't make sense and doesn't work all the time.
        # Why would the ith play link be related to the ith work link?
        if i >= 0 and i < plinks_size:
            ifrom2 = plinks_ifrom[i]
            ito2 = plinks_ito[i]

            x1 = wards_x[ifrom2]
            y1 = wards_y[ifrom2]
            x2 = wards_x[ito2]
            y2 = wards_y[ito2]

            dx = x1 - x2
            dy = y1 - y2

            distance2 = sqrt(dx*dx + dy*dy)

            if distance != distance2:
                if ninvalid < 10:
                    print(plinks_size)
                    print(f"WARNING: DIFFERENT DISTANCES {i} {distance} vs "
                          f"{distance2}, {ifrom} vs {ifrom2} "
                          f"and {ito} vs {ito2}")
                elif ninvalid == 10:
                    print("NOT PRINTING ANY MORE!")

                ninvalid += 1
                n_invalid += 1

            plinks_distance[i] = distance2
        else:
            n_invalid += 1

    if n_invalid > 0:
        print(f"WARNING: Set {n_invalid} invalid plink distances!")

    print(f"Total distance equals {total_distance}")

    return network
