
from metawards import Parameters, Disease

import pytest
import os

script_dir = os.path.dirname(__file__)
ncovparams_csv = os.path.join(script_dir, "data", "ncovparams.csv")


def test_parameter():

    d = Disease.get_disease("ncov")

    # first sanity test that we can create this disease
    p = Parameters.create("ncov")

    assert(p.disease_params == d)

    # and that it can be "str'd"
    s = str(p)
    print(s)

    # assert that invalid diseases throw KeyError
    with pytest.raises(KeyError):
        p = Parameters.create("not a disease")

    p.read_file(ncovparams_csv, 0)

    assert(p.disease_params.beta[2] == 0.95)
    assert(p.disease_params.beta[3] == 0.95)
    assert(p.disease_params.progress[1] == 0.19)
    assert(p.disease_params.progress[2] == 0.91)
    assert(p.disease_params.progress[3] == 0.91)
