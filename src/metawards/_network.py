
from dataclasses import dataclass
from typing import List

from ._parameters import Parameters
from ._nodes import Nodes
from ._links import Links
from ._population import Population

__all__ = ["Network"]


@dataclass
class Network:
    """This class represents a network of wards. The network comprises
       nodes (representing wards), connected with links which represent
       work (predictable) links. There are also additional links for
       play (unpredictable/random) and weekend
    """

    """The list of nodes (wards) in the network"""
    nodes: Nodes = None
    """The links between nodes (work)"""
    to_links: Links = None
    """The links between nodes (play)"""
    play: Links = None
    """The links between nodes (weekend)"""
    weekend: Links = None

    """The number of nodes in the network"""
    nnodes: int = 0
    """The number of links in the network"""
    nlinks: int = 0
    """The number of play links in the network"""
    plinks: int = 0

    """The maximum allowable number of nodes in the network"""
    max_nodes: int = 10050
    """The maximum allowable number of links in the network"""
    max_links: int = 2414000

    """To seed provides additional seeding information"""
    to_seed: List[int] = None

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
            from ._utils import build_wards_network
            build_function = build_wards_network

        network = build_function(params=params,
                                 max_nodes=max_nodes,
                                 max_links=max_links)

        if calculate_distances:
            network.add_distances(distance_function=distance_function)

        if params.input_files.seed:
            from ._utils import read_done_file
            to_seed = read_done_file(params.input_files.seed)
            nseeds = len(to_seed)

            print(to_seed)
            print(f"Number of seeds equals {nseeds}")
            network.to_seed = to_seed

        # By default, we initialise the network ready for a run,
        # namely make sure everything is reset and the population
        # is at work
        print("Reset everything...")
        network.reset_everything()

        print("Rescale play matrix...")
        network.rescale_play_matrix()

        print("Move population from play to work...")
        network.move_from_play_to_work()

        return network

    def add_distances(self, distance_function=None):
        """Read in the positions of all of the nodes (wards) and calculate
           the distances of the links.

           Optionally you can specify the function to use to
           read the positions and calculate the distances.
           By default this is mw.utils.add_wards_network_distance
        """

        if distance_function is None:
            from ._utils import add_wards_network_distance
            distance_function = add_wards_network_distance

        distance_function(self)

        # now need to update the dynamic distance cutoff based on the
        # maximum distance between nodes
        print("Get min/max distances...")
        (_mindist, maxdist) = self.get_min_max_distances()

        self.params.dyn_dist_cutoff = maxdist + 1

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
        try:
            return self._min_max_distances
        except Exception:
            pass

        from ._utils import get_min_max_distances
        self._min_max_distances = get_min_max_distances(self)

        return self._min_max_distances

    def reset_everything(self):
        """Resets the network ready for a new run of the model"""
        from ._utils import reset_everything
        reset_everything(self)

    def rescale_play_matrix(self):
        """Rescale the play matrix"""
        from ._utils import rescale_play_matrix
        rescale_play_matrix(self)

    def move_from_play_to_work(self):
        """Move the population from play to work"""
        from ._utils import move_population_from_play_to_work
        move_population_from_play_to_work(self)

    def run(self, population: Population,
                  seed: int = None,
                  output_dir: str = "tmp",
                  nsteps: int = None,
                  s: int = None):
        """Run the model simulation for the passed population.
           The random number seed is given in 'seed'. If this
           is None, then a random seed is used.

           All output files are written to 'output_dir'

           The simulation will continue until the infection has
           died out or until 'nsteps' has passed (keep as 'None'
           to prevent exiting early).

           s is used to select the 'to_seed' entry to seed
           the nodes
        """
        from pygsl import rng as gsl_rng

        rng = gsl_rng.rng()

        if seed is None:
            import random
            seed = random.randint(10000, 99999999)

        print(f"Using random number seed: {seed}")
        rng.set(seed)

        # Create space to hold the results of the simulation
        print("Initialise infections...")
        infections = self.initialise_infections()

        print("Initialise play infections...")
        play_infections = self.initialise_play_infections()

        # test seeding of the random number generator by drawing and printing
        # 5 random numbers - this is temporary, and only used to
        # facilitate comparison to the original C code
        for i in range(1,6):
            r = rng.binomial(0.5, 100)
            print(f"random number {i} equals {r}")

        from ._utils import run_model
        population = run_model(network=self,
                               population=population.initial,
                               infections=infections,
                               play_infections=play_infections,
                               rng=rng, s=s, output_dir=output_dir,
                               nsteps=nsteps)

        # do we want to save infections and play_infections for inspection?

        return population
