
cimport cython

from libc.math cimport floor

from .._network import Network

__all__ = ["recalculate_work_denominator_day",
           "recalculate_play_denominator_day"]


@cython.boundscheck(False)
@cython.wraparound(False)
def recalculate_work_denominator_day(network: Network):
    """Recalculate the denominator_d for the wards (nodes) in
       the network for the normal links
    """
    params = network.params

    if params is None:
        return

    wards = network.nodes
    links = network.to_links

    cdef double sum = 0
    cdef int i = 0

    cdef double [::1] wards_denominator_d = wards.denominator_d
    cdef double [::1] wards_denominator_n = wards.denominator_n

    for i in range(1, network.nnodes+1):
        wards_denominator_d[i] = 0.0
        wards_denominator_n[i] = 0.0

    cdef int j = 0
    cdef int [::1] links_ifrom = links.ifrom
    cdef int [::1] links_ito = links.ito
    cdef double [::1] links_suscept = links.suscept
    cdef int ifrom = 0
    cdef int ito = 0

    for j in range(1, network.nlinks+1):
        ifrom = links_ifrom[j]
        ito = links_ito[j]
        suscept = links_suscept[j]
        wards_denominator_d[ito] += suscept
        wards_denominator_n[ifrom] += suscept
        sum += suscept

    print(f"recalculate_work_denominator_day sum = {sum}")


def recalculate_play_denominator_day(network: Network):
    """Recalculate the denominator_d for the wards (nodes) in
       the network for the play links
    """
    params = network.params

    if params is None:
        return

    wards = network.nodes
    links = network.play

    cdef int i = 0
    cdef double [::1] wards_denominator_pd = wards.denominator_pd
    cdef double [::1] wards_denominator_p = wards.denominator_p

    for i in range(1, network.nnodes+1):  # 1-indexed
        wards.denominator_pd[i] = 0
        wards.denominator_p[i] = 0

    cdef double sum = 0.0
    cdef int j = 0
    cdef int [::1] links_ifrom = links.ifrom
    cdef int [::1] links_ito = links.ito
    cdef int ifrom = 0
    cdef int ito = 0
    cdef double weight = 0.0
    cdef double [::1] links_weight = links.weight
    cdef double denom = 0.0
    cdef double [::1] wards_play_suscept = wards.play_suscept

    for j in range(1, network.plinks+1):  # 1-indexed
        ifrom = links_ifrom[j]
        ito = links_ito[j]
        weight = links_weight[j]
        denom = weight * wards_play_suscept[ifrom]
        wards_denominator_pd[ito] += denom

        sum += denom

    print(f"recalculate_play_denominator_day sum 1 = {sum}")

    sum = 0.0
    cdef double play_suscept = 0

    for i in range(1, network.nnodes+1):  # 1-indexed
        pd = wards_denominator_pd[i]
        play_suscept = wards_play_suscept[i]

        wards_denominator_pd[i] = floor(pd + 0.5)
        wards_denominator_p[i] = play_suscept

        if play_suscept < 0.0:
            print(f"Negative play_suscept? {wards[i]}")

        sum += play_suscept

    print(f"recalculate_play_denominator_day sum 2 = {sum}")
