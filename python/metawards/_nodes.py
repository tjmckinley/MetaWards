
import numpy as np

from ._node import Node

__all__ = ["Nodes"]


def _resize(array, N, default_value):
    """Resize the passed numpy array to size N, adding 'default_value'
       if this will grow the array
    """
    if N < array.size:
        return np.resize(array, N)
    else:
        return np.concatenate( (array, np.full(N-array.size,
                                               default_value,
                                               array.dtype)) )


class Nodes:
    """This is a container class for Nodes. This uses Numpy arrays
       to store a list of Node objects as a "struct of arrays".
       This should improve speed of loading and access.
    """
    def __init__(self, N: int=0):
        """Create a container for up to "N" nodes"""
        if N <= 0:
            self._is_null = True
        else:
            self._is_null = False

            int_t = np.int32        # all data should fit into an int32
            float_t = np.float64    # original code uses doubles

            # Struct of arrays for each piece of data. See the
            # Node class for information about what each variable
            # holds. Code uses "-1" to represent a null value
            self.label = np.full(N, -1, int_t)
            self.begin_to = np.full(N, -1, int_t)
            self.end_to = np.full(N, -1, int_t)
            self.self_w = np.full(N, -1, int_t)

            self.begin_p = np.full(N, -1, int_t)
            self.end_p = np.full(N, -1, int_t)
            self.self_p = np.full(N, -1, int_t)

            self.begin_we = np.full(N, -1, int_t)
            self.end_we = np.full(N, -1, int_t)
            self.self_we = np.full(N, -1, int_t)

            self.day_foi = np.full(N, 0.0, float_t)
            self.night_foi = np.full(N, 0.0, float_t)
            self.weekend_foi = np.full(N, 0.0, float_t)

            self.play_suscept = np.full(N, 0.0, float_t)
            self.save_play_suscept = np.full(N, 0.0, float_t)

            self.denominator_n = np.full(N, 0.0, float_t)
            self.denominator_d = np.full(N, 0.0, float_t)

            self.denominator_p = np.full(N, 0.0, float_t)
            self.denominator_pd = np.full(N, 0.0, float_t)

            self.x = np.full(N, 0.0, float_t)  # no good initialiser for x
            self.y = np.full(N, 0.0, float_t)  # no good initialiser for y

            self.b = np.full(N, 0.0, float_t)

            self.id = N * [None]   # this is a list of strings
            self.vacid = np.full(N, -1, int_t)

    def is_null(self):
        return self._is_null

    def __len__(self):
        """Return the number of nodes in this container"""
        if self._is_null:
            return 0
        else:
            return self.label.size

    def assert_not_null(self):
        """Assert that this collection of nodes is not null"""
        assert not self.is_null()

    def assert_valid_index(self, i):
        """Assert that the passed index 'i' is valid for this collection.
           This will return the index with  Python reverse indexing,
           so that "-1" refers to the last node in the collection
        """
        self.assert_not_null()
        n = len(self)

        if i < 0:
            i = n + i

        if i < 0 or i >= n:
            raise IndexError(f"Invalid node index {i}. Number of nodes "
                             f"in this container equals {n}")

        return i

    def __getitem__(self, i: int):
        """Return the node at index 'i'. Note that this is a
           deep copy of the node. Changing the node will not change
           the data in this container. To update the data in this
           container you need to use __setitem__, e.g. via the
           index operator (see __setitem__)
        """
        i = self.assert_valid_index(i)

        return Node(label=self.label[i],
                    begin_to=self.begin_to[i],
                    end_to=self.end_to[i],
                    self_w=self.self_w[i],

                    begin_p=self.begin_p[i],
                    end_p=self.end_p[i],
                    self_p=self.self_p[i],

                    begin_we=self.begin_we[i],
                    end_we=self.end_we[i],
                    self_we=self.self_we[i],

                    day_foi=self.day_foi[i],
                    night_foi=self.night_foi[i],
                    weekend_foi=self.weekend_foi[i],

                    play_suscept=self.play_suscept[i],
                    save_play_suscept=self.save_play_suscept[i],

                    denominator_n=self.denominator_n[i],
                    denominator_d=self.denominator_d[i],

                    denominator_p=self.denominator_p[i],
                    denominator_pd=self.denominator_pd[i],

                    x=self.x[i],
                    y=self.y[i],

                    b=self.b[i],

                    id=self.id[i],
                    vacid=self.vacid[i])

    def __setitem__(self, i: int, value: Node):
        """Set the item as index 'i' equal to 'value'. This deep-copies
           'value' into this container
        """
        i = self.assert_valid_index(i)

        self.label[i] = value.label if value.label is not None else -1
        self.begin_to[i] = value.begin_to if value.begin_to is not None else -1
        self.end_to[i] = value.end_to if value.end_to is not None else -1
        self.self_w[i] = value.self_w if value.self_w is not None else -1

        self.begin_p[i] = value.begin_p if value.begin_p is not None else -1
        self.end_p[i] = value.end_p if value.end_p is not None else -1
        self.self_p[i] = value.self._p if value.self_p is not None else -1

        self.begin_we[i] = value.begin_we if value.begin_we is not None else -1
        self.end_we[i] = value.end_we if value.end_we is not None else -1
        self.self_we[i] = value.self_we if value.self_we is not None else -1

        self.day_foi[i] = value.day_foi if value.day_foi is not None else 0.0
        self.night_foi[i] = value.night_foi if value.night_foi is not None else 0.0
        self.weekend_foi[i] = value.weekend_foi if value.weekend_foi is not None else 0.0

        self.play_suscept[i] = value.play_suscept if value.play_suscept is not None else 0.0
        self.save_play_suscept[i] = value.save_play_suscept if value.save_play_suscept is not None else 0.0

        self.denominator_n[i] = value.denominator_n if value.denominator_n is not None else 0.0
        self.denominator_d[i] = value.denominator_d if value.denominator_d is not None else 0.0

        self.denominator_p[i] = value.denominator_p if value.denominator_p is not None else 0.0
        self.denominator_pd[i] = value.denominator_pd if value.denominator_pd is not None else 0.0

        self.x[i] = value.x if value.x is not None else 0.0
        self.y[i] = value.y if value.y is not None else 0.0

        self.b[i] = value.b if value.b is not None else 0.0

        self.id[i] = value.id  # this is a python list and can have None
        self.vacid[i] = value.vacid if value.vacid is not None else -1

    def resize(self, N: int):
        """Resize this container to hold 'N' nodes. This will expand
           the container if 'N' is greater than len(self), or will
           contract the container (deleting excess nodes) if 'N'
           is less than len(self). This function is called typically
           when you pre-allocate a large Nodes container, and then
           want to reduce the size to fit the number of loaded nodes
        """
        if self.is_null():
            # Assign to a new Nodes object created with this size
            self.__dict__ = Nodes(N).__dict__
            return
        elif N <= 0:
            self.__dict__ = Nodes(0).__dict__

        size = len(self)

        if N == size:
            return

        self.label = _resize(self.label, N, -1)
        self.begin_to = _resize(self.begin_to, N, -1)
        self.end_to = _resize(self.end_to, N, -1)
        self.self_w = _resize(self.self_w, N, -1)

        self.begin_p = _resize(self.begin_p, N, -1)
        self.end_p = _resize(self.end_p, N, -1)
        self.self_p = _resize(self.self_p, N, -1)

        self.begin_we = _resize(self.begin_we, N, -1)
        self.end_we = _resize(self.end_we, N, -1)
        self.self_we = _resize(self.self_we, N, -1)

        self.day_foi = _resize(self.day_foi, N, 0.0)
        self.night_foi = _resize(self.night_foi, N, 0.0)
        self.weekend_foi = _resize(self.weekend_foi, N, 0.0)

        self.play_suscept = _resize(self.play_suscept, N, 0.0)
        self.save_play_suscept = _resize(self.save_play_suscept, N, 0.0)

        self.denominator_n = _resize(self.denominator_n, N, 0.0)
        self.denominator_d = _resize(self.denominator_d, N, 0.0)

        self.denominator_p = _resize(self.denominator_p, N, 0.0)
        self.denominator_pd = _resize(self.denominator_pd, N, 0.0)

        self.x = _resize(self.x, N, 0.0)
        self.y = _resize(self.y, N, 0.0)

        self.b = _resize(self.b, N, 0.0)

        self.vacid = _resize(self.vacid, N, -1)

        if N < len(self.id):
            self.id = self.id[0:N]
        else:
            self.id += (N - len(self.id)) * [None]
