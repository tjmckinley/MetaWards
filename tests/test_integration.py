
import pytest
import os

from metawards import Parameters, Network, run_model, Population

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

    try:
        params = Parameters.load(parameters="march29", repository=data_repo)
    except Exception as e:
        print(f"Unable to load parameter files. Make sure that you have "
              f"cloned the MetaWardsData repository and have set the "
              f"environment variable METAWARDSDATA to point to the "
              f"local directory containing the repository, e.g. the "
              f"default is $HOME/GitHub/MetaWardsData")
        raise e

    params.set_disease("ncov")
    params.set_input_files("2011Data")

    params.read_file(inputfile, line_num)

    params.UV = UV
    params.static_play_at_home = 0
    params.play_to_work = 0
    params.work_to_play = 0
    params.daily_imports = 0.0

    print("Building the network...")
    network = Network.build(params=params, calculate_distances=True)

    print("Reset everything...")
    network.reset_everything()

    print("Rescale play matrix...")
    network.rescale_play_matrix()

    print("Move population from play to work...")
    network.move_from_play_to_work()

    s = -1

    print("Initialise infections...")
    infections = network.initialise_infections()

    print("Initialise play infections...")
    play_infections = network.initialise_play_infections()

    print("Run the model...")
    population = run_model(network=network,
                           population=57104043,
                           infections=infections,
                           play_infections=play_infections,
                           rng=rng, s=s, output_dir="tmp",
                           nsteps=20)

    print("End of the run")

    print(f"Model output:  {population}")

    # The original C code has this expected population after 20 steps
    expected = Population(initial=57104043,
                          susceptibles=56081923,
                          latent=61,
                          total=17,
                          recovereds=76,
                          n_inf_wards=24)

    print(f"Expect output: {expected}")

    assert population == expected


if __name__ == "__main__":
    test_integration()
