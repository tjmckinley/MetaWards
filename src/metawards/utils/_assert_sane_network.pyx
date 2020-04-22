
from .._network import Network

__all__ = ["assert_sane_network"]


def assert_sane_network(network: Network):
    """This function runs through and checks that the passed network
       is sane. If it is not, it prints some information and raises
       an AssertionError
    """
    pass

    # Will add sanity checks as I get to fully understand this
    # data layout...
