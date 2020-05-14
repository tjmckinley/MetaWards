
from typing import Union as _Union
from typing import List as _List

from cython.parallel import parallel, prange

from .._networks import Networks
from .._infections import Infections
from .._demographics import DemographicID, DemographicIDs

from ..utils._profiler import Profiler
from ..utils._get_array_ptr cimport get_int_array_ptr, get_double_array_ptr

__all__ = ["go_isolate", "go_isolate_serial", "go_isolate_parallel"]


def go_isolate_parallel(go_from: _Union[DemographicID, DemographicIDs],
                        go_to: DemographicID,
                        network: Networks,
                        infections: Infections,
                        profiler: Profiler,
                        nthreads: int,
                        self_isolate_stage: int = 2,
                        duration: int = 7,
                        release_to: DemographicID = None,
                        **kwargs) -> None:
    """This go function will move individuals from the "from"
       demographic(s) to the "to" demographic if they show any
       signs of infection (the disease stage is greater or equal
       to 'self_isolate_stage' - by default this is level '2',
       which is one level above "latent"). Individuals are held
       in the new demographic for "duration" days, before being
       returned either to their original demographic, or
       released to the "release_to" demographic

       Parameters
       ----------
       from: DemographicID or DemographicIDs
         ID (name or index) or IDs of the demographics to scan for
         infected individuals
       to: DemographicID
         ID (name or index) of the demographic to send infected
         individuals to
       network: Networks
         The networks to be modelled. This must contain all of the
         demographics that are needed for this go function
       self_isolate_stage: int
         The stage of infection an individual must be at before they
         are moved into this demographic
       duration: int
         The number of days an individual should isolate for
       release_to: DemographicID
         ID (name or index) that the individual should move to after
         existing isolation. If this is not set, then the individual
         will return to their original demographic
    """

    # make sure that all of the needed demographics exist, and
    # convert them into a canonical form (indexes, list[indexes])
    if not isinstance(go_from, list):
        go_from = [go_from]

    subnets = network.subnets
    demographics = network.demographics
    subinfs = infections.subinfs

    go_from = [demographics.get_index(x) for x in go_from]

    go_to = demographics.get_index(go_to)

    to_subnet = subnets[go_to]
    to_subinf = subinfs[go_to]

    if release_to is not None:
        release_to = demographics.get_index(release_to)
        release_subnet = subnets[release_to]
        release_subinf = subinfs[release_to]
    else:
        release_subnet = None
        release_subinf = None

    cdef int N_INF_CLASSES = infections.N_INF_CLASSES

    if self_isolate_stage < 0 or self_isolate_stage >= N_INF_CLASSES:
        raise ValueError(
            f"The start stage of self-isolation {self_isolate_stage} "
            f"is invalid for a disease with {N_INF_CLASSES} stages")

    cdef int start_stage = self_isolate_stage

    cdef int nnodes_plus_one = 0
    cdef int nlinks_plus_one = 0

    cdef int * work_infections_i
    cdef int * play_infections_i

    cdef int * to_work_infections_i
    cdef int * to_play_infections_i

    cdef int * release_work_infections_i
    cdef int * release_play_infections_i

    cdef int nsubnets = len(subnets)

    cdef int num_threads = nthreads

    cdef int ii = 0
    cdef int i = 0
    cdef int j = 0

    p = profiler.start("search_and_move")

    for ii in go_from:
        subnet = subnets[ii]
        subinf = subinfs[ii]
        nnodes_plus_one = subinf.nnodes + 1
        nlinks_plus_one = subinf.nlinks + 1

        for i in range(start_stage, N_INF_CLASSES):
            work_infections_i = get_int_array_ptr(subinf.work[i])
            play_infections_i = get_int_array_ptr(subinf.play[i])

            to_work_infections_i = get_int_array_ptr(to_subinf.work[i])
            to_play_infections_i = get_int_array_ptr(to_subinf.play[i])

            with nogil, parallel(num_threads=num_threads):
                for j in prange(1, nlinks_plus_one, schedule="static"):
                    if work_infections_i[j] > 0:
                        to_work_infections_i[j] = to_work_infections_i[j] + \
                                                  work_infections_i[j]
                        work_infections_i[j] = 0

                for j in prange(1, nnodes_plus_one, schedule="static"):
                    if play_infections_i[j] > 0:
                        to_play_infections_i[j] = to_play_infections_i[j] + \
                                                  play_infections_i[j]
                        play_infections_i[j] = 0

    p = p.stop()

    # release loop...


def go_isolate_serial(go_from: _Union[DemographicID, DemographicIDs],
                      go_to: DemographicID,
                      network: Networks,
                      infections: Infections,
                      profiler: Profiler,
                      self_isolate_stage: int = 2,
                      duration: int = 7,
                      release_to: DemographicID = None,
                      **kwargs) -> None:
    """This go function will move individuals from the "from"
       demographic(s) to the "to" demographic if they show any
       signs of infection (the disease stage is greater or equal
       to 'self_isolate_stage' - by default this is level '2',
       which is one level above "latent"). Individuals are held
       in the new demographic for "duration" days, before being
       returned either to their original demographic, or
       released to the "release_to" demographic

       Parameters
       ----------
       from: DemographicID or DemographicIDs
         ID (name or index) or IDs of the demographics to scan for
         infected individuals
       to: DemographicID
         ID (name or index) of the demographic to send infected
         individuals to
       network: Networks
         The networks to be modelled. This must contain all of the
         demographics that are needed for this go function
       self_isolate_stage: int
         The stage of infection an individual must be at before they
         are moved into this demographic
       duration: int
         The number of days an individual should isolate for
       release_to: DemographicID
         ID (name or index) that the individual should move to after
         existing isolation. If this is not set, then the individual
         will return to their original demographic
    """

    # make sure that all of the needed demographics exist, and
    # convert them into a canonical form (indexes, list[indexes])
    if not isinstance(go_from, list):
        go_from = [go_from]

    subnets = network.subnets
    demographics = network.demographics
    subinfs = infections.subinfs

    go_from = [demographics.get_index(x) for x in go_from]

    go_to = demographics.get_index(go_to)

    if go_to in go_from:
        raise ValueError(
            f"You cannot move to {go_to} as it is also in {go_from}")

    to_subnet = subnets[go_to]
    to_subinf = subinfs[go_to]

    if release_to is not None:
        release_to = demographics.get_index(release_to)
        release_subnet = subnets[release_to]
        release_subinf = subinfs[release_to]
    else:
        release_subnet = None
        release_subinf = None

    cdef int N_INF_CLASSES = infections.N_INF_CLASSES

    if self_isolate_stage < 0 or self_isolate_stage >= N_INF_CLASSES:
        raise ValueError(
            f"The start stage of self-isolation {self_isolate_stage} "
            f"is invalid for a disease with {N_INF_CLASSES} stages")

    cdef int start_stage = self_isolate_stage

    cdef int nnodes_plus_one = 0
    cdef int nlinks_plus_one = 0

    cdef int * work_infections_i
    cdef int * play_infections_i

    cdef int * to_work_infections_i
    cdef int * to_play_infections_i

    cdef int * release_work_infections_i
    cdef int * release_play_infections_i

    cdef int nsubnets = len(subnets)

    cdef int ii = 0
    cdef int i = 0
    cdef int j = 0

    p = profiler.start("search_and_move")

    for ii in go_from:
        subnet = subnets[ii]
        subinf = subinfs[ii]
        nnodes_plus_one = subinf.nnodes + 1
        nlinks_plus_one = subinf.nlinks + 1

        for i in range(start_stage, N_INF_CLASSES):
            work_infections_i = get_int_array_ptr(subinf.work[i])
            play_infections_i = get_int_array_ptr(subinf.play[i])

            to_work_infections_i = get_int_array_ptr(to_subinf.work[i])
            to_play_infections_i = get_int_array_ptr(to_subinf.play[i])

            for j in range(1, nlinks_plus_one):
                if work_infections_i[j] > 0:
                    to_work_infections_i[j] = to_work_infections_i[j] + \
                                                work_infections_i[j]
                    work_infections_i[j] = 0

            for j in range(1, nnodes_plus_one):
                if play_infections_i[j] > 0:
                    to_play_infections_i[j] = to_play_infections_i[j] + \
                                                play_infections_i[j]
                    play_infections_i[j] = 0

    p = p.stop()

    # release loop...

def go_isolate(nthreads: int = 1, **kwargs) -> None:
    """This go function will move individuals from the "from"
       demographic(s) to the "to" demographic if they show any
       signs of infection (the disease stage is greater or equal
       to 'self_isolate_stage' - by default this is level '2',
       which is one level above "latent"). Individuals are held
       in the new demographic for "duration" days, before being
       returned either to their original demographic, or
       released to the "release_to" demographic

       Parameters
       ----------
       from: DemographicID or DemographicIDs
         ID (name or index) or IDs of the demographics to scan for
         infected individuals
       to: DemographicID
         ID (name or index) of the demographic to send infected
         individuals to
       network: Networks
         The networks to be modelled. This must contain all of the
         demographics that are needed for this go function
       self_isolate_stage: int
         The stage of infection an individual must be at before they
         are moved into this demographic
       duration: int
         The number of days an individual should isolate for
       release_to: DemographicID
         ID (name or index) that the individual should move to after
         existing isolation. If this is not set, then the individual
         will return to their original demographic
    """

    if nthreads > 1:
        go_isolate_parallel(nthreads=nthreads, **kwargs)
    else:
        go_isolate_serial(**kwargs)
