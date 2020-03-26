
from dataclasses import dataclass
from typing import Tuple

__all__ = ["Disease"]

# This is the type for the Disease parameters
_Tuple_N = Tuple[float, float, float, float, float]

_N_INF_CLASSES = 5   # should equal number of items in above tuple
                     # (would be great if typing.Tuple had a function
                     #  to return this...)

_diseases = {}

class Disease:
    """This class holds the parameters about a single disease"""
    beta: _Tuple_N
    progress: _Tuple_N
    TooIllToMove: _Tuple_N
    ContribFOI: _Tuple_N

    @staticmethod
    def N_INF_CLASSES():
        global _N_INF_CLASSES
        return _N_INF_CLASSES

    @staticmethod
    def set_disease(name: str, disease):
        """Set the parameters for the named disease"""
        if not isinstance(disease, Disease):
            raise TypeError("The disease should be type 'Disease'")

        global _diseases
        _diseases[name.lower().strip()] = disease

    @staticmethod
    def get_disease(name: str):
        """Return the parameters for the named disease"""
        global _diseases
        try:
            return _diseases[name.lower().strip()]
        except KeyError:
            raise KeyError(f"There are no parameters for disease '{name}' "
                           f"Known diseases are {list(_diseases.keys())}")

# Initialise the _diseases dictionary with data for ncov. Ideally
# this would come from a json data file (or equivalent) to stop
# researchers having to edit this code. They can use the
# "set_disease" function above to change this though
_ncov = Disease()

_ncov.beta = (0.0, 0.0, 0.95, 0.95, 0.0)
_ncov.progress = (1.0, 0.1923, 0.909091, 0.909091, 0.0)
_ncov.TooIllToMove = (0.0, 0.0, 0.0, 0.0, 0.0)
_ncov.ContribFOI = (1.0, 1.0, 1.0, 1.0, 0.0)

Disease.set_disease("ncov", _ncov)
