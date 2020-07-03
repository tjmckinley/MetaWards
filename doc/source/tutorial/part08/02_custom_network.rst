=========================
Creating a Custom Network
=========================

While the default networks supplied in ``MetaWardsData`` model the UK, there
is nothing to stop you creating your own network to model any country or
region. Indeed, you can use the concepts of ``wards``, ``workers`` and
``players`` in a more generic way to model lots of different environments,
e.g.

* Using wards to represent different university buildings, and then track
  disease spread between buildings as staff and students move around.
* Using wards to represent care homes, hospitals and homes in a single
  region, and then model the motion of staff, patients and the general
  population between these different environments.

Network file formats
--------------------

A lot of data needs to be loaded to define the network. There are two
file formats for specifying this data;

1. :doc:`A set of fixed-format files <../../fileformats/network>` that
   contain the data in a set of files that are contained in a single
   directory. This is an older format that is used predominantly for
   older model networks.

2. :doc:`A JSON-format file <../../fileformats/network_json>` that contains
   all of the data needed to describe the network in a single file.

While you can edit these files directly, this can be error-prone. We thus
recommend that you create and edit files using a Python script, as described
below.

Creating and editing Networks in Python
---------------------------------------

Ward.

