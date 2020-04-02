"""
Python version of the MetaWards program

Details of authorship / license etc to be written here

"""

from ._parameters import *
from ._disease import *
from ._inputfiles import *
from ._node import *
from ._link import *
from ._population import *
from ._network import *
from ._profiler import *

# All of the functions are now hidden in the 'utils' submodule
from . import _utils as utils

# import the pyx cython-compiled modules
from ._nodes import *
from ._links import *

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
