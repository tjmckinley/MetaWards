#!/bin/env/python3
#cython: linetrace=False
# MUST ALWAYS DISABLE AS WAY TOO SLOW FOR ITERATE

cimport cython

from libc.math cimport sqrt

from .._network import Network
from .._population import Population

from ..utils._workspace import Workspace

from ..utils._get_array_ptr cimport get_int_array_ptr, get_double_array_ptr

__all__ = ["output_dispersal"]


def output_dispersal(network: Network, population: Population,
                     output_dir: OutputFiles,
                     workspace: Workspace,
                     infections: Infections,
                     **kwargs):
    """This will calculate and output the geographic dispersal
       of the outbreak

       Parameters
       ----------
       network: Network
         The network over which the outbreak is being modelled
       population: Population
         The population experiencing the outbreak
       output_dir: OutputFiles
         The directory in which to place all output files
       workspace: Workspace
         A workspace that can be used to extract data
       infections: Infections
         Space to hold the infections
       kwargs
         Extra argumentst that are ignored by this function
    """

    mean_xy_file = output_dir.open("MeanXY.dat"))
    var_xy_file = output_dir.open("VarXY.dat"))
    dispersal_file = output_dir.open("Dispersal.dat"))


