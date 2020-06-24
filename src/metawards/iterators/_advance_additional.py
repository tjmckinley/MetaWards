
from typing import Union as _Union

from .._network import Network
from .._networks import Networks
from .._population import Population
from ..utils._profiler import Profiler
from .._infections import Infections

__all__ = ["advance_additional"]



def _get_day(s, network, row, rng):
    if s is None:
        row.append("1")
        return 1

    try:
        day = int(s)
        row.append(s)
        return day
    except Exception:
        pass

    try:
        day = _get_random(s, rng)
        row.append(f"{s} : {day}")
        return day
    except Exception:
        pass

    # read the day from a string
    try:
        from datetime import date
        d = date.fromisoformat(s)
    except Exception:
        d = None

    if d is None:
        try:
            from dateparser import parse
            d = parse(s).date()
        except Exception:
            d = None

    if d is None:
        raise ValueError(f"Could not interpret a day or date from '{s}'")

    row.append(f"{s} : {d.isoformat()}")
    return d


def _get_ward(s, network, row, rng):
    if s is None:
        row.append("1")
        return 1

    if isinstance(network, Networks):
        raise TypeError("This should be a Network object...")

    try:
        index = _get_random(s, rng, 1, network.nnodes)
        try:
            row.append(f"{s} : {index} : {network.info[index]}")
        except Exception:
            row.append(f"{s} : {index}")

        return index
    except Exception:
        pass

    index = network.get_node_index(s)

    try:
        row.append(f"{s} : {network.info[index]}")
    except Exception:
        row.append(s)

    return index


def _get_number_to_seed(s, network, row, rng):
    if s is None:
        row.append("0")
        return 0

    try:
        n = int(s)
        row.append(s)
        return n
    except Exception:
        pass

    try:
        n = _get_random(s, rng)
        row.append(f"{s} : {n}")
        return n
    except Exception as e:
        from ..utils._console import Console
        Console.error(f"{e.__class__}: {e}")
        pass

    raise ValueError(f"Could not interpret the number to seed from {s}")


def _get_demographic(s, network, row, rng):
    if s is None:
        row.append(None)
        return s
    elif isinstance(network, Network):
        row.append(None)
        return None
    elif s == "overall":
        row.append(None)
        return None

    index = network.demographics.get_index(s)

    if str(index) != s:
        row.append(f"{s} : {index}")
    else:
        row.append(s)

    return index


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
            lines = FILE.readlines()
    else:
        Console.print(f"Loading additional seeds from the command line")
        lines = filename.split("\\n")

    seeds = []

    table = Table()
    table.add_column("Day")
    table.add_column("Demographic")
    table.add_column("Ward")
    table.add_column("Number seeded")

    import csv

    try:
        dialect = csv.Sniffer().sniff(lines[0], delimiters=[" ", ","])
    except Exception:
        Console.warning(
            f"Could not identify what sort of separator to use to "
            f"read the additional seeds, so will assume commas. If this is "
            f"wrong then could you add commas to separate the "
            f"fields?")
        dialect = csv.excel  #  default comma-separated file

    for line in csv.reader(lines, dialect=dialect,
                           quoting=csv.QUOTE_ALL,
                           skipinitialspace=True):

        words = []

        # yes, the original files really do mix tabe and spaces... need
        # to extract these separately!
        for l in line:
            for p in l.split("\t"):
                words.append(p)

        if len(words) == 0:
            continue

        if len(words) < 3:
            raise ValueError(
                f"Can not interpret additional seeds from the line '{line}'")

        row = []

        # yes, this is really the order of the seeds - "t num loc"
        # is in the file as "t loc num"
        day = _get_day(words[0], network, row, rng)

        if len(words) == 4:
            demographic = _get_demographic(words[3], network, row, rng)

            if demographic is not None:
                # we need the right network to get the ward below
                network = network.subnets[demographic]
        else:
            demographic = None
            row.append(None)

        ward = _get_ward(words[2], network, row, rng)
        seed = _get_number_to_seed(words[1], network, row, rng)
        seeds.append((day, ward, seed, demographic))
        table.add_row(row)

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
        if seed[0] == population.day:
            ward = seed[1]
            num = seed[2]

            if isinstance(network, Networks):
                demographic = seed[3]

                if demographic is None:
                    # not specified, so seed the first demographic
                    demographic = 0
                else:
                    demographic = network.demographics.get_index(demographic)

                network = network.subnets[demographic]
                wards = network.nodes
                play_infections = infections.subinfs[demographic].play
            else:
                demographic = None
                wards = network.nodes
                play_infections = infections.play

            try:
                ward = network.get_node_index(ward)

                if wards.play_suscept[ward] < num:
                    Console.warning(
                        f"Not enough susceptibles in ward for seeding")
                else:
                    wards.play_suscept[ward] -= num
                    if demographic is not None:
                        Console.print(
                            f"seeding demographic {demographic} "
                            f"play_infections[0][{ward}] += {num}")
                    else:
                        Console.print(
                            f"seeding play_infections[0][{ward}] += {num}")

                    play_infections[0][ward] += num

            except Exception as e:
                Console.error(
                    f"Unable to seed the infection using {seed}. The "
                    f"error was {e.__class__}: {e}. Please double-check "
                    f"that you are trying to seed a node that exists "
                    f"in this network.")
                raise e

    p.stop()
