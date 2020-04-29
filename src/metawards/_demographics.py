
from dataclasses import dataclass as _dataclass
from dataclasses import field as _field
from typing import List as _List
from typing import Dict as _Dict

from ._demographic import Demographic

__all__ = ["Demographics"]


@_dataclass
class Demographics:
    """This class holds metadata about all of the demographics
       being modelled
    """
    #: The list of individual Demographic objects, one for each
    #: demographic being modelled
    demographics: _List[Demographic] = _field(default_factory=list)

    #: Map from index to names of demographics - enables lookup by name
    _names: _Dict[str, int] = _field(default_factory=dict)

    def add(self, demographic: Demographic):
        """Add a demographic to the set to be modelled"""
        if demographic.name in self._names:
            raise ValueError(
                    f"There is already a demographic called "
                    f"{demographic.name} in this set. Please rename "
                    f"and try again.")

        self.demographics.append(demographic)
        self._names[demographic.name] = len(self.demographics) - 1
