
def parse_args():
    """Parse all of the command line arguments"""
    import argparse
    import sys

    parser = argparse.ArgumentParser(
                    description="MetaWards simple plotting program - see "
                                "https://github.com/metawards/metawards "
                                "for more information",
                    prog="metawards-plot")

    parser.add_argument('--version', action="store_true",
                        default=None,
                        help="Print the version information about "
                             "metawards-plot")

    parser.add_argument("-i", "--input", type=str,
                        help="Full path to the 'results.csv.bz2' file "
                             "that you want to quickly plot.")

    parser.add_argument("-o", "--output", type=str, default=None,
                        help="Directory in which you want to place the "
                             "graphs. By default this is the same directory "
                             "as contains the 'results.csv.bz2' file")

    parser.add_argument("--format", type=str, default="pdf",
                        help="Desired format of the graphs that are "
                             "produced. Good formats are 'pdf' for "
                             "publication graphics and 'png' or 'jpeg' "
                             "for webpages.")

    args = parser.parse_args()

    if args.version:
        from metawards import get_version_string
        print(get_version_string())
        sys.exit(0)

    return (args, parser)


def cli():
    """Main function for the metawards-plot command line interface.
       This is a simple program that creates basic plots of the output
       data. The aim is to make visualisation of the data as quick
       and painless as possible.
    """
    import sys

    args, parser = parse_args()

    output_csv = args.input

    if output_csv is None:
        parser.print_help()
        sys.exit(0)

    from metawards.analysis import save_summary_plots

    filenames = save_summary_plots(results=output_csv,
                                   output_dir=args.output,
                                   format=args.format,
                                   verbose=True)

    print(f"Written graphs to {', '.join(filenames)}")


if __name__ == "__main__":
    cli()
