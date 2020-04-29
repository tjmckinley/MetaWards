
from dataclasses import dataclass as _dataclass

from ._variableset import VariableSet

__all__ = ["Demographic"]


@_dataclass
class Demographic:
    """This class represents a single demographic"""

    #: The name of this demographic. This will be used as a label,
    #: and should be unique within the Demographics
    name: str = None

    #: The proportion of "work" (fixed movement) members in this
    #: demographic out of the entire population. This can either
    #: be a single number, or a list with a value for every ward.
    #: Whichever way is used, the sum of "work_ratio" for each demographic
    #: must equal 1.0 in each ward (every member of the work population
    #: must be represented)
    work_ratio: float = 0.0

    #: The proportion of "play" (random movement) members in this
    #: demographic out of the entire population. This can also either
    #: be a single number, or a list with a value for every ward.
    #: Whichever way is used, the sum of "play_ratio" for each demographic
    #: must equal 1.0 in each ward (every member of the play population
    #: must be represented)
    play_ratio: float = 0.0

    #: How the parameters for this demographic should be changed compared
    #: to the parameters used for the whole population. This is currently
    #: changed to fixed values, but future developments in VariableSet
    #: will support rules for varying relative to the whole population.
    #: If this is None then this demographic will have the same
    #: parameters as the whole population
    adjustment: VariableSet = None
