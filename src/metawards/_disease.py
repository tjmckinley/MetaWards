
from dataclasses import dataclass
from typing import List

__all__ = ["Disease"]

_N_INF_CLASSES = 5   # the number of parameters in each list

_diseases = {}

@dataclass
class Disease:
    """This class holds the parameters about a single disease"""
    beta: List[float] = None
    progress: List[float] = None
    too_ill_to_move: List[float] = None
    contrib_foi: List[float] = None

    def __str__(self):
        return f"beta = {self.beta}\n" \
               f"progress = {self.progress}\n" \
               f"too_ill_to_move = {self.too_ill_to_move}\n" \
               f"contrib_foi = {self.contrib_foi}\n"

    def __eq__(self, other):
        return self.beta == other.beta and \
               self.progress == other.progress and \
               self.too_ill_to_move == other.too_ill_to_move and \
               self.contrib_foi == other.contrib_foi

    @staticmethod
    def N_INF_CLASSES():
        global _N_INF_CLASSES
        return _N_INF_CLASSES

    @staticmethod
    def set_disease(name: str, disease):
        """Set the parameters for the named disease"""
        if not isinstance(disease, Disease):
            raise TypeError("The disease should be type 'Disease'")

        try:
            assert(len(disease.beta) == _N_INF_CLASSES)
            assert(len(disease.progress) == _N_INF_CLASSES)
            assert(len(disease.too_ill_to_move) == _N_INF_CLASSES)
            assert(len(disease.contrib_foi) == _N_INF_CLASSES)
        except Exception:
            raise ValueError(f"The number of parameters for each list "
                             f"in the disease must be {_N_INF_CLASSES}")

        global _diseases
        _diseases[str(name).lower().strip()] = disease

    @staticmethod
    def get_disease(name: str):
        """Return the parameters for the named disease"""
        global _diseases
        try:
            return _diseases[str(name).lower().strip()]
        except KeyError:
            raise KeyError(f"There are no parameters for disease '{name}' "
                           f"Known diseases are {list(_diseases.keys())}")

# Initialise the _diseases dictionary with data for ncov. Ideally
# this would come from a json data file (or equivalent) to stop
# researchers having to edit this code. They can use the
# "set_disease" function above to change this though
_ncov = Disease()

_ncov.beta = [0.0, 0.0, 0.95, 0.95, 0.0]
_ncov.progress = [1.0, 0.1923, 0.909091, 0.909091, 0.0]
_ncov.too_ill_to_move = [0.0, 0.0, 0.0, 0.0, 0.0]
_ncov.contrib_foi = [1.0, 1.0, 1.0, 1.0, 0.0]

Disease.set_disease("ncov", _ncov)
