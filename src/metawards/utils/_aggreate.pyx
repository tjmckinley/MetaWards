
from .._networks import Networks
from .._infections import Infections

__all__ = ["aggregate_networks"]


def aggregate_networks(network: Networks, infections: Infections) -> None:
    """Aggregate all of the infection data from the demographic
       sub-networks into an overall total set of infection data
       that is stored in the overall network and infections

       Parameters
       ----------
       network: Networks
         The collection of networks to be aggregated
       infections: Infections
         The complete set of infection data
    """

