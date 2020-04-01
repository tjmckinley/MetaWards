
from cpython cimport array

import array   # timing shows quicker for random access
               # than numpy

__all__ = ["create_int_array", "create_double_array",
           "create_string_array", "resize_array"]


cdef array.array _int_array_template = array.array('i', [])
cdef array.array _dbl_array_template = array.array('d', [])


def create_string_array(size: int, default: str=None):
    """Create an array of python strings of size 'size', optionally
       initialised with 'default'
    """
    return size * [default]   # this is a list of strings


def resize_array(a, size: int, default: any = None):
    """Resize the passed array to size 'size', adding 'default'
       if this will grow the array
    """
    if size < len(a):
        return a[0:size]
    elif len(a) == 0:
        typecode = None

        try:
            typecode = a.typecode
        except:
            typecode = None

        if typecode is None:
            return create_string_array(size, default)
        elif typecode == "i":
            return create_int_array(size, default)
        elif typecode == "d":
            return create_double_array(size, default)
        else:
            raise AssertionError(f"Unrecognised array typecode {typecode}")

    elif isinstance(a[0], str):
        a = a + ((len(a) - size) * [default])
        assert(len(a) == size)
        return a
    else:
        return a + array(a.typecode, (size-len(a))*[default])


def create_double_array(size: int, default: float=None):
    """Create a new array.array of the specified size. If
       default is set then all values will be initialised to
       'default'
    """
    cdef int s = size
    cdef array.array dbl_array
    dbl_array = array.clone(_dbl_array_template, size, zero=False)

    cdef int i
    cdef double d

    if default is not None:
        d = default
        for i in range(0,s):
            dbl_array[i] = d

    return dbl_array


def create_int_array(size: int, default: int=None):
    """Create a new array.array of the specified size. If
       default is set then all values will be initialised to
       'default'
    """
    cdef int s = size
    cdef array.array int_array
    int_array = array.clone(_int_array_template, size, zero=False)

    cdef int i, d

    if default is not None:
        d = default
        for i in range(0,s):
            int_array[i] = d

    return int_array
