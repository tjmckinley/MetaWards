
from metawards import Parameters, Network, Population, Demographics, WardID, \
    Ward, PersonType
from metawards.movers import MoveGenerator

import os
import pytest

script_dir = os.path.dirname(__file__)
demography_json = os.path.join(script_dir, "data", "demography.json")


def test_move_generator():
    m = MoveGenerator(fraction=0.3)
    assert m.fraction() == 0.3

    m = MoveGenerator(number=1000)
    assert m.number() == 1000

    params = Parameters()
    params.set_disease("lurgy")

    network = Network.single(params, Population(initial=1000))

    m = MoveGenerator(from_stage="E")
    assert m.generate(network) == [[0, 1, 0, 1]]
    assert m.should_move_all()
    assert m.fraction() == 1.0
    assert m.number() > 7000000000

    m = MoveGenerator(from_stage="E", to_stage="R")
    assert m.generate(network) == [[0, 1, 0, 4]]
    assert m.should_move_all()

    m = MoveGenerator(to_stage="R")
    assert m.generate(network) == [[0, 0, 0, 4],
                                   [0, 1, 0, 4],
                                   [0, 2, 0, 4],
                                   [0, 3, 0, 4],
                                   [0, 4, 0, 4]]
    assert m.should_move_all()

    m = MoveGenerator(from_stage=["E", "I1"])
    assert m.generate(network) == [[0, 1, 0, 1],
                                   [0, 2, 0, 2]]
    assert m.should_move_all()

    m = MoveGenerator(from_stage=["E", "I1"], to_stage=["I1", "I2"])
    assert m.generate(network) == [[0, 1, 0, 2],
                                   [0, 2, 0, 3]]
    assert m.should_move_all()

    m = MoveGenerator(from_stage=["E", "I1"], to_stage="R")
    assert m.generate(network) == [[0, 1, 0, 4],
                                   [0, 2, 0, 4]]
    assert m.should_move_all()

    m = MoveGenerator()
    assert m.generate(network) == [[0, 0, 0, 0],
                                   [0, 1, 0, 1],
                                   [0, 2, 0, 2],
                                   [0, 3, 0, 3],
                                   [0, 4, 0, 4]]
    assert m.should_move_all()

    demographics = Demographics.load(demography_json)

    networks = demographics.specialise(network)

    m = MoveGenerator()
    assert m.generate(networks) == [[0, 0, 0, 0],
                                    [0, 1, 0, 1],
                                    [0, 2, 0, 2],
                                    [0, 3, 0, 3],
                                    [0, 4, 0, 4],
                                    [1, 0, 1, 0],
                                    [1, 1, 1, 1],
                                    [1, 2, 1, 2],
                                    [1, 3, 1, 3],
                                    [1, 4, 1, 4],
                                    [2, 0, 2, 0],
                                    [2, 1, 2, 1],
                                    [2, 2, 2, 2],
                                    [2, 3, 2, 3],
                                    [2, 4, 2, 4]
                                    ]

    m = MoveGenerator(from_stage="E")
    assert m.generate(networks) == [[0, 1, 0, 1],
                                    [1, 1, 1, 1],
                                    [2, 1, 2, 1]
                                    ]

    m = MoveGenerator(to_stage="R")
    assert m.generate(networks) == [[0, 0, 0, 4],
                                    [0, 1, 0, 4],
                                    [0, 2, 0, 4],
                                    [0, 3, 0, 4],
                                    [0, 4, 0, 4],
                                    [1, 0, 1, 4],
                                    [1, 1, 1, 4],
                                    [1, 2, 1, 4],
                                    [1, 3, 1, 4],
                                    [1, 4, 1, 4],
                                    [2, 0, 2, 4],
                                    [2, 1, 2, 4],
                                    [2, 2, 2, 4],
                                    [2, 3, 2, 4],
                                    [2, 4, 2, 4]
                                    ]

    m = MoveGenerator(from_demographic="red")
    assert m.generate(networks) == [[0, 0, 0, 0],
                                    [0, 1, 0, 1],
                                    [0, 2, 0, 2],
                                    [0, 3, 0, 3],
                                    [0, 4, 0, 4]]

    m = MoveGenerator(to_demographic="blue")
    assert m.generate(networks) == [[0, 0, 2, 0],
                                    [0, 1, 2, 1],
                                    [0, 2, 2, 2],
                                    [0, 3, 2, 3],
                                    [0, 4, 2, 4],
                                    [1, 0, 2, 0],
                                    [1, 1, 2, 1],
                                    [1, 2, 2, 2],
                                    [1, 3, 2, 3],
                                    [1, 4, 2, 4],
                                    [2, 0, 2, 0],
                                    [2, 1, 2, 1],
                                    [2, 2, 2, 2],
                                    [2, 3, 2, 3],
                                    [2, 4, 2, 4]
                                    ]

    m = MoveGenerator(to_demographic="blue", to_stage="R")
    assert m.generate(networks) == [[0, 0, 2, 4],
                                    [0, 1, 2, 4],
                                    [0, 2, 2, 4],
                                    [0, 3, 2, 4],
                                    [0, 4, 2, 4],
                                    [1, 0, 2, 4],
                                    [1, 1, 2, 4],
                                    [1, 2, 2, 4],
                                    [1, 3, 2, 4],
                                    [1, 4, 2, 4],
                                    [2, 0, 2, 4],
                                    [2, 1, 2, 4],
                                    [2, 2, 2, 4],
                                    [2, 3, 2, 4],
                                    [2, 4, 2, 4]
                                    ]

    m = MoveGenerator(from_demographic="red", to_demographic="blue",
                      from_stage=["I1", "I2"], to_stage="R")

    assert m.generate(networks) == [[0, 2, 2, 4],
                                    [0, 3, 2, 4]]

    m = MoveGenerator(to_ward=1)

    assert m.generate_wards(network) == [[None, (PersonType.PLAYER, 1)]]
    assert m.generate_wards(networks) == [[None, (PersonType.PLAYER, 1)]]
    assert not m.should_move_all()
    assert m.fraction() == 1.0
    assert m.number() > 7000000000

    bristol = Ward("bristol")
    london = Ward("london")
    oxford = Ward("oxford")

    bristol.add_workers(0, destination=london)
    bristol.add_workers(0, destination=oxford)
    london.add_workers(0, destination=bristol)
    london.add_workers(0, destination=oxford)

    network = Network.from_wards(bristol+london+oxford)

    assert len(network.nodes) == network.nnodes + 1
    assert len(network.links) == network.nlinks + 1

    assert network.nnodes == 3
    assert network.nlinks == 4

    m = MoveGenerator(from_ward=["bristol", WardID("bristol", "london")],
                      to_ward="oxford", fraction=0.3, number=100)
    assert not m.should_move_all()
    assert m.fraction() == 0.3
    assert m.number() == 100

    player = PersonType.PLAYER
    worker = PersonType.WORKER

    print(m.generate_wards(network))

    assert m.generate_wards(network) == [[(player, 1), (player, 3)],
                                         [(worker, 1), (player, 3)]
                                         ]

    m = MoveGenerator(from_ward=WardID("oxford", "bristol"), to_ward=1)

    with pytest.raises(KeyError):
        m.generate_wards(network)

    oxford.add_workers(0, destination=bristol)

    network = Network.from_wards(bristol+london+oxford)

    print(m.generate_wards(network))
    assert m.generate_wards(network) == [[(worker, 5), (player, 1)]]

    m = MoveGenerator(from_ward=WardID("bristol", "bristol"),
                      to_ward="oxford")

    with pytest.raises(KeyError):
        m.generate_wards(network)

    bristol.add_workers(0, destination=bristol)

    network = Network.from_wards(bristol + london + oxford)

    print(m.generate_wards(network))
    assert m.generate_wards(network) == [[(worker, 1), (player, 3)]]

    assert network.links.ifrom[1] == network.links.ito[1]
    assert network.links.ifrom[1] == network.get_node_index("bristol")

    m = MoveGenerator(to_ward=WardID("london", "bristol"))

    print(m.generate_wards(network))
    assert m.generate_wards(network) == [[None, (worker, 4)]]

    assert network.links.ifrom[4] == network.get_node_index("london")
    assert network.links.ito[4] == network.get_node_index("bristol")


if __name__ == "__main__":
    test_move_generator()
