
from metawards import Parameters, Network, Population
from metawards.movers import MoveGenerator


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


if __name__ == "__main__":
    test_move_generator()
