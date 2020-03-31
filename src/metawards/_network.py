
from dataclasses import dataclass

from ._parameters import Parameters
from ._nodes import Nodes
from ._links import Links

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
    nodes: Nodes = None        # The list of nodes (wards) in the network
    to_links: Links = None     # The links between nodes (work)
    play: Links = None         # The links between nodes (play)
    weekend: Links = None      # The links between nodes (weekend)

    nnodes: int = 0            # the number of nodes in the network
    nlinks: int = 0            # the number of links in the network
    plinks: int = 0            # the number of play links in the network

    params: Parameters = None  # The parameters used to generate this network

