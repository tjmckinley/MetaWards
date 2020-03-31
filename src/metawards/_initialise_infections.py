
from array import array

from ._network import Network

__all__ = ["initialise_infections",
           "initialise_play_infections"]


def initialise_infections(network: Network):
    """Initialise the data structure used to store the infections"""

    params = network.params

    if params is None:
        return None

    disease = params.disease_params

    n = disease.N_INF_CLASSES()

    infections = []

    nlinks = network.nlinks + 1

    int_t = "i"
    null_int = nlinks * [0]

    for _ in range(0, n):
        infections.append( array(int_t, null_int) )

    return infections


def initialise_play_infections(network: Network):
    """Initialise the space used to store the play infections"""

    params = network.params

    if params is None:
        return None

    disease = params.disease_params

    n = disease.N_INF_CLASSES()

    infections = []

    nnodes = network.nnodes + 1

    int_t = "i"
    null_int = nnodes * [0]

    for _ in range(0, n):
        infections.append( array(int_t, null_int) )

    return infections
