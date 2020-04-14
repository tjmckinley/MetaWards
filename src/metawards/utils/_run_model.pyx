
import os as _os

from .._network import Network
from .._parameters import Parameters
from ._workspace import Workspace
from .._population import Population, Populations
from ._profiler import Profiler, NullProfiler
from ._iterate import iterate
from ._iterate_weekend import iterate_weekend
from ._open_files import open_files
from ._clear_all_infections import clear_all_infections
from ._seeding import seed_all_wards, seed_infection_at_node,  \
                      load_additional_seeds, infect_additional_seeds
from ._extract_data import extract_data


__all__ = ["run_model"]


def run_model(network: Network,
              infections, play_infections,
              rngs, s: int,
              output_dir: str = ".",
              population: Population = Population(initial=57104043),
              nsteps: int=None,
              profile: bool=True,
              nthreads: int=None,
              IMPORTS: bool = False,
              EXTRASEEDS: bool = True):
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
        output_dir: str
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
        IMPORTS: bool
             Whether or not to use the IMPORT routines
        EXTRASEEDS: bool
             Whether or not to import EXTRASEEDS

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

    to_seed = network.to_seed

    # create a workspace in which to run the model
    p = p.start("allocate workspace")
    workspace = Workspace(network=network, params=params)
    p = p.stop()

    # create space to hold the population trajectory
    trajectory = Populations()

    if not _os.path.exists(output_dir):
        _os.mkdir(output_dir)

    if not _os.path.isdir(output_dir):
        raise AssertionError(f"The specified output directory ({output_dir}) "
                             f"does not appear to be a valid directory")

    EXPORT = open(_os.path.join(output_dir, "ForMattData.dat"), "w")

    p = p.start("open_files")
    files = open_files(output_dir)
    p = p.stop()

    p = p.start("clear_all_infections")
    clear_all_infections(infections=infections,
                         play_infections=play_infections)
    p = p.stop()

    if s < 0:
        print(f"Negative value of s? {s}")
        to_seed = 0
    else:
        to_seed = to_seed[s]

    print(f"node_seed {to_seed}")

    if not IMPORTS:
        p = p.start("seeding_imports")
        if s < 0:
            seed_all_wards(network=network,
                           play_infections=play_infections,
                           expected=params.daily_imports,
                           population=population.initial)
        else:
            seed_infection_at_node(network=network, params=params,
                                   seed=to_seed,
                                   infections=infections,
                                   play_infections=play_infections)
        p = p.stop()

    p = p.start("extract_data")
    cdef int infecteds = extract_data(network=network, infections=infections,
                                      play_infections=play_infections,
                                      files=files,
                                      workspace=workspace,
                                      nthreads=nthreads,
                                      population=population)
    p = p.stop()

    # save the initial population
    trajectory.append(population)

    cdef int day = 0
    cdef int timestep = population.day

    if population.date:
        day = population.date.weekday() + 1  # 1 = Monday

    if EXTRASEEDS:
        p = p.start("load_additional_seeds")
        additional_seeds = []

        if params.additional_seeds is not None:
            for additional in params.additional_seeds:
                additional_seeds += load_additional_seeds(additional)
        p = p.stop()

    p = p.start("run_model_loop")
    while (infecteds != 0) or (timestep < 5):
        if profile:
            p2 = Profiler()
        else:
            p2 = NullProfiler()

        p2 = p2.start(f"timing for iteration {timestep}")

        if EXTRASEEDS:
            p2 = p2.start("additional_seeds")
            infect_additional_seeds(network=network, params=params,
                                    infections=infections,
                                    play_infections=play_infections,
                                    additional_seeds=additional_seeds,
                                    timestep=timestep)
            p2 = p2.stop()

        iterate(network=network,
                population=population,
                infections=infections,
                play_infections=play_infections,
                rngs=rngs, profiler=p2, nthreads=nthreads)

        print(f"\n {timestep} {infecteds}")

        p2 = p2.start("extract_data")
        infecteds = extract_data(network=network, infections=infections,
                                 play_infections=play_infections,
                                 files=files,
                                 workspace=workspace,
                                 population=population,
                                 nthreads=nthreads,
                                 profiler=p2)
        p2 = p2.stop()

        timestep += 1
        population.day += 1

        if population.date:
            from datetime import timedelta
            population.date += timedelta(days=1)

        if nsteps is not None:
            if timestep >= nsteps:
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

    print(f"Infection died ... Ending at time {timestep}")

    return trajectory
