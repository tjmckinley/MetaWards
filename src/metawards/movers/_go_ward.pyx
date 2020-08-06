
from typing import Union as _Union
from typing import List as _List

cimport cython
from cython.parallel import parallel, prange
from libc.stdint cimport uintptr_t

from libc.math cimport ceil

from .._network import Network
from .._networks import Networks
from .._infections import Infections

from ..utils._ran_binomial cimport _ran_binomial, \
                                   _get_binomial_ptr, binomial_rng

from ..utils._console import Console

from ..utils._array import create_int_array
from ..utils._get_array_ptr cimport get_int_array_ptr, get_double_array_ptr

from ._movegenerator import MoveGenerator

__all__ = ["go_stage", "go_stage_serial", "go_stage_parallel"]


def go_ward_parallel(generator: MoveGenerator,
                     network: _Union[Network, Networks],
                     infections: Infections,
                     nthreads: int,
                     rngs,
                     profiler,
                     fraction: float = 1.0,
                     number: int = None,
                     #record: MoveRecord = None,
                     **kwargs) -> None:
    """This go function will move individuals from 'from_ward' to
       'to_ward'. Both 'from_ward' and 'to_ward' are WardIDs, which
       specify either a single player ward, or a single worker
       commuter link between wards. 'from_ward' can be a single or
       a list of WardIDs.

       It is ok to move an individual from being a player in a single
       ward to being a worker on a single commuter link (or vice versa).

       By default, this will move individuals at all disease stages
       and in all demographics. You can limit the movements to only
       specific disease stages or demographics by passing in
       'from_demographic' and 'from_stage'. You can also add movements
       to a different demographic or stage by passing in
       'to_demographic' and 'to_stage'

       By default this will move all matching individuals. You can
       move a subset of individuals if 'fraction' is
       less than 1, e.g. 0.5 would move 50% of individuals (chosen using
       a random binomial distribution). Or, you can move a specified
       number of individuals by setting 'number' to the number you
       wish to move. If you set both number and fraction, then
       a randomly drawn fraction of number will be moved. Note
       that this will only move as many individuals as available,
       and will not error if there are no enough to move.

       If you want a record of all moves, then pass in 'record',
       which will be updated.

       Parameters
       ----------
       from: WardID or list[WardID]
         The ward(s) or ward connection(s) to move from
       to: WardID
         The ward or ward connection to move to
       from_stage: int or list[int]
         The stage to move from (or list of stages if there are multiple
         from demographics)
       to_stage: int
         The stage to move to
       from_demographic: DemographicID or DemographicIDs
         ID (name or index) or IDs of the demographics to scan for
         infected individuals
       to_demographic: DemographicID
         ID (name or index) of the isolation demographic to send infected
         individuals to
       network: Networks
         The networks to be modelled. This must contain all of the
         demographics that are needed for this go function
       fraction: float or List[float]
         The fraction (percentage) of individuals who are moved.
       rngs:
         Thread-safe random number generators used to choose the fraction
         of individuals
       record: MoveRecord
         An optional record to which to record the moves that are performed
    """
    raise NotImplementedError("Write the code Chris!")

def go_ward_serial(**kwargs) -> None:
    go_ward_parallel(nthreads=1, **kwargs)


def go_ward(nthreads: int = 1, **kwargs) -> None:
    """This go function will move individuals from the "from_stage"
       stage(s) of the "from" demographic(s), from the specified
       ward(s) (or ward-connection(s)) to the specified ward
       (or ward-connection) of the "to_stage" stage of the "to" demographic.
       This will move either workers or players, and can move workers to become
       players, or players to become workers. If a ward is specified,
       then this is a player, while a ward-connection specifies
       a worker. This can move a subset of individuals if 'fraction' is
       less than 1, e.g. 0.5 would move 50% of individuals (chosen using
       a random binomial distribution)

       Parameters
       ----------
       from: DemographicID or DemographicIDs
         ID (name or index) or IDs of the demographics to scan for
         infected individuals
       to: DemographicID
         ID (name or index) of the isolation demographic to send infected
         individuals to
       from_stage: int or list[int]
         The stage to move from (or list of stages if there are multiple
         from demographics)
       to_stage: int
         The stage to move to
       from_ward: WardID or list[WardID]
         The ward(s) or ward connection(s) to move from
       to_ward: WardID
         The ward or ward connection to move to
       network: Networks
         The networks to be modelled. This must contain all of the
         demographics that are needed for this go function
       fraction: float or List[float]
         The fraction (percentage) of individuals who are moved.
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
