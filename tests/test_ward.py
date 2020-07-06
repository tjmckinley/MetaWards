
from metawards import WardInfo, Ward, Wards, Parameters, Network
from metawards.utils import Profiler, Console
import json
import pytest


def test_ward_json():
    w = WardInfo(name="something", alternate_names=["one", "two"],
                 code="123", alternate_codes=["1", "2", "cat"],
                 authority="somewhere", authority_code="s123",
                 region="place name", region_code="r789")

    s = json.dumps(w.to_data())
    print(s)

    w2 = WardInfo.from_data(json.loads(s))

    assert w == w2

    ward = Ward(id=10, info=w)

    ward.set_position(x=1500, y=2500, units="m")
    ward.set_num_players(1200)
    ward.set_num_workers(500)

    ward.add_workers(number=30, destination=1)
    ward.add_workers(number=20, destination=30)

    ward.add_player_weight(weight=0.2, destination=30)
    ward.add_player_weight(weight=0.5, destination=1)

    print(ward)

    s = json.dumps(ward.to_data())

    print(s)

    ward2 = Ward.from_data(json.loads(s))

    assert json.dumps(ward.to_data()) == json.dumps(ward2.to_data())
    assert ward == ward2

    ward2.set_id(30)

    ward3 = Ward.from_data(json.loads(s))
    ward3.set_id(1)

    wards = Wards([ward, ward2, ward3])

    print(wards)

    assert wards[ward.id()] == ward
    assert wards[ward2.id()] == ward2
    assert wards[ward3.id()] == ward3

    s = json.dumps(wards.to_data())

    print(s)

    wards2 = Wards.from_data(json.loads(s))

    assert wards == wards2

    ward3.set_id(4)
    wards2.insert(ward3)

    assert wards != wards2


@pytest.mark.slow
def test_ward_conversion():
    # load all of the parameters
    try:
        params = Parameters.load(parameters="march29")
    except Exception as e:
        print(f"Unable to load parameter files. Make sure that you have "
              f"cloned the MetaWardsData repository and have set the "
              f"environment variable METAWARDSDATA to point to the "
              f"local directory containing the repository, e.g. the "
              f"default is $HOME/GitHub/MetaWardsData")
        raise e

    params.set_input_files("2011Data")

    print("Building the network...")
    network = Network.build(params=params)

    profiler = Profiler()

    profiler = profiler.start("to_json")
    wards = network.to_wards(profiler=profiler)

    print("Converting to data...")
    data = wards.to_data(profiler=profiler)

    print("Converting to json...")
    profiler = profiler.start("Convert to JSON")
    s = json.dumps(data)
    profiler = profiler.stop()

    profiler = profiler.stop()  #  end to_json

    print(f"Done: {s[0:250]}...")

    print(f"Converting from json...")
    profiler = profiler.start("Convert from JSON")

    profiler = profiler.start("from_json")
    data = json.loads(s)
    profiler = profiler.stop()

    wards2 = Wards.from_data(data, profiler=profiler)

    network2 = Network.from_wards(wards2, profiler=profiler)

    profiler = profiler.stop()

    Console.print(profiler)


if __name__ == "__main__":
    test_ward_json()
    test_ward_conversion()
