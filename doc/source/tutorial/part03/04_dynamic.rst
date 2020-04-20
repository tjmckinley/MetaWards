=================================
Responding to changing conditions
=================================

We've now created a lock-down advance function, but are currently
triggering this function in an iterator based on a fixed number
of days since the outbreak started.

A better approach would be to trigger the lock-down based on the
number of individuals who are detected as infected in the model.

To do this, edit your ``lockdown.py`` script and copy in the following;

.. code-block:: python

  from metawards.iterators import iterate_working_week, \
                                  advance_infprob, \
                                  advance_fixed, \
                                  advance_play

  def advance_lockdown(**kwargs):
      print("We are on lockdown")
      advance_infprob(scale_rate=0.25, **kwargs)
      advance_play(**kwargs)

  def iterate_lockdown(population, **kwargs):
      if not hasattr(population, "lockdown_state"):
          population.lockdown_state = "before"
          population.is_locked_down = False

      if population.lockdown_state == "before":
          if population.total > 5000:
              population.lockdown_state = "lockdown"
              population.lockdown_started = population.day
              population.is_locked_down = True

      if population.is_locked_down:
          return [advance_lockdown]
      else:
          return iterate_working_week(population=population,
                                      **kwargs)

The first thing we do here is see if the ``population`` has a
``lockdown_state`` variable using the standard Python
`hasattr function <https://docs.python.org/3/library/functions.html#hasattr>`__.
This variable won't exist on the first call to
to ``iterate_lockdown``, and so here we
set the ``lockdown_state`` to ``before``
and set the flag ``population.is_locked_down`` to ``False``.

Next, we check if the lockdown is in the ``before`` state. If it is,
then if the total infected population is greater than 5000 we change
the ``lockdown_state`` to ``lockdown``, save the day the lockdown
started to ``population.lockdown_started``, and set the flag
``population.is_locked_down`` to ``True``.

Finally, we either return our ``advance_lockdown`` advance function,
or the standard advance functions for a working week depending
on the value of the ``population.is_locked_down`` flag.

Run the model and draw the overview graph using;

.. code-block:: bash

  metawards -d lurgy3 --additional ExtraSeedsLondon.dat --iterator lockdown
  metawards-plot -i output/results.csv.bz2 --format jpg --dpi 150

You should now see that the lockdown takes effect some time after the
infected population grows above 5000. This tips the curve and reduces
the spread of the disease. You can see what my graphs looked like here;

.. image:: ../../images/tutorial_3_4_1_overview.jpg
   :alt: Overview image of a automatic lockdown

Releasing lockdown
------------------

We can use the data in ``population`` to decide when to release the
lockdown as well. For example, we could release when the size of the
infected population drops below 2000. To do this, edit your ``lockdown.py``
file to read;

.. code-block:: python

  from metawards.iterators import iterate_working_week, \
                                  advance_infprob, \
                                  advance_fixed, \
                                  advance_play

  def advance_lockdown(**kwargs):
      print("We are on lockdown")
      advance_infprob(scale_rate=0.25, **kwargs)
      advance_play(**kwargs)

  def iterate_lockdown(population, **kwargs):
      if not hasattr(population, "lockdown_state"):
          population.lockdown_state = "before"
          population.is_locked_down = False

      if population.lockdown_state == "before":
          if population.total > 5000:
              population.lockdown_state = "lockdown"
              population.lockdown_started = population.day
              population.is_locked_down = True

      elif population.lockdown_state == "lockdown":
          if population.total < 2000:
              population.lockdown_state = "after"
              population.lockdown_ended = population.day
              population.is_locked_down = False

      if population.is_locked_down:
          return [advance_lockdown]
      else:
          return iterate_working_week(population=population,
                                      **kwargs)

Run the model as before and see what happens...

To start, the lockdown has worked and the number of infections has fallen.
However, the lockdown has been released completely once the number of
infections fell below 2000. This meant that there were still lots of
infected individuals with a large susceptible population. Unsurprisingly,
the infection quickly grew again, e.g. as seen in the print out from
my run here;

::

    79 2360
    S: 56044530    E: 167    I: 2087    R: 35293    IW: 138   TOTAL POPULATION 56081910
    We are on lockdown

    80 2254
    S: 56044384    E: 143    I: 2003    R: 35547    IW: 144   TOTAL POPULATION 56081934
    We are on lockdown

    81 2146
    S: 56044232    E: 146    I: 1878    R: 35821    IW: 147   TOTAL POPULATION 56081931

    82 2024
    S: 56043435    E: 152    I: 1792    R: 36698    IW: 706   TOTAL POPULATION 56081925

    83 1944
    S: 56042700    E: 797    I: 1708    R: 36872    IW: 655   TOTAL POPULATION 56081280

    84 2505
    S: 56042027    E: 735    I: 2277    R: 37038    IW: 600   TOTAL POPULATION 56081342

    85 3012
    S: 56041403    E: 673    I: 2806    R: 37195    IW: 570   TOTAL POPULATION 56081404

    86 3479
    S: 56040636    E: 624    I: 3286    R: 37531    IW: 691   TOTAL POPULATION 56081453

    87 3910
    S: 56039299    E: 767    I: 3683    R: 38328    IW: 1138   TOTAL POPULATION 56081310

    88 4450
    S: 56037905    E: 1337    I: 4205    R: 38630    IW: 1196   TOTAL POPULATION 56080740

    89 5542
    S: 56036337    E: 1394    I: 5221    R: 39125    IW: 1320   TOTAL POPULATION 56080683

Relaxing, not removing lockdown
-------------------------------

The problem is that we treated lockdown like a binary switch, and
immediately went back to normal once it was lifted.

Instead, we need to release the lockdown in stages. To model this,
edit your ``lockdown.py`` to contain the following.

.. code-block:: python

    from metawards.iterators import iterate_working_week, \
                                    advance_infprob, \
                                    advance_fixed, \
                                    advance_play

    def advance_lockdown(population, **kwargs):
        print(f"We are on lockdown ({population.lockdown_scale_rate})")
        advance_infprob(scale_rate=population.lockdown_scale_rate,
                        **kwargs)
        advance_play(population=population, **kwargs)

    def iterate_lockdown(population, **kwargs):
        try:
            population.lockdown_state
        except Exception:
            population.lockdown_state = "before"
            population.is_locked_down = False
            population.lockdown_scale_rate = 0.25

        if population.lockdown_state == "before":
            if population.total > 5000:
                population.lockdown_state = "lockdown"
                population.lockdown_started = population.day
                population.is_locked_down = True

        elif population.lockdown_state == "lockdown":
            if population.total < 2000:
                population.lockdown_state = "relaxed_lockdown"
                population.lockdown_ended = population.day
                population.lockdown_scale_rate = 0.5
                population.is_locked_down = True

        elif population.lockdown_state == "relaxed_lockdown":
            if population.total < 1000:
                population.lockdown_scale_rate = 0.75
            else:
                population.lockdown_scale_rate = 0.5

        if population.is_locked_down:
            return [advance_lockdown]
        else:
            return iterate_working_week(population=population,
                                        **kwargs)

In this code we have created a new lockdown state that we've called
``relaxed_lockdown``. This is entered when the number of infections
drops below 2000. In this state controls can be released that
correspond to now only halving the infection rate (``scale_rate``
is increased to 0.5 from 0.25 during the strong lockdown).
In the ``relaxed_lockdown`` state the infected population
is always checked. If it is below 1000 then the lockdown can be
relaxed even more, with the ``scale_rate`` increasing from 0.5
to 0.75. However, if the infected population rises above 1000,
then the lockdown is tightened and the ``scale_rate`` is lowered
again to 0.5.

Have a go at running using this iterator. What do you see? In my
case I see the model moving from lockdown (``scale_factor==0.25``),
through relaxed lockdown (``scale_factor==0.5``) to light
lockdown (``scale_factor==0.75``) during the outbreak, which
is brought under control. The overview plots are here;

.. image:: ../../images/tutorial_3_4_2_overview.jpg
   :alt: Overview image of a automatically relaxing lockdown

There is a small second peak as the lockdown is relaxed, but
this seems to be under control.

.. warning::
  Remember, we cannot read too much into single **model runs**
  as these are very stochastic simulations. We would need to
  run models many times and average before we could gain real
  insight.

Returning to work
-----------------

Because Python is dynamically typed, we can set whatever flags
or add whatever data we want to the ``population`` object that
we need (or indeed to any Python object).

Let's now add an extra flag that will be used by
``advance_lockdown`` to call ``advance_fixed`` if the lockdown
has been lifted sufficiently for people to return to work.
Copy the below into your ``lockdown.py`` file;

.. code-block:: python

    from metawards.iterators import iterate_working_week, \
                                    advance_infprob, \
                                    advance_fixed, \
                                    advance_play

    def advance_lockdown(population, **kwargs):
        print(f"We are on lockdown ({population.lockdown_scale_rate})")
        print(f"is_work_locked_down == {population.is_work_locked_down}")
        advance_infprob(scale_rate=population.lockdown_scale_rate,
                        **kwargs)

        advance_play(population=population, **kwargs)

        if not population.is_work_locked_down:
            advance_fixed(population=population, **kwargs)

    def iterate_lockdown(population, **kwargs):
        try:
            population.lockdown_state
        except Exception:
            population.lockdown_state = "before"
            population.is_locked_down = False
            population.lockdown_scale_rate = 0.25
            population.is_work_locked_down = False

        if population.lockdown_state == "before":
            if population.total > 5000:
                population.lockdown_state = "lockdown"
                population.lockdown_started = population.day
                population.is_locked_down = True
                population.is_work_locked_down = True

        elif population.lockdown_state == "lockdown":
            if population.total < 2000:
                population.lockdown_state = "relaxed_lockdown"
                population.lockdown_ended = population.day
                population.lockdown_scale_rate = 0.5
                population.is_locked_down = True
                population.is_work_locked_down = False

        elif population.lockdown_state == "relaxed_lockdown":
            population.is_work_locked_down = False

            if population.total < 1000:
                population.lockdown_scale_rate = 0.75
            else:
                population.lockdown_scale_rate = 0.5

        if population.is_locked_down:
            return [advance_lockdown]
        else:
            return iterate_working_week(population=population,
                                        **kwargs)

This is getting longer, but I hope you can see that all we have
added is a ``population.is_work_locked_down`` flag, plus some
extra code to flip this between ``True`` and ``False``. This flag
is read by ``advance_lockdown``, which calls ``advance_fixed``
if the flag is ``False``.

Run the model and plot the graphs. What do you see?

For me, again I see smooth movement between the different lockdown
stages. However, the peak after entering the relaxed lockdown
state is much higher, possibly because more infected people are
able to move between wards.

.. image:: ../../images/tutorial_3_4_3_overview.jpg
   :alt: Overview image of a automatically relaxing lockdown
