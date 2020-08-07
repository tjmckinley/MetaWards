
from typing import Union as _Union
from typing import List as _List

cimport cython
from cython.parallel import parallel, prange
from libc.stdint cimport uintptr_t

from libc.math cimport ceil

from .._network import Network, PersonType
from .._networks import Networks
from .._infections import Infections

from ..utils._ran_binomial cimport _ran_binomial, \
                                   _get_binomial_ptr, binomial_rng

from ..utils._console import Console

from ..utils._array import create_int_array
from ..utils._get_array_ptr cimport get_int_array_ptr, get_double_array_ptr

from ._movegenerator import MoveGenerator
from ._moverecord import MoveRecord

__all__ = ["go_stage", "go_stage_serial", "go_stage_parallel"]


def go_ward_parallel(generator: MoveGenerator,
                     network: _Union[Network, Networks],
                     infections: Infections,
                     nthreads: int,
                     rngs,
                     record: MoveRecord = None,
                     **kwargs) -> None:
    """This go function will move individuals according to the flexible
       move specification described by the passed 'generator'.

       If you want a record of all moves, then pass in 'record',
       which will be updated.

       Parameters
       ----------
       generator: MoveGenerator
         Fully describes all of the moves that should be performed
       network: Network or Networks
         The network(s) in which the individuals will be moved
       infections: Infections
         Current record of infections
       nthreads: int
         Number of threads over which to parallelise the move
       rngs:
         Thread-safe random number generators used to choose the fraction
         of individuals
       record: MoveRecord
         An optional record to which to record the moves that are performed
    """
    # get the demographic/stage moves, plus the ward-level moves
    stages = generator.generate(network)
    wards = generator.generate_wards(network)

    if isinstance(network, Network):
        subnets = [network]
        subinfs = [infections]
    else:
        subnets = network.subnets
        subinfs = infections.subinfs

    cdef int from_stage = 0
    cdef int to_stage = 1

    cdef int number = 0
    cdef double fraction = 0.0

    cdef int nnodes_plus_one = 0
    cdef int nlinks_plus_one = 0

    cdef int * to_work_infections
    cdef int * from_work_infections

    cdef int * to_play_infections
    cdef int * from_play_infections

    cdef double * from_links_weight
    cdef double * to_links_weight

    cdef double * from_links_suscept
    cdef double * to_links_suscept

    cdef double * from_play_suscept
    cdef double * to_play_suscept

    cdef double * from_save_play_suscept
    cdef double * to_save_play_suscept

    cdef int num_threads = nthreads

    updated = create_int_array(nthreads, 0)
    cdef int * have_updated = get_int_array_ptr(updated)

    cdef int i = 0
    cdef int nmove = 0

    cdef int record_moves = 1

    if record is None:
        record_moves = 0

    affected_subnets = {}

    worker = PersonType.WORKER
    player = PersonType.PLAYER

    for stage in stages:
        fraction = generator.fraction()
        number = generator.number()

        if fraction == 0.0 or number == 0:
            continue

        affected_subnets[stage[0]] = 1
        affected_subnets[stage[2]] = 1

        from_net = subnets[stage[0]]
        from_infs = subinfs[stage[0]]
        from_stage = stage[1]
        to_net = subnets[stage[2]]
        to_infs = subinfs[stage[2]]
        to_stage = stage[3]

        from_links_weight = get_double_array_ptr(from_net.links.weight)
        to_links_weight = get_double_array_ptr(to_net.links.weight)

        from_save_play_suscept = get_double_array_ptr(
                                        from_net.nodes.save_play_suscept)
        to_save_play_suscept = get_double_array_ptr(
                                        to_net.nodes.save_play_suscept)

        if from_stage >= 0:
            from_work_infections = get_int_array_ptr(
                                            from_infs.work[from_stage])
            from_play_infections = get_int_array_ptr(
                                            from_infs.play[from_stage])
        else:
            from_links_suscept = get_double_array_ptr(
                                            from_net.links.suscept)
            from_play_suscept = get_double_array_ptr(
                                            from_net.nodes.play_suscept)

        if to_stage >= 0:
            to_work_infections = get_int_array_ptr(
                                            to_infs.work[to_stage])
            to_play_infections = get_int_array_ptr(
                                            to_infs.play[to_stage])
        else:
            to_links_suscept = get_double_array_ptr(
                                            to_net.links.suscept)
            to_play_suscept = get_double_array_ptr(
                                            to_net.nodes.play_suscept)

        if generator.should_move_all():
            if stage[0] == stage[2] and stage[1] == stage[3]:
                # nothing to move
                continue

            with no_gil(), parallel(num_threads=num_threads):
                thread_id = cython.parallel.threadid()
                rng = _get_binomial_ptr(rngs_view[thread_id])

                # loop over workers
                for i in prange(1, nlinks_plus_one, schedule="static"):
                    if from_stage >= 0:
                        nmove = min(number, from_work_infections[i])
                    else:
                        nmove = min(number, <int>from_links_suscept[i])

                    if fraction != 1.0:
                        nmove = _ran_binomial(rng, fraction, nmove)

                    if nmove > 0:
                        have_updated[thread_id] = 1

                        if record_moves:
                            with gil:
                                record.add(from_demographic=stage[0],
                                           to_demographic=stage[2],
                                           from_stage=from_stage,
                                           to_stage=to_stage,
                                           from_type=worker,
                                           to_type=worker,
                                           from_ward=i,
                                           to_ward=i,
                                           number=nmove
                                           )

                        if to_stage >= 0:
                            to_work_infections[i] = \
                                            to_work_infections[i] + nmove
                        else:
                            to_links_suscept[i] = \
                                                to_links_suscept[i] + nmove

                        if from_stage >= 0:
                            from_work_infections[i] = \
                                            from_work_infections[i] - nmove
                        else:
                            from_links_suscept[i] = \
                                            from_links_suscept[i] - nmove

                        to_links_weight[j] = to_links_weight[i] + nmove
                        links_weight[j] = links_weight[i] - nmove
                # end of loop over workers

                # loop over players
                for i in prange(1, nnodes_plus_one, schedule="static"):
                    if from_stage >= 0:
                        nmove = min(number, from_play_infections[i])
                    else:
                        nmove = min(number, <int>from_links_suscept[i])

                    if fraction != 1.0:
                        nmove = _ran_binomial(rng, fraction, nmove)

                    if nmove > 0:
                        have_updated[thread_id] = 1

                        if record_moves:
                            with gil:
                                record.add(from_demographic=stage[0],
                                           to_demographic=stage[2],
                                           from_stage=from_stage,
                                           to_stage=to_stage,
                                           from_type=player,
                                           to_type=player,
                                           from_ward=i,
                                           to_ward=i,
                                           number=nmove
                                           )

                        if to_stage >= 0:
                            to_play_infections[i] = \
                                        to_play_infections[i] + nmove
                        else:
                            to_play_suscept[i] = \
                                        to_play_suscept[i] + nmove

                        if from_stage >= 0:
                            from_play_infections[i] = \
                                    from_play_infections[i] - nmove
                        else:
                            from_play_suscept[i] = \
                                    from_play_suscept[i] - nmove

                        to_save_play_suscept[i] = \
                                    to_save_play_suscept[i] + nmove
                        from_save_play_suscept[j] = \
                                    from_save_play_suscept[j] - nmove
                # end of loop over players
            # end of parallel section
        # end of if should move all
        else:
            pass

        #end of else (if should move all)
    # end of loop over stages

    if sum(updated) > 0:
        # we need to recalculate the denominators for the subnets that
        # are involved in this move
        for i in affected_subnets.keys():
            subnets[i].recalculate_denominators(profiler=profiler)


def go_ward_serial(**kwargs) -> None:
    go_ward_parallel(nthreads=1, **kwargs)


def go_ward(nthreads: int = 1, **kwargs) -> None:
    """This go function will move individuals according to the flexible
       move specification described by the passed 'generator'.

       If you want a record of all moves, then pass in 'record',
       which will be updated.

       Parameters
       ----------
       generator: MoveGenerator
         Fully describes all of the moves that should be performed
       network: Network or Networks
         The network(s) in which the individuals will be moved
       infections: Infections
         Current record of infections
       nthreads: int
         Number of threads over which to parallelise the move
       rngs:
         Thread-safe random number generators used to choose the fraction
         of individuals
       record: MoveRecord
         An optional record to which to record the moves that are performed
    """
    if nthreads > 1:
        go_ward_parallel(nthreads=nthreads, **kwargs)
    else:
        go_ward_serial(**kwargs)
