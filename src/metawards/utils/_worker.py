
from typing import Union as _Union
from typing import Dict as _Dict

from .._network import Network
from .._networks import Networks
from .._demographics import Demographics
from .._parameters import Parameters
from .._outputfiles import OutputFiles

import os
import sys
from contextlib import contextmanager

__all__ = ["run_worker", "prepare_worker"]

global_network = None


@contextmanager
def silence_output():
    """Nice way to silence stdout and stderr - thanks to
       Emil Stenström in
       https://stackoverflow.com/questions/6735917/redirecting-stdout-to-nothing-in-python
    """
    new_out = open(os.devnull, "w")
    old_out = sys.stdout
    sys.stdout = new_out

    new_err = open(os.devnull, "w")
    old_err = sys.stderr
    sys.stderr = new_err

    try:
        yield new_out
    finally:
        sys.stdout = old_out
        sys.stderr = old_err


def prepare_worker(params: Parameters, demographics: Demographics,
                   options: _Dict[str, any]) -> _Union[Network, Networks]:
    """Prepare a worker to receive work to run a model using the passed
       parameters. This will build the network specified by the
       parameters and will store it in global memory ready to
       be used for a model run. Note that these are
       silent, printing nothing to stdout or stderr

       Parameters
       ----------
       params: Parameters
         Parameters used to build the network
       demographics: Demographics
         If not None, then demographics used to specialise the Network
         into Networks
    """
    # switch off printing to stdout and stderr
    with silence_output():
        global global_network

        max_nodes = options["max_nodes"]
        max_links = options["max_links"]
        nthreads = options["nthreads"]
        seed = options["seed"]

        if demographics is not None:
            from ._ran_binomial import seed_ran_binomial
            from ._parallel import create_thread_generators

            if seed == 0:
                # this is a special mode that a developer can use to force
                # all jobs to use the same random number seed (15324) that
                # is used for comparing outputs. This should NEVER be used
                # for production code
                rng = seed_ran_binomial(seed=15324)
            else:
                rng = seed_ran_binomial(seed=seed+7)

                rngs = create_thread_generators(rng, nthreads)
        else:
            rngs = None

        del options["max_nodes"]
        del options["max_links"]

        profiler = options["profiler"]

        if global_network is None:
            network = Network.build(params=params,
                                    calculate_distances=True,
                                    profiler=profiler,
                                    max_nodes=max_nodes,
                                    max_links=max_links)

            if demographics is not None:

                network = demographics.specialise(network, rngs=rngs,
                                                  nthreads=nthreads,
                                                  profiler=profiler)

            global_network = network

        else:
            global_network.update(params=params,
                                  demographics=demographics,
                                  rngs=rngs, nthreads=nthreads,
                                  profiler=profiler)

        return global_network


def run_worker(arguments):
    """Ask the worker to run a model using the passed variables and
       options. This will write to options['output_dir'] and will
       also return the population object that contains the final
       population data.

       WARNING - the iterator and extractor arguments rely on the
       workers starting in the same directory as the main process,
       so that they can load the same python files (if the user
       is using a custom iterator or extractor)
    """
    params = arguments["params"]
    demographics = arguments["demographics"]
    options = arguments["options"]

    # first, build and prepare the Network(s). This is built once
    # from the parameters and demographics by loading files from
    # the filesystem, as sending this over the physical network
    # would be too expensive. Subsequent calls to this function
    # after the Network(s) has been built will call
    # network.update(params, demographics)
    network = prepare_worker(params=params, demographics=demographics,
                             options=options)

    # next, run the job, writing to output
    from ._run_models import redirect_output

    outdir = options["output_dir"]
    auto_bzip = options["auto_bzip"]
    del options["auto_bzip"]

    # if the user wanted to remove this directory then they would
    # have done so in the main process - no need to check again
    with OutputFiles(outdir, check_empty=False, force_empty=False,
                     prompt=None, auto_bzip=auto_bzip) as output_dir:
        options["output_dir"] = output_dir

        with redirect_output(output_dir.get_path()):
            output = network.run(**options)

            return output
