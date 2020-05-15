"""
.. currentmodule:: metawards

Classes
=======

.. autosummary::
    :toctree: generated/

    Demographic
    Demographics
    Disease
    Infections
    InputFiles
    Link
    Links
    Network
    Networks
    Node
    Nodes
    OutputFiles
    Parameters
    Population
    Populations
    VariableSet
    VariableSets
    WardInfo
    WardInfos
    Workspace

Functions
=========

.. autosummary::
    :toctree: generated/

    get_version_string

"""

from . import analysis
from . import app
from . import movers
from . import mixers
from . import extractors
from . import iterators
from . import utils
from ._version import get_versions
from ._links import *
from ._nodes import *
from ._wardinfo import *
from ._workspace import *
from ._infections import *
from ._variableset import *
from ._outputfiles import *
from ._networks import *
from ._network import *
from ._population import *
from ._link import *
from ._node import *
from ._inputfiles import *
from ._disease import *
from ._demographics import *
from ._demographic import *
from ._parameters import *
import sys as _sys

if _sys.version_info < (3, 7):
    print("MetaWards requires Python version 3.7 or above.")
    print("Your python is version")
    print(_sys.version)
    _sys.exit(-1)

__all__ = ["get_version_string"]


# import the pyx cython-compiled modules

__manual_version__ = "0.9.0"

_v = get_versions()
__version__ = _v['version']

if __version__.find("untagged") != -1:
    __version__ = __manual_version__

__branch__ = _v['branch']
__repository__ = _v['repository']
__revisionid__ = _v['full-revisionid']
del _v
del get_versions


def get_version_string():
    """Return a version string for metawards which can be printed
       into a file or written out to the screen
    """
    from ._version import get_versions
    v = get_versions()

    if v['version'].find("untagged") != -1:
        # the version couldn't be found - this is likely because this
        # is run as part of github actions or in a disconnected repo.
        # We need to drop back to '__manual_version__'
        v['version'] = __manual_version__

    lines = []

    lines.append(
        f"# metawards version {v['version']}")

    lines.append(f"## Source information")
    lines.append(f"* repository: {v['repository']}")
    lines.append(f"* branch: {v['branch']}")
    lines.append(f"* revision: {v['full-revisionid']}")
    lines.append(f"* last modified: {v['date']}")

    if v["dirty"]:
        lines.append(
            "\nWARNING: This version has not been committed to git, "
            "so you may not be able to recover the original "
            "source code that was used to generate this run!\n"
            "-------------")

    from metawards import get_repository
    repository, v = get_repository(error_on_missing=False)

    if repository is None:
        lines.append(
            "\nWARNING: MetaWardsData cannot be found! "
            "Please see https://metawards.org/model_data "
            "for instructions on how to download and "
            "install this necessary data.\n"
            "-------------")
    else:
        lines.append(f"## MetaWardsData information")
        lines.append(f"* version: {v['version']}")
        lines.append(f"* repository: {v['repository']}")
        lines.append(f"* branch: {v['branch']}")

        if v["is_dirty"]:
            lines.append(
                "\nWARNING: This data has not been committed to git. "
                "You may not be able to reproduce this run.\n"
                "----------------")

    lines.append("")
    lines.append(f"## Additional information")
    lines.append(f"Visit https://metawards.org for more information")
    lines.append(f"about metawards, its authors and its license")

    return "\n".join(lines)


def print_version_string():
    from metawards.utils import Console
    Console.print(get_version_string(), markdown=True)


_system_input = input


def input(prompt: str, default="y"):
    """Wrapper for 'input' that returns 'default' if it detected
       that this is being run from within a batch job or other
       service that doesn't have access to a tty
    """
    import sys

    try:
        if sys.stdin.isatty():
            return _system_input(prompt)
        else:
            print(f"Not connected to a console, so having to use the "
                  f"default ({default})")
            return default
    except Exception as e:
        print(f"Unable to get the input: {e.__class__} {e}")
        print(f"Using the default ({default}) instead")
        return default
