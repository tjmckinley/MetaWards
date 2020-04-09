#!/bin/env python3
"""
The metawards command line program.

Usage:
    To get the help for this program and the list of all of the
    arguments (with defaults) use;

    metawards --help
"""

__all__ = ["get_parallel_scheme", "parse_args", "get_hostfile",
           "get_cores_per_node", "get_threads_per_task",
           "scoop_supervisor", "mpi_supervisor",
           "cli"]


def get_parallel_scheme():
    """This function tries to work out which of the different parallel
       methods we should use to distribute work between multiple processes.

       Detected schemes are "mpi4py", "scoop", and if none of these
       are found, then "multiprocessing"
    """
    import sys

    if "mpi4py" in sys.modules:
        return "mpi4py"
    elif "scoop" in sys.modules:
        return "scoop"
    else:
        return "multiprocessing"


def parse_args():
    """Parse all of the command line arguments"""
    import argparse
    import sys

    parser = argparse.ArgumentParser(
                    description="MetaWards epidemic modelling - see "
                                "https://github.com/metawards/metawards "
                                "for more information",
                    prog="metawards")

    parser.add_argument('--version', action="store_true",
                        default=None,
                        help="Print the version information about metawards")

    parser.add_argument('-i', '--input', type=str,
                        help="Input file for the simulation that specifies "
                             "the adjustable parameters to change for each "
                             "run of the model. You must supply some "
                             "input to run a model!")

    parser.add_argument('-l', '--line', type=str, default=None, nargs="*",
                        help="Line number (or line numbers) containing the "
                             "values of adjustable parameters to run for this "
                             "run (or runs) of the model If this isn't "
                             "specified then model runs will be performed "
                             "for adjustable parameters given on all lines "
                             "from the input file. You can specify many "
                             "numbers, and ranges are also accepted, e.g. "
                             "'-l 5 6-10 12,13,14' etc. Note that the line "
                             "numbers are 0-indexed, e.g. the first line of "
                             "the file is line 0. Ranges are inclusive, "
                             "so 3-5 is the same as 3 4 5")

    parser.add_argument("-r", '--repeats', type=int, default=1,
                        help="The number of repeat runs of the model to "
                             "perform for each value of the adjustable "
                             "parameters. By default only a single "
                             "run will be performed for each set of "
                             "adjustable parameters")

    parser.add_argument('-s', '--seed', type=int, default=None,
                        help="Random number seed for this run "
                             "(default is to use a random seed)")

    parser.add_argument('-a', '--additional', type=str, default=None,
                        nargs="*",
                        help="File (or files) containing additional "
                             "seed of outbreak for the model. These are "
                             "used to seed additional infections on "
                             "specific days at different locations "
                             "during a model run")

    parser.add_argument('-o', '--output', type=str, default="output",
                        help="Path to the directory in which to place all "
                             "output files (default 'output'). This "
                             "directory will be subdivided if multiple "
                             "adjustable parameter sets or repeats "
                             "are used.")

    parser.add_argument('-u', '--UV', type=float, default=1.0,
                        help="Value for the UV parameter for the model "
                             "(default is 1.0)")

    parser.add_argument('-d', '--disease', type=str, default="ncov",
                        help="Name of the disease to model "
                             "(default is 'ncov')")

    parser.add_argument('-I', '--input-data', type=str, default="2011Data",
                        help="Name of the input data set for the network "
                             "(default is '2011Data')")

    parser.add_argument('-p', '--parameters', type=str, default="march29",
                        help="Name of the input parameter set used to "
                             "control the simulation (default 'march29')")

    parser.add_argument('-R', '--repository', type=str, default=None,
                        help="Path to the MetaWardsData repository. If "
                             "unspecified this defaults to the value "
                             "in the environment variable METAWARDSDATA "
                             "or, if that isn't specified, to "
                             "$HOME/GitHub/MetaWardsData")

    parser.add_argument('-P', '--population', type=int, default=57104043,
                        help="Initial population (default 57104043)")

    parser.add_argument('-n', '--nsteps', type=int, default=None,
                        help="Maximum number of steps (days) to run for the "
                             "simulation. Each step represents one day in the "
                             "outbreak (default is to run until the "
                             "outbreak has finished).")

    parser.add_argument('--nthreads', type=int, default=None,
                        help="Number of threads over which parallelise an "
                             "individual model run. The total number of "
                             "cores used by metawards will be "
                             "nprocesses x nthreads")

    parser.add_argument("--nprocs", type=int, default=None,
                        help="The number of processes over which to "
                             "parallelise the different model runs for "
                             "different adjustable parameter sets and "
                             "repeats. By default this will automatically "
                             "work out the number of processes based on "
                             "the way metawards is launched. Use this "
                             "option if you want to specify the number "
                             "of processes manually.")

    parser.add_argument('--hostfile', type=str, default=None,
                        help="The hostfile containing the names of the "
                             "compute nodes over which to run a parallel "
                             "job. If this is not set, the program will "
                             "attempt to automatically get this information "
                             "from the cluster queueing system. Use this "
                             "if the auto-detection fails")

    parser.add_argument('--cores-per-node', type=int, default=None,
                        help="Set the number of processor cores available "
                             "on each of the compute nodes in the cluster "
                             "that will be used to run the models "
                             "(if a cluster is used). If this is not "
                             "set then the program will attempt to "
                             "get this information from the cluster "
                             "queueing system. Use this option if the "
                             "auto-detection fails.")

    parser.add_argument('--profile', action="store_true",
                        default=None, help="Enable profiling of the code")

    parser.add_argument('--no-profile', action="store_true",
                        default=None, help="Disable profiling of the code")

    parser.add_argument('--mpi', action="store_true", default=None,
                        help="Force use of MPI to parallelise across runs")

    parser.add_argument('--scoop', action="store_true", default=None,
                        help="Force use of scoop to parallelise across runs")

    # this hidden option is used to tell the main process started using
    # mpi that it shouldn't try to become a supervisor
    parser.add_argument('--already-supervised', action="store_true",
                        default=None, help=argparse.SUPPRESS)

    args = parser.parse_args()

    if args.version:
        from metawards import get_version_string
        print(get_version_string())
        sys.exit(0)

    return (args, parser)


def get_hostfile(args):
    """Attempt to find the name of the hostfile used to specify the hosts
       to use in a cluster
    """
    if args.hostfile:
        return args.hostfile

    import os

    # PBS
    hostfile = os.getenv("PBS_NODEFILE")

    if hostfile:
        return hostfile

    # SLURM
    hostfile = os.getenv("SLURM_HOSTFILE")

    if hostfile:
        return hostfile

    return None


def get_cores_per_node(args):
    """Return the number of cores per node in the cluster"""
    if args.cores_per_node:
        return args.cores_per_node

    import os

    try:
        cores_per_node = int(os.getenv("METAWARDS_CORES_PER_NODE"))

        if cores_per_node > 0:
            return cores_per_node

    except Exception:
        pass

    raise ValueError("You must specify the number of cores per node "
                     "using --cores-per-node or by setting the "
                     "environment variable METAWARDS_CORES_PER_NODE")


def get_threads_per_task(args):
    if args.nthreads:
        return args.nthreads

    import os

    try:
        nthreads = int(os.getenv("METAWARDS_THREADS_PER_TASK"))

        if nthreads > 0:
            return nthreads

        nthreads = int(os.getenv("OMP_NUM_THREADS"))

        if nthreads > 0:
            return nthreads
    except Exception:
        pass

    raise ValueError("You must specify the number of threads per task "
                     "using --nthreads or by setting the "
                     "environment variables METAWARDS_THREADS_PER_TASK "
                     "or OMP_NUM_THREADS")


def scoop_supervisor(hostfile, args):
    """Function used by the scoop supervisor to get the information needed to
       form the scoop call to run a scoop version of the program
    """
    import os
    import sys
    print("RUNNING A SCOOP PROGRAM")

    outdir = args.output

    if not os.path.exists(outdir):
        os.mkdir(outdir)

    cores_per_node = get_cores_per_node(args)

    print(f"Will run jobs assuming {cores_per_node} cores per compute node")

    # based on the number of threads requested and the number of cores
    # per node, we can work out the number of scoop processes to start,
    # and can write a hostfile that will create the right layout
    nthreads = get_threads_per_task(args)

    print(f"Will use {nthreads} OpenMP threads per model run...")

    tasks_per_node = int(cores_per_node / nthreads)

    print(f"...meaning that the number of model runs per node will be "
          f"{tasks_per_node}")

    # Next, read the hostfile to get a unique list of hostnames
    hostnames = {}

    with open(hostfile, "r") as FILE:
        line = FILE.readline()
        while line:
            hostname = line.strip()
            hostnames[hostname] = 1
            line = FILE.readline()

    hostnames = list(hostnames.keys())
    hostnames.sort()

    print(f"Number of compute nodes equals {len(hostnames)}")
    print(", ".join(hostnames))

    # how many tasks can we perform in parallel?
    nprocs = tasks_per_node * len(hostnames)

    if args.nprocs:
        if nprocs != args.nprocs:
            print(f"WARNING: You are using a not-recommended number of "
                  f"processes {args.nprocs} for the cluster {nprocs}.")

        nprocs = args.nprocs

    print(f"Total number of parallel processes to run will be {nprocs}")
    print(f"Total number of cores in use will be {nprocs*nthreads}")

    # Now write a new hostfile that round-robins the MPI tasks over
    # the nodes for 'tasks_per_node' runs
    hostfile = os.path.join(outdir, "hostfile")
    print(f"Writing hostfile to {hostfile}")

    with open(hostfile, "w") as FILE:
        i = 0
        while i < nprocs:
            for hostname in hostnames:
                FILE.write(hostname + "\n")
                i += 1

                if i == nprocs:
                    break

    # now craft the scoop command that will use this hostfile to
    # run the job - remember to pass the option to stop the main process
    # attempting to become a supervisor itself...

    import subprocess
    import shlex

    pyexe = sys.executable
    script = os.path.abspath(sys.argv[0])
    args = " ".join(sys.argv[1:])

    # also need to tell the main program the number of processes
    # as it can't work it out itself
    cmd = f"{pyexe} -m scoop --hostfile {hostfile} -n {nprocs} " \
          f"{script} --already-supervised {args} --nprocs {nprocs}"

    print(f"Executing scoop job using '{cmd}'")

    try:
        args = shlex.split(cmd)
        subprocess.run(args).check_returncode()
    except Exception as e:
        print("ERROR: Something went wrong!")
        print(f"{e.__class__}: {e}")
        sys.exit(-1)

    print("Scoop processes completed successfully")


def mpi_supervisor(hostfile, args):
    """Function used by the MPI supervisor to get the information needed to
       form the mpiexec call to run an MPI version of the program
    """
    import os
    import sys
    print("RUNNING AN MPI PROGRAM")

    outdir = args.output

    if not os.path.exists(outdir):
        os.mkdir(outdir)

    cores_per_node = get_cores_per_node(args)

    print(f"Will run jobs assuming {cores_per_node} cores per compute node")

    # based on the number of threads requested and the number of cores
    # per node, we can work out the number of mpi processes to start,
    # and can write a hostfile that will create the right layout
    nthreads = get_threads_per_task(args)

    print(f"Will use {nthreads} OpenMP threads per model run...")

    tasks_per_node = int(cores_per_node / nthreads)

    print(f"...meaning that the number of model runs per node will be "
          f"{tasks_per_node}")

    # Next, read the hostfile to get a unique list of hostnames
    hostnames = {}

    with open(hostfile, "r") as FILE:
        line = FILE.readline()
        while line:
            hostname = line.strip()
            hostnames[hostname] = 1
            line = FILE.readline()

    hostnames = list(hostnames.keys())
    hostnames.sort()

    print(f"Number of compute nodes equals {len(hostnames)}")
    print(", ".join(hostnames))

    # how many tasks can we perform in parallel?
    nprocs = tasks_per_node * len(hostnames)

    if args.nprocs:
        if nprocs != args.nprocs:
            print(f"WARNING: You are using an unrecommended number of "
                  f"processes {args.nprocs} for the cluster {nprocs}.")

        nprocs = args.nprocs

    print(f"Total number of parallel processes to run will be {nprocs}")
    print(f"Total number of cores in use will be {nprocs*nthreads}")

    # Now write a new hostfile that round-robins the MPI tasks over
    # the nodes for 'tasks_per_node' runs
    hostfile = os.path.join(outdir, "hostfile")
    print(f"Writing hostfile to {hostfile}")

    with open(hostfile, "w") as FILE:
        i = 0
        while i < nprocs:
            for hostname in hostnames:
                FILE.write(hostname + "\n")
                i += 1

                if i == nprocs:
                    break

    # now craft the mpiexec command that will use this hostfile to
    # run the job - remember to pass the option to stop the main process
    # attempt to become a supervisor itself...
    mpiexec = os.getenv("MPIEXEC")

    if mpiexec is None:
        mpiexec = "mpiexec"

    # check for weird mpiexecs...
    import subprocess
    import shlex

    try:
        args = shlex.split(f"{mpiexec} -v")
        p = subprocess.run(args, stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT)
        v = p.stdout.decode("utf-8").strip()
        print(f"{mpiexec} -v => {v}")

        if v.find("HPE HMPT") != -1:
            raise ValueError(
                "metawards needs a more modern MPI library than HPE's, "
                "so please compile to another MPI and use that.")
    except Exception as e:
        print(f"[ERROR] {e.__class__} {e}")

    pyexe = sys.executable
    script = os.path.abspath(sys.argv[0])
    args = " ".join(sys.argv[1:])

    cmd = f"{mpiexec} -np {nprocs} -hostfile {hostfile} " \
          f"{pyexe} -m mpi4py {script} --already-supervised {args}"

    print(f"Executing MPI job using '{cmd}'")

    try:
        args = shlex.split(cmd)
        subprocess.run(args).check_returncode()
    except Exception as e:
        print("ERROR: Something went wrong!")
        print(f"{e.__class__}: {e}")
        sys.exit(-1)

    print("MPI processes completed successfully")


def cli():
    """Main function for the command line interface. This does one of three
       things:

       1. If this is the main process, then it parses the arguments and
          runs and manages the jobs

       2. If this is a worker process, then it starts up and waits for work

       3. If this is a supervisor process, then it query the job scheduling
          system for information about the compute nodes to use, and will then
          set up and run a manager (main) process that will use those
          nodes to run the jobs
    """

    # get the parallel scheme now before we import any other modules
    # so that it is clear if mpi4py or scoop (or another parallel module)
    # has been imported via the required "-m module" syntax
    parallel_scheme = get_parallel_scheme()

    if parallel_scheme == "mpi4py":
        from mpi4py import MPI
        comm = MPI.COMM_WORLD
        nprocs = comm.Get_size()
        rank = comm.Get_rank()

        if rank != 0:
            # this is a worker process, so should not do anything
            # more until it is given work in the pool
            print(f"Starting worker process {rank+1} of {nprocs-1}...")
            return
        else:
            print("Starting main process...")

    elif parallel_scheme == "scoop":
        print("STARTING SCOOP PROCESS")

    import sys
    import bz2
    import os

    args, parser = parse_args()

    if not args.already_supervised:
        hostfile = get_hostfile(args)
        if hostfile:
            # The user has asked to run a parallel job - this means that this
            # process is the parallel supervisor
            if args.mpi:
                mpi_supervisor(hostfile, args)
                return
            elif args.scoop:
                scoop_supervisor(hostfile, args)
                return

            # neither is preferred - if scoop is installed then use that
            try:
                import scoop
                have_scoop = True
            except Exception:
                have_scoop = False

            if have_scoop:
                scoop_supervisor(hostfile, args)
                return

            # do we have MPI?
            try:
                import mpi4py
                have_mpi4py = True
            except Exception:
                have_mpi4py = False

            if have_mpi4py:
                mpi_supervisor(hostfile, args)
                return

            # we don't have any other option, just keep going and
            # use multiprocessing - in this case we don't need a
            # supervisor and this is the main process

    # This is now the code for the main process
    if args.input is None:
        parser.print_help(sys.stdout)
        sys.exit(0)

    # import the parameters here to speed up the display of help
    from metawards import Parameters, Network, Population, get_version_string

    # print the version information first, so that there is enough
    # information to enable someone to reproduce this run
    print(get_version_string())

    # load all of the parameters
    try:
        params = Parameters.load(parameters=args.parameters)
    except Exception as e:
        print(f"Unable to load parameter files. Make sure that you have "
              f"cloned the MetaWardsData repository and have set the "
              f"environment variable METAWARDSDATA to point to the "
              f"local directory containing the repository, e.g. the "
              f"default is $HOME/GitHub/MetaWardsData")
        raise e

    # should we profile the code? (default yes, as it doesn't cost anything)
    profile = args.profile

    if args.no_profile:
        profile = False
    elif profile is None:
        profile = False

    # load the disease and starting-point input files
    params.set_disease(args.disease)
    params.set_input_files(args.input_data)

    # get the line numbers of the input file to read
    if args.line is None or len(args.line) == 0:
        linenums = None
        print(f"Using parameters from all lines of {args.input}")
    else:
        from metawards.utils import string_to_ints
        linenums = string_to_ints(args.line)

        if len(linenums) == 0:
            print(f"You cannot read no lines from {args.input}?")
            sys.exit(-1)
        elif len(linenums) == 1:
            print(f"Using parameters from line {linenums[0]} of {args.input}")
        else:
            print(f"Using parameters from lines {linenums} of {args.input}")

    variables = params.read_variables(args.input, linenums)

    if args.additional is None or len(args.additional) == 0:
        print("Not using any additional seeds...")
    else:
        for additional in args.additional:
            print(f"Loading additional seeds from {additional}")
            params.add_seeds(additional)

    nrepeats = args.repeats

    if nrepeats is None or nrepeats < 1:
        nrepeats = 1

    if nrepeats == 1:
        print("Performing a single run of each set of parameters")
    else:
        print(f"Performing {nrepeats} runs of each set of parameters")

    variables = variables.repeat(nrepeats)

    nthreads = args.nthreads

    if nthreads is None or nthreads < 1:
        from metawards.utils import get_available_num_threads
        nthreads = get_available_num_threads()

    print(f"Number of threads to use for each model run is {nthreads}")

    nprocs = args.nprocs

    if nprocs is None or nprocs < 1:
        from metawards.utils import get_number_of_processes
        nprocs = get_number_of_processes(parallel_scheme, nprocs)

    print(f"Number of processes used to parallelise model runs is {nprocs}")

    if nprocs > 1:
        print(f"Parallelisation will be achieved using {parallel_scheme}")

    # extra parameters that are set
    params.UV = args.UV

    # set these extra parameters to 0
    params.static_play_at_home = 0
    params.play_to_work = 0
    params.work_to_play = 0
    params.daily_imports = 0.0

    # the size of the starting population
    population = Population(initial=args.population)

    print("\nBuilding the network...")
    network = Network.build(params=params, calculate_distances=True,
                            profile=profile)

    print("\nRun the model...")
    from metawards.utils import run_models

    result = run_models(network=network, variables=variables,
                        population=population, nprocs=nprocs,
                        nthreads=nthreads, seed=args.seed,
                        nsteps=args.nsteps, output_dir=args.output,
                        profile=profile, parallel_scheme=parallel_scheme)

    # write the result to a csv file that can be easily read by R or
    # pandas - this will be written compressed to save space
    results_file = os.path.join(args.output, "results.csv.bz2")
    print(f"\nWriting a summary of all results into the compressed\n"
          f"csv file {results_file}. You can use this to quickly\n"
          f"look at statistics across all runs using e.g. R or pandas")

    with bz2.open(results_file, "wt") as FILE:
        FILE.write("variables,repeat,step,susceptibles,latent,"
                   "total,n_inf_wards\n")
        for varset, trajectory in result:
            start = f"{varset.fingerprint()},{varset.repeat_index()},"

            for i, pop in enumerate(trajectory):
                FILE.write(f"{start}{i},{pop.susceptibles},"
                           f"{pop.latent},{pop.total},{pop.n_inf_wards}\n")

    print("End of the run")


if __name__ == "__main__":
    cli()

else:
    # this is one of the worker processes - make sure that they
    # have imported metawards
    from metawards.utils import run_worker
