
from libc.math cimport sqrt, ceil, floor

from array import array

from ._parameters import Parameters
from ._network import Network
from ._node import Node
from ._nodes import Nodes
from ._link import Link
from ._links import Links


__all__ = ["read_done_file",
           "reset_everything",
           "rescale_play_matrix",
           "move_population_from_play_to_work"]


def move_population_from_play_to_work(network: Network, params: Parameters,
                                      rng):
    """And Vice Versa From Work to Play
       The relevant parameters are par->PlayToWork
                                   and par->WorkToPlay

       When both are 0, don't do anything;
       When PlayToWork > 0 move par->PlayToWork proportion from Play to Work.
       When WorkToPlay > 0 move par->WorkToPlay proportion from Work to Play.
    """

    cdef double check = 0.0     # don't use check and
                                # doesn't use the random generator?

    links = network.to_links   # workers, regular movements
    wards = network.nodes
    play = network.play        # links of players

    cdef int i = 0
    cdef double [:] links_suscept = links.suscept
    cdef double [:] wards_play_suscept = wards.play_suscept
    cdef int [:] links_ifrom = links.ifrom
    cdef double to_move = 0.0
    cdef double work_to_play = params.work_to_play
    cdef double play_to_work = params.play_to_work

    if params.work_to_play > 0.0:
        for i in range(1, network.nlinks+1):
            suscept = links_suscept[i]
            to_move = ceil(suscept * work_to_play)

            if to_move > suscept:
                print(f"to_move > links[{i}].suscept")

            links_suscept[i] -= to_move
            wards_play_suscept[links_ifrom[i]] += to_move

    cdef int ifrom = 0
    cdef int [:] play_ifrom = play.ifrom
    cdef double [:] play_weight = play.weight
    cdef double [:] wards_save_play_suscept = wards.save_play_suscept
    cdef double countrem = 0.0
    cdef temp, p

    if params.play_to_work > 0.0:
        for i in range(1, network.plinks+1):
            ifrom = play_ifrom[i]

            temp = play_to_work * (play_weight[i] *
                                   wards_save_play_suscept[ifrom])

            to_move = floor(temp)
            p = temp - to_move

            countrem += p

            if countrem >= 1.0:
                to_move += 1.0
                countrem -= 1.0

            if wards_play_suscept[ifrom] < to_move:
                to_move = wards_play_suscept[ifrom]

            wards_play_suscept[ifrom] -= to_move
            links_suscept[i] += to_move

    recalculate_work_denominator_day(network=network, params=params)
    recalculate_play_denominator_day(network=network, params=params)


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


def recalculate_work_denominator_day(network: Network, params: Parameters):

    wards = network.nodes
    links = network.to_links

    cdef double sum = 0
    cdef int i = 0

    cdef double [:] wards_denominator_d = wards.denominator_d
    cdef double [:] wards_denominator_n = wards.denominator_n

    for i in range(1, network.nnodes+1):
        wards_denominator_d[i] = 0.0
        wards_denominator_n[i] = 0.0

    cdef int j = 0
    cdef int [:] links_ifrom = links.ifrom
    cdef int [:] links_ito = links.ito
    cdef double [:] links_suscept = links.suscept
    cdef int ifrom = 0
    cdef int ito = 0

    for j in range(1, network.nlinks+1):
        ifrom = links_ifrom[j]
        ito = links_ito[j]
        suscept = links_suscept[j]
        wards_denominator_d[ito] += suscept
        wards_denominator_n[ifrom] += suscept
        sum += suscept

    print(f"recalculate_work_denominator_day sum = {sum}")


def recalculate_play_denominator_day(network: Network, params: Parameters):

    wards = network.nodes
    links = network.play

    cdef int i = 0
    cdef double [:] wards_denominator_pd = wards.denominator_pd
    cdef double [:] wards_denominator_p = wards.denominator_p

    for i in range(1, network.nnodes+1):  # 1-indexed
        wards.denominator_pd[i] = 0
        wards.denominator_p[i] = 0

    cdef double sum = 0.0
    cdef int j = 0
    cdef int [:] links_ifrom = links.ifrom
    cdef int [:] links_ito = links.ito
    cdef int ifrom = 0
    cdef int ito = 0
    cdef double weight = 0.0
    cdef double [:] links_weight = links.weight
    cdef double denom = 0.0
    cdef double [:] wards_play_suscept = wards.play_suscept

    for j in range(1, network.plinks+1):  # 1-indexed
        ifrom = links_ifrom[j]
        ito = links_ito[j]
        weight = links_weight[j]
        denom = weight * wards_play_suscept[ifrom]
        wards_denominator_pd[ito] += denom

        sum += denom

    print(f"recalculate_play_denominator_day sum 1 = {sum}")

    sum = 0.0
    cdef double play_suscept = 0

    for i in range(1, network.nnodes+1):  # 1-indexed
        pd = wards_denominator_pd[i]
        play_suscept = wards_play_suscept[i]

        wards_denominator_pd[i] = floor(pd + 0.5)
        wards_denominator_p[i] = play_suscept

        if play_suscept < 0.0:
            print(f"Negative play_suscept? {wards[i]}")

        sum += play_suscept

    print(f"recalculate_play_denominator_day sum 2 = {sum}")


def rescale_play_matrix(network: Network, params: Parameters):
    """ Static Play At Home rescaling.
	    for 1, everyone stays at home.
	    for 0 a lot of people move around.
    """

    links = network.play
    # nodes = network.nodes  # check if this is not needed in the code
                             # as it was declared in the original function

    cdef double static_play_at_home = params.static_play_at_home
    cdef double sclfac = 0.0
    cdef int j = 0
    cdef int ifrom = 0
    cdef int ito = 0
    cdef int [:] links_ito = links.ito
    cdef int [:] links_ifrom = links.ifrom
    cdef double [:] links_weight = links.weight
    cdef double [:] links_suscept = links.suscept

    if static_play_at_home > 0:
        # if we are making people stay at home, then do this loop through nodes
        # Rescale appropriately!
        sclfac = 1.0 - static_play_at_home

        for j in range(1, network.plinks+1):  # 1-indexed
            ifrom = links_ifrom[j]
            ito = links_ito[j]

            if ifrom != ito:
                # if it's not the home ward, then reduce the
                # number of play movers
                links_weight[j] = links_suscept[j] * sclfac
            else:
                # if it is the home ward
                suscept = links_suscept[j]
                links_weight[j] = ((1.0 - suscept) * static_play_at_home) + \
                                   suscept

    recalculate_play_denominator_day(network=network, params=params)


def reset_work_matrix(network: Network):
    links = network.to_links

    cdef int i = 0
    cdef int [:] links_ifrom = links.ifrom
    cdef double [:] links_suscept = links.suscept
    cdef double [:] links_weight = links.weight

    for i in range(1, network.nlinks+1):  # 1-indexed
        if links_ifrom[i] == -1:
            print(f"Missing a link at index {i}")
        else:
            links_suscept[i] = links_weight[i]


def reset_play_matrix(network: Network):
    links = network.play

    cdef int i = 0
    cdef int [:] links_ifrom = links.ifrom
    cdef double [:] links_suscept = links.suscept
    cdef double [:] links_weight = links.weight

    for i in range(1, network.plinks+1):  # 1-indexed
        if links.ifrom[i] == -1:
            print(f"Missing a play link at index {i}?")
        else:
            links.weight[i] = links.suscept[i]


def reset_play_susceptibles(network: Network):
    nodes = network.nodes

    cdef int i = 0
    cdef int [:] nodes_label = nodes.label
    cdef double [:] nodes_play_suscept = nodes.play_suscept
    cdef double [:] nodes_save_play_suscept = nodes.save_play_suscept

    for i in range(1, network.nnodes+1):  # 1-indexed
        if nodes_label[i] == -1:
            print(f"Missing a node at index {i}?")
            # create a null node - need to check if this is the best thing
            # to do
            nodes[i] = Node()
        else:
            nodes_play_suscept[i] = nodes_save_play_suscept[i]


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


def fill_in_gaps(network: Network):
    """Fills in gaps in the network"""
    nodes = network.nodes
    links = network.to_links

    cdef int added = 0
    cdef int i = 0
    cdef int link_to = 0
    cdef int [:] links_ito = links.ito
    cdef int [:] nodes_label = nodes.label

    cdef int nnodes = network.nnodes

    for i in range(1, network.nlinks+1):  # careful of 1-indexing
        link_to = links_ito[i]
        if nodes_label[link_to] != link_to:
            print(f"ADDING LINK {i} {link_to} {network.nnodes}")
            nodes_label[link_to] = link_to
            nnodes += 1

            added += 1
            assert added < 20   # something if too many missing links

    network.nnodes = nnodes


def build_play_matrix(network: Network, params: Parameters,
                      max_links: int):

    nodes = network.nodes
    links = Links(max_links + 1)

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

    try:
        with open(params.input_files.play) as FILE:
            # resets the node label as a flag to check progress?
            for j in range(1, network.nnodes+1):
                nodes_label[j] = -1

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

                line = FILE.readline()
    except Exception as e:
        raise ValueError(f"{params.input_files.play} is corrupted or "
                         f"unreadable? Error = {e.__class__}: {e}")

    renormalise = (params.input_files.play == params.input_files.work)

    for j in range(1, nlinks+1):   # careful 1-indexed
        if renormalise:
            links_weight[j] /= nodes_denominator_p[links_ifrom[j]]

        links_suscept[j] = links_weight[j]

    fill_in_gaps(network)

    cdef int i1 = 0
    cdef int i2 = 0
    cdef double [:] nodes_save_play_suscept = nodes.save_play_suscept

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

    print(f"Number of play links equals {nlinks}")

    network.plinks = nlinks
    network.play = links
