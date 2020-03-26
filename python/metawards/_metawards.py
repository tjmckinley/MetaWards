
from ._parameters import Parameters
from ._network import Network


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

    for i in range(1, len(network.to_links)):
        link = links[i]
        if network.nodes[link.ito].label != link.ito:
            network.nodes[link.ito].label = link.ito
            network.nnodes += 1


def build_play_matrix(network: Network, params: Parameters):



def build_wards_network(params: Parameters):
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

    from ._network import Network
    from ._node import Node
    from ._tolink import ToLink

    nodes = {}
    links = [ToLink()]  # the code uses 1-indexing

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

                if from_id not in nodes:
                    node = Node(label=from_id)
                    nodes[from_id] = node

                if to_id not in nodes:
                    node = Node(label=to_id)
                    nodes[to_id] = node

                if nodes[from_id].begin_to is None:
                    nodes[from_id].begin_to = nlinks
                    nodes[from_id].end_to = nlinks
                    nnodes += 1

                if from_id == to_id:
                    nodes[from_id].self_w = nlinks

                nodes[from_id].end_to += 1

                # original code does int(weight) even though this is a float?
                link = ToLink(ifrom=from_id, ito=to_id, weight=int(weight),
                            suscept=int(weight))

                links.append(link)

                # again, int(weight) is in the code despite these being floats?
                nodes[from_id].denominator_n += int(weight)
                nodes[to_id].denominator_d += int(weight)

                line = FILE.readline()
    except Exception as e:
        raise ValueError(f"{params.input_files.work} is corrupted or "
                         f"unreadable? Error = {e.__class__}: {e}")

    network = Network(nnodes=nnodes, nlinks=nlinks)

    if nnodes != len(nodes):
        raise AssertionError(f"Disagreement in number of nodes? {nnodes} "
                             f"versus {len(nodes)}?")

    network.nodes = (1 + nnodes) * [None]  # 1-indexing the nodes array
    network.to_links = links

    for key, value in nodes.items():
        if key < 0 or key > nnodes:
            raise AssertionError(f"Invalid node key {key}: nnodes = {nnodes}")

        network.nodes[key] = value

    fill_in_gaps(network)

    build_play_matrix(network, params)

    return network


def build_wards_network_distance(params: Parameters):
    """Calls BuildWardsNetwork (as above), but adds extra bit, to
       read LocationFile and calculate distances of links, put them
       in net->to_links[i].distance
       Distances are not included in the play matrix
    """

    network = build_wards_network(params)


    return network
