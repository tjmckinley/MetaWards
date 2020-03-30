
from array import array   # timing shows quicker for random access
                          # than numpy

from ._tolink import ToLink

__all__ = ["ToLinks"]


def _resize(a, N, default_value):
    """Resize the passed array to size N, adding 'default_value'
       if this will grow the array
    """
    if N < len(a):
        return a[0:N]
    else:
        return a + array(a.typecode, N*[default_value])


class ToLinks:
    """This is a container class for ToLinks. This uses arrays
       to store a list of ToLink objects as a "struct of arrays".
       This should improve speed of loading and access.
    """
    def __init__(self, N: int=0):
        """Create a container for up to "N" ToLinks"""
        if N <= 0:
            self._is_null = True
        else:
            self._is_null = False

            int_t = "i"        # all data should fit into an int32
            float_t = "d"      # original code uses doubles

            null_int = N * [-1]
            null_float = N * [0.0]

            # Struct of arrays for each piece of data. See the
            # ToLink class for information about what each variable
            # holds. Code uses "-1" to represent a null value
            self.ifrom = array(int_t, null_int)
            self.ito = array(int_t, null_int)

            self.weight = array(float_t, null_float)
            self.suscept = array(float_t, null_float)
            self.distance = array(float_t, null_float)

            self.A = array(int_t, null_int)

    def is_null(self):
        return self._is_null

    def __len__(self):
        """Return the number of links in this container"""
        if self._is_null:
            return 0
        else:
            return len(self.ifrom)

    def assert_not_null(self):
        """Assert that this collection of links is not null"""
        assert not self.is_null()

    def assert_valid_index(self, i):
        """Assert that the passed index 'i' is valid for this collection.
           This will return the index with Python reverse indexing,
           so that "-1" refers to the last link in the collection
        """
        self.assert_not_null()
        n = len(self)

        if i < 0:
            i = n + i

        if i < 0 or i >= n:
            raise IndexError(f"Invalid link index {i}. Number of links "
                             f"in this container equals {n}")

        return i

    def __getitem__(self, i: int):
        """Return the link at index 'i'. Note that this is a
           deep copy of the link. Changing the link will not change
           the data in this container. To update the data in this
           container you need to use __setitem__, e.g. via the
           index operator (see __setitem__)
        """
        i = self.assert_valid_index(i)

        return ToLink(ifrom=self.ifrom[i], ito=self.ito[i],
                      weight=self.weight[i], suscept=self.suscept[i],
                      distance=self.distance[i], A=self.A[i])

    def __setitem__(self, i: int, value: ToLink):
        """Set the item as index 'i' equal to 'value'. This deep-copies
           'value' into this container
        """
        i = self.assert_valid_index(i)

        self.ifrom[i] = value.ifrom if value.ifrom is not None else -1
        self.ito[i] = value.ito if value.ito is not None else -1
        self.weight[i] = value.weight if value.weight is not None else 0.0
        self.suscept[i] = value.suscept if value.suscept is not None else 0.0
        self.distance[i] = value.distance if value.distance is not None else 0.0
        self.A[i] = value.A if value.A is not None else -1

    def resize(self, N: int):
        """Resize this container to hold 'N' links. This will expand
           the container if 'N' is greater than len(self), or will
           contract the container (deleting excess links) if 'N'
           is less than len(self). This function is called typically
           when you pre-allocate a large ToLinks container, and then
           want to reduce the size to fit the number of loaded links
        """
        if self.is_null():
            # Assign to a new ToLinks object created with this size
            self.__dict__ = ToLinks(N).__dict__
            return
        elif N <= 0:
            self.__dict__ = ToLinks(0).__dict__

        size = len(self)

        if N == size:
            return

        self.ifrom = _resize(self.ifrom, N, -1)
        self.ito = _resize(self.ito, N, -1)
        self.weight = _resize(self.weight, N, 0.0)
        self.suscept = _resize(self.suscept, N, 0.0)
        self.distance = _resize(self.distance, N, 0.0)
        self.A = _resize(self.A, N, -1)
