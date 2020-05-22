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
100%).

We can adjust this value to examine impact of reduced self-isolation
compliance on the outbreak.

To do this, update your ``move_isolate.py`` move function to;

.. code-block:: python

    from metawards import Population
    from metawards import Networks
    from metawards.movers import go_isolate, go_to

    def move_isolate(network: Networks, population: Population, **kwargs):
        user_params = network.params.user_params

        ndays = 7
        isolate_stage = 2
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

Here we have added ``compliance_fraction``, set to ``0.5`` so represent
50% of individuals complying with the need to go into self-isolation.
This fraction is passed as ``fraction`` to the ``go_isolate`` function.

Run ``metawards`` using;

.. code-block:: bash

   metawards -d lurgy4 -D demographics.json -a ExtraSeedsLondon.dat --mixer mix_isolate --mover move_isolate --nsteps 365

You should see that infection spreads slowly, as the 50% of individuals who
each day decide not to self-isolate from stage 2 of the lurgy infect the
susceptible population. A plot of the the demographics shows exponential
growth in the disease, e.g. via;

.. code-block:: bash

   metawards-plot -i output/trajectory.csv.bz2

.. image:: ../../images/tutorial_6_4_1.jpg
   :alt: Demographics for 50% self-isolation compliance

Breaking quarantine early
-------------------------

Compliance with self-isolation requests applies as much to remaining
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
        compliance_fraction = 0.5

        # fraction who leave early, counting from the longest to
        # shortest stay in isolation. 50% leave after 6 days, while
        # only 0% leave after 1 day
        leave_early = [0.5, 0.4, 0.3, 0.2, 0.1, 0.0]

        day = population.day % ndays
        isolate = f"isolate_{day}"

        funcs = []

        for i in range(1, ndays):
            quarantine = f"isolate_{(day + i) % ndays}"
            fraction_leave = leave_early[i-1]
            go_release_early = lambda **kwargs: go_to(go_from=quarantine,
                                                    go_to="released",
                                                    fraction=fraction_leave,
                                                    **kwargs)

            funcs.append(go_release_early)

        go_isolate_day = lambda **kwargs: go_isolate(
                                            go_from="home",
                                            go_to=isolate,
                                            self_isolate_stage=isolate_stage,
                                            fraction=compliance_fraction,
                                            **kwargs)

        go_released = lambda **kwargs: go_to(go_from=isolate,
                                            go_to="released",
                                            **kwargs)

        return funcs + [go_released, go_isolate_day]

Here, we've created a new set of go functions called ``go_release_early``.
There is one for each ``isolate_N`` demographic *except* for the
demographic to which individuals will be moved on each day.

This ``go_release_early`` function moves a fraction of individuals from
the ``isolate_N`` demographic to ``released``, representing that fraction
breaking their quarantine early. This fraction is taken from the list
``leave_early``, which counts down from ``0.5`` to ``0.0``. The first value
(``0.5``) is the fraction for individuals that have been isolating the longest
(6 days), and the last value (``0.0``) is the fraction for the individuals
who only entered isolation the previous day.

These ``go_release_early`` functions are added before ``go_released``
and ``go_isolate_day``.

Now run ``metawards`` using your ``move_isolate.py`` via;

.. code-block:: bash

   metawards -d lurgy4 -D demographics.json -a ExtraSeedsLondon.dat --mixer mix_isolate --mover move_isolate --nsteps 365

You should see that the disease spreads, now both from individuals who
choose not to self-isolate, and now also from individuals who break
their quarantine early.

