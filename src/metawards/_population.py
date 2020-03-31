
from dataclasses import dataclass

__all__ = ["Population"]


@dataclass
class Population:
    """This class holds information about the progress of the
       disease through the population
    """
    initial: int = 0        # the initial population loaded into the model
    susceptibles: int = 0   # the number of members who could be infected
    latent: int = 0         # the number of latent infections
    total: int = 0          # the total number of infections
    recovereds: int = 0     # the total number of recovered members
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
