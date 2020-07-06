
from typing import List as _List

from ._ward import Ward

__all__ = ["Wards"]


class Wards:
    """This class holds an entire network of Ward objects"""

    def __init__(self, wards: _List[Ward] = None):
        """Construct, optionally from a list of Ward objects"""
        self._wards = []

        if wards is not None:
            self.insert(wards)

    def __str__(self):
        if len(self) == 0:
            return "Wards::null"
        elif len(self) < 10:
            return f"[ {', '.join([str(x) for x in self._wards])} ]"
        else:
            s = f"[ {', '.join([str(x) for x in self._wards[0:6]])}, ... "
            s += f"{', '.join([str(x) for x in self._wards[-3:]])} ]"

            return s

    def __eq__(self, other):
        return self.__class__ == other.__class__ and \
            self.__dict__ == other.__dict__

    def insert(self, wards: _List[Ward]):
        """Append the passed wards onto this list"""
        if not isinstance(wards, list):
            wards = [wards]

        for ward in wards:
            if isinstance(ward, Wards):
                self.insert(ward._wards)
            elif ward is None:
                continue
            elif not isinstance(ward, Ward):
                raise TypeError(
                    f"You cannot append a {ward} to a list of Ward objects!")

        # get the largest ID and then resize the list...
        largest_id = 0

        for ward in wards:
            if isinstance(ward, Ward):
                if ward.id() > largest_id:
                    largest_id = ward.id()

        if largest_id > len(self._wards):
            self._wards += [None] * (largest_id - len(self._wards) + 1)

        for ward in wards:
            if isinstance(ward, Ward):
                self._wards[ward.id()] = ward

    def add(self, ward: Ward):
        """Synonym for insert"""
        self.insert(ward)

    def __getitem__(self, id):
        """Return the ward with specified id"""
        return self._wards[id]

    def __len__(self):
        return len(self._wards)

    def assert_sane(self):
        """Make sure that we don't refer to any non-existent wards"""
        if len(self._wards) == 0:
            return

        nwards = len(self._wards) - 1

        for i, ward in enumerate(self._wards):
            if ward is None:
                continue

            if i != ward.id():
                raise AssertionError(f"{ward} should have index {i}")

            for c in ward.work_connections():
                if c < 1 or c > nwards:
                    raise AssertionError(
                        f"{ward} has a work connection to an invalid "
                        f"ward ID {c}. Range should be 1 <= n <= {nwards}")
                elif self._wards[c] is None:
                    raise AssertionError(
                        f"{ward} has a work connection to a null "
                        f"ward ID {c}. This ward is null")

            for c in ward.play_connections():
                if c < 1 or c > nwards:
                    raise AssertionError(
                        f"{ward} has a play connection to an invalid "
                        f"ward ID {c}. Range should be 1 <= n <= {nwards}")
                elif self._wards[c] is None:
                    raise AssertionError(
                        f"{ward} has a play connection to a null "
                        f"ward ID {c}. This ward is null")

    def to_data(self):
        """Return a data representation of these wards that can
           be serialised to JSON
        """
        if len(self) > 0:
            self.assert_sane()
            return [x if x is None else x.to_data() for x in self._wards]
        else:
            return None

    @staticmethod
    def from_data(data):
        """Return the Wards constructed from a data represnetation,
           which may have come from deserialised JSON
        """
        if data is None or len(data) == 0:
            return Wards()

        wards = Wards()
        wards._wards = [x if x is None else Ward.from_data(x) for x in data]

        wards.assert_sane()

        return wards
