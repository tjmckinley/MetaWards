====================
Conditional Pathways
====================

In the last example we saw how each demographic can be given a different
disease pathway. In this section, we will see how to use move functions
to move individuals between pathways. We did this before
:doc:`when we modelled quarantine. <../part06/05_quarantine>`
Now, we will see how, by using different disease stages, we can create
a range of different pathways through which different individuals
can conditionally progress.

Modelling a hospital
--------------------

In this example we will create a model of a hospital. The demographics
involved will be;

* ``patients`` : Patients at the hospital who are infected with the lurgy
* ``staff`` : Hospital staff who care for the patients
* ``home`` : The general population who are neither patients or staff

Members of the ``staff`` and ``home`` demographics will move along the
stages of the lurgy according to ``lurgy4.json``. Hospital ``patients``
will move through two hospital states, which we will refer to as
``H1`` and ``H2``. These are defined in the file ``lurgy_hospital.json``,
which you should create and copy in the below;

::

  { "name"             : "The Lurgy (hospital patients)",
    "version"          : "June 10th 2020",
    "author(s)"        : "Christopher Woods",
    "contact(s)"       : "christopher.woods@bristol.ac.uk",
    "reference(s)"     : "Completely ficticious disease - no references",
    "beta"             : [0.0, 0.0, 0.2, 0.2, 0.0],
    "progress"         : [1.0, 1.0, 0.2, 0.2, 0.0],
    "too_ill_to_move"  : [0.0, 0.0, 1.0, 1.0, 1.0],
    "contrib_foi"      : [0.0, 0.0, 1.0, 1.0, 0.0]
  }

.. note::

   Every disease must include the ``*`` and ``E`` stages, which are
   stages 0 and 1, and the ``R`` stage which is the last stage. This
   means that ``H1`` and ``H2`` are stages 2 and 3 in this file, both
   of which have ``beta == 0.2``, ``progress == 0.2`` and
   ``too_ill_to_move == 1.0``. While the ``H1`` and ``H2`` stages
   are identical now, we will look to change them later in this
   tutorial.

The aim of the model will be that 20% of those suffering in the ``I2``
stage of ``lurgy4.json`` will be moved to the ``H1`` stage of
``lurgy_hospital.json``, and will then progress to ``H2`` and then
``R`` in the hospital.

We will next set that 10% of the worker population are hospital staff, while,
initially, nobody has the lurgy, and so there are no hospital patients.
We can set this using the file ``demographics.json``, which you should
create and copy in the below;

::

    {
        "demographics" : ["home", "staff", "patients"],
        "work_ratios"  : [ 0.90,   0.10,     0.00 ],
        "play_ratios"  : [ 1.00,   0.00,     0.00 ],
        "diseases"     : [ null,   null,   "lurgy_hospital" ]
    }

Next, we need a mixing function that will model the interactions between
hospital staff, patients and the general population. We will use the
following interaction matrix;

.. list-table::
   :widths: 25 25 25 25
   :header-rows: 1
   :stub-columns: 1

   * -
     - home
     - staff
     - patients
   * - home
     - 1.0
     - 1.0
     - 0.0
   * - staff
     - 1.0
     - 1.0
     - 0.5
   * - patients
     - 0.0
     - 0.5
     - 0.0

This matrix sets that the ``home`` and ``staff`` demographics are equally
exposed to each other, and so equally infect each other. This makes sense,
as hospital staff return home and will mix with the general population.

This matrix sets that the ``home`` and ``patient`` demographics do not
interact and so are not exposed to each other or can infect each other.
This is because there is no visiting or other direct interactions between
a patient and the general population.

Next, this matrix sets that the ``staff`` and ``patients`` are equally
exposed to each other, but take precautions such that the force of infection
between these demographics is reduced by 50%.

Finally, the ``patients`` group are isolated from one another, and so
do not infect one another. At the moment this is moot, as all patients
in this model are already infected. However, you could add a susceptible
patient population who do not have the lurgy, and then use this final
element in the matrix to control the force of infection between patients.

To use this interaction matrix, create a mixer in ``mix_hospital.py``
and copy in the below.

.. code-block:: python

    from metawards.mixers import merge_using_matrix

    def mix_shield(network, **kwargs):
        matrix = [ [1.0, 1.0, 0.0],
                [1.0, 1.0, 0.5],
                [0.0, 0.5, 0.0] ]

        network.demographics.interaction_matrix = matrix

        return [merge_using_matrix]

.. note::

   This is essentially an identical mixing function as that used
   in the :doc:`shielding example <../../part05/03_custom>`.

Conditionally moving to hospital
--------------------------------

The new part of this example is that we need to add a move function that
will move 20% of individuals who are in the ``I2`` stage to
hospital, in the ``H1`` stage. We can do this by writing a move function
into the file ``move_hospital.py``, which you should create and
copy in the below;

.. code-block:: python

    from metawards.movers import go_stage


    def move_hospital(**kwargs):
        func = lambda **kwargs: go_stage(go_from=["home", "staff"],
                                         go_to=["patients"],
                                         from_stage=4,
                                         to_stage=2,
                                         fraction=0.2,
                                         **kwargs)

        return [func]

This move function returns :meth:`~metawards.movers.go_stage`. This is
very similar to :meth:`~metawards.movers.go_to`, except you also specify
the ``from_stage`` and ``to_stage``, which are the stage(s) to move from,
and the stage to move to. In this case, we will move 20% of individuals
from the ``I2``
stage from the ``home`` and ``staff`` demographics, which is stage 4
of ``lurgy4.json``. We will move these individuals to stage 2, which is
``H2``, in the ``patients`` demographic.

Now this is set, we can run the model using;

.. code-block:: bash

