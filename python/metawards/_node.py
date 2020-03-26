
from dataclasses import dataclass

__all__ = ["Node"]


@dataclass
class Node:
    """This is a node in the network"""
    label: int = None           # The node's label
    begin_to: int = None        # where to links begin in link list
    end_to: int = None			# how many to links in link list
    self_w: int = None

    begin_p: int = None         # play matrix begin and end in link vector
    end_p: int = None
    self_p: int = None

    begin_we: int = None        # weekend begin and end
    end_we: int = None
    self_we: int = None

    DayFOI: float = None        # numerator only
    NightFOI: float = None      # numerator only
    WeekendFOI: float = None    # numerator only

    play_suscept: float = None
    save_play_suscept: float = None

    Denominator_N: float = None  #Denominator only
    Denominator_D: float = None  # Maybe won't need

    Denominator_P: float = None
    Denominator_PD: float = None
    x: float = None
    y: float = None
    b: float = None

    id: str = None
    vacid: int = None
