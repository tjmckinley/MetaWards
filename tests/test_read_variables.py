
from metawards import Parameters, Disease, VariableSet, VariableSets

import os
import pytest

script_dir = os.path.dirname(__file__)
ncovparams_csv = os.path.join(script_dir, "data", "ncovparams.csv")

l0 = {'beta2': 0.95, 'beta3': 0.95,
      'progress1': 0.19, 'progress2': 0.91, 'progress3': 0.91}

l1 = {'beta2': 0.90, 'beta3': 0.93,
      'progress1': 0.18, 'progress2': 0.92, 'progress3': 0.90}

vars01 = VariableSets()
vars01.append(l0)
vars01.append(l1)

vars0 = VariableSets()
vars0.append(l0)

vars1 = VariableSets()
vars1.append(l1)


@pytest.mark.parametrize('lines, expect',
                         [(0, vars0),
                          (1, vars1),
                          ([0, 1], vars01),
                          ([1, 0], vars01)])
def test_read_variables(lines, expect):
    result = Parameters.read_variables(ncovparams_csv, lines)
    print(f"{result} == {expect}?")
    assert result == expect


def test_parameterset():
    vars0 = VariableSet(l0)

    assert vars0.repeat_index() == 1

    for key, value in l0.items():
        assert key in vars0.variable_names()
        assert value in vars0.variable_values()
        assert vars0.variables()[key] == value

    vars1 = VariableSet(l1, 2)

    assert vars1.repeat_index() == 2

    for key, value in l1.items():
        assert key in vars1.variable_names()
        assert value in vars1.variable_values()
        assert vars1.variables()[key] == value

    assert vars0.fingerprint() != vars1.fingerprint()
    assert vars0.fingerprint() != vars0.fingerprint(include_index=True)
    assert vars1.fingerprint() != vars1.fingerprint(include_index=True)

    variables = VariableSets()
    assert len(variables) == 0

    variables.append(vars0)
    variables.append(vars1)

    assert len(variables) == 2
    assert variables[0] == vars0
    assert variables[1] == vars1

    variables = variables.repeat(5)

    assert len(variables) == 10

    for i in range(0, 5):
        idx0 = 2*i
        idx1 = idx0 + 1

        assert variables[idx0] == l0
        assert variables[idx1] == l1
        assert variables[idx0].fingerprint() == vars0.fingerprint()
        assert variables[idx1].fingerprint() == vars1.fingerprint()
        assert variables[idx0].repeat_index() == i+1
        assert variables[idx1].repeat_index() == i+1


def test_set_variables():
    d = Disease.load("ncov")

    p = Parameters()
    p.set_disease("ncov")

    assert p.disease_params == d

    variables = VariableSet(l1)

    p2 = p.set_variables(variables)

    assert p.disease_params == d
    assert p2.disease_params != d

    assert p2.disease_params.beta[2] == 0.9
    assert p2.disease_params.beta[3] == 0.93
    assert p2.disease_params.progress[1] == 0.18
    assert p2.disease_params.progress[2] == 0.92
    assert p2.disease_params.progress[3] == 0.90

    variables = VariableSet(l0)

    p3 = p2.set_variables(variables)

    assert p3.disease_params.beta[2] == 0.95
    assert p3.disease_params.beta[3] == 0.95
    assert p3.disease_params.progress[1] == 0.19
    assert p3.disease_params.progress[2] == 0.91
    assert p3.disease_params.progress[3] == 0.91

