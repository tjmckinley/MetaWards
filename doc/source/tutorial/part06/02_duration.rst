=======================
Self-isolation duration
=======================

In the last section we saw how self-isolation and a population that
took steps to reduce transmissability of the virus could dramatically
reduce the spread of the disease. However, in that model infected
individuals were moved into self-isolation for the entire duration
of the outbreak. This is clearly unrealistic.

Using demographics to represent days
------------------------------------

Typical advice to someone who is self-isolating is that they should
self-isolate for a set number of days. We can model this by using
different self-isolation demographics to represent the different
days that individuals start their self-isolation. For example,
if self-isolation was for seven days, then we could have a
self-isolation demographic for each day of the week. Once a week
is up, then the individuals who are self-isolating in that
day-demographic are released and moved to the "released" demographic.
Newly infected individuals for that day are then moved into
the now-empty day-demographic.

To do this, create a new demographics file called ``demographics.json``
and copy in the below;

::

    {
      "demographics" : ["home", "released",
                        "isolate_0", "isolate_1", "isolate_2",
                        "isolate_3", "isolate_4", "isolate_5",
                        "isolate_6" ],
      "work_ratios"  : [ 1.0, 0.0,
                         0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0 ],
      "play_ratios"  : [ 1.0, 0.0,
                         0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0 ]
    }

This creates the ``home`` demographic, plus one ``isolate`` demographic
for each day of the week. There is also a ``released`` demographic
that will be used to release individuals from self-isolation.

We start with all individuals placed into the ``home`` demographic. We will
now write a custom move function that will move individuals into the
assigned ``isolate_N`` demographic for the day in which they develop
symptoms. This move function will move them into the ``released`` demographic
once they have spent seven days in self-isolation. To do this,
create a move function called ``move_isolate.py`` and copy in the below;

.. code-block:: python



