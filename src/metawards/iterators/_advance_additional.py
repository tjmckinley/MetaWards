
from typing import Union as _Union

from .._network import Network
from .._networks import Networks
from .._population import Population
from ..utils._profiler import Profiler
from .._infections import Infections

__all__ = ["advance_additional"]


def _get_ward(s, network, rng):
    if s is None:
        return 1

    if isinstance(network, Networks):
        raise TypeError("This should be a Network object...")

    try:
        from .._interpret import Interpret
        index = Interpret.integer(s, rng=rng, minval=1, maxval=network.nnodes)
        return network.get_node_index(index)
    except Exception:
        pass

    return network.get_node_index(s)


def _get_demographic(s, network):
    if s is None:
        return s
    elif isinstance(network, Network):
        return None
    elif s == "overall":
        return None

    return network.demographics.get_index(s)


def _load_additional_seeds(network: _Union[Network, Networks],
                           filename: str, rng):
    """Load additional seeds from the passed filename. This returns
       the added seeds. Note that the filename can be interpreted
       as the actual contents of the file, meaning that for short
       content, it is quicker to pass this than the filename
    """
    import os as _os
    from ..utils._console import Console, Table

    if _os.path.exists(filename):
        Console.print(f"Loading additional seeds from {filename}")
        with open(filename, "r") as FILE:
            ilines = FILE.readlines()
    else:
        Console.print(f"Loading additional seeds from the command line")
        ilines = filename.split("\\n")

    lines = []

    for line in ilines:
        for l in line.split(";"):
            lines.append(l.strip())

    seeds = []

    table = Table()
    table.add_column("Day")
    table.add_column("Demographic")
    table.add_column("Ward")
    table.add_column("Number seeded")

    import csv

    # remove any initial comment lines (breaks sniffing below)
    while lines[0].strip().startswith("#"):
        lines.pop(0)

    # remove any empty initial lines (breaks sniffing below)
    while len(lines[0].strip()) == 0:
        lines.pop(0)

    try:
        dialect = csv.Sniffer().sniff(lines[0], delimiters=[" ", ","])
    except Exception:
        words = lines[0].strip().split(" ")

        if len(words) > 1:
            Console.warning(
                f"Could not identify what sort of separator to use to "
                f"read the additional seeds, so will assume commas. If this "
                f"is wrong then could you add commas to separate the "
                f"fields?")

        dialect = csv.excel  #  default comma-separated file

    titles = None
    nwords = None

    for line in csv.reader(lines, dialect=dialect,
                           quoting=csv.QUOTE_ALL,
                           skipinitialspace=True):

        words = []

        # yes, the original files really do mix tabs and spaces... need
        # to extract these separately!
        for l in line:
            rest_commented = False

            for p in l.split("\t"):
                p = p.strip()
                if p.startswith("#"):
                    rest_commented = True
                    break

                words.append(p)

            if rest_commented:
                break

        if len(words) == 0:
            continue

        if nwords is None:
            nwords = len(words)

        if len(words) < nwords:
            continue

        if titles is None:
            if "day" in words or "number" in words or "ward" in words or \
                    "demographics" in words:
                titles = {}

                try:
                    titles["day"] = words.index("day")
                except Exception:
                    pass

                try:
                    titles["number"] = words.index("number")
                except Exception:
                    pass

                try:
                    titles["ward"] = words.index("ward")
                except Exception:
                    pass

                try:
                    titles["demographic"] = words.index("demographic")
                except Exception:
                    pass

                continue
            else:
                # try to guess the values based on the number of items and
                # their type
                if nwords == 1:
                    titles = {"number": 0, "day": 1, "ward": 2}
                    words.append(1)
                    words.append(1)
                elif nwords == 2:
                    titles = {"day": 0, "number": 1, "ward": 2}
                    words.append(1)
                elif nwords == 3:
                    titles = {"day": 0, "number": 1, "ward": 2}
                else:
                    # yes, this is really the order of the seeds - "t num loc"
                    titles = {"day": 0, "number": 1,
                              "ward": 2, "demographic": 3}

        row = []

        from .._interpret import Interpret

        # is in the file as "t loc num"
        day = titles.get("day", None)

        if day is not None:
            day = Interpret.day_or_date(words[day], rng=rng)
        else:
            day = 1

        row.append(str(day))

        this_network = network

        demographic = titles.get("demographic", None)

        if demographic is not None:
            demographic = _get_demographic(words[demographic], network=network)

        if demographic is not None:
            # we need the right network to get the ward below
            this_network = network.subnets[demographic]
        else:
            demographic = None

        if isinstance(this_network, Networks):
            # The demographic has not been specified, so this must be
            # the first demographic
            this_network = network.subnets[0]

        row.append(str(demographic))

        ward = titles.get("ward", None)

        if ward is not None:
            ward = _get_ward(words[ward], network=this_network, rng=rng)
        else:
            ward = 1

        try:
            row.append(f"{ward} : {this_network.info[ward]}")
        except Exception:
            row.append(str(ward))

        seed = titles.get("number", None)

        if seed is not None:
            seed = Interpret.integer(words[seed], rng=rng, minval=0)
        else:
            seed = 0

        row.append(str(seed))
        table.add_row(row)

        seeds.append((day, ward, seed, demographic))

    Console.print(table.to_string())

    return seeds


def setup_additional_seeds(network: _Union[Network, Networks],
                           profiler: Profiler,
                           rng,
                           **kwargs):
    """Setup function that reads in the additional seeds held
       in `params.additional_seeds` and puts them ready to
       be used by `advance_additional` to import additional
       infections at specified times in specified wards
       during the outbreak

       Parameters
       ----------
       network: Network or Networks
         The network to be seeded
       profiler: Profiler
         Profiler used to profile this function
       rng:
         Random number generator used to generate any random seeding
       kwargs
         Arguments that are not used by this setup function
    """
    params = network.params

    p = profiler.start("load_additional_seeds")
    additional_seeds = []

    if params.additional_seeds is not None:
        for additional in params.additional_seeds:
            additional_seeds += _load_additional_seeds(network=network,
                                                       filename=additional,
                                                       rng=rng)
    p = p.stop()

    return additional_seeds


def advance_additional(network: _Union[Network, Networks],
                       population: Population,
                       infections: Infections,
                       profiler: Profiler,
                       rngs,
                       **kwargs):
    """Advance the infection by infecting additional wards based
       on a pre-determined pattern based on the additional seeds

       Parameters
       ----------
       network: Network or Networks
         The network being modelled
       population: Population
         The population experiencing the outbreak - also contains the day
         of the outbreak
       infections: Infections
         Space to hold the infections
       rngs:
         The list of thread-safe random number generators, one per thread
       profiler: Profiler
         Used to profile this function
       kwargs
         Arguments that aren't used by this advancer
    """

    if not hasattr(network, "_advance_additional_seeds"):
        network._advance_additional_seeds = \
            setup_additional_seeds(network=network, profiler=profiler,
                                   rng=rngs[0])

    from ..utils._console import Console

    additional_seeds = network._advance_additional_seeds

    p = profiler.start("additional_seeds")
    for seed in additional_seeds:
        if seed[0] == population.day or seed[0] == population.date:
            ward = seed[1]
            num = seed[2]

            if isinstance(network, Networks):
                demographic = seed[3]

                if demographic is None:
                    # not specified, so seed the first demographic
                    demographic = 0
                else:
                    demographic = network.demographics.get_index(demographic)

                seed_network = network.subnets[demographic]
                seed_wards = seed_network.nodes
                seed_links = seed_network.links
                seed_infections = infections.subinfs[demographic].play
                seed_work_infections = infections.subinfs[demographic].work
            else:
                demographic = None
                seed_network = network
                seed_wards = seed_network.nodes
                seed_links = seed_network.links
                seed_infections = infections.play
                seed_work_infections = infections.work

            try:
                ward = seed_network.get_node_index(ward)

                num_to_seed = min(num, seed_wards.play_suscept[ward])

                if num_to_seed > 0:
                    seed_wards.play_suscept[ward] -= num_to_seed
                    if demographic is not None:
                        Console.print(
                            f"seeding demographic {demographic} "
                            f"play_infections[0][{ward}] += {num_to_seed}")
                    else:
                        Console.print(f"seeding play_infections[0][{ward}] "
                                      f"+= {num_to_seed}")

                    seed_infections[0][ward] += num_to_seed

                num -= num_to_seed

                if num <= 0:
                    continue

                try:
                    link = seed_links.get_index_of_link(ward, ward)
                except Exception:
                    link = None

                if link is not None:
                    num_to_seed = int(min(num, seed_links.suscept[link]))

                    if num_to_seed > 0:
                        seed_links.suscept[link] -= num_to_seed
                        if demographic is not None:
                            Console.print(
                                f"seeding demographic {demographic} "
                                f"work_infections[0][{link}] += {num_to_seed}")
                        else:
                            Console.print(f"seeding work_infections[0][{link}]"
                                          f" += {num_to_seed}")

                        seed_work_infections[0][link] += num_to_seed

                    num -= num_to_seed

                if num > 0:
                    Console.warning(
                        f"Could not fully seed the ward {ward}. "
                        f"Number remaining equals {num}.")

            except Exception as e:
                Console.error(
                    f"Unable to seed the infection using {seed}. The "
                    f"error was {e.__class__}: {e}. Please double-check "
                    f"that you are trying to seed a node that exists "
                    f"in this network.")
                raise e

    p.stop()
