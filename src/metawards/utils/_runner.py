

from .._network import Network
from .._population import Population
from ._profiler import Profiler

import os
import sys

__all__ = ["get_number_of_processes", "run_models"]


def get_number_of_processes(parallel_scheme: str, nprocs: int = None):
    """This function works out how many processes have been set
       by the paralellisation system called 'parallel_scheme'
    """
    if nprocs is None:
        if parallel_scheme == "multiprocessing":
            return 1
        else:
            raise ValueError(
                    f"You must specify the number of processes to "
                    f"use for parallel scheme '{parallel_scheme}'")

    if parallel_scheme == "mpi4py":
        return 4
    elif parallel_scheme == "scoop":
        return 4
    elif parallel_scheme == "multiprocessing":
        return 4
    else:
        raise ValueError(
            f"Unrecognised parallelisation scheme {parallel_scheme}")


def fingerprint(i, l):
    """Create a fingerprint for the output directory for the ith set
       of parameters that are contained in the passed dictionary 'l'.

       The format will be;

       AAAAAA_B_C_D_E_F

       where A is the set number 'i', and B, C, D, E and F are the
       values of the parameters in input order. To save space, this
       are rounded where possible and any "0." is removed, e.g.

       000001:9:93:18:92:9

       will be set 1, with parameters 0.90, 0.93, 0.18, 0.92, 0.90
    """
    s = "%06d" % (i+1)
    for val in l.values():
        v = str(val)
        if v.startswith("0"):
            v = v[1:]
        if v.startswith("."):
            v = v[1:]
        s += "_" + v
    return s


def run_models(network: Network, variables, population: Population,
               nprocs: int, nthreads: int, seed: int,
               nsteps: int, output_dir: str, profile: Profiler,
               parallel_scheme: str):

    # this variable is used to pick out some of the additional seeds?
    s = -1

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    if len(variables) == 1:
        # no need to do anything complex - just a single run
        params = network.params.set_variables(variables[0])

        network.update(params, profile=profile)

        population = network.run(population=population, seed=seed,
                                 s=s, nsteps=nsteps,
                                 output_dir=output_dir,
                                 profile=profile,
                                 nthreads=nthreads)
        return population

    # generate the random number seeds for all of the jobs
    # (for testing, we will use the same seed so that I can check
    #  that they are all working)
    seeds = []

    for i in range(0, len(variables)):
        seeds.append(seed)

    # create the output directories for all of the jobs, and also create
    # the output text files
    outdirs = []

    for i in range(0, len(variables)):
        f = fingerprint(i, variables[i])

        d = os.path.join(output_dir, f)

        # create the directory now to make sure none of the jobs will fail
        if not os.path.exists(d):
            os.mkdir(d)

        outdirs.append(d)

    # save the old stdout and stderr
    stdout = sys.stdout
    stderr = sys.stderr

    outputs = []

    print(f"Running {len(variables)} jobs using {nprocs} process(es)")

    if nprocs == 1:
        # no need to use a pool, as we will repeat this calculation
        # several times
        for i, variable in enumerate(variables):
            seed = seeds[i]
            outdir = outdirs[i]

            print(f"Running parameter set {i+1} of {len(variables)} "
                  f"using seed {seed}")
            print(f"All output written to {outdir}...")

            outfile = open(os.path.join(outdir, "output.txt"), "w")
            errfile = open(os.path.join(outdir, "output.err"), "w")

            sys.stdout = outfile
            sys.stderr = errfile

            try:
                print(f"Running variable set {i+1}")
                print(f"Variables: {variable}")
                print(f"Random seed: {seed}")
                print(f"nthreads: {nthreads}")

                # no need to do anything complex - just a single run
                params = network.params.set_variables(variables[0])

                network.update(params, profile=profile)

                output = network.run(population=population, seed=seed,
                                     s=s, nsteps=nsteps,
                                     output_dir=outdir,
                                     profile=profile,
                                     nthreads=nthreads)

                sys.stdout = stdout
                sys.stderr = stderr

                outfile.close()
                errfile.close()

                outputs.append(output)
            except Exception as e:
                # restore stdout and stderr
                sys.stdout = stdout
                sys.stderr = stderr
                outfile.close()
                errfile.close()
                raise e
        # end of loop over variable sets
    else:
        # build a pool...

        # get all members of the pool to load the parameters and network

        # now get them all to run through the work...

        print("Even more to do...")

    return outputs
