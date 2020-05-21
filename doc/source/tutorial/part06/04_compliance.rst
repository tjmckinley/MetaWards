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

   The move function

Scan compliance for going into isolation.

Breaking quarantine early
-------------------------

Now do the same for leaving quarantine. Scan the compliance fraction.
