
__all__ = ["import_graphics_modules",
           "save_summary_plots",
           "create_overview_plot",
           "create_average_plot"]


def import_graphics_modules(verbose=False):
    """Imports pandas and matplotlib in a safe way, giving a good
       error message if something goes wrong.

       Parameters
       ----------
       verbose: bool
         Whether or not to print to the screen to signal progress...

       Returns
       -------
       (pd, plt)
          The pandas (pd) and matplotlib.pyplot (plt) modules
    """
    try:
        if verbose:
            print("Importing graphics modules...")
        import pandas as pd
        import matplotlib.pyplot as plt
    except ImportError:
        print("You must have pandas and matplotlib installed to run "
              "metawards-plot")
        print("Install using either `pip install pandas` if you are using")
        print("pip, or 'conda install pandas' if you are using conda.")
        raise ImportError("Cannot produce the plot as pandas and matplotlib "
                          "are not installed.")

    return (pd, plt)


def create_overview_plot(df):
    """Create a summary plot of the result.csv data held in the
       passed pandas dataframe. This returns the figure for you
       to save if desired (or just call ``plt.show()`` to show
       it in Jupyter)

       Parameters
       ----------
       df : Pandas Dataframe
         The pandas dataframe containing the data from results.csv.bz2

       Returns
       -------
       fig
         The matplotlib figure containing the summary plot
    """
    _, plt = import_graphics_modules()

    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(10, 10))

    i = 0
    j = 0

    for column in ["E", "I", "IW", "R"]:
        ax = df.pivot(index="date", columns="repeat",
                      values=column).plot.line(ax=axes[i][j])
        ax.tick_params('x', labelrotation=90)
        ax.get_legend().remove()
        ax.set_title(column)
        ax.set_ylabel("Population")

        j += 1
        if j == 2:
            j = 0
            i += 1

    fig.tight_layout(pad=1)

    return fig


def create_average_plot(df):
    """Create an average plot of the result.csv data held in the
       passed pandas dataframe. This returns the figure for you
       to save if desired (or just call ``plt.show()`` to show
       it in Jupyter)

       Parameters
       ----------
       df : Pandas Dataframe
         The pandas dataframe containing the data from results.csv.bz2

       Returns
       -------
       fig
         The matplotlib figure containing the summary plot
    """
    _, plt = import_graphics_modules()

    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(10, 10))

    mean_average = df.groupby("date").mean()
    stddev = df.groupby("date").std()

    i = 0
    j = 0

    for column in ["E", "I", "IW", "R"]:
        ax = mean_average.plot.line(y=column, yerr=stddev[column],
                                    ax=axes[i][j])
        ax.tick_params('x', labelrotation=90)
        ax.get_legend().remove()
        ax.set_title(column)
        ax.set_ylabel("Population")

        j += 1
        if j == 2:
            j = 0
            i += 1

    fig.tight_layout(pad=1)

    return fig


def save_summary_plots(results: str, output_dir: str = None,
                       format: str = "pdf", dpi: int = 300,
                       verbose=False):
    """Create summary plots of the data contained in the passed
       'results.csv.bz2' file that was produced by metawards
       and save them to disk.

       Parameters
       ----------
       results: str
         The full path to the file containing the results. This
         **must** have been created by ``metawards``
       output_dir: str
         Path to the directory in which you want to place the graphs.
         This defaults to the same directory that contains 'results'
       format: str
         The format to use to save the graphs. This defaults to 'pdf'
       dpi: int
         The dots-per-inch to use when saving bitmap graphics (e.g.
         png, jpg etc)
       verbose: bool
         Whether or not to print progress to the screen

       Returns
       -------
       (overview, average): Tuple(str, str)
         Full file paths to the 'overview' and 'average graphs that
         this function produces
    """
    pd, _ = import_graphics_modules(verbose=verbose)
    import os

    if verbose:
        print(f"Reading data from {results}...")

    df = pd.read_csv(results)

    if output_dir is None:
        output_dir = os.path.dirname(results)

    if format is None:
        format = "pdf"

    overview = os.path.join(output_dir, f"overview.{format}")

    if verbose:
        print(f"Creating overview plot...")

    fig = create_overview_plot(df)

    if verbose:
        print(f"Saving to {overview}...")

    fig.savefig(overview, dpi=dpi)

    average = os.path.join(output_dir, f"average.{format}")

    if verbose:
        print(f"Creating average plot...")
    fig = create_average_plot(df)

    if verbose:
        print(f"Saving to {average}...")

    fig.savefig(average, dpi=dpi)

    return (overview, average)
