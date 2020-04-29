
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
    total: Network = None

    #: The list of Networks, one for each demographic, ordered in the
    #: same order as the "Demographics" object. This is empty if
    #: only a single demographic is modelled
    subnet: _List[Network] = _field(default_factory=list)

    #: Metadata about each of the demographics being modelled. This is
    #: None if only a single demographic is modelled
    demographics: Demographics = None
