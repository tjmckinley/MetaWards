
from ._wardinfo import WardInfo

__all__ = ["Ward"]


def _as_positive_integer(number: int):
    try:
        number = int(number)
    except Exception:
        raise ValueError(f"{number} is not an integer")

    if number < 1:
        raise ValueError(f"{number} is not greater than 0")

    return number


def _as_positive_float(number: float):
    try:
        number = float(number)
    except Exception:
        raise ValueError(f"{number} is not a floating point number")

    if number < 0:
        raise ValueError(f"{number} is not greater or equal to zero")

    return number


class Ward:
    """This class holds all of the information about a Ward. It is used
       to create and edit Networks
    """

    def __init__(self, id: int = None, name: str = None, code: str = None,
                 authority: str = None, region: str = None,
                 info: WardInfo = None):
        """Construct a new Ward, optionally supplying information about
           the ward

           Parameters
           ----------
           id: int
             The identifier for the ward. This must be an integer that
             is greater or equal to 1. Every ward in a network must have
             a unique ID. Typically the IDs should be contiguous, as this
             ID is used as the index into the Network array
           name: str
             The name of this ward. This can be used to find the ward.
           code: str
             The code of this ward. This is used when wards are identified
             by codes, rather than names
           authority: str
             The local authority name for this node
           region: str
             The name of the region containing this ward
           info: WardInfo
             The complete WardInfo used to identify this ward.
        """
        if id is None:
            self._id = None
            return

        if info is not None:
            if not isinstance(info, WardInfo):
                raise TypeError(
                    f"The passed WardInfo {info} must be of type WardInfo")
            from copy import deepcopy
            self._info = deepcopy(info)
        else:
            self._info = WardInfo()

        if name is not None:
            self._info.name = str(name)

        if code is not None:
            self._info.code = str(code)

        if authority is not None:
            self._info.authority = str(authority)

        if region is not None:
            self._info.region = str(region)

        try:
            id = int(id)
        except Exception:
            raise TypeError(f"The passed ID {id} must be an integer")

        if id < 1:
            raise ValueError(
                f"The passed ID {id} must be greater or equal to 1")

        self._id = id

        self._workers = {}
        self._players = {id: 1.0}

        self._num_workers = 0
        self._num_players = 0

        self._pos = {}

    def __str__(self):
        if self.is_null():
            return "Ward::null"
        else:
            return f"Ward( id={self._id}, name={self.name()}, " \
                f"num_workers={self.num_workers()}, " \
                f"num_players={self.num_players()} )"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.__class__ == other.__class__ and \
            self.__dict__ == other.__dict__

    def is_null(self):
        return self._id is None

    def id(self):
        """Return the ID of this ward"""
        return self._id

    def name(self):
        """Return the name of this ward"""
        return self._info.name

    def code(self):
        """Return the code of this ward"""
        return self._info.code

    def authority(self):
        """Return the local authority of this ward"""
        return self._info.authority

    def region(self):
        """Return the region containing this ward"""
        return self._info.region

    def info(self):
        """Return (a copy of) the WardInfo containing all ward
           identifying metadata
        """
        from copy import deepcopy
        return deepcopy(self._info)

    def assert_sane(self):
        """Assert that the data in this ward is sane"""
        assert self._id is not None and self._id > 0

        assert sum(self._players.values()) == 1.0

        assert sum(self._workers.values()) == self._num_workers

    def set_name(self, name: str):
        """Set the name of this ward"""
        self._info.name = str(name)

    def set_id(self, id: int):
        """Set the ID of this ward"""
        try:
            id = int(id)
        except Exception:
            raise TypeError(f"The ID {id} must be an integer")

        if id < 1:
            raise ValueError(
                f"The passed ID {id} must be greater or equal to 1")

        self._info.id = id

    def set_code(self, code: str):
        """Set the code of this ward"""
        self._info.code = str(code)

    def set_authority(self, authority: str):
        """Set the local authority of this ward"""
        self._info.authority = str(authority)

    def set_region(self, region: str):
        """Set the region of this ward"""
        self._info.region = str(region)

    def set_info(self, info: WardInfo):
        """Set the info of this ward"""
        if not isinstance(info, WardInfo):
            raise TypeError(f"The ward info {info} must be a WardInfo object")

        from copy import deepcopy
        self._info = deepcopy(info)

    def add_workers(self, number: int, destination: int = None):
        """Add some workers to this ward, specifying their destination
           if they work out of ward
        """
        if destination is None:
            destination = self._id

        number = _as_positive_integer(number)
        destination = _as_positive_integer(destination)

        if destination not in self._workers:
            self._workers[destination] = 0

        self._workers[destination] += number
        self._num_workers += number

    def subtract_workers(self, number: int, destination: int = None):
        """Remove some workers from this ward, specifying their destination
           if they work out of ward
        """
        if destination is None:
            destination = self._id

        number = _as_positive_integer(number)

        if destination not in self._workers:
            return

        if number >= self._workers[destination]:
            self._num_workers -= self._workers[destination]
            del self._workers[destination]
        else:
            self._workers -= number
            self._num_workers -= number

    def add_player_weight(self, weight: float, destination: int = None):
        """Add the weight for players who will randomly move to
           the specified destination to play (or to play in the home
           ward if destination is not set). Note that the sum of
           player weights must be 1.0. Adding a weight to a non-home
           ward will subtract that weight from the home ward. Note that
           you cannot add a weight such that this is more than one
        """
        if destination is None:
            destination = self._id

        weight = _as_positive_float(weight)
        destination = _as_positive_integer(destination)

        if destination == self._id:
            raise ValueError(
                f"You cannot set the player weight of the home ward "
                f"{self._id} as this is derived from the weights of "
                f"players moving to other wards")

        if weight > self._players[self._id]:
            raise ValueError(
                f"You cannot add {weight} to {destination} as this is greater "
                f"than the remaining weight of the home {self._id} ward "
                f"{self._players[self._id]}. You can only add a weight that "
                f"is less than this value")

        if destination not in self._players:
            self._players[destination] = 0

        self._players[destination] += weight
        self._players[self._id] -= weight

    def get_workers(self, destination: int = None):
        """Return the number of workers who commute to the specified
           destination ward (or who commute to their home ward if
           destination is not set)
        """
        if destination is None:
            return self._workers.get(self._id, 0)
        else:
            return self._workers.get(_as_positive_integer(destination), 0)

    def get_players(self, destination: int = None):
        """Return the fraction of players who will play in the
           specified destination ward (or who play in their home
           ward if destination is not set)
        """
        if destination is None:
            return self._players.get(self._id, 0.0)
        else:
            return self._players.get(_as_positive_integer(destination), 0.0)

    def num_workers(self):
        """Return the total number of workers who make their home
           in this ward
        """
        return self._num_workers

    def num_players(self):
        """Return the total number of players who make their home
           in this ward
        """
        return self._num_players

    def population(self):
        """Return the total population of this ward"""
        return self._num_workers + self._num_players

    def set_num_players(self, number: int):
        """Set the number of players in this ward"""
        self._num_players = _as_positive_integer(number)

    def set_num_workers(self, number: int):
        """Set the number of workers in this ward."""
        number = _as_positive_integer(number)

        delta = number - self._num_workers

        if delta > 0:
            # add the workers as individuals who commute to their home ward
            self.add_workers(delta)

        elif delta < 0:
            # can we remove just the workers who commute to their home ward?
            if delta <= self.get_workers():
                self.subtract_workers(delta)
            else:
                raise ValueError(
                    f"Cannot set the number of workers to {number} as there "
                    f"are not enough home workers to subtract")

    def get_worker_lists(self):
        """Return a pair of arrays, containing the destination wards
           and worker populations for this ward
        """
        from .utils._array import create_int_array

        keys = list(self._workers.keys())
        keys.sort()

        wards = create_int_array(len(keys))
        pops = create_int_array(len(keys))

        for i, key in enumerate(keys):
            wards[i] = key
            pops[i] = self._workers[key]

        return (wards, pops)

    def get_player_lists(self):
        """Return a pair of arrays, containing the destination wards
           and player weights for this ward
        """
        from .utils._array import create_double_array

        keys = list(self._players.keys())
        keys.sort()

        wards = create_double_array(len(keys))
        weights = create_double_array(len(keys))

        for i, key in enumerate(keys):
            wards[i] = key
            weights[i] = self._players[key]

        return (wards, weights)

    def set_position(self, x: float = None, y: float = None,
                     lat: float = None, long: float = None,
                     units: str = "m"):
        """Set the position of the centre of this ward. This can
           be set either as x/y coordinates or latitude/longitude
           coordinates.

           Parameters
           ----------
           x: float
             The x coordinates if x/y are used. The units are set
             via the 'units' argument
           y: float
             The y coordinates if x/y are used. The units are set
             via the 'units' argument
           units: str
             The units for x/y coordinates. This should be "m" for
             meters or "km" for kilometers
           lat: float
             The latitude if lat/long coordinates are used
           long: float
             The longitude if lat/long coordinates are used
        """
        if x is not None:
            if y is None or lat is not None or long is not None:
                raise ValueError(
                    f"You must set either x/y or lat/long, but not both!")

            if units is None:
                units = "m"

            units = str(units).strip().lower()

            if units in ["m", "meter", "meters"]:
                units = 0.001
            elif units in ["km", "kilometer", "kilometers"]:
                units = 1.0
            else:
                raise ValueError(
                    f"Unrecognised units {units}. This should be either "
                    f"'m' or 'km'")

            self._pos = {"x": units * float(x),
                         "y": units * float(y)}

        elif lat is not None:
            if long is None or x is not None or y is not None:
                raise ValueError(
                    f"You must set either x/y or lat/long, but not both!")

            self._pos = {"lat": float(lat),
                         "long": float(long)}

        else:
            raise ValueError(f"You must set either x/y or lat/long")

    def position(self):
        """Return the position of the center of this ward. This will
           return a dictionary containing either the {"x", "y"}
           coordinates (in kilometers) or containing the
           {"lat", "long"} coordinates, or an empty dictionary
           if cooordinates have not been set.
        """
        from copy import deepcopy
        return deepcopy(self._pos)

    def to_data(self):
        """Return a dictionary that can be serialised to JSON"""
        data = {}

        data["id"] = self._id
        data["position"] = self.position()
        data["info"] = self.info().to_data()

        workers = self.get_worker_lists()

        data["num_workers"] = self.num_workers()
        data["num_players"] = self.num_players()

        data["workers"] = {"destination": workers[0].tolist(),
                           "population": workers[1].tolist()}

        players = self.get_player_lists()

        data["players"] = {"destination": players[0].tolist(),
                           "weights": players[1].tolist()}

        return data

    @staticmethod
    def from_data(data):
        """Return a Ward that has been created from the passed dictionary
           (e.g. which has been deserialised from JSON)
        """

        if data is None or len(data) == 0:
            return Ward()

        ward = Ward(id=data.get("id", None),
                    info=WardInfo.from_data(data.get("info", {})))

        pos = data.get("position", {})

        ward.set_position(x=pos.get("x", None), y=pos.get("y", None),
                          lat=pos.get("lat", None), long=pos.get("long", None),
                          units="km")
        ward.set_num_workers(data.get("num_workers", 0))
        ward.set_num_players(data.get("num_players", 0))

        workers = data.get("workers", {})

        for d, p in zip(workers.get("destination", []),
                        workers.get("population", [])):
            d = _as_positive_integer(d)
            p = _as_positive_integer(p)

            ward._workers[d] = p

        players = data.get("players", {})

        for d, w in zip(players.get("destination", []),
                        players.get("weights", [])):
            d = _as_positive_integer(d)
            w = _as_positive_float(w)

            ward._players[d] = w

        ward.assert_sane()

        return ward
