

from typing import Tuple as _Tuple

from .._network import Network, PersonType
from .._wardid import WardID

from ._get_array_ptr cimport get_int_array_ptr

def network_get_index(network: Network, id: WardID) -> _Tuple[PersonType, int]:
    """Return the index of the Node or Link that corresponds
        to the passed WardID. If this is a player, then it will
        be the index into Node, while if this is for a worker,
        then it will be the index of the Link that corresponds
        to the ward-ward commuter link. This returns a tuple
        of the PersonType (WORKER or PLAYER) plus the index
        into the appropriate array.

        This raises a KeyError if there is no ward or ward-link
        that matches the WardID
    """
    if id.is_null():
        raise ValueError(f"Cannot get the index of a null WardID")

    cdef int home = network.get_node_index(id.home())

    if id.is_ward():
        return (PersonType.PLAYER, home)

    cdef int commute = network.get_node_index(id.commute())

    # need to see if there is a work link between these
    # two wards...
    wards = network.nodes
    links = network.links

    cdef int * wards_begin_to = get_int_array_ptr(wards.begin_to)
    cdef int * wards_end_to = get_int_array_ptr(wards.end_to)

    cdef int * links_ifrom = get_int_array_ptr(links.ifrom)
    cdef int * links_ito = get_int_array_ptr(links.ito)

    cdef int i = 0
    cdef int index = -1
    cdef int ifrom = 0
    cdef int ito = 0

    with nogil:
        if wards_begin_to[home] != -1 and wards_end_to[home] != -1:
            for i in range(wards_begin_to[home], wards_end_to[home]):
                ifrom = links_ifrom[i]
                ito = links_ito[i]

                if ifrom == home and ito == commute:
                    index = i
                    break

    if index == -1:
        raise KeyError(
            f"There is no work connection between ward {home} and "
            f"ward {commute}")

    return (PersonType.WORKER, index)
