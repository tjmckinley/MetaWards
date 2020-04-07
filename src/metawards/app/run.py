#!/bin/env python3

"""
The metawards command line program.

Usage:
    To get the help for this program and the list of all of the
    arguments (with defaults) use;

    metawards --help
"""


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


def cli():
    # get the parallel scheme now before we import any other modules
    # so that it is clear if mpi4py or scoop (or another parallel module)
    # has been imported via the required "-m module" syntax
    parallel_scheme = get_parallel_scheme()

    import sys
    import argparse

    parser = argparse.ArgumentParser(
                    description="MetaWards epidemic modelling - see "
                                "https://github.com/metawards/metawards "
                                "for more information",
                    prog="metawards")

    parser.add_argument('-i', '--input', type=str,
                        help="Input file for the simulation that specifies "
                             "the adjustable parameters to change for each "
                             "run of the model.")

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

    parser.add_argument("--nprocs", type=int, default=None,
                        help="The number of processes over which to "
                             "parallelise the different model runs for "
                             "different adjustable parameter sets and "
                             "repeats. By default this will automatically "
                             "work out the number of processes based on "
                             "the way metawards is launched. Use this "
                             "option if you want to specify the number "
                             "or processes manually.")

    parser.add_argument('-s', '--seed', type=int, default=None,
                        help="Random number seed for this run "
                             "(default is to use a random seed)")

    parser.add_argument('-a', '--additional', type=str, default=None,
                        help="File (or files) containing additional "
                             "seed of outbreak for the model. These are "
                             "used to seed additional infections on "
                             "specific days at different locations "
                             "during a model run")

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

    parser.add_argument('-o', '--output', type=str, default="output",
                        help="Path to the directory in which to place all "
                             "output files (default 'output'). This "
                             "directory will be subdivided if multiple "
                             "adjustable parameter sets or repeats "
                             "are used.")

    parser.add_argument('--profile', action="store_true",
                        default=None, help="Enable profiling of the code")

    parser.add_argument('--no-profile', action="store_true",
                        default=None, help="Disable profiling of the code")

    parser.add_argument('--version', action="store_true",
                        default=None,
                        help="Print the version information about metawards")

    args = parser.parse_args()

    if args.version:
        from metawards import get_version_string
        print(get_version_string())
        sys.exit(0)

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

    sys.exit(0)

    # load the disease and starting-point input files
    params.set_disease(args.disease)
    params.set_input_files(args.input_data)

    # start from the parameters in the specified line number of the
    # provided input file
    params.read_file(args.input, args.line)

    # extra parameters that are set
    params.UV = args.UV

    # set these extra parameters to 0
    params.static_play_at_home = 0
    params.play_to_work = 0
    params.work_to_play = 0
    params.daily_imports = 0.0

    # the size of the starting population
    population = Population(initial=args.population)

    print("Building the network...")
    network = Network.build(params=params, calculate_distances=True,
                            profile=profile)

    print("Run the model...")
    population = network.run(population=population, seed=args.seed,
                             s=-1, nsteps=args.nsteps,
                             output_dir=args.output,
                             profile=profile,
                             nthreads=args.nthreads
                             )

    print("End of the run")

    print(f"Model output:  {population}")


if __name__ == "__main__":
    cli()
