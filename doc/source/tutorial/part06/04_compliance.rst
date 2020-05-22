======================
Conditional Compliance
======================

In the last section we saw that self-isolation will only work if
individuals self-isolate at an early stage of the lurgy, and for 5-7 days.

However, that model and conclusion is flawed. The model assumed that
everyone who had reached the self-isolation stage would elect to
self-isolate, and would remain their for the full required duration.

Unfortunately, this is not realistic. Many individuals would not
self-isolate, e.g. because they don't feel that ill, don't recognise
the symptoms, have financial or social pressures to keep going out
etc. Equally, many may break quarantine early, if they feel better or
more mobile.

To model this, we need to conditionally send only a percentage of
individuals into self-isolation. And then, for each day quarantine,
we need to release an increasing percentage back to their normal
behaviour.

Moving a fraction of individuals
--------------------------------

Both the :meth:`~metawards.movers.go_isolate` and
:meth:`~metawards.movers.go_to` go functions accept the ``fraction``
keyword argument. This argument sets the percentage (or fraction)
of the population who should move. By default this is ``1.0`` (representing
100%). This fraction is used to sample a random number of individuals
according to a binomial distribution.

We can adjust this value to examine impact of reduced self-isolation
compliance on the outbreak.

To do this, update your ``move_isolate.py`` move function to;

.. code-block:: python

    from metawards import Population
    from metawards import Networks
    from metawards.movers import go_isolate, go_to

    def move_isolate(network: Networks, population: Population, **kwargs):
        ndays = 7
        isolate_stage = 3
        compliance_fraction = 0.5

        day = population.day % ndays
        isolate = f"isolate_{day}"

        go_isolate_day = lambda **kwargs: go_isolate(
                                            go_from="home",
                                            go_to=isolate,
                                            self_isolate_stage=isolate_stage,
                                            fraction=compliance_fraction,
                                            **kwargs)

        go_released = lambda **kwargs: go_to(go_from=isolate,
                                            go_to="released",
                                            **kwargs)

        return [go_released, go_isolate_day]

Here we have added ``compliance_fraction``, set to ``0.5`` to represent,
on average, to 50% of individuals complying with the need to go into
self-isolation. This fraction is passed as ``fraction`` to the
``go_isolate`` function.

Run ``metawards`` using;

.. code-block:: bash

   metawards -d lurgy4 -D demographics.json -a ExtraSeedsLondon.dat --mixer mix_isolate --mover move_isolate --nsteps 365

You should see that infection spreads quickly, as the 50% of individuals who
each day decide not to self-isolate from stage 2 of the lurgy infect the
susceptible population. The outbreak should end with approximately
two thirds of those infected recovering in ``released`` (and so had
isolated), and one third recovering in ``home`` (having never isolated).
A plot of the the demographics shows this more clearly;

.. code-block:: bash

   metawards-plot -i output/trajectory.csv.bz2

.. image:: ../../images/tutorial_6_4_1.jpg
   :alt: Demographics for 50% self-isolation compliance

Scanning compliance
-------------------

We can investigate the effect of different levels of compliance by
scanning through ``compliance_fraction``. Update your ``move_isolate.py``
to read;

.. code-block:: python

    from metawards import Population
    from metawards import Networks
    from metawards.movers import go_isolate, go_to

    def move_isolate(network: Networks, population: Population, **kwargs):
        user_params = network.params.user_params

        ndays = 7
        isolate_stage = 3
        compliance_fraction = user_params["compliance"]

        day = population.day % 7
        isolate = f"isolate_{day}"

        go_isolate_day = lambda **kwargs: go_isolate(
                                            go_from="home",
                                            go_to=isolate,
                                            self_isolate_stage=isolate_stage,
                                            fraction=compliance_fraction,
                                            **kwargs)

        go_released = lambda **kwargs: go_to(go_from=isolate,
                                            go_to="released",
                                            **kwargs)

        return [go_released, go_isolate_day]

The only change here is that we now set ``compliance_fraction`` from the
``compliance`` user defined parameter.

Now create a scan file called ``scan_compliance.dat`` that contains;

::

    .compliance
        1.00
        0.95
        0.90
        0.85
        0.80
        0.75
        0.70
        0.65
        0.60
        0.55
        0.50

This scans ``compliance`` from ``1.00`` to ``0.50`` in increments of ``0.05``.

This is the command to run a single scan locally;

.. code-block:: bash

   metawards -d lurgy4 -D demographics.json -a ExtraSeedsLondon.dat --mixer mix_isolate --mover move_isolate --extractor extract_none --nsteps 365 -i scan_compliance.dat

You will likely need a cluster to perform repeats, so here is a suitable
PBS and slurm job file;

::

    #!/bin/bash
    #PBS -l walltime=12:00:00
    #PBS -l select=4:ncpus=64:mem=64GB
    # The above sets 4 nodes with 64 cores each

    source $HOME/envs/metawards/bin/activate

    # change into the directory from which this job was submitted
    cd $PBS_O_WORKDIR

    metawards -d lurgy4 -D demographics.json -a ExtraSeedsLondon.dat \
            --mixer mix_isolate --mover move_isolate --extractor extract_none \
            --nsteps 365 -i scan_compliance.dat --repeats 8 \
            --nthreads 16 --force-overwrite-output --no-spinner --theme simple

::

    #!/bin/bash
    #SBATCH --time=01:00:00
    #SBATCH --ntasks=4
    #SBATCH --cpus-per-task=64
    # The above sets 4 nodes with 64 cores each

    source $HOME/envs/metawards/bin/activate

    metawards -d lurgy4 -D demographics.json -a ExtraSeedsLondon.dat \
            --mixer mix_isolate --mover move_isolate --extractor extract_none \
            --nsteps 365 -i scan_compliance.dat --repeats 8 \
            --nthreads 16 --force-overwrite-output --no-spinner --theme simple

You can generate the animations of the demographic...

Breaking quarantine early
-------------------------

From the above, we see that we need at least XX% of individuals to
comply with self-isolation. However, compliance with self-isolation
requests applies as much to remaining
in quarantine as joining. We can represent a fraction of individuals
leaving quarantine early each day by passing ``fraction`` to
:meth:`~metawards.movers.go_to`. Do this by updating your
``move_isolate.py`` to read;

.. code-block:: python

    from metawards import Population
    from metawards import Networks
    from metawards.movers import go_isolate, go_to

    def move_isolate(network: Networks, population: Population, **kwargs):
        user_params = network.params.user_params

        ndays = 7
        isolate_stage = 2
        compliance_fraction = 0.8

        # fraction who leave early, counting from the longest to
        # shortest stay in isolation. 50% leave after 6 days, while
        # only 0% leave after 1 day
        leave_early = [0.5, 0.4, 0.3, 0.2, 0.1, 0.0]

        day = population.day % 7
        isolate = f"isolate_{day}"

        go_early = []

        # have to define this functions one-by-one and not in a loop
        # otherwise python will bind all functions to the value of i
        # of the last iteration of the loop
        go_early.append(lambda **kwargs: go_to(
                                go_from=f"isolate_{(day + 1) % 7}",
                                go_to="released",
                                fraction=leave_early[0],
                                **kwargs))
        go_early.append(lambda **kwargs: go_to(
                                go_from=f"isolate_{(day + 2) % 7}",
                                go_to="released",
                                fraction=leave_early[1],
                                **kwargs))
        go_early.append(lambda **kwargs: go_to(
                                go_from=f"isolate_{(day + 3) % 7}",
                                go_to="released",
                                fraction=leave_early[2],
                                **kwargs))
        go_early.append(lambda **kwargs: go_to(
                                go_from=f"isolate_{(day + 4) % 7}",
                                go_to="released",
                                fraction=leave_early[3],
                                **kwargs))
        go_early.append(lambda **kwargs: go_to(
                                go_from=f"isolate_{(day + 5) % 7}",
                                go_to="released",
                                fraction=leave_early[4],
                                **kwargs))
        go_early.append(lambda **kwargs: go_to(
                                go_from=f"isolate_{(day + 6) % 7}",
                                go_to="released",
                                fraction=leave_early[5],
                                **kwargs))

        go_isolate_day = lambda **kwargs: go_isolate(
                                            go_from="home",
                                            go_to=isolate,
                                            self_isolate_stage=isolate_stage,
                                            fraction=compliance_fraction,
                                            **kwargs)

        go_released = lambda **kwargs: go_to(go_from=isolate,
                                            go_to="released",
                                            **kwargs)

        return go_early + [go_released, go_isolate_day]

.. note::
   It would be nicer and less error-prone if we could create the
   ``go_early`` functions in a loop. However, this would not work
   because of the way that Python lambda functions bind their arguments.
   If we did this, the arguments from the last iteration of the loop
   would be used for all of the ``go_early`` functions, i.e. we would
   try to move individuals out of the same ``isolate_N`` demographic
   six times.

.. note::
   Note that we've set ``compliance`` to 0.8 based on the results of the
   last scan.

Here, we've created a new set of go functions called ``go_release_early``.
There is one for each ``isolate_N`` demographic *except* for the
demographic to which individuals will be moved on each day.

This ``go_release_early`` function moves a fraction of individuals from
the ``isolate_N`` demographic to ``released``, representing that fraction
breaking their quarantine early. This fraction is taken from the list
``leave_early``, which counts down from ``0.5`` to ``0.0``. The first value
(``0.5``) is the fraction for individuals that have been isolating the longest
(six days), and the last value (``0.0``) is the fraction for the individuals
who only entered isolation the previous day.

These ``go_release_early`` functions are added before ``go_released``
and ``go_isolate_day``.

Now run ``metawards`` using your ``move_isolate.py`` via;

.. code-block:: bash

   metawards -d lurgy4 -D demographics.json -a ExtraSeedsLondon.dat --mixer mix_isolate --mover move_isolate --nsteps 365

You should see that the disease spreads, now both from individuals who
choose not to self-isolate, and now also from individuals who break
their quarantine early.

