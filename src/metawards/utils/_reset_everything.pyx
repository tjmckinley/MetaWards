
cimport cython

from .._network import Network
from .._node import Node

__all__ = ["reset_work_matrix", "reset_play_matrix",
           "reset_play_susceptibles", "reset_everything"]


@cython.boundscheck(False)
@cython.wraparound(False)
def reset_work_matrix(network: Network):
    links = network.to_links

    cdef int i = 0
    cdef int [::1] links_ifrom = links.ifrom
    cdef double [::1] links_suscept = links.suscept
    cdef double [::1] links_weight = links.weight

    for i in range(1, network.nlinks+1):  # 1-indexed
        if links_ifrom[i] == -1:
            print(f"Missing a link at index {i}")
        else:
            links_suscept[i] = links_weight[i]

@cython.boundscheck(False)
@cython.wraparound(False)
def reset_play_matrix(network: Network):
    links = network.play

    cdef int i = 0
    cdef int [::1] links_ifrom = links.ifrom
    cdef double [::1] links_suscept = links.suscept
    cdef double [::1] links_weight = links.weight

    for i in range(1, network.plinks+1):  # 1-indexed
        if links.ifrom[i] == -1:
            print(f"Missing a play link at index {i}?")
        else:
            links.weight[i] = links.suscept[i]


@cython.boundscheck(False)
@cython.wraparound(False)
def reset_play_susceptibles(network: Network):
    nodes = network.nodes

    cdef int i = 0
    cdef int [::1] nodes_label = nodes.label
    cdef double [::1] nodes_play_suscept = nodes.play_suscept
    cdef double [::1] nodes_save_play_suscept = nodes.save_play_suscept

    for i in range(1, network.nnodes+1):  # 1-indexed
        if nodes_label[i] == -1:
            print(f"Missing a node at index {i}?")
            # the data will already be initialised to 0
        else:
            nodes_play_suscept[i] = nodes_save_play_suscept[i]


def reset_everything(network: Network):
    reset_work_matrix(network)
    reset_play_matrix(network)
    reset_play_susceptibles(network)

    # if weekend
    #    reset_weekend_matrix(network)

    params = network.params

    if params:
        N_INF_CLASSES = params.disease_params.N_INF_CLASSES()

        params.disease_params.contrib_foi = N_INF_CLASSES * [0]

        for i in range(0, N_INF_CLASSES-1):   # why -1?
            params.disease_params.contrib_foi[i] = 1

        network.params = params
