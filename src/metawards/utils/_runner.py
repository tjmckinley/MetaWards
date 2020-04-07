

from .._network import Network
from .._population import Population
from ._profiler import Profiler

__all__ = ["get_number_of_processes", "run_models"]


def get_number_of_processes(parallel_scheme):
    """This function works out how many processes have been set
       by the paralellisation system called 'parallel_scheme'
    """
    if parallel_scheme == "mpi4py":
        return 4
    elif parallel_scheme == "scoop":
        return 4
    elif parallel_scheme == "multiprocessing":
        return 4
    else:
        raise ValueError(
            f"Unrecognised parallelisation scheme {parallel_scheme}")


def run_models(network: Network, variables, population: Population,
               nprocs: int, nthreads: int, seed: int,
               nsteps: int, output_dir: str, profile: Profiler,
               parallel_scheme: str):

    # this variable is used to pick out some of the additional seeds?
    s = -1

    if len(variables) == 1:
        # no need to do anything complex - just a single run
        params = network.params.set_variables(variables[0])

        network.update(params, profile=profile)

        population = network.run(population=population, seed=seed,
                                 s=s, nsteps=nsteps,
                                 output_dir=output_dir,
                                 profile=profile,
                                 nthreads=nthreads)
        return population

    elif nprocs == 1:
        # no need to use a pool, as we will repeat this calculation
        # several times
        print("Lots to do...")

        return []
    else:
        # build a pool...

        # get all members of the pool to load the parameters and network

        # now get them all to run through the work...

        print("Even more to do...")

        return []
