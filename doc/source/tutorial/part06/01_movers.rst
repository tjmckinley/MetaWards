=======================
Movers and go functions
=======================

Demographics in ``metawards`` are a powerful concept that enables the
modelling of a wide variety of different scenarios. Just as *work*
and *play* have very general meanings in ``metawards``, so to do
*demographics*. We use it to mean any group of individuals. It is fluid,
in the sense that an individual can move between different demographics
during a *model run*, with the constraint that they can only belong
to one demographic at a time.

Demographic for self-isolation
------------------------------

Individuals are moved between demographics during a model run using
:doc:`mover functions <../../api/index_MetaWards_movers>`. These are
plugins that return the ``go functions`` that are used to make individuals
go from one demographic to another.

This is best demonstrated by example. In this example we will use
demographics to model the effect of self-isolation or
quarantine during an outbreak.

First, create a new ``demographics.json`` file that contains;

::

    {
        "demographics" : ["home", "isolate", "released"],
        "work_ratios"  : [ 1.0,      0.0,       0.0    ],
        "play_ratios"  : [ 1.0,      0.0,       0.0    ]
    }

This specifies three demographics:

1. ``home`` - this holds the entire population and represents individuals
   behaving "normally", e.g. continuing to *work* and *play*.
2. ``isolate`` - this currently has no members. We will use this demographic
   to represent individuals who are self-isolating or in quarantine, e.g.
   they will not *work* or *play* and will not contribute to the
   force of infection of their home ward.
3. ``released`` - this currently has no members. We will use this demographic
   to represent individuals who have been released from self-isolation or
   quarantine. They will be free to resume their normal behaviour, e.g.
   they wil return to *work* and *play*.

Moving individuals to isolation
-------------------------------

Next, create a custom :doc:`move function <../../api/index_MetaWards_movers>`
called ``move_isolate`` by creating a file called ``move_isolate.py``
and copying in the below;

.. code-block:: python

    from metawards.movers import go_isolate

    def move_isolate(**kwargs):
        func = lambda **kwargs: go_isolate(go_from="home",
                                           go_to="isolate",
                                           release_to="released",
                                           self_isolate_stage=2,
                                           duration=7,
                                            **kwargs)

        return [func]

This defines a custom :doc:`move function <../../api/index_MetaWards_movers>`
called ``move_isolate``. This returns the
``go function`` :meth:`~metawards.movers.go_isolate` that is
provided in :mod:`metawards.movers`. This
:meth:`~metawards.movers.go_isolate` function scans through the
demographics idenfied by ``go_from`` to search for individuals who
are showing signs of infection, i.e. individuals in a disease stage
that is greater or equal to ``self_isolate_stage``.

:meth:`~metawards.movers.go_isolate` moves these infected individuals
from their existing demographic into the new demographic identified
by ``go_to``. Individuals are held here for ``duration`` days, before
being released to the demographic identified by ``release_to``.

This go function has several parameters that must be set before it
can be returned by ``move_isolate``. We set these parameters by using
`lambda <https://chryswoods.com/parallel_python/lambda.html>`__ to create
a new anonymous go function where those arguments are bound to fixed
values.

.. note::
   Here is a `good explanation of lambda and argument binding <https://chryswoods.com/parallel_python/lambda.html>`__
   if you've never seen this before. In this case we have bound
   ``go_from`` to equal ``"home"``, ``go_to`` to equal ``"isolate"``,
   ``release_to`` to equal ``"released"``, ``self_isolate_stage`` to equal
   ``2`` and ``duration`` to equal ``7``. This means that these values
   will be used every time the ``go_isolate`` function returned
   from ``move_isolate`` is called.

Mixing without infection
------------------------

Next, create a :doc:`mixer <../api/index_MetaWards_mixers>` in
``mix_isolate.py`` and copy in the below;

.. code-block:: python

    from metawards.mixers import merge_using_matrix

    def mix_isolate(network, **kwargs):

        matrix = [ [1.0, 0.0, 1.0],
                   [0.0, 0.0, 0.0],
                   [1.0, 0.0, 1.0] ]

        network.demographics.interaction_matrix = matrix

        return [merge_using_matrix]

This mixer specifies an interaction matrix that merges the FOIs evenly
between the ``home`` and ``released`` demographics, while preventing
any contribution to FOI from individuals in the ``isolate`` demographic.
This includes turning off all interactions between isolated individuals,
hence why ``matrix[1][1] == 0``.

Running the model
-----------------

You can run the simulation by passing in your custom mover using the
``--mover`` command line argument, and your custom mixer using the
``--mixer`` command line argument. We will seed the infection using
``ExtraSeedsBrighton.dat`` and will use the parameters from ``lurgy3.json``
which you should copy into this directory. Run the job using;

.. code-block:: bash

   metawards -d lurgy3 -D demographics.json -a ExtraSeedsBrighton.dat --mover move_isolate --mixer mix_isolate

.. note::
   Note that we are using the ``lurgy3`` parameters that were
   :doc:`optimised earlier <../part02/05_refining>`. These include the
   long-lived asymptomatic but infectious stage 3 of the disease.

You should see a trajectory that looks something like this;

::

    S: 56082077  E: 0  I: 0  R: 0  IW: 0  POPULATION: 56082077
        home  S: 56082077  E: 0  I: 0  R: 0  IW: 0  POPULATION: 56082077
     isolate  S:        0  E: 0  I: 0  R: 0  IW: 0  POPULATION:        0
    released  S:        0  E: 0  I: 0  R: 0  IW: 0  POPULATION:        0

    0 0

    seeding demographic 0 play_infections[0][2124] += 5
    S: 56082072  E: 5  I: 0  R: 0  IW: 0  POPULATION: 56082077
        home  S: 56082072  E: 5  I: 0  R: 0  IW: 0  POPULATION: 56082077
     isolate  S:        0  E: 0  I: 0  R: 0  IW: 0  POPULATION:        0
    released  S:        0  E: 0  I: 0  R: 0  IW: 0  POPULATION:        0

    1 0

    S: 56082072  E: 0  I: 5  R: 0  IW: 0  POPULATION: 56082077
        home  S: 56082072  E: 0  I: 5  R: 0  IW: 0  POPULATION: 56082077
     isolate  S:        0  E: 0  I: 0  R: 0  IW: 0  POPULATION:        0
    released  S:        0  E: 0  I: 0  R: 0  IW: 0  POPULATION:        0

    2 5

    S: 56082072  E: 0  I: 5  R: 0  IW: 0  POPULATION: 56082077
        home  S: 56082072  E: 0  I: 0  R: 0  IW: 0  POPULATION: 56082072
     isolate  S:        0  E: 0  I: 5  R: 0  IW: 0  POPULATION:        5
    released  S:        0  E: 0  I: 0  R: 0  IW: 0  POPULATION:        0

    3 5

    S: 56082072  E: 0  I: 5  R: 0  IW: 0  POPULATION: 56082077
        home  S: 56082072  E: 0  I: 0  R: 0  IW: 0  POPULATION: 56082072
     isolate  S:        0  E: 0  I: 5  R: 0  IW: 0  POPULATION:        5
    released  S:        0  E: 0  I: 0  R: 0  IW: 0  POPULATION:        0

    4 5

    S: 56082072  E: 0  I: 2  R: 3  IW: 0  POPULATION: 56082077
        home  S: 56082072  E: 0  I: 0  R: 0  IW: 0  POPULATION: 56082072
     isolate  S:        0  E: 0  I: 2  R: 3  IW: 0  POPULATION:        5
    released  S:        0  E: 0  I: 0  R: 0  IW: 0  POPULATION:        0

    5 5

    S: 56082072  E: 0  I: 2  R: 3  IW: 0  POPULATION: 56082077
        home  S: 56082072  E: 0  I: 0  R: 0  IW: 0  POPULATION: 56082072
     isolate  S:        0  E: 0  I: 2  R: 3  IW: 0  POPULATION:        5
    released  S:        0  E: 0  I: 0  R: 0  IW: 0  POPULATION:        0

    6 2

    S: 56082072  E: 0  I: 1  R: 4  IW: 0  POPULATION: 56082077
        home  S: 56082072  E: 0  I: 0  R: 0  IW: 0  POPULATION: 56082072
     isolate  S:        0  E: 0  I: 1  R: 4  IW: 0  POPULATION:        5
    released  S:        0  E: 0  I: 0  R: 0  IW: 0  POPULATION:        0

    7 2

    S: 56082072  E: 0  I: 0  R: 5  IW: 0  POPULATION: 56082077
        home  S: 56082072  E: 0  I: 0  R: 0  IW: 0  POPULATION: 56082072
     isolate  S:        0  E: 0  I: 0  R: 5  IW: 0  POPULATION:        5
    released  S:        0  E: 0  I: 0  R: 0  IW: 0  POPULATION:        0

The infection was seeded with five individuals on day 1. They had a
latent infection for a day (``E == 5``), before developing symptoms
on day 2 (``I == 5``). At the beginning of day 3 then were moved
into the ``isolate`` demographic, in which they were unable to
infect others, and so progressed through the disease until they had
all recovered by day 8.

The asymptomatic stage
----------------------

Self-isolation appeared to have worked well. However, we neglected
to account for the asymptomatic ``stage 3`` of the lurgy. We modelled
the disease such that symptoms only appeared in stage 3, but individuals
were infectious from stage 2. We need to update our ``move_isolate`` function
so that individuals only self-isolate at stage 3, when they realise
that they have symptoms. Edit ``move_isolate.py`` and change it to read;

.. code-block:: python

    from metawards.movers import go_isolate

    def move_isolate(**kwargs):
        func = lambda **kwargs: go_isolate(go_from="home",
                                           go_to="isolate",
                                           release_to="released",
                                           self_isolate_stage=3,
                                           duration=7,
                                            **kwargs)

        return [func]

(we have just changed ``self_isolate_stage`` from ``2`` to ``3``).

Now run ``metawards`` again using;

.. code-block:: bash

   metawards -d lurgy3 -D demographics.json -a ExtraSeedsBrighton.dat --mover move_isolate --mixer mix_isolate


