

from .._network import Network
from .._population import Population
from ._profiler import Profiler

from contextlib import contextmanager

import os
import sys

__all__ = ["get_number_of_processes", "run_models", "redirect_output"]


def get_number_of_processes(parallel_scheme: str, nprocs: int = None):
    """This function works out how many processes have been set
       by the paralellisation system called 'parallel_scheme'
    """
    if nprocs is None:
        if parallel_scheme == "multiprocessing":
            return 1
        elif parallel_scheme == "mpi4py":
            from mpi4py import MPI
            comm = MPI.COMM_WORLD
            nprocs = comm.Get_size()
            return nprocs
        elif parallel_scheme == "scoop":
            raise ValueError(
                    f"You must specify the number of processes for "
                    f"scoop to parallelise over")
        else:
            raise ValueError(
                    f"You must specify the number of processes to "
                    f"use for parallel scheme '{parallel_scheme}'")

    if parallel_scheme == "mpi4py":
        from mpi4py import MPI
        comm = MPI.COMM_WORLD
        n = comm.Get_size()

        if n < nprocs:
            return n
        else:
            return nprocs
    elif parallel_scheme == "scoop":
        return 4
    elif parallel_scheme == "multiprocessing":
        return nprocs
    else:
        raise ValueError(
            f"Unrecognised parallelisation scheme {parallel_scheme}")


@contextmanager
def redirect_output(outdir):
    """Nice way to redirect stdout and stderr - thanks to
       Emil Stenström in
       https://stackoverflow.com/questions/6735917/redirecting-stdout-to-nothing-in-python
    """
    new_out = open(os.path.join(outdir, "output.txt"), "w")
    old_out = sys.stdout
    sys.stdout = new_out

    new_err = open(os.path.join(outdir, "output.err"), "w")
    old_err = sys.stderr
    sys.stderr = new_err

    try:
        yield new_out
    finally:
        sys.stdout = old_out
        sys.stderr = old_err
        new_out.close()
        new_err.close()


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

        trajectory = network.run(population=population, seed=seed,
                                 s=s, nsteps=nsteps,
                                 output_dir=output_dir,
                                 profile=profile,
                                 nthreads=nthreads)

        return [(variables[0], trajectory)]

    # generate the random number seeds for all of the jobs
    # (for testing, we will use the same seed so that I can check
    #  that they are all working)
    seeds = []

    if seed == 0:
        # this is a special mode that a developer can use to force
        # all jobs to use the same random number seed (15324) that
        # is used for comparing outputs. This should NEVER be used
        # for production code
        print("** WARNING: Using special mode to fix all random number")
        print("** WARNING: seeds to 15324. DO NOT USE IN PRODUCTION!!!")

        for i in range(0, len(variables)):
            seeds.append(15324)

    else:
        from ._ran_binomial import seed_ran_binomial, ran_int
        rng = seed_ran_binomial(seed)

        # seed the rngs used for the sub-processes using this rng
        for i in range(0, len(variables)):
            seeds.append(ran_int(rng, 10000, 99999999))

    # set the output directories for all of the jobs - this is based
    # on the fingerprint, so should be unique for each job
    outdirs = []

    for v in variables:
        f = v.fingerprint(include_index=True)
        d = os.path.join(output_dir, f)
        outdirs.append(d)

    outputs = []

    print(f"\nRunning {len(variables)} jobs using {nprocs} process(es)")

    if nprocs == 1:
        # no need to use a pool, as we will repeat this calculation
        # several times
        for i, variable in enumerate(variables):
            seed = seeds[i]
            outdir = outdirs[i]

            if not os.path.exists(outdir):
                os.mkdir(outdir)

            print(f"\nRunning parameter set {i+1} of {len(variables)} "
                  f"using seed {seed}")
            print(f"All output written to {outdir}...")

            with redirect_output(outdir):
                print(f"Running variable set {i+1}")
                print(f"Variables: {variable}")
                print(f"Random seed: {seed}")
                print(f"nthreads: {nthreads}")

                # no need to do anything complex - just a single run
                params = network.params.set_variables(variable)

                network.update(params, profile=profile)

                output = network.run(population=population, seed=seed,
                                     s=s, nsteps=nsteps,
                                     output_dir=outdir,
                                     profile=profile,
                                     nthreads=nthreads)

                outputs.append((variable, output))

            print(f"Completed job {i+1} of {len(variables)}")
            print(variable)
            print(output[-1])
        # end of loop over variable sets
    else:
        from ._worker import run_worker

        # create all of the parameters and options to run
        arguments = []

        for i, variable in enumerate(variables):
            seed = seeds[i]
            outdir = outdirs[i]

            arguments.append({
                "params": network.params.set_variables(variable),
                "options": {"seed": seed,
                            "output_dir": outdir,
                            "population": population,
                            "s": s,
                            "nsteps": nsteps,
                            "profile": profile,
                            "nthreads": nthreads}
            })

        if parallel_scheme == "multiprocessing":
            # run jobs using a multiprocessing pool
            print("\nRunning jobs in parallel using a multiprocessing pool...")
            from multiprocessing import Pool
            with Pool(processes=nprocs) as pool:
                results = pool.map(run_worker, arguments)

                for i, result in enumerate(results):
                    print(f"\nCompleted job {i+1} of {len(variables)}")
                    print(variables[i])
                    print(result[-1])
                    outputs.append((variables[i], result))

        elif parallel_scheme == "mpi4py":
            # run jobs using a mpi4py pool
            print("\nRunning jobs in parallel using a mpi4py pool...")
            from mpi4py import futures
            with futures.MPIPoolExecutor(max_workers=nprocs) as pool:
                results = pool.map(run_worker, arguments)

                for i, result in enumerate(results):
                    print(f"\nCompleted job {i+1} of {len(variables)}")
                    print(variables[i])
                    print(result[-1])
                    outputs.append((variables[i], result))

        elif parallel_scheme == "scoop":
            # run jobs using a scoop pool
            print("\nRunning jobs in parallel using a scoop pool...")
            from scoop import futures

            results = futures.map(run_worker, arguments)

            for i, result in enumerate(results):
                print(f"\nCompleted job {i+1} of {len(variables)}")
                print(variables[i])
                print(result[-1])
                outputs.append((variables[i], result))

        else:
            raise ValueError(f"Unrecognised parallelisation scheme "
                             f"{parallel_scheme}.")

    return outputs
