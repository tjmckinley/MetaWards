
from .._network import Network
from .._wards import Wards
from .._ward import Ward

from ._console import Console
from ._profiler import Profiler

__all__ = ["load_from_wards", "save_to_wards"]


def load_from_wards(wards: Wards) -> Network:
    """Build and return a Network from the passed set of Wards"""
    pass


def save_to_wards(network: Network) -> Wards:
    """Build a return a set of Wards constructed from the passed Network"""

    p = Profiler().start("save_to_wards")

    wards = network.nodes
    links = network.links
    play = network.play
    info = network.info

    nnodes_plus_one = network.nnodes + 1

    have_info = (len(info) > 1)

    wards = [None]

    update_freq = 100

    p = p.start("Convert wards")
    with Console.progress() as progress:
        task = progress.add_task("Converting to wards", total=nnodes_plus_one)

        for i in range(1, nnodes_plus_one):
            ward = Ward(id=wards.label[i])

            if have_info:
                ward.set_info(info[i])

            ward.set_num_players(wards.save_play_suscept[i])

            wards.append(ward)

            if i % update_freq == 0:
                progress.update(task, completed=i)

        progress.update(task, completed=nnodes_plus_one, force_update=True)

    p = p.stop()

    p = p.start("Create Wards")
    wards = Wards(wards)
    p = p.stop()

    p = p.start("Assert sane")
    #wards.assert_sane()
    p = p.stop()

    p = p.stop()
    Console.print(p)

    return wards

