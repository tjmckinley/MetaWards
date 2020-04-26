
from metawards import Network, Parameters


def test_lookup():
    params = Parameters()
    params.set_input_files("2011Data")
    params.set_disease("ncov")

    network = Network.build(params, profile=True)

    info = network.info

    bristol = info.find("Bristol")

    assert len(bristol) == 0

    clifton = info.find("Clifton")

    for c in clifton:
        assert info[c].name.find("Clifton") != -1

    assert len(clifton) == 13

    clifton2 = info.find("clifton")

    assert clifton == clifton2

    bristol = info.find_by_authority("bristol")

    assert len(bristol) == 35

    clifton_bristol = info.find("Clifton", authority="Bristol")

    assert len(clifton_bristol) == 2

    clifton_bristol = info.find("clifton", authority="bristol",
                                best_match=True)

    assert clifton_bristol == 3662

    clifton = info[clifton_bristol]

    assert clifton.name == "Clifton"
    assert clifton.code == "E05001980"
    assert clifton.alternate_names[0] == "Clifton"
    assert clifton.alternate_codes[0] == "E36000533"
    assert clifton.authority == "Bristol, City of"
    assert clifton.authority_code == "E06000023"

    clifton2 = info.find_by_code("E05001980")

    assert clifton2[0] == clifton_bristol


if __name__ == "__main__":
    test_lookup()
