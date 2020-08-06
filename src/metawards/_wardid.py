from __future__ import annotations

from typing import Union as _Union
from typing import List as _List

__all__ = ["WardID"]


class WardID:
    """A simple class that identifies a Ward (or Wards),
       or a connection between Wards. This could be used,
       e.g. to specify ward moves
    """

    def __init__(self, home: _Union[WardID, str, int] = None,
                 commute: _Union[WardID, str, int] = None):
        """Construct a WardID that identifies the 'home' ward, and (optionally)
           the 'commute' ward if this is a ward-link (used to identify
           workers)
        """
        if isinstance(home, WardID):
            home = home._home

        if isinstance(commute, WardID):
            commute = commute._home

        if home is None:
            if commute is not None:
                raise ValueError("You cannot specify a commute without a home")

            self._home = None
            self._commute = None
            return

        self._home = home
        self._commute = commute

    def __eq__(self, other):
        return self._home == other._home and self._commute == other._commute

    def is_null(self):
        """Return whether or not this is null"""
        return self._home is None

    def is_ward(self):
        """Return whether or not this specifies a single ward"""
        return self._home is not None and self._commute is None

    def is_ward_connection(self):
        """Return whether or not this is a ward connection
           (has both a home and commute ward)
        """
        return self._home is not None and self._commute is not None

    def __str__(self):
        if self.is_null():
            return "WardID::null"
        elif self.is_ward():
            return str(self._home)
        else:
            return f"{self._home}=>{self._commute}"

    def __repr__(self):
        return self.__str__()

    def home(self):
        """ Return the home ward"""
        return self._home

    def commute(self):
        """Return the commute ward is this is a ward connection"""
        return self._commute
