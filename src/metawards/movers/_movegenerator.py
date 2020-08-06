
from typing import Union as _Union

from .._wardid import WardID
from .._network import Network
from .._networks import Networks

__all__ = ["MoveGenerator"]


def _int_or_str(x):
    try:
        return int(x)
    except Exception:
        return str(x)


def _parse_int_or_str(x):
    if isinstance(x, list):
        if len(x) == 0:
            return None
        else:
            return [_int_or_str(y) for y in x]
    elif x is not None:
        return [_int_or_str(x)]
    else:
        return None


def _parse_ward(x):
    if isinstance(x, list):
        if len(x) == 0:
            return None
        else:
            return [y if isinstance(y, WardID) else WardID(y) for y in x]
    elif x is not None:
        return [x if isinstance(x, WardID) else WardID(x)]
    else:
        return None


class MoveGenerator:
    def __init__(self, from_demographic=None, to_demographic=None,
                 from_stage=None, to_stage=None,
                 from_ward=None, to_ward=None,
                 fraction: float = 1.0,
                 number: int = None):
        self._from_demo = _parse_int_or_str(from_demographic)
        self._to_demo = _parse_int_or_str(to_demographic)

        self._from_stage = _parse_int_or_str(from_stage)
        self._to_stage = _parse_int_or_str(to_stage)

        self._from_ward = _parse_ward(from_ward)
        self._to_ward = _parse_ward(to_ward)

        self._fraction = float(fraction)

        if self._fraction < 0:
            self._fraction = 0.0
        elif self._fraction > 1:
            self._fraction = 1.0

        if number is not None:
            self._number = int(number)

            if self._number < 0:
                self._number = 0
        else:
            #  a large number that is greater than any ward population
            self._number = 2 ** 32

    def generate(self, network: _Union[Network, Networks]):
        """Return a list indexes of the demographics plus infexes
           of the disease stages for from and to for the
           passed networok. This returns a list of quads of
           indicies, e.g.

           [ [from_demographic, from_stage, to_demographic, to_stage],
             [from_demographic, from_stage, to_demographic, to_stage],
             ...
           ]
        """
        if isinstance(network, Network):
            # make sure that we are only working with a single demographic

            disease = network.params.disease_params

            from_stages = self._from_stage
            to_stages = self._to_stage

            if from_stages is None:
                from_stages = list(range(0, len(disease)))
            else:
                from_stages = [disease.get_index(x) for x in from_stages]

            if to_stages is None:
                to_stages = from_stages
            elif len(to_stages) == 1:
                to_stages = len(from_stages) * \
                    [disease.get_index(to_stages[0])]
            elif len(to_stages) != len(from_stages):
                raise ValueError(
                    f"{from_stages} incompatible with {to_stages}")
            else:
                to_stages = [disease.get_index(x) for x in to_stages]

            return [[0, x, 0, y] for x, y in zip(from_stages, to_stages)]
        else:
            raise NotImplementedError("Write the code Chris ;-)")
