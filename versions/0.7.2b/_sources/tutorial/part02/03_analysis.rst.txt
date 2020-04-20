====================
Analysing the output
====================

The ``results.csv.bz2`` file contains all of the population trajectories
from the nine model runs. You can explore this using Python pandas, R,
or Excel :doc:`as you did before <../part01/02_repeating>`. Using
ipython or Jupyter notebooks with pandas, we can load up the file;

.. code-block:: python

   >>> import pandas as pd
   >>> df = pd.read_csv("output/results.csv.bz2")
   >>> print(df)
          fingerprint  repeat  beta[2]  too_ill_to_move[2]  day  ...         S  E  I        R  IW
     0            3_0       1      0.3                 0.0    0  ...  56082077  0  0        0   0
     1            3_0       1      0.3                 0.0    1  ...  56082077  0  0        0   0
     2            3_0       1      0.3                 0.0    2  ...  56082072  5  0        0   0
     3            3_0       1      0.3                 0.0    3  ...  56082072  0  5        0   0
     4            3_0       1      0.3                 0.0    4  ...  56082070  0  5        2   2
     ...          ...     ...      ...                 ...  ...  ...       ... .. ..      ...  ..
     1587         5_5       1      0.5                 0.5  172  ...  49969606  0  2  6112469   0
     1588         5_5       1      0.5                 0.5  173  ...  49969606  0  2  6112469   0
     1589         5_5       1      0.5                 0.5  174  ...  49969606  0  2  6112469   0
     1590         5_5       1      0.5                 0.5  175  ...  49969606  0  1  6112470   0
     1591         5_5       1      0.5                 0.5  176  ...  49969606  0  0  6112471   0

     [1592 rows x 11 columns]

This is very similar to before, except now we have extra columns giving
the values of the variables that are being adjusted (columns
``beta[2]`` and ``too_ill_to_move[2]``. We also now have a use for the
``fingerprint`` column, which contains a unique identifier for each
pair of adjustable variables.

.. note::
   The fingerprint is constructed by removing the leading ``0.`` from
   the value of the adjustable variable, and the joining the values
   together using underscores. Thus ``0.3  0.0`` becomes ``3_0``,
   while ``0.5 0.5`` becomes ``5_5``.

Finding peaks
-------------

We can use ``.groupby`` to group the results with the same fingerprint
together. Then the ``.max`` function can be used to show the maximum
values of selected columns from each group, e.g.

.. code-block:: python

  >>> df.groupby("fingerprint")[["day", "E","I", "IW", "R"]].max()
             day       E        I    IW         R
  fingerprint
  3_0          175  155437   769541  8510   6369771
  3_25         171  141362   698977  8493   5811758
  3_5          185  170973   847554  8531   6998635
  4_0          178  235224  1162678  8573   9251310
  4_25         172  250029  1235252  8566   9808872
  4_5          174  289890  1435946  8582  11322621
  5_0          175  394132  1949529  8584  14703554
  5_25         177  492045  2434433  8586  18009857
  5_5          176  157752   779038  8522   6112471

From this, we can see that higher peaks occured for higher values
of **beta**, which is expected. However, larger values of
**too_ill_to_move** also seemed to slightly increase the peaks,
which seems counter-intuitive. If is only for the high **beta**
value of 0.5 that the increased **too_ill_to_move** of 0.5 has
resulted in a much smaller peak.

.. warning::

  Do not over-interpret the results of single runs, such as the above.
  The result for 5_0 here has a peak in infections of 14.7 million.
  The peak for the :doc:`last job <01_disease>` which used the
  same disease parameters, but a different random number seed,
  had a peak in infections of ~20 million. There is a lot of random
  error in these calculations and multiple *model runs* must be
  averaged over to gain a good understanding.

Plotting the output
-------------------

There are lots of plots you would likely want to draw, so it is recommended
that you use a tool such as R, Pandas or Excel to create the plots that
will let you explore the data in full. For a quick set of plots, you
can again use ``metawards-plot`` to generate some overview plots. To
do this type;

.. code-block:: bash

  metawards-plot -i output/results.csv.bz2 --format jpg --dpi 300

.. note::
   We have used the 'jpg' image format here are we want to create animations.
   You can choose from many different formats, e.g. 'pdf' for publication
   quality graphs, 'png' etc. Use the ``--dpi`` option to set the
   resolution when creating bitmap (png, jpg) images.

As there are multiple fingerprints, this will produce multiple overview
graphs (one overview per fingerprint, and if you have run multiple
repeats, then one average per fingerprint too).

The fingerprint value is included in the graph name, and they will
all be plotted on the same axes. This means that they could be joined
together into an animation. As well as plotting, ``metawards-plot`` has
an animation mode that can be used to join images together. To run this,
use;

.. code-block:: bash

  metawards-plot --animate output/overview*.jpg

.. note::
   You can only animate image files (e.g. jpg, png). You can't animate
   pdfs (yet - although
   `pull requests welcome <https://github.com/metawards/MetaWards/pulls>`__)

Here is the animation.

.. image:: ../../images/tutorial_2_3.gif
   :alt: Animated overview graphs from the parameter sweep

Jupyter notebook
----------------

In addition, to the ``metawards-plot`` command, we also have a
:download:`Jupyter notebook <../../notebooks/2_3_analysis.ipynb>`
which you can look at which breaks down exactly how ``metawards-plot``
uses pandas and matplotlib to render multi-fingerprint graphs.
