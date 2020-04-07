
cimport cython
from ._network import Network

__all__ = ["fill_in_gaps"]


@cython.boundscheck(False)
@cython.wraparound(False)
def fill_in_gaps(network: Network):
    """Fills in gaps in the network"""
    nodes = network.nodes
    links = network.to_links

    cdef int added = 0
    cdef int i = 0
    cdef int link_to = 0
    cdef int [::1] links_ito = links.ito
    cdef int [::1] nodes_label = nodes.label

    cdef int nnodes = network.nnodes

    for i in range(1, network.nlinks+1):  # careful of 1-indexing
        link_to = links_ito[i]
        if nodes_label[link_to] != link_to:
            print(f"ADDING LINK {i} {link_to} {network.nnodes}")
            nodes_label[link_to] = link_to
            nnodes += 1

            added += 1
            assert added < 20   # something if too many missing links

    network.nnodes = nnodes
