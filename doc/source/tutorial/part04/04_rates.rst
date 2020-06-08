========================
Extracting rates by ward
========================

One of the major applications of a custom extractor is to enable you
to add your own live-analysis that is performed while the simulation
is running. This is much faster than having ``metawards`` write all
data to disk, and then running analysis in a post-processing step.

To analyse data, you need to understand the
:class:`~metawards.Workspace` class.

Workspace
---------

The :class:`~metawards.Workspace` class provides a workspace in which data
is accumulated and analysis performed. It is cleared between iterations,
and holds the following information;

Data indexed by disease stage:
    * ``inf_tot``: The total number of workers in each disease stage, summed over all wards.

    * ``pinf_tot``: The total number of players in each disease stage, summed over all wards.

    * ``n_inf_wards``: The number of wards which have at least one individual in the disease stage,

Data indexed by ward:
    * ``total_inf_ward``: The total number of infections in each ward

    * ``total_new_inf_ward``: The total number of new infections in each ward

    * ``incidence``: The incidence of infection in each ward

    * ``S_in_wards``: The total population in the ``S`` state in each ward

    * ``E_in_wards``: The total population in the ``E`` state in each ward

    * ``I_in_wards``: The total population in the ``I`` state in each ward

    * ``R_in_wards``: The total population in the ``R`` state in each ward

Data indexed by disease stage and then by ward
   * ``ward_inf_tot``: The total population in each disease stage in each ward

Extracting the population in I1
-------------------------------

We can use a custom extractor to report the total number of individuals
who are in the first ``I`` stage (I1) for each ward for each day.

To do this, create a new extractor called ``extract_i1.py`` and copy
in the below;

.. code-block:: python

    from metawards.extractors import extract_default


    def output_i1(population, workspace, output_dir, **kwargs):
        # Open the file "total_i1.csv" in the output directory
        FILE = output_dir.open("total_i1.csv")

        ward_inf_tot = workspace.ward_inf_tot

        # The I1 state is stage 2
        I1_inf_tot = ward_inf_tot[2]

        FILE.write(str(population.day) + ",")
        FILE.write(",".join([str(x) for x in I1_inf_tot]) + "\n")


    def extract_i1(**kwargs):
        # return all of the functions from "extract_default"
        # plus our new "output_i1"
        funcs = extract_default(**kwargs)
        funcs.append(output_i1)
        return funcs

This defines a new output function called ``output_i1``. This calls the
``open`` function of the :class:`~metawards.OutputFiles` object held
in ``output_dir`` to open the file ``total_i1.csv`` in the output
directory.

.. note::

   The :class:`~metawards.OutputFiles` class is clever enough to only
   open the file once, and will automatically close it when needed. It
   will also ensure that the file is opened in the correct output
   directory for a *model run* and will compress the file using bz2
   if the ``--auto-bzip`` command-line option has been passed (the default),
   or will disable automatic compression if ``--no-auto-bzip`` is set.

The function then gets ``I1_inf_tot`` from the third disease stage data
held in ``workspace.ward_inf_tot``. The third stage is the first ``I``
stage as the first stage (``ward_inf_tot[0]``) is a special ``*`` stage,
used for advanced bookkeeping, while the second stage (``ward_inf_tot[1]``)
is the latent, ``E`` stage.

.. note::

   The ``*`` stage is used to help evaluate how many wards see new infections.
   Individuals are moved into the ``*`` stage at the point of infection,
   and are moved into the ``E`` stage on the day after infection. By default,
   individuals in the ``*`` stage are counted into ``R``, which is why this
   does not appear to rise continuously. You can control how individuals
   in the ``*`` stage are counted using either ``--star-is-E`` to count them
   as ``E`` (additional latent stage), ``--star-is-R`` to count them as
   ``R`` (default behaviour) or ``--disable-star`` to remove the ``*``
   stage and instead treat this first stage as the one and only ``E`` stage.
   Note that if you do this, you will need to update the disease files to
   remove the ``*`` stage, and to update your above extractor as now
   stage 1 will be the first ``I`` stage.

Now that we have the population in the ``I1`` stage in each ward in
``I1_inf_tot``, we write this as a comma-separated line to the file,
starting each line with the day number obtained from the passed
:class:`~metawards.Population` typed ``population`` object.

To use your extractor run ``metawards`` using;

.. code-block:: bash

   metawards -d lurgy3 --extract extract_i1 -a ExtraSeedsLondon.dat --nsteps 30

.. note::

   Note that we've set ``nsteps`` to 30 for illustration only,
   just to limit the runtime and the size of the file. In a real production
   run you wouldn't need to set the number of steps.

You should see that your file called ``total_i1.csv.bz2`` has been created
in the output directory, and that this contains the populations of the ``I1``
state for each ward.

Calculating rates
-----------------

As well as outputting raw data, you can also perform some simple analysis
that is run live during the *model run*. For example, you may want to record
the number of individuals entering each state, so that you can calculate
the rate of progress across states.

To do this, you will need to save the ``ward_inf_tot`` data from the previous
day's state. You can do this by adding it as a custom attribute to the
workspace.

Create a new extractor by creating ``extract_rate.py`` and copying in the below;

.. code-block:: python

    from metawards.extractors import extract_default
    from copy import deepcopy


    def output_rate(population, workspace, output_dir, **kwargs):
        if not hasattr(workspace, "output_rate_previous"):
            # This is the first day, so we cannot calculate the rate.
            # Instead, just save today's data so that it can be
            # be used tomorrow
            workspace.output_rate_previous = deepcopy(workspace.ward_inf_tot)
            return

        # get yesterday's data
        ward_inf_previous = workspace.output_rate_previous

        # get today's data
        ward_inf_tot = workspace.ward_inf_tot

        # calculate and write the difference between the two to files for
        # each disease stage...
        for i in range(0, workspace.n_inf_classes):
            FILE = output_dir.open(f"rate_{i}.csv")

            FILE.write(str(population.day))

            # loop over the data for each ward and write the
            # difference to the file
            for old, new in zip(ward_inf_previous[i], ward_inf_tot[i]):
                FILE.write("," + str(new - old))

            FILE.write("\n")

        # save today's data so that it can be used tomorrow
        workspace.output_rate_previous = deepcopy(ward_inf_tot)


    def extract_rate(**kwargs):
        funcs = extract_default(**kwargs)
        funcs.append(output_rate)
        return funcs

This extractor looks a little more complex, but it builds on what you have
seen before. It defines ``output_rate``, which if the function that will
output the rates, and ``extract_rate`` which returns all of the functions
from ``extract_default``, plus your new ``output_rate`` function.

The first job of ``output_rate`` is to determine if it has been called on
the first day of the model. If it has, then there is no previous data
from "yesterday" that can be used to calculate the rate. The function
detects if this is the case by checking for a new custom attribute
that will be under the control of this function. We will call this
attribute ``output_rate_previous``, so to minimise the risk of a name
collision. If this attribute doesn't exist, then we must be on the first
day. We this save today's data so that it can be used tomorrow.

If the attribute does exist, then we can calculate a rate. We do that by
getting yesterday's data from ``output_rate_previous`` and todays data
from ``workspace.ward_inf_tot``. We then loop over all of the disease
stages, and open an output file for each stage (called ``rate_{i}.csv``).
We then write into this file the day, then the difference between today's
and yesterday's population in ward, for this ``ith`` disease stage.

Finally, we save today's data into ``workspace.output_rate_previous``, so
that it can be used tomorrow as yesterday's data.

Run this extractor in ``metawards`` using;

.. code-block:: bash

   metawards -d lurgy3 --extract extract_rate -a ExtraSeedsLondon.dat --nsteps 30

(again, we are limiting this to 30 steps just for demonstration reasons)

You should see that you have files ``rate_0.csv.bz2``, ``rate_1.csv.bz2`` etc.
now created in the output directory. If you look at these files you should
see that they contain the differences between the populations in each ward
for each disease stage between each day.
