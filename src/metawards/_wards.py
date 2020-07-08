
from typing import List as _List

from .utils._profiler import Profiler, NullProfiler

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

    def num_work_links(self):
        """Return the total number of work links"""
        n = 0

        for ward in self._wards:
            if ward is not None:
                n += ward.num_work_links()

        return n

    def num_play_links(self):
        """Return the total number of play links"""
        n = 0

        for ward in self._wards:
            if ward is not None:
                n += ward.num_play_links()

        return n

    def num_players(self):
        """Return the total number of players in this network"""
        num = 0

        for ward in self._wards:
            if ward is not None:
                num += ward.num_players()

        return num

    def num_workers(self):
        """Return the total number of workers in this network"""
        num = 0

        for ward in self._wards:
            if ward is not None:
                num += ward.num_workers()

        return num

    def population(self):
        """Return the total population in this network"""
        num = 0

        for ward in self._wards:
            if ward is not None:
                num += ward.population()

        return num

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

    def to_data(self, profiler: Profiler = None):
        """Return a data representation of these wards that can
           be serialised to JSON
        """
        if len(self) > 0:
            if profiler is None:
                profiler = NullProfiler()

            p = profiler.start("to_data")
            p = p.start("assert_sane")
            self.assert_sane()
            p = p.stop()

            p = p.start("convert_wards")

            nwards = len(self._wards)

            from .utils._console import Console
            with Console.progress(visible=(nwards > 250)) as progress:
                data = []
                task = progress.add_task("Converting to data", total=nwards)

                for i, ward in enumerate(self._wards):
                    if ward is None:
                        data.append(None)
                    else:
                        data.append(ward.to_data())

                    if i % 250 == 0:
                        progress.update(task, completed=i+1)

                progress.update(task, completed=nwards, force_update=True)

            p = p.stop()
            p = p.stop()

            return data

        else:
            return None

    @staticmethod
    def from_data(data, profiler: Profiler = None):
        """Return the Wards constructed from a data represnetation,
           which may have come from deserialised JSON
        """
        if data is None or len(data) == 0:
            return Wards()

        if profiler is None:
            profiler = NullProfiler()

        p = profiler.start("from_data")

        p = p.start("convert_wards")
        wards = Wards()

        nwards = len(data)

        from .utils._console import Console
        with Console.progress(visible=(nwards > 250)) as progress:
            task = progress.add_task("Converting from data", total=nwards)

            w = []

            for i, x in enumerate(data):
                if x is None:
                    w.append(None)
                else:
                    w.append(Ward.from_data(x))

                if i % 250 == 0:
                    progress.update(task, completed=i+1)

            progress.update(task, completed=nwards, force_update=True)

            wards._wards = w
        p = p.stop()

        p = p.start("assert_sane")
        wards.assert_sane()
        p = p.stop()

        p = p.stop()

        return wards
