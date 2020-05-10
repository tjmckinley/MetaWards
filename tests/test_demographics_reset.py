
import os
import pytest

from metawards import Parameters, Network, Population, OutputFiles, \
    Demographics
from metawards.mixers import merge_using_matrix
from metawards.utils import Profiler

script_dir = os.path.dirname(__file__)
ncovparams_csv = os.path.join(script_dir, "data", "ncovparams.csv")
redblue_json = os.path.join(script_dir, "data", "redblue.json")


def mix_shield(network, **kwargs):
    matrix = [[0.2, 0.1],
              [0.8, 1.0]]

    network.demographics.interaction_matrix = matrix

    return [merge_using_matrix]


@pytest.mark.slow
def test_demographics_reset(prompt=None):
    """This test runs several runs one after another with the expectation
       that they should all give the same result. This tests that the
       network is being correctly reset after each run. This test
       uses a mixer and demographics to show that these can be reset
    """

    # user input parameters
    import random
    seed = random.randint(100000, 1000000)
    inputfile = ncovparams_csv
    line_num = 0
    UV = 0.0

    # load all of the parameters
    try:
        params = Parameters.load(parameters="march29")
    except Exception as e:
        print(f"Unable to load parameter files. Make sure that you have "
              f"cloned the MetaWardsData repository and have set the "
              f"environment variable METAWARDSDATA to point to the "
              f"local directory containing the repository, e.g. the "
              f"default is $HOME/GitHub/MetaWardsData")
        raise e

    # load the disease and starting-point input files
    params.set_disease(os.path.join(script_dir, "data", "ncov.json"))
    params.set_input_files("2011Data")
    params.add_seeds("ExtraSeedsBrighton.dat")

    # start from the parameters in the specified line number of the
    # provided input file
    variables = params.read_variables(inputfile, line_num)

    # extra parameters that are set
    params.UV = UV
    params.static_play_at_home = 0
    params.play_to_work = 0
    params.work_to_play = 0
    params.daily_imports = 0.0

    # the size of the starting population
    population = Population(initial=57104043)

    profiler = Profiler()

    nsteps = 20

    demographics = Demographics.load(redblue_json)

    print("Building the network...")
    network = Network.build(params=params, calculate_distances=True,
                            profiler=profiler)

    network = network.specialise(demographics, nthreads=2, profiler=profiler)

    params = params.set_variables(variables[0])
    network.update(params, profiler=profiler)

    print("Running model 1...")
    outdir = os.path.join(script_dir, "test_integration_output")

    network.update(params, profiler=profiler)

    with OutputFiles(outdir, force_empty=True, prompt=prompt) as output_dir:
        trajectory1 = network.run(population=population, seed=seed,
                                  output_dir=output_dir,
                                  nsteps=nsteps, profiler=profiler,
                                  mixer=mix_shield,
                                  nthreads=2)

    OutputFiles.remove(outdir, prompt=None)

    # this should reset the network
    print("Running model 2...")
    network.update(params, profiler=profiler)

    with OutputFiles(outdir, force_empty=True, prompt=prompt) as output_dir:
        trajectory2 = network.run(population=population, seed=seed,
                                  output_dir=output_dir,
                                  nsteps=nsteps, profiler=profiler,
                                  mixer=mix_shield,
                                  nthreads=2)

    OutputFiles.remove(outdir, prompt=None)

    # this should reset the network
    print("Running model 3...")
    network.update(params, profiler=profiler)

    with OutputFiles(outdir, force_empty=True, prompt=prompt) as output_dir:
        trajectory3 = network.run(population=population, seed=seed,
                                  output_dir=output_dir,
                                  nsteps=nsteps, profiler=profiler,
                                  mixer=mix_shield,
                                  nthreads=2)

    OutputFiles.remove(outdir, prompt=None)

    print("End of the run")

    print(profiler)

    print(f"Model 1 output: {trajectory1}")
    print(f"Model 2 output: {trajectory2}")
    print(f"Model 3 output: {trajectory3}")

    assert trajectory1 == trajectory2
    assert trajectory1 == trajectory3


if __name__ == "__main__":
    test_demographics_reset()
