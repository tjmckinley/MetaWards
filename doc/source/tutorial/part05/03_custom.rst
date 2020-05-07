===============================================
Using custom merge functions to model shielding
===============================================

So far you have modelled multiple demographics, but they either
interacted fully with each other during an outbreak, or have
not interacted at all.

One of the benefits of using demographics is that we can model
different levels of interaction between different groups. To do
this, we will need to set up an interaction matrix between
demographics, and to call this via a custom mixer.

Interaction matrix
------------------

An interaction matrix specifies how much the *force of infection* (FOI)
calculated from one demographic influences another. It is an asymmetric
matrix, e.g. for our "red" and "blue" demographics it could be;

.. list-table::
   :widths: 30 35 35
   :header-rows: 1
   :stub-columns: 1

   * -
     - red
     - blue
   * - red
     - 0.2
     - 0.1
   * - blue
     - 0.8
     - 1.0

The diagonals of this matrix show how much infections in each demographic
affect that demographic, i.e. how easily the infection spreads within the
demographic. It is effectively equivalent to ``scale_uv``.
The top-left value (0.2) says that "red" demographic is adopting lockdown
measures that scale down the FOI between "red" individuals by 0.2.

In contrast, the bottom-right value (1.0) says that no measures are being
taken within the "blue" demographic, and the FOI calculated from infections
within that demographic are not scaled.

The top-left value (0.1) gives the amount by which the "red" demographic
affected by the "blue" demographic, i.e. how easily infections from the "blue"
demographic can be transmitted to the "red" demographic. This low value of
0.1 indicates that care is taken by members of the "blue" demographic to
not infect members of the "red" demographic.

The bottom-left value (0.8) is the reverse, namely how much the "blue"
demographic is affected by the "red" demographic, i.e. how easily infections
from the "red" demographic can be transmitted to the "blue" demographic.
The larger value of 0.8 indicates that the "blue" demographic are still
being infected by "red", e.g. perhaps because they are treating or caring
for members of that demographic.

The values in this matrix correspond to a potential shielding scenario,
whereby measures are taken by the "blue" demographic to shield the
"red" demographic from infection.

Custom mixers
-------------

We can use this interaction matrix by creating a custom mixer.
Create a file called ``shield.py`` and add the following;

.. code-block:: python

    from metawards.mixers import merge_using_matrix

    def mix_shield(network, **kwargs):
        matrix = [ [0.2, 0.1],
                   [0.8, 1.0] ]

        network.demographics.interaction_matrix = matrix

        return [merge_using_matrix]


You set the mixer to use using the `--mixer` flag, e.g. run ``metawards``
using;

.. code-block:: bash

   metawards -d lurgy2 -D demographics.json -a ExtraSeedsLondon.dat --mixer shield

You should see that, while the infection moves through most of the "blue"
demographic, it is relatively contained within the "red" demographic.

You can plot the trajectory using;

.. code-block:: bash

   metawards-plot -i output/trajectory.csv.bz2

You should see a plot similar to this;

.. image:: ../../images/tutorial_5_3_1_demographics.jpg
   :alt: Disease trajectory for a shielding scenario for the red demographic

Adjusting shielding parameters
------------------------------

This has worked well, in that the shielded "red" demographic has been
protected from the disease. However, using scaling factors of 0.2 and
0.1 is quite extreme, especially over the four months of the model
outbreak.

We can use adjustable parameters to investigate how much shielding is
needed to protect the "red" demographic. To do this, update your
``shield.py`` file to contain;

.. code-block:: python



.. code-block:: bash

   metawards -d lurgy2 -D demographics.json -a ExtraSeedsLondonBlue.dat --mixer shield --user-variables shield.inp -i scan.dat

