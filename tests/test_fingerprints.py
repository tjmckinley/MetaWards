
import pytest

from metawards import VariableSet


@pytest.mark.parametrize('vals',
                         [[0.4],
                          [0, 1, 2, 3, 4],
                          [0.5, 0.7, True, False, 1.3, 22.9]
                          ])
def test_fingerprints(vals):
    fingerprint = VariableSet.create_fingerprint(vals=vals)

    result, repeat = VariableSet.extract_values(fingerprint)

    assert result == vals
    assert repeat is None

    for i in range(0, 10):
        fingerprint = VariableSet.create_fingerprint(vals=vals, index=i,
                                                     include_index=True)

        result, repeat = VariableSet.extract_values(fingerprint)

        assert result == vals
        assert repeat == i
