
from typing import Union as _Union
from typing import List as _List

from .._networks import Networks
from .._infections import Infections

from ..utils._profiler import Profiler
from ..utils._get_array_ptr cimport get_int_array_ptr, get_double_array_ptr

__all__ = ["go_isolate"]


DemographicID = _Union[str, int]
DemographicIDs = _List[DemographicID]


def go_isolate(go_from: _Union[DemographicID, DemographicIDs],
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

    cdef int * work_infections
    cdef int * play_infections

    cdef int * to_work_infections
    cdef int * to_play_infections

    cdef int * release_work_infections
    cdef int * release_play_infections

    cdef int nsubnets = len(subnets)

    cdef int i = 0
    cdef int j = 0
    cdef int k = 0

    p = profiler.start("search_and_move")

    for i in range(0, nsubnets):
        subnet = subnets[i]
        subinf = subinfs[i]
        nnodes_plus_one = subinf.nnodes + 1
        nlinks_plus_one = subinf.nlinks + 1

        for j in range(start_stage, N_INF_CLASSES):
            work_infections = get_int_array_ptr(subinf.work[j])
            play_infections = get_int_array_ptr(subinf.play[j])

            to_work_infections = get_int_array_ptr(to_subinf.play[j])
            to_play_infections = get_int_array_ptr(to_subinf.work[j])

            for k in range(1, nnodes_plus_one):
                if play_infections[k] > 0:
                    to_play_infections[k] = to_play_infections[k] + \
                                            play_infections[k]
                    play_infections[k] = 0

            for k in range(1, nlinks_plus_one):
                if work_infections[k] > 0:
                    to_work_infections[k] = to_work_infections[k] + \
                                            work_infections[k]
                    work_infections[k] = 0

    p = p.stop()

    # release loop...
