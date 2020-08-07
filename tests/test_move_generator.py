
from metawards import Parameters, Network, Population, Demographics
from metawards.movers import MoveGenerator

import os

script_dir = os.path.dirname(__file__)
demography_json = os.path.join(script_dir, "data", "demography.json")


def test_move_generator():
    params = Parameters()
    params.set_disease("lurgy")

    network = Network.single(params, Population(initial=1000))

    m = MoveGenerator(from_stage="E")
    assert m.generate(network) == [[0, 1, 0, 1]]

    m = MoveGenerator(from_stage="E", to_stage="R")
    assert m.generate(network) == [[0, 1, 0, 4]]

    m = MoveGenerator(to_stage="R")
    assert m.generate(network) == [[0, 0, 0, 4],
                                   [0, 1, 0, 4],
                                   [0, 2, 0, 4],
                                   [0, 3, 0, 4],
                                   [0, 4, 0, 4]]

    m = MoveGenerator(from_stage=["E", "I1"])
    assert m.generate(network) == [[0, 1, 0, 1],
                                   [0, 2, 0, 2]]

    m = MoveGenerator(from_stage=["E", "I1"], to_stage=["I1", "I2"])
    assert m.generate(network) == [[0, 1, 0, 2],
                                   [0, 2, 0, 3]]

    m = MoveGenerator(from_stage=["E", "I1"], to_stage="R")
    assert m.generate(network) == [[0, 1, 0, 4],
                                   [0, 2, 0, 4]]

    m = MoveGenerator()
    assert m.generate(network) == [[0, 0, 0, 0],
                                   [0, 1, 0, 1],
                                   [0, 2, 0, 2],
                                   [0, 3, 0, 3],
                                   [0, 4, 0, 4]]

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


if __name__ == "__main__":
    test_move_generator()
