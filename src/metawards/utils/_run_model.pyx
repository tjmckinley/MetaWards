#!/bin/env/python3
#cython: boundscheck=False
#cython: cdivision=True
#cython: initializedcheck=False
#cython: cdivision_warnings=False
#cython: wraparound=False
#cython: binding=False
#cython: initializedcheck=False
#cython: nonecheck=False
#cython: overflowcheck=False

cimport cython
import os as _os

from .._network import Network
from .._parameters import Parameters
from ._workspace import Workspace
from .._population import Population, Populations
from ._profiler import Profiler, NullProfiler
from ._iterate import iterate
from ._iterate_weekend import iterate_weekend
from ._open_files import open_files
from ._vaccination import allocate_vaccination, how_many_vaccinated, \
                          vaccinate_same_id
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
              MAXSIZE: int=10050,
              VACCINATE: bool = False,
              IMPORTS: bool = False,
              EXTRASEEDS: bool = True,
              WEEKENDS: bool = False):
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
           MAXSIZE: int
             The maximum number of nodes that can be loaded - this is needed
             as memory is pre-allocated before reading
           VACCINATE: bool
             Whether to use the VACCINATE routines
           IMPORTS: bool
             Whether or not to use the IMPORT routines
           EXTRASEEDS: bool
             Whether or not to import EXTRASEEDS
           WEEKENDS: bool
             Whether or not to treat weekends differently to weekdays
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

    int_t = "i"    # signed int64
    float_t = "d"  # double (float64)

    size = MAXSIZE   # suspect this will be the number of nodes

    if not _os.path.exists(output_dir):
        _os.mkdir(output_dir)

    if not _os.path.isdir(output_dir):
        raise AssertionError(f"The specified output directory ({output_dir}) "
                             f"does not appear to be a valid directory")

    EXPORT = open(_os.path.join(output_dir, "ForMattData.dat"), "w")

    if VACCINATE:
        from ._vaccination import allocate_vaccination
        p = p.start("allocate_vaccinate")
        (vac, wards_ra,
         risk_ra, sort_ra, VACF,
         trigger) = allocate_vaccination(network, output_dir)
        p = p.stop()

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

    elif WEEKENDS:
        day = 1  # day number of the week, 1-5 = weekday, 6-7 = weekend

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

        if WEEKENDS:
            if day > 5:
                p2 = p2.start("iterate_weekend")
                iterate_weekend(network=network, infections=infections,
                                play_infections=play_infections,
                                params=params, rngs=rngs, timestep=timestep,
                                population=population.initial,
                                profiler=p2, nthreads=nthreads)
                p2 = p2.stop()
                print("weekend")
            else:
                p2 = p2.start("iterate")
                iterate(network=network, infections=infections,
                        play_infections=play_infections,
                        params=params, rngs=rngs, timestep=timestep,
                        population=population.initial,
                        profiler=p2, nthreads=nthreads)
                p2 = p2.stop()
                print("normal day")

            if day == 7:
                day = 0

            day += 1
        else:
            p2 = p2.start("iterate")
            iterate(network=network, infections=infections,
                    play_infections=play_infections,
                    params=params, rngs=rngs, timestep=timestep,
                    population=population.initial,
                    profiler=p2, nthreads=nthreads)
            p2 = p2.stop()

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

        # Disabling, as Leon says he doesn't need this anymore
        #p2 = p2.start("extract_data_for_graphics")
        #extract_data_for_graphics(network=network, infections=infections,
        #                          play_infections=play_infections,
        #                          workspace=workspace, FILE=EXPORT,
        #                          profiler=p2)
        #p2 = p2.stop()

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

        if VACCINATE:
            p2 = p2.start("vaccinate")
            #vaccinate_wards(network=network, wards_ra=wards_ra,
            #                infections=infections,
            #                play_infections=play_infections,
            #                vac=vac, params=params)

            if infecteds > params.global_detection_thresh:
                trigger = 1

            if trigger == 1:
                #vaccinate_county(network=network, risk_ra=risk_ra,
                #                 sort_ra=sort_ra,
                #                 infections=infections,
                #                 play_infections=play_infections,
                #                 vac=vac, params=params)

                vaccinate_same_id(network=network, risk_ra=risk_ra,
                                  sort_ra=sort_ra,
                                  infections=infections,
                                  play_infections=play_infections,
                                  vac=vac, params=params)

                if params.disease_params.contrib_foi[0] == 1.0:
                    N_INF_CLASSES = len(infections)
                    for j in range(0, N_INF_CLASSES-1):
                        params.disease_params.contrib_foi[j] = 0.2

            VACF.write("%d %d\n" % (timestep, how_many_vaccinated(vac)))

            p2 = p2.stop()

        # end of "IF VACCINATE"
        p2 = p2.stop()

        if not p2.is_null():
            print(f"\n{p2}\n")

        # save the population trajectory
        trajectory.append(population)

    # end of while loop

    p = p.stop()

    p = p.start("closing_files")
    EXPORT.close()

    if VACCINATE:
        VACF.close()

    for FILE in files:
        FILE.close()

    p = p.stop()
    p.stop()

    if not p.is_null():
        print(f"\nOVERALL MODEL TIMING\n{p}")

    print(f"Infection died ... Ending at time {timestep}")

    return trajectory
