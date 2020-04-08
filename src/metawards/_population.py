
from dataclasses import dataclass
from typing import List
from copy import deepcopy

__all__ = ["Population", "Populations"]


@dataclass
class Population:
    """This class holds information about the progress of the
       disease through the population
    """
    initial: int = 0        # the initial population loaded into the model
    susceptibles: int = 0   # the number of members who could be infected
    latent: int = 0         # the number of latent infections
    total: int = 0          # the total number of infections
    recovereds: int = 0     # the total number of recovered members
    n_inf_wards: int = 0    # the number of infected in wards

    @property
    def population(self) -> int:
        return self.susceptibles + self.total + self.recovereds

    def __str__(self):
        return f"S: {self.susceptibles}    " \
               f"E: {self.latent}    " \
               f"I: {self.total}    " \
               f"R: {self.recovereds}    " \
               f"IW: {self.n_inf_wards}   " \
               f"TOTAL POPULATION {self.population}"


@dataclass
class Populations:
    """This class holds the trajectory of Population objects recorded
       for every step (day) of a model outbreak
    """
    _trajectory: List[Population] = None  # the trajectory of Populations

    def __str__(self):
        if len(self) == 0:
            return "Populations:empty"
        else:
            return f"Latest (day {len(self)-1}): {self._trajectory[-1]}"

    def __getitem__(self, i: int):
        """Return the ith Population in the trajectory"""
        if self._trajectory is None:
            raise IndexError("No trajectory data collected")
        else:
            return self._trajectory[i]

    def __len__(self):
        if self._trajectory is None:
            return 0
        else:
            return len(self._trajectory)

    def append(self, population: Population):
        """Append the next step in the trajectory"""
        if not isinstance(population, Population):
            raise TypeError("Only Population objects should be recorded!")

        if self._trajectory is None:
            self._trajectory = []

        self._trajectory.append(deepcopy(population))
