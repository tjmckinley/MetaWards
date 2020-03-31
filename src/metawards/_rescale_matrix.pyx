
from ._network import Network

__all__ = ["rescale_play_matrix"]


def rescale_play_matrix(network: Network):
    """ Static Play At Home rescaling.
	    for 1, everyone stays at home.
	    for 0 a lot of people move around.
    """

    params = network.params

    if params is None:
        return

    links = network.play

    cdef double static_play_at_home = params.static_play_at_home
    cdef double sclfac = 0.0
    cdef int j = 0
    cdef int ifrom = 0
    cdef int ito = 0
    cdef int [:] links_ito = links.ito
    cdef int [:] links_ifrom = links.ifrom
    cdef double [:] links_weight = links.weight
    cdef double [:] links_suscept = links.suscept

    if static_play_at_home > 0:
        # if we are making people stay at home, then do this loop through nodes
        # Rescale appropriately!
        sclfac = 1.0 - static_play_at_home

        for j in range(1, network.plinks+1):  # 1-indexed
            ifrom = links_ifrom[j]
            ito = links_ito[j]

            if ifrom != ito:
                # if it's not the home ward, then reduce the
                # number of play movers
                links_weight[j] = links_suscept[j] * sclfac
            else:
                # if it is the home ward
                suscept = links_suscept[j]
                links_weight[j] = ((1.0 - suscept) * static_play_at_home) + \
                                   suscept

    from ._utils import recalculate_play_denominator_day
    recalculate_play_denominator_day(network)
