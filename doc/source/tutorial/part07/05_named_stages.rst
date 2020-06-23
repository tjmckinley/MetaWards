====================
Named Disease Stages
====================

In the last section you learned how to use demographics with different
disease stages to model hospital and ICU admissions. While this worked,
the calculation of statistics from the simulation was slightly hacky,
as the disease stages were still labelled ``E``, ``I`` and ``R``, when
we really wanted to refer to them as ``H1``, ``H2`` etc.

Fortunately, ``metawards`` supports custom naming of disease stages.
You can do this by adding a ``stage`` field to the disease file.

Simple example
--------------

For example, here is a simple disease file that uses stages ``A``,
``B`` and ``C``. Please create the file ``named.json`` and copy in the
below;

::

    {
        "stage"            : [ "A", "B", "C" ],
        "beta"             : [ 0.0, 0.5, 0.0 ],
        "progress"         : [ 1.0, 1.0, 0.0 ],
        "too_ill_to_move"  : [ 0.0, 0.0, 0.0 ],
        "contrib_foi"      : [ 1.0, 1.0, 0.0 ],
        "start_symptom"    : 1
    }

.. note::

   Note that we've not included the ``name``, ``author`` or other metadata
   fields as these are not needed for this simple example. These are optional
   fields. We recommend you include them when you want to publish a disease
   file.

This file defines three disease stages, called ``A``, ``B`` and ``C``.
The first stage (``A``) is not infectious, as ``beta["A"]`` is ``0.0``.
The infectious stage is ``B``, as ``beta["B"]`` is ``0.5``. The final
stage is ``C``, which is not infectious, and is where the disease ends
(``progress["C"]`` is ``0.0``).

Run ``metawards`` using this disease file via;

.. code-block:: bash

   metawards -a ExtraSeedsLondon.dat -d named.json --nsteps 20

You should see output similar to;

::

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Day 0 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Loading additional seeds from /Users/chris/GitHub/MetaWardsData/extra_seeds/ExtraSeedsLondon.dat
    (1, 255, 5, None)
    S: 56082077  A: 0  B: 0  C: 0  IW: 0  POPULATION: 56082077

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Day 1 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    seeding play_infections[0][255] += 5
    S: 56082072  A: 0  B: 5  C: 0  IW: 0  POPULATION: 56082077
    Number of infections: 5

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Day 2 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    S: 56082067  A: 5  B: 0  C: 5  IW: 2  POPULATION: 56082077
    Number of infections: 10

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Day 3 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    S: 56082067  A: 0  B: 5  C: 5  IW: 0  POPULATION: 56082077
    Number of infections: 10

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Day 4 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    S: 56082063  A: 4  B: 0  C: 10  IW: 3  POPULATION: 56082077
    Number of infections: 14

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Day 5 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    S: 56082063  A: 0  B: 4  C: 10  IW: 0  POPULATION: 56082077
    Number of infections: 14

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Day 6 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    S: 56082062  A: 1  B: 0  C: 14  IW: 1  POPULATION: 56082077
    Number of infections: 15

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Day 7 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    S: 56082062  A: 0  B: 1  C: 14  IW: 0  POPULATION: 56082077
    Number of infections: 15

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Day 8 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    S: 56082062  A: 0  B: 0  C: 15  IW: 0  POPULATION: 56082077
    Number of infections: 15

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Day 9 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    S: 56082062  A: 0  B: 0  C: 15  IW: 0  POPULATION: 56082077
    Number of infections: 15

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Day 10 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    S: 56082062  A: 0  B: 0  C: 15  IW: 0  POPULATION: 56082077
    Number of infections: 15

.. note::

   Note that the simulation gets stuck in the ``C`` state. This is because
   any individual who is not in ``S`` or ``R`` is counted as an infection,
   and so the 15 individuals in ``C`` are counted as infecteds. To prevent
   the model running forever we set the maximum number of days to
   20 via ``--nsteps 20``.

As you can see, the output now records movement from ``S`` to ``A``, ``B``
and then ``C``. This data is also recorded in the output files, e.g.

.. code-block:: python

   >> import pandas as pd
   >> df = pd.read_csv("output/results.csv.bz2")
   >> df.head()
      fingerprint  repeat  day        date         S  E  I  A  B   C  R  IW   UV
    0      REPEAT       1    0  2020-06-23  56082077  0  0  0  0   0  0   0  1.0
    1      REPEAT       1    1  2020-06-24  56082072  0  0  0  5   0  0   0  1.0
    2      REPEAT       1    2  2020-06-25  56082067  0  0  5  0   5  0   2  1.0
    3      REPEAT       1    3  2020-06-26  56082067  0  0  0  5   5  0   0  1.0
    4      REPEAT       1    4  2020-06-27  56082063  0  0  4  0  10  0   3  1.0
   >> df = pd.read_csv("output/trajectory.csv.bz2")
   >> df.head()
       day        date demographic         S  E  I  A  B   C  R  IW
    0    0  2020-06-23     overall  56082077  0  0  0  0   0  0   0
    1    1  2020-06-24     overall  56082072  0  0  0  5   0  0   0
    2    2  2020-06-25     overall  56082067  0  0  5  0   5  0   2
    3    3  2020-06-26     overall  56082067  0  0  0  5   5  0   0
    4    4  2020-06-27     overall  56082063  0  0  4  0  10  0   3

Additional columns have been added to the tables in these files for the
``A``, ``B`` and ``C`` states.

Sub-stages example
------------------

You can have multiple named sub-stages of each stage, e.g. instead of
having a single infectious ``B`` stage, you can have ``B1``, ``B2`` and
``B3``. The totals reported for a the ``B`` stage will be the sum of
the number of individuals in each sub-stage. For example, edit
``named.json`` to read;

::

    {
        "stage"            : [ "A", "B1", "B2", "B3", "C" ],
        "beta"             : [ 0.0, 0.2,  0.8,  0.1,  0.0 ],
        "progress"         : [ 1.0, 1.0,  1.0,  1.0,  0.0 ],
        "too_ill_to_move"  : [ 0.0, 0.0,  0.2,  0.8,  0.0 ],
        "contrib_foi"      : [ 1.0, 1.0,  1.0,  1.0,  0.0 ],
        "start_symptom"    : 1
    }

Here we've expanded the ``B`` stage into three infectious sub-stages
(``B1``, ``B2`` and ``B3``), similar to the three stages of the lurgy.

Run ``metawards`` using this disease file via;

.. code-block:: bash

   metawards -a ExtraSeedsLondon.dat -d named.json --nsteps 20

You should see in the output that the population of ``A``, ``B`` and ``C``
are summarised, e.g.

::

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Day 0 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Loading additional seeds from /Users/chris/GitHub/MetaWardsData/extra_seeds/ExtraSeedsLondon.dat
    (1, 255, 5, None)
    S: 56082077  A: 0  B: 0  C: 0  IW: 0  POPULATION: 56082077

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Day 1 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    seeding play_infections[0][255] += 5
    S: 56082072  A: 0  B: 5  C: 0  IW: 0  POPULATION: 56082077
    Number of infections: 5

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Day 2 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    S: 56082071  A: 1  B: 5  C: 0  IW: 1  POPULATION: 56082077
    Number of infections: 6

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Day 3 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    S: 56082067  A: 4  B: 6  C: 0  IW: 4  POPULATION: 56082077
    Number of infections: 10

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Day 4 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    S: 56082066  A: 1  B: 5  C: 5  IW: 1  POPULATION: 56082077
    Number of infections: 11

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Day 5 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    S: 56082064  A: 2  B: 6  C: 5  IW: 2  POPULATION: 56082077
    Number of infections: 13

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Day 6 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    S: 56082060  A: 4  B: 7  C: 6  IW: 4  POPULATION: 56082077
    Number of infections: 17

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Day 7 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    S: 56082058  A: 2  B: 7  C: 10  IW: 2  POPULATION: 56082077
    Number of infections: 19

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Day 8 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    S: 56082053  A: 5  B: 8  C: 11  IW: 4  POPULATION: 56082077
    Number of infections: 24

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Day 9 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    S: 56082053  A: 0  B: 11  C: 13  IW: 0  POPULATION: 56082077
    Number of infections: 24

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Day 10 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    S: 56082049  A: 4  B: 7  C: 17  IW: 4  POPULATION: 56082077
    Number of infections: 28

These are also summarised in the ``output/results.csv.bz2`` and
``output/trajectory.csv.bz2`` files.

However, the actual populations in each individual stage are given in the
``play_infections.csv.bz2`` (play infections), ``work_infections.csv.bz2``
(work infections) and ``number_infected_wards.csv.bz2`` (number of infected
wards) files, e.g.

.. code-block:: python

   >>> import pandas as pd
   >>> df = pd.read_csv("output/total_infections.csv.bz2")
   >>> df.head()
       day  A  B1  B2  B3  C
    0    1  0   5   0   0  0
    1    2  1   0   5   0  0
    2    3  4   1   0   5  0
    3    4  1   4   1   0  5
    4    5  2   1   4   1  5
   >>> df = pd.read_csv("output/number_infected_wards.csv.bz2")
   >>> df.head()
       day  A  B1  B2  B3  C
    0    1  0   1   0   0  0
    1    2  1   0   1   0  0
    2    3  4   1   0   1  0
    3    4  1   4   1   0  1
    4    5  2   1   4   1  1

These files are very useful if you want to see, e.g. how many workers
are infected at each different stage on each day, or how many wards
have a population infected in the ``B1`` state on each day.

