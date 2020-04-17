
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


def create_overview_plot(df, match_axes=True):
    """Create a summary plot of the result.csv data held in the
       passed pandas dataframe. This returns the figure for you
       to save if desired (or just call ``plt.show()`` to show
       it in Jupyter)

       If the dataframe contains multiple fingerprints, then this
       will return a dictionary of figures, one for each fingerprint,
       indexed by fingerprint

       Parameters
       ----------
       df : Pandas Dataframe
         The pandas dataframe containing the data from results.csv.bz2
       match_axes: bool
         If true (default) then this will ensure that all of the plots
         for different fingerprints are put on the same axis scale

       Returns
       -------
       fig
         The matplotlib figure containing the summary plot, or a
         dictionary of figures if there are multiple fingerprints
    """
    _, plt = import_graphics_modules()

    fingerprints = df["fingerprint"].unique()

    figs = {}

    min_date = None
    max_date = None
    max_y = {}
    min_y = {}

    columns = ["E", "I", "IW", "R"]

    if len(fingerprints) > 1 and match_axes:
        for fingerprint in fingerprints:
            df2 = df[df["fingerprint"] == fingerprint]

            for column in columns:
                min_d = df2["day"].min()
                max_d = df2["day"].max()
                min_val = df2[column].min()
                max_val = df2[column].max()

                if min_date is None:
                    min_date = min_d
                    max_date = max_d
                else:
                    if min_d < min_date:
                        min_date = min_d
                    if max_d > max_date:
                        max_date = max_d

                if column not in min_y:
                    min_y[column] = min_val
                    max_y[column] = max_val
                else:
                    if min_val < min_y[column]:
                        min_y[column] = min_val
                    if max_val > max_y[column]:
                        max_y[column] = max_val

    for fingerprint in fingerprints:
        df2 = df[df["fingerprint"] == fingerprint]

        fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(10, 10))

        i = 0
        j = 0

        for column in columns:
            ax = df2.pivot(index="date", columns="repeat",
                           values=column).plot.line(ax=axes[i][j])
            ax.tick_params('x', labelrotation=90)
            ax.get_legend().remove()
            ax.set_ylabel("Population")

            if len(fingerprints) > 1 and match_axes:
                ax.set_xlim(min_date, max_date)
                ax.set_ylim(min_y[column], 1.1*max_y[column])

            if len(fingerprints) > 1:
                ax.set_title(f"{fingerprint} : {column}")
            else:
                ax.set_title(column)

            j += 1
            if j == 2:
                j = 0
                i += 1

        fig.tight_layout(pad=1)
        figs[fingerprint] = fig

    if len(figs) == 0:
        return None
    elif len(figs) == 1:
        return figs[list(figs.keys())[0]]
    else:
        return figs


def create_average_plot(df):
    """Create an average plot of the result.csv data held in the
       passed pandas dataframe. This returns the figure for you
       to save if desired (or just call ``plt.show()`` to show
       it in Jupyter)

       Note that this won't do anything unless there are multiple
       repeats of the model run in the output. In that case, it
       will return None

       If the dataframe contains multiple fingerprints, then this
       will return a dictionary of figures, one for each fingerprint,
       indexed by fingerprint

       Parameters
       ----------
       df : Pandas Dataframe
         The pandas dataframe containing the data from results.csv.bz2

       Returns
       -------
       fig
         The matplotlib figure containing the summary plot, or None
         if there are no repeats over which to average. A dictionary
         of figures will be returned if the dataframe contains multiple
         fingerprint - the dictionaries will be indexed by fingerprint
    """
    fingerprints = df["fingerprint"].unique()

    figs = {}

    for fingerprint in fingerprints:
        df2 = df[df["fingerprint"] == fingerprint]

        nrepeats = len(df2["repeat"].unique())

        if nrepeats > 1:
            _, plt = import_graphics_modules()

            fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(10, 10))

            mean_average = df2.groupby("date").mean()
            stddev = df2.groupby("date").std()

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
            figs[fingerprint] = fig

    if len(figs) == 0:
        return None
    elif len(figs) == 1:
        return figs[list(figs.keys())[0]]
    else:
        return figs


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
       filenames: List(str)
         Full file paths of all of the files written by this function
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

    filenames = []

    if verbose:
        print(f"Creating overview plot(s)...")

    figs = create_overview_plot(df)

    if not isinstance(figs, dict):
        figs = {"fingerprint": figs}

    for fingerprint, fig in figs.items():
        if len(figs) == 1:
            filename = os.path.join(output_dir, f"overview.{format}")
        else:
            filename = os.path.join(output_dir,
                                    f"overview_{fingerprint}.{format}")

        if verbose:
            print(f"Saving to {filename}...")

        fig.savefig(filename, dpi=dpi)
        filenames.append(filename)

    if verbose:
        print(f"Creating average plot(s)...")

    figs = create_average_plot(df)

    if figs is None:
        print("Nothing to plot")
    else:
        if not isinstance(figs, dict):
            figs = {"fingerprint": figs}

        for fingerprint, fig in figs.items():
            if len(figs) == 1:
                filename = os.path.join(output_dir, f"average.{format}")
            else:
                filename = os.path.join(output_dir,
                                        f"average_{fingerprint}.{format}")

            if verbose:
                print(f"Saving to {filename}...")

            fig.savefig(filename, dpi=dpi)
            filenames.append(filename)

    return filenames
