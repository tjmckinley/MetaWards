====================
Adjustable Variables
====================

We have now adjusted the **disease file** for the lurgy, which has
resulted in a *model run* that has involved a larger section of the
population in the disease outbreak. However, the values we chose
for the parameters in the **disease file** were made up. They had
no basis in reality, which means that it is difficult to use this
model to make good predictions.

``metawards`` is designed to support parameter searches that seek to
adjust the disease parameters so that predictions from *model runs*
can be matched to observed reality. The idea is that variables are
adjusted until the *model runs* can reliably capture the observed
behaviour of an outbreak, at which point the model may then act
as a good prediction of the future.

Choosing what to adjust
-----------------------

In the last section we introduced a new stage to the lurgy in which
infected individuals were very mobile (**too_ill_to_move** was 0.0),
but also very infectious (**beta** was 0.5).

This was introduced as stage 3 of the lurgy. We need therefore to tune
the **beta[2]** and **too_ill_to_move[2]** parameters (remembering that
we count from zero). What we want to do is vary these two parameters
and see how they affect the model outbreak.

To do this, in your current directory create a file called ``lurgyparams.csv``
and copy in the text below;

::

  beta[2]  too_ill_to_move[2]
    0.3         0.00
    0.4         0.00
    0.5         0.00
    0.3         0.25
    0.4         0.25
    0.5         0.25
    0.3         0.50
    0.4         0.50
    0.5         0.50

This file has two columns of numbers; ``beta[2]`` which shows how to
adjust the **beta[2]** value, and ``too_ill_to_move[2]`` which shows
how to adjust the **too_ill_to_move[2]** value. Each row of this file
represents a single model run using this pair of values. For example,
the line ``0.3       0.00`` will set **beta[2]** to 0.3 and
**too_ill_to_move[2]** to 0.0.

.. note::
   The format of this file is very flexible. Columns can be space-separated
   or comma-separated, as long as this is consistent in the entire file.
   You can choose to adjust any of the parameters for any stage
   of a disease. Simply title the column with the parameter name, e.g.
   ``beta``, ``progress``, ``too_ill_to_move`` or ``contrib_foi``, and
   add the stage number in square brackets, e.g. ``beta[0]``. Remember
   that we count from zero, so stage one has index zero.

You can pass ``metawards`` this input file using the ``--input``
(or ``-i``) command-line option. This input file has nine pairs
of values of **beta[2]** and **too_ill_to_move[2]**, which means that
nine *model runs* need to be performed. To run them all, use this command;

.. code-block:: bash

   metawards -d lurgy2 -a ExtraSeedsLondon.dat --input lurgyparams.csv

This will run all nine jobs. If you have nine or more processor cores
on your computer then all of them will be run in parallel (with
individual *model runs* then using any other cores you have). If, like me,
you are running this on your laptop, then this may take 10+ minutes
to complete.

.. note::
  If you want to distribute this work over a set of disconnected
  computers, you can tell ``metawards`` to only adjust parameters
  from a subset of the lines of the input file. To do this,
  use the ``--line`` (or ``-l``) command line argument to specify
  the line or lines to process. Lines are counted from 0 being the
  top line (containing the header), and multiple lines or ranges
  can be specified, e.g. ``-l 1 2 3`` will use lines one to three,
  while ``-l 4-6`` would use lines four to six (inclusive).

.. warning::
  We are only going to use one repeat of each pair of values, which means
  that our results will suffer from a lot of random error. Ideally you
  should ask for multiple repeats using the ``--repeats`` command-line
  argument. A good value would be at least eight repeats. In this case,
  eight repeats would require 72 *model runs*. If you parallelise
  each run over 16 cores then this needs 1152 cores. Fortunately, for
  these jobs, ``metawards`` runs well in parallel
  :doc:`across a slurm or PBS cluster <../../cluster_usage>`.

Once the jobs are complete (which took 14 minutes on my laptop), you
should have output that looks similar to this;

::

  ******************************************
  *** To repeat this job use the command ***
  ******************************************

  metawards --input lurgyparams.csv --repeats 1 --seed 91914880 --additional ExtraSeedsLondon.dat --output output --UV 1.0 --disease lurgy2 --input-data 2011Data --start-date 2020-04-16 --start-day 0 --parameters march29 --repository /Users/chris/GitHub/MetaWardsData --population 57104043 --nthreads 1 --nprocs 4

  [truncated]

  Running 9 jobs using 4 process(es)

  Running jobs in parallel using a multiprocessing pool...

  Completed job 1 of 9
  (beta[2]=0.3, too_ill_to_move[2]=0.0)[repeat 1]
  2020-10-08: DAY: 175 S: 49712306    E: 0    I: 0    R: 6369771    IW: 0   TOTAL POPULATION 56082077

  Completed job 2 of 9
  (beta[2]=0.4, too_ill_to_move[2]=0.0)[repeat 1]
  2020-10-11: DAY: 178 S: 46830767    E: 0    I: 0    R: 9251310    IW: 0   TOTAL POPULATION 56082077

  Completed job 3 of 9
  (beta[2]=0.5, too_ill_to_move[2]=0.0)[repeat 1]
  2020-10-08: DAY: 175 S: 41378523    E: 0    I: 0    R: 14703554    IW: 0   TOTAL POPULATION 56082077

  Completed job 4 of 9
  (beta[2]=0.3, too_ill_to_move[2]=0.25)[repeat 1]
  2020-10-04: DAY: 171 S: 50270319    E: 0    I: 0    R: 5811758    IW: 0   TOTAL POPULATION 56082077

  Completed job 5 of 9
  (beta[2]=0.4, too_ill_to_move[2]=0.25)[repeat 1]
  2020-10-05: DAY: 172 S: 46273205    E: 0    I: 0    R: 9808872    IW: 0   TOTAL POPULATION 56082077

  Completed job 6 of 9
  (beta[2]=0.5, too_ill_to_move[2]=0.25)[repeat 1]
  2020-10-10: DAY: 177 S: 38072220    E: 0    I: 0    R: 18009857    IW: 0   TOTAL POPULATION 56082077

  Completed job 7 of 9
  (beta[2]=0.3, too_ill_to_move[2]=0.5)[repeat 1]
  2020-10-18: DAY: 185 S: 49083442    E: 0    I: 0    R: 6998635    IW: 0   TOTAL POPULATION 56082077

  Completed job 8 of 9
  (beta[2]=0.4, too_ill_to_move[2]=0.5)[repeat 1]
  2020-10-07: DAY: 174 S: 44759456    E: 0    I: 0    R: 11322621    IW: 0   TOTAL POPULATION 56082077

  Completed job 9 of 9
  (beta[2]=0.5, too_ill_to_move[2]=0.5)[repeat 1]
  2020-10-09: DAY: 176 S: 49969606    E: 0    I: 0    R: 6112471    IW: 0   TOTAL POPULATION 56082077

  Writing a summary of all results into the
  csv file /Users/chris/GitHub/tutorial/output/results.csv.bz2.
