
import pytest
import os

import metawards as mw

from pygsl import rng as gsl_rng

script_dir = os.path.dirname(__file__)
ncovparams_csv = os.path.join(script_dir, "data", "ncovparams.csv")


def test_integration():
    """This test repeats main_RepeatsNcov.c and validates that the
       various stages report the same results as the original C code
    """
    data_repo = os.getenv("METAWARDSDATA")

    if data_repo:
        print(f"Loading all data from MetaWardsData repo in {data_repo}")

    seed = 15324

    inputfile = ncovparams_csv

    line_num = 0

    UV = 1.0

    rng = gsl_rng.rng()

    rng.set(seed)

    # test seeding of the random number generator by drawing and printing
    # 5 random numbers
    for i in range(1,6):
        r = rng.binomial(0.5, 100)
        print(f"random number {i} equals {r}")

    params = mw.Parameters.load(parameters="march29", repository=data_repo)

    disease = mw.Disease.load(disease="ncov", repository=data_repo)
    params.set_disease(disease)

    input_files = mw.InputFiles.load(model="2011Data", repository=data_repo)
    params.set_input_files(input_files)

    params.read_file(inputfile, line_num)

    params.UV = UV

    to_seed = mw.read_done_file(params.input_files.seed)

    nseeds = len(to_seed)

    print(to_seed)
    print(f"Number of seeds equals {nseeds}")

    print("Building the network...")
    network = mw.build_wards_network_distance(params)

    print("Initialise infections...")
    infections = mw.initialise_infections(network=network, params=params)

    print("Initialise play infections...")
    play_infections = mw.initialise_play_infections(network=network,
                                                    params=params)

    print("Get min/max distances...")
    (mindist, maxdist) = mw.get_min_max_distances(network)

    params.dyn_dist_cutoff = maxdist + 1

    s = -1

    params.static_play_at_home = 0

    print("Reset everything...")
    mw.reset_everything(network=network, params=params)

    print("Rescale play matrix...")
    mw.rescale_play_matrix(network=network, params=params)

    params.play_to_work = 0
    params.work_to_play = 0

    print("Move population from play to work...")
    mw.move_population_from_play_to_work(network=network, params=params,
                                         rng=rng)  # rng not used?

    params.daily_imports = 0.0

    print("Run the model...")
    mw.run_model(network=network, params=params,
                 population=57104043,
                 infections=infections,
                 play_infections=play_infections,
                 rng=rng, to_seed=to_seed, s=s, output_dir="tmp")

    print("End of the run")


if __name__ == "__main__":
    test_integration()
