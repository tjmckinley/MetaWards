
import os as _os

from .._network import Network
from .._outputfiles import OutputFiles
from ._workspace import Workspace
from .._population import Population, Populations
from ._profiler import Profiler, NullProfiler
from ._iterate import iterate
from ..iterators._iterate_default import iterate_default
from ._open_files import open_files
from ._clear_all_infections import clear_all_infections
from ._extract_data import extract_data

__all__ = ["run_model"]


def run_model(network: Network,
              infections, play_infections,
              rngs, s: int,
              output_dir: OutputFiles,
              population: Population = Population(initial=57104043),
              nsteps: int = None,
              profile: bool = True,
              nthreads: int = None,
              get_advance_functions=iterate_default):
    """Actually run the model... Real work happens here. The model
       will run until completion or until 'nsteps' have been
       completed (whichever happens first)

        Parameters
        ----------
        network: Network
            The network on which to run the model
        infections: list
            The space used to record the infections
        play_infections: list
            The space used to record the play infectionss
        rngs: list
            The list of random number generators to use, one per thread
        population: Population
            The initial population at the start of the model outbreak.
            This is also used to set the date and day of the start of
            the model outbreak
        seed: int
            The random number seed used for this model run. If this is
            None then a very random random number seed will be used
        output_dir: OutputFiles
            The directory to write all of the output into
        nsteps: int
            The maximum number of steps to run in the outbreak. If None
            then run until the outbreak has finished
        profile: bool
            Whether or not to profile the model run and print out the
            results
        s: int
            Index of the seeding parameter to use
        nthreads: int
            Number of threads over which to parallelise this model run
        get_advance_functions: function
            Function that will be used to dynamically get the functions
            that will be used to advance the model at each iteration.
            Any additional files or parameters needed by these functions
            should be included in the `network.params` object.

        Returns
        -------
        trajectory: Populations
            The trajectory of the population for every day of the model run
    """
    if profile:
        p = Profiler()
    else:
        p = NullProfiler()

    p = p.start("run_model")

    params = network.params

    if params is None:
        return population

    from copy import deepcopy
    population = deepcopy(population)

    # create a workspace in which to run the model
    p = p.start("allocate workspace")
    workspace = Workspace(network=network, params=params)
    p = p.stop()

    # create space to hold the population trajectory
    trajectory = Populations()

    EXPORT = output_dir.open("ForMattData.dat")

    p = p.start("open_files")
    files = open_files(output_dir)
    p = p.stop()

    p = p.start("clear_all_infections")
    clear_all_infections(infections=infections,
                         play_infections=play_infections)
    p = p.stop()

    # get and call all of the functions that need to be called to set
    # up the model run
    p = p.start("setup_funcs")
    setup_funcs = get_advance_functions(nthreads=nthreads, setup=True)

    for setup_func in setup_funcs:
        setup_func(network=network, population=population,
                   infections=infections, play_infections=play_infections,
                   rngs=rngs, profiler=p, nthreads=nthreads)
    p = p.stop()

    # Now get the population and network data for the first day of the
    # model ("day zero", unless a future day has been set by the user)
    p = p.start("extract_data")
    infecteds = extract_data(network=network, infections=infections,
                             play_infections=play_infections,
                             files=files,
                             workspace=workspace,
                             nthreads=nthreads,
                             population=population)
    p = p.stop()

    # save the initial population
    trajectory.append(population)

    p = p.start("run_model_loop")
    iteration_count = 0

    # keep looping until the outbreak is over or until we have completed
    # at least 5 loop iterations
    while (infecteds != 0) or (iteration_count < 5):
        if profile:
            p2 = Profiler()
        else:
            p2 = NullProfiler()

        p2 = p2.start(f"timing for day {population.day}")

        iterate(network=network,
                population=population,
                infections=infections,
                play_infections=play_infections,
                rngs=rngs,
                get_advance_functions=get_advance_functions,
                profiler=p2, nthreads=nthreads)

        print(f"\n {population.day} {infecteds}")

        p2 = p2.start("extract_data")
        infecteds = extract_data(network=network, infections=infections,
                                 play_infections=play_infections,
                                 files=files,
                                 workspace=workspace,
                                 population=population,
                                 nthreads=nthreads,
                                 profiler=p2)
        p2 = p2.stop()

        iteration_count += 1
        population.day += 1

        if population.date:
            from datetime import timedelta
            population.date += timedelta(days=1)

        if nsteps is not None:
            if iteration_count >= nsteps:
                trajectory.append(population)
                print(f"Exiting model run early at nsteps = {nsteps}")
                break

        p2 = p2.stop()

        if not p2.is_null():
            print(f"\n{p2}\n")

        # save the population trajectory
        trajectory.append(population)

    # end of while loop
    p = p.stop()

    p = p.start("closing_files")
    EXPORT.close()

    for FILE in files:
        FILE.close()

    p = p.stop()
    p.stop()

    if not p.is_null():
        print(f"\nOVERALL MODEL TIMING\n{p}")

    print(f"Infection died ... Ending on day {population.day}")

    return trajectory
