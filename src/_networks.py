
from dataclasses import dataclass as _dataclass


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