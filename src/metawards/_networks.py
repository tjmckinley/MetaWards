
from dataclasses import dataclass as _dataclass
from dataclasses import field as _field
from typing import List as _List

from ._network import Network
from ._demographics import Demographics

__all__ = ["Networks"]


@_dataclass
class Networks:
    """This is a combination of Network objects which together represent
       an entire diverse population. Each individual Network is used to
       model the disease outbreak within a single demographic of the
       population. Multiple demographics are modelled by combining
       multiple networks. Special merge functions enable joint
       FOIs to be calculated, through which an outbreak in one
       network can cross-infect a demographic in another network.

       The Networks can be very independent, and don't necessarily
       need to have the same links. However, it is assumed (and checked)
       that each network will have the same nodes.
    """

    #: The overall Network, which contains a combination of all of the
    #: sub-networks. This is used for summary analysis and also as
    #: a means of merging and distributing data between sub-networks
    overall: Network = None

    #: The list of Networks, one for each demographic, ordered in the
    #: same order as the "Demographics" object. This is empty if
    #: only a single demographic is modelled
    subnet: _List[Network] = _field(default_factory=list)

    #: Metadata about each of the demographics being modelled. This is
    #: None if only a single demographic is modelled
    demographics: Demographics = None

    @staticmethod
    def build(network: Network, demographics: Demographics):
        """Build the set of networks that will model the passed
           demographics based on the overall population model
           in the passed network

           Parameters
           ----------
           network: Network
             The overall population model - this contains the base
             parameters, wards, work and play links that define
             the model outbreak

           demographics: Demographics
             Information about each of the demographics to be modelled.
             Note that the sum of the "work" and "play" populations
             across all demographics must be 1.0 in all wards in
             the model

           Returns
           -------
           networks: Networks
             The set of Networks that represent the model run over the
             full set of different demographics
        """
        if demographics is None or len(demographics) < 2:
            raise ValueError(f"You can only create a Networks object "
                             f"with a valid Demographics that contains "
                             f"more than one demographic")

        networks = []

        # specialise the network for each demographic
        for i in range(0, len(demographics)):
            networks.append(network.specialise(demographics[i]))

        # now verify that the sum of the populations in each ward across
        # all demographics equals the sum of the overall population in
        # each ward

        result = Networks()
        result.overall = network
        result.networks = networks
        result.demographics = demographics

        return result
