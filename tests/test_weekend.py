
from metawards import Ward, Wards, Parameters, Network, OutputFiles, \
    Population

import os
import sys
import pytest

script_dir = os.path.dirname(__file__)


def _run_player():
    w1 = Ward(id=1, name="w1")
    w1.set_num_players(1000)

    w2 = Ward(id=2, name="w2")
    w2.set_num_players(1000)

    w1.add_player_weight(0.5, w2)
    w2.add_player_weight(0.5, w1)

    wards = Wards([w1, w2])

    # load all of the parameters
    try:
        params = Parameters.load(parameters="march29")
    except Exception as e:
        print("Unable to load parameter files. Make sure that you have "
              "cloned the MetaWardsData repository and have set the "
              "environment variable METAWARDSDATA to point to the "
              "local directory containing the repository, e.g. the "
              "default is $HOME/GitHub/MetaWardsData")
        raise e

    params.set_disease(os.path.join(script_dir, "data", "ncov.json"))
    params.add_seeds("5")

    population = Population(initial=wards.population())

    network = Network.from_wards(wards, params=params)

    print("Run the model...")
    outdir = os.path.join(script_dir, "test_weekend_output")

    try:
        with OutputFiles(outdir, force_empty=True) as output_dir:
            trajectory = network.run(population=population,
                                     output_dir=output_dir,
                                     nthreads=1)
    except Exception as e:
        raise e
    finally:
        OutputFiles.remove(outdir, prompt=None)

    print("End of the run")

    return trajectory


def _run_worker():
    w1 = Ward(id=1, name="w1")
    w1.add_workers(1000)

    w2 = Ward(id=2, name="w2")
    w2.add_workers(1000)

    w1.add_player_weight(0.5, w2)
    w2.add_player_weight(0.5, w1)

    wards = Wards([w1, w2])

    # load all of the parameters
    try:
        params = Parameters.load(parameters="march29")
    except Exception as e:
        print("Unable to load parameter files. Make sure that you have "
              "cloned the MetaWardsData repository and have set the "
              "environment variable METAWARDSDATA to point to the "
              "local directory containing the repository, e.g. the "
              "default is $HOME/GitHub/MetaWardsData")
        raise e

    params.set_disease(os.path.join(script_dir, "data", "ncov.json"))
    params.add_seeds("5")

    population = Population(initial=wards.population())

    network = Network.from_wards(wards, params=params)

    print("Run the model...")
    outdir = os.path.join(script_dir, "test_weekend_output")

    try:
        with OutputFiles(outdir, force_empty=True) as output_dir:
            trajectory = network.run(population=population,
                                     output_dir=output_dir,
                                     nthreads=1)
    except Exception as e:
        raise e
    finally:
        OutputFiles.remove(outdir, prompt=None)

    print("End of the run")

    return trajectory


def _run_worker_as_player():
    w1 = Ward(id=1, name="w1")
    w1.add_workers(1000)

    w2 = Ward(id=2, name="w2")
    w2.add_workers(1000)

    w1.add_player_weight(0.5, w2)
    w2.add_player_weight(0.5, w1)

    wards = Wards([w1, w2])

    # load all of the parameters
    try:
        params = Parameters.load(parameters="march29")
    except Exception as e:
        print("Unable to load parameter files. Make sure that you have "
              "cloned the MetaWardsData repository and have set the "
              "environment variable METAWARDSDATA to point to the "
              "local directory containing the repository, e.g. the "
              "default is $HOME/GitHub/MetaWardsData")
        raise e

    params.set_disease(os.path.join(script_dir, "data", "ncov.json"))
    params.add_seeds("5")

    population = Population(initial=wards.population())

    network = Network.from_wards(wards, params=params)

    print("Run the model...")
    outdir = os.path.join(script_dir, "test_weekend_output")

    try:
        with OutputFiles(outdir, force_empty=True) as output_dir:
            trajectory = network.run(population=population,
                                     output_dir=output_dir,
                                     nthreads=1,
                                     iterator="iterate_weekend")
    except Exception as e:
        raise e
    finally:
        OutputFiles.remove(outdir, prompt=None)

    print("End of the run")

    return trajectory


class suppress_output:
    def __init__(self, suppress_stdout=False, suppress_stderr=False):
        self.suppress_stdout = suppress_stdout
        self.suppress_stderr = suppress_stderr
        self._stdout = None
        self._stderr = None

    def __enter__(self):
        devnull = open(os.devnull, "w")
        if self.suppress_stdout:
            self._stdout = sys.stdout
            sys.stdout = devnull

        if self.suppress_stderr:
            self._stderr = sys.stderr
            sys.stderr = devnull

    def __exit__(self, *args):
        if self.suppress_stdout:
            sys.stdout = self._stdout
        if self.suppress_stderr:
            sys.stderr = self._stderr


def test_weekend():

    num_runs = 5

    avg_players = 0
    avg_workers = 0
    avg_workers_as_players = 0

    for i in range(0, num_runs):
        with suppress_output(suppress_stdout=True, suppress_stderr=True):
            t = _run_player()
        avg_players += t[-1].recovereds

    for i in range(0, num_runs):
        with suppress_output(suppress_stdout=True, suppress_stderr=True):
            t = _run_worker()
        avg_workers += t[-1].recovereds

    for i in range(0, num_runs):
        with suppress_output(suppress_stdout=True, suppress_stderr=True):
            t = _run_worker_as_player()
            avg_workers_as_players += t[-1].recovereds

    avg_players /= num_runs
    avg_workers /= num_runs
    avg_workers_as_players /= num_runs

    print(avg_players, avg_workers, avg_workers_as_players)

    # It should be that avg_workers is roughly half of
    # avg_players, while avg_workers_as_players is roughly
    # equal to avg_players - here we are testing that they
    # are approximately equal to within 10%
    assert avg_players == pytest.approx(avg_workers_as_players, 0.1)
    assert avg_workers == pytest.approx(0.5*avg_players, 0.1)


if __name__ == "__main__":
    test_weekend()
