
from metawards import Parameters, Disease

import pytest


def test_parameter():

    d = Disease.get_disease("ncov")

    # first sanity test that we can create this disease
    p = Parameters.create("ncov")

    assert(p.beta == list(d.beta))
    assert(p.TooIllToMove == list(d.TooIllToMove))

    # and that it can be "str'd"
    s = str(p)
    print(s)

    # assert that invalid diseases throw KeyError
    with pytest.raises(KeyError):
        p = Parameters.create("not a disease")

