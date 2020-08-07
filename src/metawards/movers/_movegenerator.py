
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
            self._number = 2 ** 63

    def fraction(self):
        """Return the fraction of individuals in each ward or
           ward-link who should be moved"""
        return self._fraction

    def number(self):
        """Return the maximum number of individuals in each ward
           of ward-link who should move
        """
        return self._number

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
            if self._from_demo is not None:
                for demo in self._from_demo:
                    if demo != 0 or demo != network.name:
                        raise ValueError(
                            f"Incompatible demographic: {self._from_demo}")

            if self._to_demo is not None:
                for demo in self._to_demo:
                    if demo != 0 or demo != network.name:
                        raise ValueError(
                            f"Incompatible demographic: {self._to_demo}")

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
            from_demos = self._from_demo
            to_demos = self._to_demo

            if from_demos is None:
                from_demos = list(range(0, len(network.subnets)))
            else:
                from_demos = [network.demographics.get_index(x)
                              for x in from_demos]

            if to_demos is None:
                to_demos = from_demos
            elif len(to_demos) == 1:
                to_demos = len(from_demos) * \
                    [network.demographics.get_index(to_demos[0])]
            elif len(to_demos) != len(from_demos):
                raise ValueError(
                    f"{from_demos} incompatible wiht {to_demos}")
            else:
                to_demos = [network.demographics.get_index(x)
                            for x in to_demos]

            moves = []

            for from_demo, to_demo in zip(from_demos, to_demos):
                from_disease = network.subnets[from_demo].params.disease_params
                to_disease = network.subnets[to_demo].params.disease_params

                from_stages = self._from_stage
                to_stages = self._to_stage

                if len(from_disease) != len(to_disease):
                    raise ValueError(
                        f"Cannot demographics without specifying the disease "
                        f"stages to move because the disease for demographic "
                        f"{from_demo} ({from_disease}) is different to the "
                        f"disease for {to_demo} ({to_disease})")

                if from_stages is None:
                    from_stages = list(range(0, len(from_disease)))
                else:
                    from_stages = [from_disease.get_index(x)
                                   for x in from_stages]

                if to_stages is None:
                    to_stages = from_stages
                elif len(to_stages) == 1:
                    to_stages = len(from_stages) * \
                        [to_disease.get_index(to_stages[0])]
                elif len(to_stages) != len(from_stages):
                    raise ValueError(
                        f"{from_stages} incompatible with {to_stages}")
                else:
                    to_stages = [to_disease.get_index(x) for x in to_stages]

                moves += [[from_demo, x, to_demo, y]
                          for x, y in zip(from_stages, to_stages)]

            return moves

    def should_move_all(self):
        """Return whether or not all individuals in the specified
           demographics / disease stages should be moved
        """
        return self._from_ward is None and self._to_ward is None

    def generate_wards(self, network):
        """Return a list of ward to ward moves for workers and players.
           This returns None if all individuals should be moved
        """
        if self.should_move_all():
            return None

        if isinstance(network, Networks):
            network = network.overall

        from_wards = self._from_ward
        to_wards = self._to_ward

        if from_wards is None:
            if len(to_wards) != 1:
                raise ValueError(
                    f"You cannot move multiple ward-worth of individuals "
                    f"to more than one ward")

            return [[None, network.get_index(to_wards[0])]]

        from_wards = [network.get_index(x) for x in from_wards]

        if to_wards is None:
            to_wards = from_wards
        elif len(to_wards) == 1:
            to_wards = len(from_wards) * [network.get_index(to_wards[0])]
        elif len(to_wards) != len(from_wards):
            raise ValueError(
                f"to_wards and from_wards must have the same size if both "
                f"specify more than one ward")
        else:
            to_wards = [network.get_index(x) for x in to_wards]

        return [[x, y] for x, y in zip(from_wards, to_wards)]
