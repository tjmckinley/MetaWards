======================
Extracting by location
======================

.. code-block:: python

    matched_wards = None
    headers = []

    def output_location(network, population, workspace, output_dir, **kwargs):
        ward = "clifton"
        authority = "bristol"

        global matched_wards, headers

        if matched_wards is None:
            matched_wards = network.info.find(name=ward, authority=authority)
            headers = []
            headers.append("day")

            for ward in matched_wards:
                headers.append(f"'{network.info[ward].name}'")

        locfile = output_dir.open("clifton.dat", headers=headers, sep=",")

        locfile.write(str(population.day))

        for ward in matched_wards:
            total = workspace.total_inf_ward[ward]
            locfile.write("," + str(total))

        locfile.write("\n")

    def extract_location(**kwargs):
        from metawards.extractors import extract_default

        return extract_default(**kwargs) + [output_location]

Extracting data by named location.

:class:`~metawards.WardInfo` contains the data.
:class:`~metawards.WardInfos` has the search functions.
