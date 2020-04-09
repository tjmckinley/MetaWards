.. _ref_api:

=============
Documentation
=============

The metawards program and associated Python module is composed
of three main units;

* The `metawards <index_MetaWards.html>`__ top-level Python module, which is
  what you should use if you want to write new Python programs that
  integrate metawards functionality. These could include plugging
  metawards as a model into a higher-level statictical
  analysis package.

* The `metawards <index_MetaWards_app.html>`__ command line program, which is
  what most people would use to run metawards. This program comes with
  full help that is provided by typing ``metawards --help``.

* The `metawards.utils <index_MetaWards_utils.html>`__ utility Python module which
  contains lots of functions that are used by metawards to build and
  perform model runs. These functions are internal to metawards and are
  not designed to be used outside of this program.

.. toctree::
   :maxdepth: 1

   index_MetaWards
   index_MetaWards_utils
   index_MetaWards_app
