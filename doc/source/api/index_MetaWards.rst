.. _ref-MetaWards:

MetaWards
=========

This is the top-level Python package that provides the core objects to
build and run MetaWards models.

The package centers around a few core objects:

`Nodes <generated/metawards.Nodes.html>`__ / `Node <generated/metawards.Node.html>`__
    These represent the individual electoral wards in
    which progress of the disease is tracked.

`Links <generated/metawards.Links.html>`__ / `Link <generated/metawards.Link.html>`__
    These represent the connections between electoral wards,
    including how people commute between wards for work. These
    therefore provide the routes via which the disease
    can spread.

`Parameters <generated/metawards.Parameters.html>`__
    This is the holder of all model parameters that can describe,
    e.g. the proportion of day versus night, cutoff distance
    for transmission between wards etc.
    Example parameter sets are held in the
    `MetaWardsData <https://github.com/metawards/MetaWardsData>`__
    repository.

`Disease <generated/metawards.Disease.html>`__
    This is the holder of disease parameters, used to change the model
    to represent different types of disease outbreaks. Different
    disease models are held in the
    `MetaWardsData <https://github.com/metawards/MetaWardsData>`__
    repository.

`InputFiles <generated/metawards.InputFiles.html>`__
    This holds information about all of the input files that are
    used to build the network of wards and links. All of the
    input data is held in the
    `MetaWardsData <https://github.com/metawards/MetaWardsData>`__
    repository.

`Network <generated/metawards.NetWork.html>`__
    This is the complete network of Nodes and Links built using
    the data loaded from the InputFiles, set up to model the
    disease whose parameters are in a Disease, using model run
    parameters held in a Parameters object. A Network is
    self-contained, containing everything needed for a model run.
    The Network.run function runs the model.

`VariableSet <generated/metawards.VariableSet.html>`__ / `VariableSets <generated/metawards.VariableSets.html>`__
    The model contains adjustable variables,
    which must be adjusted so that the model can match observed
    real-life data. A VariableSet contains a set of variables to
    be adjusted, while VariableSets is a collection of such
    changes that should be explored over multiple model runs.

`Population <generated/metawards.Population.html>`__ / `Populations <generated/metawards.Populations.html>`__
    A model run will result in a trajectory of
    changes in populations of people who have progressed along
    different stages of the disease (e.g. from being
    *susceptible to infection* (S), to being
    *removed from the outbreak* (R) - either because they
    have recovered or have sadly perished). A Population holds
    the numbers in each state for a single day in the outbreak,
    while Populations holds the full trajectory.

All of the above classes (and others in the top-level package) are
described `in more detail here <index_api_MetaWards.html>`__;

.. toctree::
   :maxdepth: 1

   index_api_MetaWards
