
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

    day_foi: float = 0.0        # numerator only
    night_foi: float = 0.0      # numerator only
    weekend_foi: float = 0.0    # numerator only

    play_suscept: float = 0.0
    save_play_suscept: float = 0.0

    denominator_n: float = 0.0  #Denominator only
    denominator_d: float = 0.0  # Maybe won't need

    denominator_p: float = 0.0
    denominator_pd: float = 0.0
    x: float = 0.0
    y: float = 0.0
    b: float = 0.0

    id: str = None
    vacid: int = None
