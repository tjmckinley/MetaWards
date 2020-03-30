
from array import array

from ._network import Network
from ._parameters import Parameters

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

        int_t = "i"
        float_t = "d"

        null_int_N_INF_CLASSES = N_INF_CLASSES * [0]
        null_int_MAXSIZE = MAXSIZE * [0]

        self.N_INF_CLASSES = N_INF_CLASSES
        self.MAXSIZE = MAXSIZE

        self.inf_tot = array(int_t, null_int_N_INF_CLASSES)
        self.pinf_tot = array(int_t, null_int_N_INF_CLASSES)
        self.n_inf_wards = array(int_t, null_int_N_INF_CLASSES)

        self.total_inf_ward = array(int_t, null_int_MAXSIZE)
        self.total_new_inf_ward = array(int_t, null_int_MAXSIZE)

    def zero_all(self):
        """Reset the values of all of the arrays to zero"""
        cdef int i = 0

        cdef int [:] inf_tot = self.inf_tot
        cdef int [:] pinf_tot = self.pinf_tot
        cdef int [:] n_inf_wards = self.n_inf_wards

        cdef int [:] total_inf_ward = self.total_inf_ward
        cdef int [:] total_new_inf_ward = self.total_new_inf_ward

        for i in range(0, self.N_INF_CLASSES):
            inf_tot[i] = 0
            pinf_tot[i] = 0
            n_inf_wards[i] = 0

        for i in range(0, self.MAXSIZE):
            total_inf_ward[i] = 0
            total_new_inf_ward[i] = 0
