
from ._network import Network
from ._parameters import Parameters
from typing import List

__all__ = ["run_model"]


def run_model(network: Network, params: Parameters,
              infections: List[int], play_infections: List[int],
              rng, to_seed: List[float], s: int):
    """Actually run the model... Real work happens here"""
    # todo
    pass
