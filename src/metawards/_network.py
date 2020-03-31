
from dataclasses import dataclass

from ._parameters import Parameters
from ._nodes import Nodes
from ._links import Links

__all__ = ["Network"]


@dataclass
class Network:
    """This class represents a network of wards. The network comprises
       nodes (representing wards), connected with links which represent
       work (predictable) links. There are also additional links for
       play (unpredictable/random) and weekend
    """
    nodes: Nodes = None        # The list of nodes (wards) in the network
    to_links: Links = None     # The links between nodes (work)
    play: Links = None         # The links between nodes (play)
    weekend: Links = None      # The links between nodes (weekend)

    nnodes: int = 0            # the number of nodes in the network
    nlinks: int = 0            # the number of links in the network
    plinks: int = 0            # the number of play links in the network

    params: Parameters = None  # The parameters used to generate this network

    @staticmethod
    def build(params: Parameters,
              calculate_distances: bool=True,
              build_function=None,
              distance_function=None,
              max_nodes:int = 10050,
              max_links:int = 2414000):
        """Builds and returns a new Network that is described by the
           passed parameters. If 'calculate_distances' is True, then
           this will also read in the ward positions and add
           the distances between the links.

           Optionally you can supply your own function to build the network,
           by supplying 'build_function'. By default, this is
           metawards.utils.build_wards_network.

           Optionally you can supply your own function to read and
           calculate the distances by supplying 'build_function'.
           By default this is metawards.add_wards_network_distance

           The network is built in allocated memory, so you need to specify
           the maximum possible number of nodes and links. The memory buffers
           will be shrunk back after building.
        """
        if build_function is None:
            from metawards.utils import build_wards_network
            build_function = build_wards_network

        network = build_function(params=params,
                                 max_nodes=max_nodes,
                                 max_links=max_links)

        # save the parameters used to build the network
        # within the network - this will save having to pass
        # them separately, which is error-prone
        network.params = params

        if calculate_distances:
            network.add_distances(distance_function=distance_function)

        return network

    def add_distances(self, distance_function=None):
        """Read in the positions of all of the nodes (wards) and calculate
           the distances of the links.

           Optionally you can specify the function to use to
           read the positions and calculate the distances.
           By default this is mw.utils.add_wards_network_distance
        """

        if distance_function is None:
            from metawards.utils import add_wards_network_distance
            distance_function = add_wards_network_distance

        distance_function(self)

    def initialise_infections(self):
        """Initialise and return the space that will be used
           to track infections
        """
        from ._utils import initialise_infections
        return initialise_infections(self)

    def initialise_play_infections(self):
        """Initialise and return the space that will be used
           to track play infections
        """
        from ._utils import initialise_play_infections
        return initialise_play_infections(self)

    def get_min_max_distances(self):
        """Calculate and return the minimum and maximum distances
           between nodes in the network
        """
        from ._utils import get_min_max_distances
        return get_min_max_distances(self)
