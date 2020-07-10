
from metawards import Ward, Wards, Network
import json


def test_wards():
    wards = Wards()
    bristol = Ward(id=1, name="Bristol")
    london = Ward(id=2, name="London")
    bristol.add_workers(500)
    bristol.add_workers(500, destination=2)
    bristol.set_num_players(750)
    london.add_workers(8500)
    london.add_workers(100, destination=1)
    london.set_num_players(10000)
    print(bristol)
    print(london)

    wards.add(bristol)
    wards.add(london)

    print(wards)

    assert wards.num_workers() == 9600
    assert wards.num_players() == 10750
    assert wards.population() == 10750 + 9600

    data = wards.to_data()

    print(data)

    wards2 = Wards.from_data(data)

    print(wards2)

    assert wards == wards2

    try:
        filename = "_test_wards.json"

        with open(filename, "w") as FILE:
            json.dump(data, FILE, indent=2)

        print("".join(open(filename).readlines()))

        with open(filename) as FILE:
            data2 = json.load(FILE)

        wards2 = Wards.from_data(data2)
        print(wards2)
        assert wards == wards2

    finally:
        import os
        os.unlink(filename)

    network = Network.from_wards(wards, disease="lurgy")

    assert network.work_population == wards.num_workers()
    assert network.play_population == wards.num_players()
    assert network.population == wards.population()

    wards2 = network.to_wards()

    assert len(wards) == len(wards2)

    for w1, w2 in zip(wards, wards2):
        if w1 is None:
            assert w2 is None
            continue

        assert w1.id() == w2.id()
        assert w1.name() == w2.name()
        assert w1.info() == w2.info()
        assert w1.num_workers() == w2.num_workers()
        assert w1.num_players() == w2.num_players()
        assert w1.get_player_lists() == w2.get_player_lists()
        assert w1.get_worker_lists() == w2.get_worker_lists()
        assert w1.position() == w2.position()

    s = wards.to_json()
    wards2 = Wards.from_json(s)

    assert wards2 == wards

    filename = wards.to_json("_test_wards_data.json", indent=4)

    print(filename)

    try:
        wards2 = Wards.from_json(filename)
    finally:
        import os
        os.unlink(filename)

    assert wards2 == wards


if __name__ == "__main__":
    test_wards()
