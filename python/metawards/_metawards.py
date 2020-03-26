
import math

from ._parameters import Parameters
from ._network import Network
from ._node import Node
from ._tolink import ToLink


__all__ = ["read_done_file",
           "build_wards_network",
           "build_wards_network_distance",
           "initialise_infections",
           "initialise_play_infections",
           "get_min_max_distances",
           "reset_everything",
           "rescale_play_matrix"]


def read_done_file(filename: str):
    """This function reads the 'done_file' from 'filename' returning the list
       of seeded nodes
    """
    try:
        print(f"{filename} -- ")

        nodes_seeded = []

        with open(filename, "r") as FILE:
            line = FILE.readline()

            # each line has a single number, which is the seed
            nodes_seeded.append( float(line.strip()) )

        return nodes_seeded

    except Exception as e:
        raise ValueError(f"Possible corruption of {filename}: {e}")


def recalculate_play_denominator_day(network: Network, params: Parameters):

    wards = network.nodes
    links = network.play

    for i in range(1, network.nnodes+1):  # 1-indexed
        wards[i].denominator_pd = 0
        wards[i].denominator_p = 0

    sum = 0.0

    for j in range(1, network.plinks+1):  # 1-indexed
        link = links[j]
        denom = link.weight * wards[link.ifrom].play_suscept
        wards[link.ito].denominator_pd += denom

        sum += denom

    print(f"recalculate_play_denominator_day sum 1 = {sum}")

    sum = 0.0

    for i in range(1, network.nnodes+1):  # 1-indexed
        ward = wards[i]

        wards[i].denominator_pd = int(math.floor(ward.denominator_pd + 0.5))

        wards[i].denominator_p = ward.play_suscept

        if ward.play_suscept < 0.0:
            print(f"Negative play_suscept? {ward}")

        sum += wards[i].denominator_p

    print(f"recalculate_play_denominator_day sum 2 = {sum}")


def rescale_play_matrix(network: Network, params: Parameters):
    """ Static Play At Home rescaling.
	    for 1, everyone stays at home.
	    for 0 a lot of people move around.
    """

    links = network.play
    # nodes = network.nodes  # check if this is not needed in the code
                             # as it was declared in the original function

    if params.static_play_at_home > 0:
        # if we are making people stay at home, then do this loop through nodes
        # Rescale appropriately!
        sclfac = 1.0 - params.static_play_at_home

        for j in range(1, network.plinks+1):  # 1-indexed
            link = links[j]

            if link.ifrom != link.ito:
                # if it's not the home ward, then reduce the
                # number of play movers
                links[j].weight = link.suscept * sclfac
            else:
                # if it is the home ward
                links[j].weight = ((1.0 - link.suscept) * \
                                   params.static_play_at_home) + \
                                  link.suscept

    recalculate_play_denominator_day(network=network, params=params)


def reset_work_matrix(network: Network):
    links = network.to_links

    for i in range(1, network.nlinks+1):  # 1-indexed
        if links[i] is None:
            print(f"Missing a link at index {i}")
        else:
            links[i].suscept = links[i].weight


def reset_play_matrix(network: Network):
    links = network.play

    for i in range(1, network.plinks+1):  # 1-indexed
        if links[i] is None:
            print(f"Missing a play link at index {i}?")
        else:
            links[i].weight = links[i].suscept


def reset_play_susceptibles(network: Network):
    nodes = network.nodes

    for i in range(1, network.nnodes+1):  # 1-indexed
        if nodes[i] is None:
            print(f"Missing a node at index {i}?")
            # create a null node - need to check if this is the best thing
            # to do
            nodes[i] = Node()
        else:
            nodes[i].play_suscept = nodes[i].save_play_suscept


def reset_everything(network: Network, params: Parameters):
    reset_work_matrix(network)
    reset_play_matrix(network)
    reset_play_susceptibles(network)

    # if weekend
    #    reset_weekend_matrix(network)

    N_INF_CLASSES = params.disease_params.N_INF_CLASSES()

    params.disease_params.contrib_foi = N_INF_CLASSES * [0]

    for i in range(0, N_INF_CLASSES-1):   # why -1?
        params.disease_params.contrib_foi[i] = 1


def get_min_max_distances(network: Network):
    """Return the minimum and maximum distances recorded in the network"""
    mindist = None
    maxdist = None

    links = network.to_links

    for link in links:
        dist = link.distance

        if dist:
            if mindist is None:
                mindist = dist
                maxdist = dist
            elif dist > maxdist:
                maxdist = dist
            elif dist < mindist:
                mindist = dist

    print(f"maxdist {maxdist} mindist {mindist}")

    if mindist > 0:
        print(f"The original code always gives a minimum distance of zero, "
              f"so setting {mindist} to zero... (check if this is correct)")

    mindist = 0

    return (mindist, maxdist)


def initialise_infections(network: Network, params: Parameters):
    disease = params.disease_params

    n = disease.N_INF_CLASSES()

    infections = []

    nlinks = network.nlinks + 1

    for _ in range(0, n):
        infections.append( nlinks * [0] )

    return infections


def initialise_play_infections(network: Network, params: Parameters):
    disease = params.disease_params

    n = disease.N_INF_CLASSES()

    infections = []

    nnodes = network.nnodes + 1

    for _ in range(0, n):
        infections.append( nnodes * [0] )

    return infections


def fill_in_gaps(network: Network):
    """Fills in gaps in the network"""
    links = network.to_links

    for i in range(1, network.nlinks+1):  # careful of 1-indexing
        link = links[i]
        if network.nodes[link.ito].label != link.ito:
            network.nodes[link.ito].label = link.ito
            network.nnodes += 1


def build_play_matrix(network: Network, params: Parameters,
                      max_links: int):

    nlinks = 0
    links = (max_links + 1) * [None]

    try:
        with open(params.input_files.play) as FILE:
            nodes = network.nodes

            # resets the node label as a flag to check progress?
            for j in range(1, network.nnodes+1): # careful of 1-indexing
                nodes[j].label = None

            line = FILE.readline()
            while line:
                words = line.split()
                from_id = int(words[0])
                to_id = int(words[1])
                weight = float(words[2])

                nlinks += 1

                if from_id == 0 or to_id == 0:
                    raise ValueError(
                                f"Zero in link list: ${from_id}-${to_id}! "
                                f"Renumber files and start again")

                if nodes[from_id].label is None:
                    nodes[from_id].label = from_id
                    nodes[from_id].begin_p = nlinks
                    nodes[from_id].end_p = nlinks

                if from_id == to_id:
                    nodes[from_id].self_p = nlinks

                nodes[from_id].end_p += 1

                links[nlinks] = ToLink(ifrom=from_id, ito=to_id,
                                       weight=weight)

                nodes[from_id].denominator_p += weight  # not denominator_p
                nodes[from_id].play_suscept += weight

                line = FILE.readline()
    except Exception as e:
        raise ValueError(f"{params.input_files.play} is corrupted or "
                         f"unreadable? Error = {e.__class__}: {e}")

    renormalise = (params.input_files.play == params.input_files.work)

    for j in range(1, nlinks+1):   # careful 1-indexed
        if renormalise:
            links[j].weight /= nodes[links[j].ifrom].denominator_p

        links[j].suscept = links[j].weight

    fill_in_gaps(network)

    try:
        with open(params.input_files.play_size, "r") as FILE:
            line = FILE.readline()

            while line:
                words = line.split()
                i1 = int(words[0])
                i2 = int(words[1])

                nodes[i1].play_suscept = i2
                nodes[i1].denominator_p = i2
                nodes[i1].save_play_suscept = i2

                line = FILE.readline()

    except Exception as e:
        raise ValueError(f"{params.input_files.play_size} is corrupted or "
                         f"unreadable? Error = {e.__class__}: {e}")

    print(f"Number of play links equals {nlinks}")

    network.plinks = nlinks
    network.play = links


def build_wards_network(params: Parameters,
                        max_nodes:int = 10050,
                        max_links:int = 2414000):
    """Creates a network from a file (specified in par->WorkFname) with format:

        * Node_1 Node_2 weight 1-2
        * Node_3 Node_4 weight 3-4
        * Node_4 Node_1 weight 4-1
        * Node_2 Node_1 weight 2-1
        * ...

         BE CAREFUL!! Weights may not be symmetric, network is built with
         asymmetric links

        play=0 builds network from input file and NOTHING ELSE
        play=1 build the play matrix in net->play
    """
    nodes = (max_nodes + 1) * [None]   # need to pre-allocate nodes and links
    links = (max_links + 1) * [None]   # both of these use 1-indexing

    nlinks = 0
    nnodes = 0

    line = None

    try:
        with open(params.input_files.work, "r") as FILE:
            # this file is a set of links of from and to node IDs, with weights
            line = FILE.readline()
            while line:
                words = line.split()
                from_id = int(words[0])
                to_id = int(words[1])
                weight = float(words[2])

                if from_id == 0 or to_id == 0:
                    raise ValueError(
                                f"Zero in link list: ${from_id}-${to_id}! "
                                f"Renumber files and start again")

                nlinks += 1

                if nodes[from_id] is None or nodes[from_id].label is None:
                    nodes[from_id] = Node(label=from_id, begin_to=nlinks,
                                          end_to=nlinks)
                    nnodes += 1

                if from_id == to_id:
                    nodes[from_id].self_w = nlinks

                nodes[from_id].end_to += 1

                # original code does int(weight) even though this is a float?
                links[nlinks] = ToLink(ifrom=from_id, ito=to_id,
                                       weight=int(weight), suscept=int(weight))

                # again, int(weight) is in the code despite these being floats?
                nodes[from_id].denominator_n += int(weight)

                if nodes[to_id] is None:
                    nodes[to_id] = Node()

                nodes[to_id].denominator_d += int(weight)

                line = FILE.readline()
    except Exception as e:
        raise ValueError(f"{params.input_files.work} is corrupted or "
                         f"unreadable? line = {line}, "
                         f"Error = {e.__class__}: {e}")

    network = Network(nnodes=nnodes, nlinks=nlinks)

    print(f"Number of nodes equals {nnodes}")
    print(f"Number of links equals {nlinks}")

    network.nodes = nodes
    network.to_links = links

    fill_in_gaps(network)

    print(f"Number of nodes after filling equals {network.nnodes}")

    build_play_matrix(network=network, params=params, max_links=max_links)

    # save memory by removing excess nodes and links
    network.nodes = network.nodes[0:network.nnodes+1]
    network.to_links = network.to_links[0:network.nlinks+1]
    network.play = network.play[0:network.plinks+1]

    return network


def build_wards_network_distance(params: Parameters):
    """Calls BuildWardsNetwork (as above), but adds extra bit, to
       read LocationFile and calculate distances of links, put them
       in net->to_links[i].distance
       Distances are not included in the play matrix
    """

    network = build_wards_network(params)

    # ncov build does not have WEEKEND defined, so not writing this code now

    wards = network.nodes
    links = network.to_links
    plinks = network.play

    line = None

    try:
        with open(params.input_files.position, "r") as FILE:
            line = FILE.readline()

            while line:
                words = line.split()
                i1 = int(words[0])
                x = float(words[1])
                y = float(words[2])

                wards[i1].x = x
                wards[i1].y = y

                line = FILE.readline()
    except Exception as e:
        raise ValueError(f"{params.input_files.position} is corrupted or "
                         f"unreadable? Error = {e.__class__}: {e}, "
                         f"line = {line}")

    total_distance = 0

    for i in range(0, network.nlinks):  # shouldn't this be range(1, nlinks+1)?
                                        # the fact there is a missing link at 0
                                        # suggests this should be...
        link = links[i]

        if link is None:
            print(f"Missing link {i}?")
            links[i] = ToLink()
            continue

        ward = wards[link.ifrom]

        if ward is None:
            print(f"Missing ward {link.ifrom}?")
            wards[link.ifrom] = Node()
            ward = wards[link.ifrom]

        x1 = ward.x
        y1 = ward.y

        ward = wards[link.ito]

        if ward is None:
            print(f"Missing ward {link.ito}?")
            wards[link.ito] = Node()
            ward = wards[link.ito]

        x2 = ward.x
        y2 = ward.y

        dx = x1 - x2
        dy = y1 - y2

        distance = math.sqrt(dx*dx + dy*dy)
        links[i].distance = distance
        total_distance += distance

        # below line doesn't make sense and doesn't work. Why would the ith
        # play link be related to the ith work link?
        #plinks[i].distance = distance

    print(f"Total distance equals {total_distance}")

    return network
