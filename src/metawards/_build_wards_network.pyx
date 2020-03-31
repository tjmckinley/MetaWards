
from ._parameters import Parameters
from ._network import Network
from ._nodes import Nodes
from ._links import Links

from ._metawards import build_play_matrix, fill_in_gaps

__all__ = ["build_wards_network"]


def build_wards_network(params: Parameters,
                        max_nodes:int = 10050,
                        max_links:int = 2414000):
    """Creates a network of wards using the information provided in
       the file specified in parameters.input_files.work.

       The format of this should be:

        * Node_1 Node_2 weight 1-2
        * Node_3 Node_4 weight 3-4
        * Node_4 Node_1 weight 4-1
        * Node_2 Node_1 weight 2-1
        * ...

         BE CAREFUL!! Weights may not be symmetric, network is built with
         asymmetric links
    """
    nodes = Nodes(max_nodes + 1)     # need to pre-allocate nodes and links
    links = Links(max_links + 1)   # both of these use 1-indexing

    cdef int nlinks = 0
    cdef int nnodes = 0

    line = None

    cdef int from_id = 0
    cdef int to_id = 0
    cdef double weight = 0.0
    cdef int iweight = 0

    cdef int [:] nodes_label = nodes.label
    cdef int [:] nodes_begin_to = nodes.begin_to
    cdef int [:] nodes_end_to = nodes.end_to
    cdef int [:] nodes_self_w = nodes.self_w

    cdef int [:] links_ito = links.ito
    cdef int [:] links_ifrom = links.ifrom
    cdef double [:] links_weight = links.weight
    cdef double [:] links_suscept = links.suscept

    cdef double [:] nodes_denominator_d = nodes.denominator_d
    cdef double [:] nodes_denominator_n = nodes.denominator_n

    try:
        with open(params.input_files.work, "r") as FILE:
            # this file is a set of links of from and to node IDs, with weights
            line = FILE.readline()
            while line:
                words = line.split()
                from_id = int(words[0])
                to_id = int(words[1])
                weight = float(words[2])
                iweight = <int>weight

                if from_id == 0 or to_id == 0:
                    raise ValueError(
                                f"Zero in link list: ${from_id}-${to_id}! "
                                f"Renumber files and start again")

                nlinks += 1

                if nodes_label[from_id] == -1:
                    nodes_label[from_id] = from_id
                    nodes_begin_to[from_id] = nlinks
                    nodes_end_to[from_id] = nlinks
                    nnodes += 1

                if from_id == to_id:
                    nodes_self_w[from_id] = nlinks

                nodes_end_to[from_id] += 1

                # original code does int(weight) even though this is a float?
                links_ifrom[nlinks] = from_id
                links_ito[nlinks] = to_id
                links_weight[nlinks] = weight
                links_suscept[nlinks] = weight

                # again, int(weight) is in the code despite these being floats?
                nodes_denominator_n[from_id] += weight
                nodes_denominator_d[to_id] += weight

                line = FILE.readline()
    except Exception as e:
        raise ValueError(f"{params.input_files.work} is corrupted or "
                         f"unreadable? line = {line}, "
                         f"Error = {e.__class__}: {e}")

    network = Network(nnodes=nnodes, nlinks=nlinks)

    network.nodes = nodes
    network.to_links = links

    print(f"Number of nodes equals {nnodes}")
    print(f"Number of links equals {nlinks}")

    fill_in_gaps(network)

    print(f"Number of nodes after filling equals {network.nnodes}")

    build_play_matrix(network=network, params=params, max_links=max_links)

    print(f"Number of nodes after build play equals {network.nnodes}")

    print(f"Resize nodes to {network.nnodes + 1}")
    network.nodes.resize(network.nnodes + 1)     # remember 1-indexed
    network.to_links.resize(network.nlinks + 1)  # remember 1-indexed
    network.play.resize(network.plinks + 1)      # remember 1-indexed

    return network
