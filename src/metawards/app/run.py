#!/bin/env python3

# This is the command-line version of metawards

def cli():
    import sys
    import argparse

    parser = argparse.ArgumentParser(
                    description="MetaWards epidemic modelling - see "
                                "https://github.com/metawards/metawards "
                                "for more information",
                    prog="metawards")

    parser.add_argument('-i', '--input', type=str,
                        help="Input file for the simulation")

    parser.add_argument('-l', '--line', type=int, default=0,
                        help="Line number from the inputfile to run "
                             "(default 0 as 0-indexed line number)")

    parser.add_argument('-s', '--seed', type=int, default=None,
                        help="Random number seed for this run "
                             "(default is to use a random seed)")

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

    parser.add_argument('-r', '--repository', type=str, default=None,
                        help="Path to the MetaWardsData repository. If "
                             "unspecified this defaults to the value "
                             "in the environment variable METAWARDSDATA "
                             "or, if that isn't specified, to "
                             "$HOME/GitHub/MetaWardsData")

    parser.add_argument('-P', '--population', type=int, default=57104043,
                        help="Initial population (default 57104043)")

    parser.add_argument('-n', '--nsteps', type=int, default=None,
                        help="Maximum number of steps to run for the "
                             "simulation (default is to run until the "
                             "epidemic has finished)")

    parser.add_argument('--nthreads', type=int, default=None,
                        help="Number of threads over which to run the "
                             "model.")

    parser.add_argument('-o', '--output', type=str, default="output",
                        help="Path to the directory in which to place all "
                             "output files (default 'output')")

    parser.add_argument('--profile', action="store_true",
                        default=True, help="Enable profiling of the code")

    parser.add_argument('--no-profile', action="store_true",
                        default=False, help="Disable profiling of the code")

    args = parser.parse_args()

    if args.input is None:
        parser.print_help(sys.stdout)
        sys.exit(0)

    # import the parameters here to speed up the display of help
    from metawards import Parameters, Network, Population

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

    # load the disease and starting-point input files
    params.set_disease(args.disease)
    params.set_input_files(args.input_data)

    # start from the parameters in the specified line number of the
    # provided input file
    params.read_file(args.input, args.line)

    # extra parameters that are set
    params.UV = args.UV

    # set these extra parameters to 0
    params.static_play_at_home = 0
    params.play_to_work = 0
    params.work_to_play = 0
    params.daily_imports = 0.0

    # the size of the starting population
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
