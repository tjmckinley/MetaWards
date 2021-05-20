
import os
import pytest

from metawards import Parameters, Network, Population, OutputFiles

script_dir = os.path.dirname(__file__)

my_iterator = os.path.join(script_dir, "iterators",
                           "cython_iterator.pyx")


def test_cython_iterator():
    """Validate that we can compile and link cython iterators
       dynamically
    """
    prompt = None

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
    params.set_disease("ncov")
    params.set_input_files("single")

    # the size of the starting population
    population = Population(initial=1000)

    print("Building the network...")
    network = Network.build(params=params)

    from metawards.iterators import build_custom_iterator

    iterator = build_custom_iterator(my_iterator, __name__)

    print("Run the model...")
    outdir = os.path.join(script_dir, "test_cython_iterator")

    with OutputFiles(outdir, force_empty=True) as output_dir:
        trajectory = network.run(population=population,
                                 output_dir=output_dir,
                                 iterator=iterator,
                                 nthreads=1)

    OutputFiles.remove(outdir, prompt=None)

    print("End of the run")

    print(f"Model output: {trajectory}")


if __name__ == "__main__":
    test_cython_iterator()
