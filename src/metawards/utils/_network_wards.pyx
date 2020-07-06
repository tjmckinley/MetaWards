
from .._network import Network
from .._wards import Wards
from .._ward import Ward

from ._console import Console
from ._profiler import Profiler
from ._get_array_ptr cimport get_int_array_ptr, get_double_array_ptr

__all__ = ["load_from_wards", "save_to_wards"]


def load_from_wards(wards: Wards, profiler: Profiler = None) -> Network:
    """Build and return a Network from the passed set of Wards"""
    if profiler is None:
        from ._profiler import NullProfiler
        profiler = NullProfiler()

    p = profiler.start("load_from_wards")


def save_to_wards(network: Network, profiler: Profiler = None) -> Wards:
    """Build a return a set of Wards constructed from the passed Network"""
    if profiler is None:
        from ._profiler import NullProfiler
        profiler = NullProfiler()

    p = profiler.start("save_to_wards")

    nodes = network.nodes
    links = network.links
    play = network.play
    info = network.info

    cdef int * nodes_label = get_int_array_ptr(nodes.label)
    cdef double * nodes_save_play_suscept = get_double_array_ptr(
                                                    nodes.save_play_suscept)

    cdef double * nodes_x = get_double_array_ptr(nodes.x)
    cdef double * nodes_y = get_double_array_ptr(nodes.y)

    cdef int * links_ifrom = get_int_array_ptr(links.ifrom)
    cdef int * links_ito = get_int_array_ptr(links.ito)
    cdef double * links_weight = get_double_array_ptr(links.weight)

    cdef int * play_ifrom = get_int_array_ptr(play.ifrom)
    cdef int * play_ito = get_int_array_ptr(play.ito)
    cdef double * play_weight = get_double_array_ptr(play.weight)

    cdef int nnodes = network.nnodes
    cdef int nnodes_plus_one = nnodes + 1
    cdef int nlinks = len(links)
    cdef int nplay = len(play)

    cdef int have_info = 1 if (len(info) > 1) else 0
    cdef int xy_coords = 1 if nodes.coordinates == "x/y" else 0

    wards = [None]

    self_weight = [None] * nnodes_plus_one

    cdef int i = 0
    cdef int update_freq = 250
    cdef int ifrom, ito
    cdef double weight
    cdef double diff

    p = p.start("Convert wards")
    with Console.progress() as progress:
        task = progress.add_task("Converting to nodes", total=nnodes_plus_one)

        for i in range(1, nnodes_plus_one):
            ward = Ward(id=nodes_label[i])

            if have_info:
                ward.set_info(info[i])

            if xy_coords:
                ward.set_position(x=nodes_x[i], y=nodes_y[i], units="km")
            else:
                ward.set_position(lat=nodes_x[i], long=nodes_y[i])

            ward.set_num_players(nodes_save_play_suscept[i])

            wards.append(ward)

            if i % update_freq == 0:
                progress.update(task, completed=i)

        progress.update(task, completed=nnodes_plus_one, force_update=True)
    p = p.stop()

    p = p.start("Convert work links")
    with Console.progress() as progress:
        task = progress.add_task("Converting work links", total=nlinks)

        for i in range(0, nlinks):
            ifrom = links_ifrom[i]
            ito = links_ito[i]
            weight = links_weight[i]

            if ifrom == -1 or ito == -1:
                # null link
                continue

            if ito <= 0 or ito > nnodes or ifrom <=0 or ifrom > nnodes:
                Console.error(f"Invalid link? {ifrom}=>{ito}")

            if ifrom == ito and ifrom == 38:
                Console.print(f"ward {ifrom} {ito} => {weight}")

            wards[ifrom].add_workers(destination=ito, number=weight)

            if i % update_freq == 0:
                progress.update(task, completed=i+1)

        progress.update(task, completed=nlinks, force_update=True)
    p = p.stop()

    p = p.start("Convert play links")
    with Console.progress() as progress:
        task = progress.add_task("Converting play links", total=nplay)

        for i in range(0, nplay):
            ifrom = play_ifrom[i]
            ito = play_ito[i]
            weight = play_weight[i]

            if ifrom == -1 or ito == -1:
                # null link
                continue

            if ito <= 0 or ito > nnodes or ifrom <=0 or ifrom > nnodes:
                Console.error(f"Invalid play link? {ifrom}=>{ito}")

            if ifrom == ito:
                self_weight[ifrom] = weight
            else:
                wards[ifrom].add_player_weight(destination=ito, weight=weight)

            if i % update_freq == 0:
                progress.update(task, completed=i+1)

        errors = []

        for i in range(1, nnodes_plus_one):
            weight = wards[i].get_players(destination=i)

            if self_weight[i] is None:
                # the weight should either be zero or one
                if weight > 0.5:
                    self_weight[i] = 1.0
                else:
                    self_weight[i] = 0.0

            diff = abs(self_weight[i] - weight)

            if diff > 1e-6:
                errors.append(
                    f"Ward {i} weight disagreement? {self_weight[i]} "
                    f"versus {weight}")

        if len(errors) > 0:
            Console.error("\n".join(errors))
            raise AssertionError("Disagreement in player weights")

        progress.update(task, completed=nlinks, force_update=True)
    p = p.stop()

    p = p.start("Create Wards")
    wards = Wards(wards)
    p = p.stop()

    p = p.start("Assert sane")
    wards.assert_sane()

    if wards.num_workers() != network.work_population:
        errors.append(
            f"Disagreement in the number of workers: "
            f"{network.work_population} versus "
            f"{wards.num_workers()}")

    if wards.num_players() != network.play_population:
        errors.append(
            f"Disagreement in the number of players: "
            f"{network.play_population} versus "
            f"{wards.num_players()}")

    if len(errors) > 0:
        Console.error("\n".join(errors))
        raise AssertionError("Disagreement in size of the population")

    p = p.stop()

    p = p.stop()

    return wards

