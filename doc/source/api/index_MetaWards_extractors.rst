====================
MetaWards.extractors
====================

These are the extractor functions that are used during a model run
to extract data from the outbreak to process and write live to files.
The functions divide into three main types,
the most important of which are described below;

The functions that decide which output functions will be called
    * :meth:`~metawards.extractors.extract_core`
    * :meth:`~metawards.extractors.extract_custom`
    * :meth:`~metawards.extractors.extract_default`
    * :meth:`~metawards.extractors.extract_small`
    * :meth:`~metawards.extractors.extract_none`

Functions that extract and output information from the outbreak
    * :meth:`~metawards.extractors.output_basic`
    * :meth:`~metawards.extractors.output_core`
    * :meth:`~metawards.extractors.output_dispersal`
    * :meth:`~metawards.extractors.output_incidence`
    * :meth:`~metawards.extractors.output_prevalence`

All of the above functions (and the many others in metawards.extractors) are
described :doc:`in more detail here <./index_api_MetaWards_extractors>`;

.. toctree::
   :maxdepth: 1

   index_api_MetaWards_extractors
