
from ._parameters import Parameters
from ._network import Network
from ._node import Node
from ._tolink import ToLink


__all__ = ["read_done_file",
           "build_wards_network",
           "build_wards_network_distance"]


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
    links = (max_links + 1) * [ToLink()]

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

                links[nlinks].ifrom = from_id
                links[nlinks].ito = to_id
                links[nlinks].weight = weight

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
    nodes = (max_nodes + 1) * [Node()]   # need to pre-allocate nodes and links
    links = (max_links + 1) * [ToLink()] # both of these use 1-indexing

    try:
        nlinks = 0
        nnodes = 0

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

                if nodes[from_id].label is None:
                    nodes[from_id].label = from_id
                    nodes[from_id].begin_to = nlinks
                    nodes[to_id].end_to = nlinks
                    nnodes += 1

                if from_id == to_id:
                    nodes[from_id].self_w = nlinks

                nodes[from_id].end_to += 1

                # original code does int(weight) even though this is a float?
                links[nlinks].ifrom = from_id
                links[nlinks].ito = to_id
                links[nlinks].weight = int(weight)
                links[nlinks].suscept = int(weight)

                # again, int(weight) is in the code despite these being floats?
                nodes[from_id].denominator_n += int(weight)
                nodes[to_id].denominator_d += int(weight)

                line = FILE.readline()
    except Exception as e:
        raise ValueError(f"{params.input_files.work} is corrupted or "
                         f"unreadable? Error = {e.__class__}: {e}")

    network = Network(nnodes=nnodes, nlinks=nlinks)

    network.nodes = nodes
    network.to_links = links

    fill_in_gaps(network)

    build_play_matrix(network=network, params=params, max_links=max_links)

    return network


def build_wards_network_distance(params: Parameters):
    """Calls BuildWardsNetwork (as above), but adds extra bit, to
       read LocationFile and calculate distances of links, put them
       in net->to_links[i].distance
       Distances are not included in the play matrix
    """

    network = build_wards_network(params)


    return network
