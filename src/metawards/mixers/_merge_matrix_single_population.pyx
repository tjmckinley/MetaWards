#!/bin/env/python3
#cython: linetrace=False
# MUST ALWAYS DISABLE AS WAY TOO SLOW FOR ITERATE

cimport cython
from cython.parallel import parallel, prange

from .._networks import Networks

from ..utils._profiler import Profiler
from ..utils._get_array_ptr cimport get_double_array_ptr
from ..utils._array import create_double_array

__all__ = ["merge_matrix_single_population"]


def merge_matrix_single_population(network: Networks, nthreads: int,
                                   profiler: Profiler, **kwargs):
    """This merge_function merges the FOIs across all demographic
       sub-networks according to the interaction matrix stored
       in networks.demographics.interaction_matrix, using
       the total number of people across all demographics summed,
       so as to better model populations that mix completely.
       In this case, the different demographics
       are assumed to be in the same population and so have
       same probability of contact. The FOIs are merged
       together where they are divided by N (where N is
       the total number of individuals summed across all demographics),
       e.g.

       N = N_i + N_j + N_k ...

       FOI_i = FOI_i / N + FOI_j / N + FOI_k / N ...
    """

    matrix = network.demographics.interaction_matrix

    if matrix is None:
        # No matrix, so nothing should interact
        return

    subnets = network.subnets
    cdef int nsubnets = len(subnets)

    if nsubnets < 2:
        # nothing to merge
        return

    # the matrix should be sized for the number of subnets
    if len(matrix) != nsubnets:
        raise ValueError(
            f"The interaction matrix must be right-sized for the number "
            f"of demographics, e.g. it must be {nsubnets}x{nsubnets}")

    # it must also be square
    for row in matrix:
        if len(row) != nsubnets:
            raise ValueError(
                f"The interaction matrix must be square, e.g. "
                f"{nsubnets}x{nsubnets}.")

    cdef int nnodes_plus_one = network.overall.nnodes + 1

    cdef int i = 0
    cdef int j = 0
    cdef int k = 0

    cdef int num_threads = nthreads

    wards = network.overall.nodes

    cdef double scl = 0.0

    cdef double * wards_day_foi = get_double_array_ptr(wards.day_foi)
    cdef double * wards_night_foi = get_double_array_ptr(wards.night_foi)

    # Note that wards_day_foi will be divided by N_day in each ward
    # and multiplied by length_day to create lambda. We thus need to
    # track N_day for the demographic and compare that against
    # N_day_total across all demographics
    n_day_total_array = create_double_array(nnodes_plus_one, 0.0)
    cdef double * n_day_total = get_double_array_ptr(n_day_total_array)
    cdef double * wards_denominator_d
    cdef double * wards_denominator_pd
    cdef double n_day_ward = 0.0

    # Equally, wards_night_foi will be divided by N_night in each ward
    # and multiplied by 1 - length_day to create lambda. We thus
    # need to track N_night for the demographic and compare that
    # against N_night_total across all demographics
    n_night_total_array = create_double_array(nnodes_plus_one, 0.0)
    cdef double * n_night_total = get_double_array_ptr(n_night_total_array)
    cdef double * wards_denominator_n
    cdef double * wards_denominator_p
    cdef double n_night_ward = 0.0

    cdef double * day_foi
    cdef double * night_foi

    cdef double * sub_day_foi
    cdef double * sub_night_foi

    # create space to calculate all of the day and night fois
    day_fois = []
    night_fois = []

    p = profiler.start("allocate")
    for i in range(0, nsubnets):
        day_fois.append(create_double_array(nnodes_plus_one, 0.0))
        night_fois.append(create_double_array(nnodes_plus_one, 0.0))
    p = p.stop()

    # calculate the total N in each ward across all demographics
    p = profiler.start("calculate_N")
    for i in range(0, nsubnets):
        sub_wards = subnets[j].nodes
        wards_denominator_d = get_double_array_ptr(sub_wards.denominator_d)
        wards_denominator_n = get_double_array_ptr(sub_wards.denominator_n)
        wards_denominator_p = get_double_array_ptr(sub_wards.denominator_p)
        wards_denominator_pd = get_double_array_ptr(sub_wards.denominator_pd)

        with nogil, parallel(num_threads=num_threads):
            for k in prange(1, nnodes_plus_one, schedule="static"):
                n_day_total[k] = n_day_total[k] + \
                                 wards_denominator_d[k] + \
                                 wards_denominator_pd[k]
                n_night_total[k] = n_night_total[k] + \
                                   wards_denominator_n[k] + \
                                   wards_denominator_p[k]
    p = p.stop()

    # calculate the merged FOIs
    p = profiler.start("accumulate")
    for i in range(0, nsubnets):
        day_foi = get_double_array_ptr(day_fois[i])
        night_foi = get_double_array_ptr(night_fois[i])

        # We will be dividing the FOI calculated here by the
        # N_day and N_night for this demographic in advance_infprob.
        # Thus we need to pre-multiply our FOIs by this value so
        # that we cancel this out.
        my_wards = subnets[i].nodes

        wards_denominator_d = get_double_array_ptr(
                                        my_wards.denominator_d)
        wards_denominator_n = get_double_array_ptr(
                                        my_wards.denominator_n)
        wards_denominator_p = get_double_array_ptr(
                                        my_wards.denominator_p)
        wards_denominator_pd = get_double_array_ptr(
                                        my_wards.denominator_pd)

        for j in range(0, nsubnets):
            sub_wards = subnets[j].nodes
            sub_day_foi = get_double_array_ptr(sub_wards.day_foi)
            sub_night_foi = get_double_array_ptr(sub_wards.night_foi)

            scl = matrix[i][j]

            with nogil, parallel(num_threads=num_threads):
                for k in prange(1, nnodes_plus_one, schedule="static"):
                    # calculate the number of individuals in the ith
                    # demographics kth ward in the daytime and nighttime
                    # (note that this assignment is thread-safe as
                    # cython makes n_day_ward and n_night_ward lastprivate)
                    n_day_ward = wards_denominator_d[k] + \
                                 wards_denominator_pd[k]
                    n_night_ward = wards_denominator_p[k] + \
                                   wards_denominator_n[k]

                    # We want to multiply the FOI by the number in
                    # the ward and then divide by the number across
                    # all demographics (it will then be divided by
                    # the number in the ward in the ith
                    # demographic in advance_infprob). Doing this will
                    # mean that the denominator for every demographic
                    # will be N_total for each ward.

                    day_foi[k] = day_foi[k] + \
                                 scl * n_day_ward * \
                                 sub_day_foi[k] / n_day_total[k]
                    night_foi[k] = night_foi[k] + \
                                   scl * n_night_ward * \
                                   sub_night_foi[k] / n_night_total[k]
    p = p.stop()

    p = profiler.start("distribute")
    for j in range(0, nsubnets):
        day_foi = get_double_array_ptr(day_fois[j])
        night_foi = get_double_array_ptr(night_fois[j])

        sub_wards = subnets[j].nodes
        sub_day_foi = get_double_array_ptr(sub_wards.day_foi)
        sub_night_foi = get_double_array_ptr(sub_wards.night_foi)

        with nogil, parallel(num_threads=num_threads):
            for k in prange(1, nnodes_plus_one, schedule="static"):
                sub_day_foi[k] = day_foi[k]
                sub_night_foi[k] = night_foi[k]
    p = p.stop()
