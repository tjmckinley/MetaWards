
from metawards import Parameters

import os
import pytest

script_dir = os.path.dirname(__file__)
ncovparams_csv = os.path.join(script_dir, "data", "ncovparams.csv")

l0 = {'beta2': 0.95, 'beta3': 0.95,
      'progress1': 0.19, 'progress2': 0.91, 'progress3': 0.91}

l1 = {'beta2': 0.90, 'beta3': 0.93,
      'progress1': 0.18, 'progress2': 0.92, 'progress3': 0.90}

@pytest.mark.parametrize('lines, expect',
    [(0, [l0]),
     (1, [l1]),
     ([0,1], [l0,l1]),
     ([1,0], [l0, l1])])
def test_read_variables(lines, expect):
    result = Parameters.read_variables(ncovparams_csv, lines)
    assert result == expect
