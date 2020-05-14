
import os
import pytest

from metawards import Parameters, Network, Population, \
    OutputFiles, VariableSets, Demographics
from metawards.mixers import mix_evenly
from metawards.movers import go_to
from metawards.utils import run_models

script_dir = os.path.dirname(__file__)
redblue_json = os.path.join(script_dir, "data", "redblue.json")


def move_red_to_blue(**kwargs):
    func = lambda **kwargs: go_to(go_from="red",
                                  go_to="blue")

    return [func]


@pytest.mark.slow
def test_go_to(prompt=None, nthreads=1):
    import random
    seed = random.randint(100000, 1000000)

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

    # the size of the starting population
    population = Population(initial=57104043)

    nsteps = 20

    demographics = Demographics.load(redblue_json)

    print("Building the network...")
    network = Network.build(params=params)

    network = network.specialise(demographics, nthreads=nthreads)

    outdir = os.path.join(script_dir, "test_go_to")

    with OutputFiles(outdir, force_empty=True, prompt=prompt) as output_dir:
        trajectory = network.copy().run(population=population, seed=seed,
                                        output_dir=output_dir,
                                        nsteps=nsteps,
                                        mixer=mix_evenly,
                                        mover=move_red_to_blue,
                                        nthreads=nthreads)

    OutputFiles.remove(outdir, prompt=None)

    print(trajectory)


if __name__ == "__main__":
    test_go_to()
