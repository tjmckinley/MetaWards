
from metawards import WardInfo, Ward, Wards
import json


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


if __name__ == "__main__":
    test_ward_json()
