
import pytest

from metawards.utils import guess_num_threads_and_procs
from metawards.utils import is_openmp_supported


@pytest.mark.parametrize('args, expected',
                         [
                             ([1, None, None, 53], (53, 1)),
                             ([2, None, None, 53], (26, 2)),
                             ([2, 20, None, 53], (20, 2)),
                             ([2, None, 2, 53], (26, 2)),
                             ([2, 10, 2, 53], (10, 2)),
                         ])
def test_guess(args, expected):
    if is_openmp_supported():
        result = guess_num_threads_and_procs(njobs=args[0],
                                             nthreads=args[1],
                                             nprocs=args[2],
                                             ncores=args[3])
        assert result == expected

@pytest.mark.parametrize('args, expected',
                         [
                             ([1, None, None, 53], (1, 1)),
                             ([2, None, None, 53], (1, 2)),
                             ([2, 20, None, 53], (1, 2)),
                             ([2, None, 2, 53], (1, 2)),
                             ([2, 10, 2, 53], (1, 2)),
                         ])
def test_no_omp(args, expected):
    if not is_openmp_supported():
        result = guess_num_threads_and_procs(njobs=args[0],
                                             nthreads=args[1],
                                             nprocs=args[2],
                                             ncores=args[3])
        assert result == expected
