
cimport cython
from libc.math cimport floor, ceil

from ._network import Network

from ._utils import recalculate_play_denominator_day, \
                    recalculate_work_denominator_day

__all__ = ["move_population_from_work_to_play",
           "move_population_from_play_to_work"]


def move_population_from_work_to_play(network: Network):
    """This function is not used or implemented, but is implied
       by the naming scheme...
    """
    raise AssertionError("Code has not been written")


@cython.boundscheck(False)
@cython.wraparound(False)
def move_population_from_play_to_work(network: Network):
    """And Vice Versa From Work to Play
       The relevant parameters are network.params.play_to_work and
                                   network.params.work_to_play

       When both are 0, don't do anything;
       When play_to_work > 0 move work_to_play proportion from play to work.
       When work_to_play > 0 move work_to_play proportion from work to play.
    """

    params = network.params

    if params is None:
        return

    links = network.to_links   # workers, regular movements
    wards = network.nodes
    play = network.play        # links of players

    cdef int i = 0
    cdef double [::1] links_suscept = links.suscept
    cdef double [::1] wards_play_suscept = wards.play_suscept
    cdef int [::1] links_ifrom = links.ifrom
    cdef double to_move = 0.0
    cdef double work_to_play = params.work_to_play
    cdef double play_to_work = params.play_to_work

    if params.work_to_play > 0.0:
        for i in range(1, network.nlinks+1):
            suscept = links_suscept[i]
            to_move = ceil(suscept * work_to_play)

            if to_move > suscept:
                print(f"to_move > links[{i}].suscept")

            links_suscept[i] -= to_move
            wards_play_suscept[links_ifrom[i]] += to_move

    cdef int ifrom = 0
    cdef int [::1] play_ifrom = play.ifrom
    cdef double [::1] play_weight = play.weight
    cdef double [::1] wards_save_play_suscept = wards.save_play_suscept
    cdef double countrem = 0.0
    cdef temp, p

    if params.play_to_work > 0.0:
        for i in range(1, network.plinks+1):
            ifrom = play_ifrom[i]

            temp = play_to_work * (play_weight[i] *
                                   wards_save_play_suscept[ifrom])

            to_move = floor(temp)
            p = temp - to_move

            countrem += p

            if countrem >= 1.0:
                to_move += 1.0
                countrem -= 1.0

            if wards_play_suscept[ifrom] < to_move:
                to_move = wards_play_suscept[ifrom]

            wards_play_suscept[ifrom] -= to_move
            links_suscept[i] += to_move

    recalculate_work_denominator_day(network)
    recalculate_play_denominator_day(network)
