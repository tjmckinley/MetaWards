
from libc.stdio cimport FILE, fopen, fscanf, fclose, feof

from ._parameters import Parameters
from ._network import Network
from ._nodes import Nodes
from ._links import Links

from ._profiler import Profiler, NullProfiler

__all__ = ["build_wards_network"]

def build_wards_network(params: Parameters,
                        profiler: Profiler = None,
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
    if profiler is None:
        profiler = NullProfiler()

    p = profiler.start("build_wards_network")

    p = p.start("allocate memory")
    nodes = Nodes(max_nodes + 1)     # need to pre-allocate nodes and links
    links = Links(max_links + 1)   # both of these use 1-indexing
    p = p.stop()

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

    p = p.start("read_work_file")

    # need to use C file reading as too slow in python
    filename = params.input_files.work.encode("UTF-8")
    cdef char* fname = filename

    cdef FILE* cfile
    cfile = fopen(fname, "r")

    if cfile == NULL:
        raise FileNotFoundError(f"No such file or directory: {filename}")

    try:
        while not feof(cfile):
            fscanf(cfile, "%d %d %lf\n", &from_id, &to_id, &weight)

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

        fclose(cfile)
    except Exception as e:
        fclose(cfile)
        raise ValueError(f"{params.input_files.work} is corrupted or "
                         f"unreadable? line = {line}, "
                         f"Error = {e.__class__}: {e}")
    p = p.stop()

    network = Network(nnodes=nnodes, nlinks=nlinks)

    network.nodes = nodes
    network.to_links = links

    print(f"Number of nodes equals {nnodes}")
    print(f"Number of links equals {nlinks}")

    # save the parameters used to build the network
    # within the network - this will save having to pass
    # them separately, which is error-prone
    network.params = params
    network.max_links = max_links
    network.max_nodes = max_nodes

    from ._utils import fill_in_gaps
    p = p.start("fill_in_gaps")
    fill_in_gaps(network)
    p = p.stop()

    print(f"Number of nodes after filling equals {network.nnodes}")

    from ._utils import build_play_matrix
    p = p.start("build_play_matrix")
    build_play_matrix(network=network, profiler=p)
    p = p.stop()

    print(f"Number of nodes after build play equals {network.nnodes}")

    print(f"Resize nodes to {network.nnodes + 1}")
    p = p.start("resize_nodes_and_links")
    network.nodes.resize(network.nnodes + 1)     # remember 1-indexed
    network.to_links.resize(network.nlinks + 1)  # remember 1-indexed
    network.play.resize(network.plinks + 1)      # remember 1-indexed
    p = p.stop()

    p.stop()

    return network
