
from dataclasses import dataclass

__all__ = ["Link"]


@dataclass
class Link:
    """This is a link between nodes in the network"""
    ifrom: int = None        # integers (indexes) of origins and destinations
    ito: int = None

    weight: float = None     # weight of link, used to save the original
                             # number of susceptibles in work matrix

    suscept: float = None    # number of susceptibles in the case of the
                             # work matrix. Used to save the weight of
                             # the play matrix

    distance: float = None   # the distance between two wards
    A: int = None            # Age index...
