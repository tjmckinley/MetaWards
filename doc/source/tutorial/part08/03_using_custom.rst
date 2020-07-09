======================
Using a Custom Network
======================

You can run a simulation using a custom network by passing filename of
the JSON file that contains the network to ``metawards`` via the
``--model`` or ``-m`` parameter.

For example, to use the ``custom_network.json`` file from the last section,
together with the ``lurgy4.json`` disease model from previous chapters,
you would run;

.. code-block:: bash

   metawards -d lurgy4 -m custom_network.json

