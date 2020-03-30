
from dataclasses import dataclass
from typing import List

from ._node import Node
from ._tolink import ToLink

__all__ = ["Network"]


@dataclass
class Network:
    """This class represents a network. The long-term plan is to
       replace this class with a good Python network library so
       that the code can be faster and more robust. As part of
       porting and learning the code I am mapping directly
       from the custom network/node/link written in C to this
       Python code
    """
    nodes: List[Node] = None
    to_links: List[ToLink] = None

    nnodes: int = 0
    nlinks: int = 0
    plinks: int = 0

    play: List[ToLink] = None
    weekend: List[ToLink] = None
