
cimport cython

from ._array import create_int_array

from .._network import Network
from .._parameters import Parameters

__all__ = ["Workspace"]


class Workspace:
    """This class provides a workspace for the running calculation.
       This pre-allocates all of the memory into arrays, which
       can then be used via cython memory views
    """
    def __init__(self, network: Network, params: Parameters):
        """Create the workspace needed to run the model for the
           passed network with the passed parameters
        """
        N_INF_CLASSES = params.disease_params.N_INF_CLASSES()
        MAXSIZE = network.nnodes + 1  # 1-indexed

        self.N_INF_CLASSES = N_INF_CLASSES
        self.MAXSIZE = MAXSIZE

        self.inf_tot = create_int_array(N_INF_CLASSES, 0)
        self.pinf_tot = create_int_array(N_INF_CLASSES, 0)
        self.n_inf_wards = create_int_array(N_INF_CLASSES, 0)

        self.total_inf_ward = create_int_array(MAXSIZE, 0)
        self.total_new_inf_ward = create_int_array(MAXSIZE, 0)

        self.total_infections = create_int_array(MAXSIZE, 0)
        self.prevalence = create_int_array(MAXSIZE, 0)

    @cython.boundscheck(False)
    @cython.wraparound(False)
    def zero_all(self):
        """Reset the values of all of the arrays to zero"""
        cdef int i = 0

        cdef int [::1] inf_tot = self.inf_tot
        cdef int [::1] pinf_tot = self.pinf_tot
        cdef int [::1] n_inf_wards = self.n_inf_wards

        cdef int [::1] total_inf_ward = self.total_inf_ward
        cdef int [::1] total_new_inf_ward = self.total_new_inf_ward
        cdef int [::1] total_infections = self.total_infections
        cdef int [::1] prevalence = self.prevalence

        for i in range(0, self.N_INF_CLASSES):
            inf_tot[i] = 0
            pinf_tot[i] = 0
            n_inf_wards[i] = 0

        for i in range(0, self.MAXSIZE):
            total_inf_ward[i] = 0
            total_new_inf_ward[i] = 0
            total_infections[i] = 0
            prevalence[i] = 0
