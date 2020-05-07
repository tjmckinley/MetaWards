==========================
Mixers and Merge-functions
==========================

In the last page you modelled outbreaks that were seeded either in
the "red" population, who were all "players", and the "blue" population,
which contained all of the "workers".

This resulted in two different outbreaks, which was understandable given
that only "workers" move between wards. One issue was that the demographics
were completely separate - infected individuals in the "red" population
couldn't infect individuals in the "blue" population and vice-versa.

This is because the :class:`~metawards.Network` for each demographic was
advanced independently, and no mixing took place.

Force of infection (FOI)
------------------------

Infected individuals in a ward contribute to the *force of infection* (FOI)
of that ward. The higher the FOI, the more likely it is that other
individuals in a ward will become infected.

The FOIs for each demographic sub-network is calculated independently,
based only on the infected individuals from that demographic. We can thus
use the FOI calculation as a way of enabling different demographics to
mix. We do this in ``metawards`` using custom functions, called
`~metawards.mixers`, that choose different "merge functions" that are
used to mix and merge calculations of FOIs across different demographics
together.

The default mixer is :func:`~metawards.mixers.mix_none`, which, as the
name suggests, performs no mixing between demographics.

Mix evenly
----------

An alternative is to use :func:`~metawards.mixers.mix_evenly`. This evenly
mixes all demographics. It sets the FOI in each ward in each demographic
equal to the sum of the FOIs in that ward across all demographics.

You can choose this mixer using the ``--mixer`` argument. Run ``metawards``
using;

.. code-block:: bash

  metawards -d lurgy2 -D demographics.json -a ExtraSeedsLondon.dat --mixer mix_evenly

You should now see that the outbreak spreads from the initial infection in
the "red" demographic to the "blue workers", who then spread it around
the country to both the "red" and "blue" groups. You can plot