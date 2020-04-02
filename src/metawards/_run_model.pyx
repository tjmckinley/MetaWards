
cimport cython
import os

from ._network import Network
from ._parameters import Parameters
from ._workspace import Workspace
from ._population import Population
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
from ._extract_data_for_graphics import extract_data_for_graphics


__all__ = ["run_model"]


@cython.boundscheck(False)
@cython.wraparound(False)
def run_model(network: Network,
              infections, play_infections,
              rng, s: int,
              output_dir: str=".",
              population: int=57104043,
              nsteps: int=None,
              profile: bool=True,
              MAXSIZE: int=10050,
              VACCINATE: bool = False,
              IMPORTS: bool = False,
              EXTRASEEDS: bool = True,
              WEEKENDS: bool = False):
    """Actually run the model... Real work happens here. The model
       will run until completion or until 'nsteps' have been
       completed (whichever happens first)
    """

    if profile:
        p = Profiler()
    else:
        p = NullProfiler()

    p = p.start("run_model")

    params = network.params

    if params is None:
        return Population(initial=population)

    to_seed = network.to_seed

    # create a workspace in which to run the model
    p = p.start("allocate workspace")
    workspace = Workspace(network=network, params=params)
    p = p.stop()

    # create a population object to monitor the outbreak
    population = Population(initial=population)

    int_t = "i"    # signed int64
    float_t = "d"  # double (float64)

    size = MAXSIZE   # suspect this will be the number of nodes

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    if not os.path.isdir(output_dir):
        raise AssertionError(f"The specified output directory ({output_dir}) "
                             f"does not appear to be a valid directory")

    EXPORT = open(os.path.join(output_dir, "ForMattData.dat"), "w")

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

    cdef int timestep = 0  # start timestep of the model
                           # (day since infection starts)

    p = p.start("extract_data")
    cdef int infecteds = extract_data(network=network, infections=infections,
                                      play_infections=play_infections,
                                      timestep=timestep, files=files,
                                      workspace=workspace,
                                      population=population)
    p = p.stop()

    cdef int day = 0

    if WEEKENDS:
        day = 1  # day number of the week, 1-5 = weekday, 6-7 = weekend

    if EXTRASEEDS:
        p = p.start("load_additional_seeds")
        additional_seeds = load_additional_seeds(
                                params.input_files.additional_seeding)
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
                                params=params, rng=rng, timestep=timestep,
                                population=population.initial,
                                profiler=p2)
                p2 = p2.stop()
                print("weekend")
            else:
                p2 = p2.start("iterate")
                iterate(network=network, infections=infections,
                        play_infections=play_infections,
                        params=params, rng=rng, timestep=timestep,
                        population=population.initial,
                        profiler=p2)
                p2 = p2.stop()
                print("normal day")

            if day == 7:
                day = 0

            day += 1
        else:
            p2 = p2.start("iterate")
            iterate(network=network, infections=infections,
                    play_infections=play_infections,
                    params=params, rng=rng, timestep=timestep,
                    population=population.initial,
                    profiler=p2)
            p2 = p2.stop()

        print(f"\n {timestep} {infecteds}")

        p2 = p2.start("extract_data")
        infecteds = extract_data(network=network, infections=infections,
                                 play_infections=play_infections,
                                 timestep=timestep, files=files,
                                 workspace=workspace,
                                 population=population,
                                 profiler=p2)
        p2 = p2.stop()

        p2 = p2.start("extract_data_for_graphics")
        extract_data_for_graphics(network=network, infections=infections,
                                  play_infections=play_infections,
                                  workspace=workspace, FILE=EXPORT,
                                  profiler=p2)
        p2 = p2.stop()

        timestep += 1

        if nsteps is not None:
            if timestep > nsteps:
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

    # end of while loop

    p = p.stop()

    p = p.start("closing_files")
    EXPORT.close()

    if VACCINATE:
        VACF.close()

    for FILE in files:
        FILE.close()

    p = p.stop()

    if not p.is_null():
        print(f"\nOVERALL MODEL TIMING\n{p}")

    print(f"Infection died ... Ending at time {timestep}")

    return population
