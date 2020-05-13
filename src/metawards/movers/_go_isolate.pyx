
from typing import Union as _Union
from typing import List as _List

from .._networks import Networks

__all__ = ["go_isolate"]


DemographicID = _Union[str, int]
DemographicIDs = _List[DemographicID]


def go_isolate(go_from: _Union[DemographicID, DemographicIDs],
               go_to: DemographicID,
               network: Networks,
               self_isolate_stage: int = 2,
               duration: int = 7,
               release_to: DemographicID = None,
                **kwargs) -> None:
    """This go function will move individuals from the "from"
       demographic(s) to the "to" demographic if they show any
       signs of infection (the disease stage is greater or equal
       to 'self_isolate_stage' - by default this is level '2',
       which is one level above "latent"). Individuals are held
       in the new demographic for "duration" days, before being
       returned either to their original demographic, or
       released to the "release_to" demographic

       Parameters
       ----------
       from: DemographicID or DemographicIDs
         ID (name or index) or IDs of the demographics to scan for
         infected individuals
       to: DemographicID
         ID (name or index) of the demographic to send infected
         individuals to
       network: Networks
         The networks to be modelled. This must contain all of the
         demographics that are needed for this go function
       self_isolate_stage: int
         The stage of infection an individual must be at before they
         are moved into this demographic
       duration: int
         The number of days an individual should isolate for
       release_to: DemographicID
         ID (name or index) that the individual should move to after
         existing isolation. If this is not set, then the individual
         will return to their original demographic
    """

    # make sure that all of the needed demographic exist
    print("Go isolate!")
