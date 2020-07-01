=============
Network Files
=============

Network files are those that define the nodes (wards) of the network,
and the links (communiting/movement) of individuals between nodes.

The Network files are a collection of files that must all exist in the
same directory. They comprise;

* ``description.json``: This file must exist in the directory, and provides
  the metadata needed to locate all of the other necessary files.
* ``work_size / play_size``: These files list the index and population of
   workers (in ``work_size``) and players (in ``play_size``) in
   each ward in the network. The total population in each ward (node) is
   the sum of the work and play populations.
* ``work``: This file lists all of the work connections between nodes, giving
  the population of workers who commute from the source node to the
  destination.
* ``play``: This file lists all of the play connections between nodes, giving
  the **proportion** of players who make random movements from the source
  node to the destination node.
* ``position``: This file contains the coordinates of the centre of each node.
  These coordinates can be X/Y or latitude/longitude coordinates.
* ``lookup``: This file contains the names and other metadata about each
  node, e.g. the name, local authority, region etc.

These files are all described below.

description.json
----------------

This is a JSON-formatted file that provides metadata about the network model
that is contained in the directory. The file describes a simple dictionary
of the following key-value pairs;

* ``work``: Filename of the ``work`` file.
* ``work_size``: Filename of the ``work_size`` file.
* ``play``: Filename of the ``play`` file.
* ``play_size``: Filename of the ``play_size`` file.
* ``position``: Filename of the ``position`` file.
* ``coordinates``: Whether the coordinates in the ``position`` file are
  in x/y (``x/y``) or latitude/longitude (``lat/long``) format.
* ``coordinate_units``: (Optional) - the units for x/y coordinates. This should
  be either ``m`` for meters, or ``km`` for kilometers. Distances in
  ``metawards`` are always reported as kilometers.
* ``lookup``: (Optional) Filename of the ``lookup`` file.
* ``lookup_columns``: (Optional) A dictionary that gives the column numbers
  (zero-indexed)for the ``code``, ``name``, ``alternate_code``,
  ``alternate_name``, ``authority_code`` and ``authority_name`` fields for
  the ward metadata.

work
----

The ``work`` file contains the list of all work connections between nodes,
giving the number of individuals who commute from the source node to the
destination node. This is a column-based file with three