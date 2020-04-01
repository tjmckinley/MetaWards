
from libc.stdio cimport FILE, fopen, fscanf, fclose, feof

from ._network import Network
from ._links import Links
from ._profiler import Profiler, NullProfiler

__all__ = ["build_play_matrix"]


def build_play_matrix(network: Network, profiler: Profiler=None):
    """Build the play matrix for the passed network"""
    if profiler is None:
        profiler = NullProfiler()

    p = profiler.start("build_play_matrix")

    params = network.params

    if params is None:
        return

    nodes = network.nodes

    p = p.start("allocate_memory")
    links = Links(network.max_links + 1)
    p = p.stop()

    cdef int nlinks = 0
    cdef int j = 0
    cdef int from_id = 0
    cdef int to_id = 0
    cdef double weight = 0.0

    cdef int [:] nodes_label = nodes.label
    cdef int [:] nodes_begin_p = nodes.begin_p
    cdef int [:] nodes_end_p = nodes.end_p
    cdef int [:] nodes_self_p = nodes.self_p

    cdef int [:] links_ifrom = links.ifrom
    cdef int [:] links_ito = links.ito
    cdef double [:] links_weight = links.weight
    cdef double [:] links_suscept = links.suscept

    cdef double [:] nodes_denominator_p = nodes.denominator_p
    cdef double [:] nodes_play_suscept = nodes.play_suscept

    p = p.start("read_play_file")

    # need to use C file reading as too slow in python
    filename = params.input_files.play.encode("UTF-8")
    cdef char* fname = filename

    cdef FILE* cfile
    cfile = fopen(fname, "r")

    if cfile == NULL:
        raise FileNotFoundError(f"No such file or directory: {filename}")

    # resets the node label as a flag to check progress?
    for j in range(1, network.nnodes+1):
        nodes_label[j] = -1

    try:
        while not feof(cfile):
            fscanf(cfile, "%d %d %lf\n", &from_id, &to_id, &weight)

            nlinks += 1

            if from_id == 0 or to_id == 0:
                raise ValueError(
                            f"Zero in link list: ${from_id}-${to_id}! "
                            f"Renumber files and start again")

            if nodes_label[from_id] == -1:
                nodes_label[from_id] = from_id
                nodes_begin_p[from_id] = nlinks
                nodes_end_p[from_id] = nlinks

            if from_id == to_id:
                nodes_self_p[from_id] = nlinks

            nodes_end_p[from_id] += 1

            links_ifrom[nlinks] = from_id
            links_ito[nlinks] = to_id
            links_weight[nlinks] = weight

            nodes_denominator_p[from_id] += weight  # not denominator_p
            nodes_play_suscept[from_id] += weight

        fclose(cfile)
    except Exception as e:
        fclose(cfile)
        raise ValueError(f"{params.input_files.play} is corrupted or "
                         f"unreadable? Error = {e.__class__}: {e}")

    p = p.stop()

    p = p.start("renormalise?")
    renormalise = (params.input_files.play == params.input_files.work)
    p = p.stop()

    p = p.start("renormalise_loop")
    for j in range(1, nlinks+1):   # careful 1-indexed
        if renormalise:
            links_weight[j] /= nodes_denominator_p[links_ifrom[j]]

        links_suscept[j] = links_weight[j]
    p = p.stop()

    from ._utils import fill_in_gaps
    p = p.start("fill_in_gaps")
    fill_in_gaps(network)
    p = p.stop()

    cdef int i1 = 0
    cdef int i2 = 0
    cdef double [:] nodes_save_play_suscept = nodes.save_play_suscept

    p = p.start("read_play_size_file")
    try:
        with open(params.input_files.play_size, "r") as FILE:
            line = FILE.readline()

            while line:
                words = line.split()
                i1 = int(words[0])
                i2 = int(words[1])

                nodes_play_suscept[i1] = i2
                nodes_denominator_p[i1] = i2
                nodes_save_play_suscept[i1] = i2

                line = FILE.readline()

    except Exception as e:
        raise ValueError(f"{params.input_files.play_size} is corrupted or "
                         f"unreadable? Error = {e.__class__}: {e}")

    p = p.stop()

    print(f"Number of play links equals {nlinks}")

    network.plinks = nlinks
    network.play = links

    p.stop()
