#!/bin/env/python3
#cython: linetrace=False
# MUST ALWAYS DISABLE AS WAY TOO SLOW FOR ITERATE

cimport cython

from libc.stdlib cimport malloc, free

from libc.math cimport cos, pi
from  ._rate_to_prob cimport rate_to_prob

from cython.parallel import parallel, prange
cimport openmp

from .._network import Network
from .._parameters import Parameters
from ._profiler import Profiler, NullProfiler
from ._import_infection import import_infection
from ._array import create_int_array, create_double_array

from ._ran_binomial cimport _ran_binomial, _get_binomial_ptr, binomial_rng

from ..iterators._advance_play import advance_play_omp
from ..iterators._advance_fixed import advance_fixed_omp
from ..iterators._advance_infprob import advance_infprob_omp

__all__ = ["iterate"]


cdef double * get_double_array_ptr(double_array):
    """Return the raw C pointer to the passed double array which was
       created using create_double_array
    """
    cdef double [::1] a = double_array
    return &(a[0])


cdef int * get_int_array_ptr(int_array):
    """Return the raw C pointer to the passed int array which was
       created using create_int_array
    """
    cdef int [::1] a = int_array
    return &(a[0])


cdef struct foi_buffer:
    int count
    int *index
    double *foi


cdef foi_buffer* allocate_foi_buffers(int nthreads, int buffer_size=4096) nogil:
    cdef int size = buffer_size
    cdef int n = nthreads

    cdef foi_buffer *buffers = <foi_buffer *> malloc(n * sizeof(foi_buffer))

    for i in range(0, nthreads):
        buffers[i].count = 0
        buffers[i].index = <int *> malloc(size * sizeof(int))
        buffers[i].foi = <double *> malloc(size * sizeof(double))

    return buffers


cdef void free_foi_buffers(foi_buffer *buffers, int nthreads) nogil:
    cdef int n = nthreads

    for i in range(0, nthreads):
        free(buffers[i].index)
        free(buffers[i].foi)

    free(buffers)


cdef void add_from_buffer(foi_buffer *buffer, double *wards_foi) nogil:
    cdef int i = 0
    cdef int count = buffer[0].count

    for i in range(0, count):
        wards_foi[buffer[0].index[i]] += buffer[0].foi[i]


cdef inline void add_to_buffer(foi_buffer *buffer, int index, double value,
                               double *wards_foi,
                               openmp.omp_lock_t *lock,
                               int buffer_size=4096) nogil:
    cdef int count = buffer[0].count

    buffer[0].index[count] = index
    buffer[0].foi[count] = value
    buffer[0].count = count + 1

    if buffer[0].count >= buffer_size:
        openmp.omp_set_lock(lock)
        add_from_buffer(buffer, wards_foi)
        openmp.omp_unset_lock(lock)
        buffer[0].count = 0


def iterate(network: Network, infections, play_infections,
            params: Parameters, rngs, timestep: int,
            population: int, nthreads: int = None,
            profiler: Profiler=None,
            is_dangerous=None,
            SELFISOLATE: bool = False,
            IMPORTS: bool = False):
    """Iterate the model forward one timestep (day) using the supplied
       network and parameters, advancing the supplied infections,
       and using the supplied random number generators (rngs)
       to generate random numbers (this is an array with one generator
       per thread). This iterates for a normal
       (working) day (with predictable movements, mixed
       with random movements)

       If SELFISOLATE is True then you need to pass in
       is_dangerous, which should be an array("i", network.nnodes)
    """
    if profiler is None:
        profiler = NullProfiler()

    p = profiler.start("iterate")

    cdef double uv = params.UV
    cdef int ts = timestep

    #starting day = 41
    cdef double uvscale = (1.0-uv/2.0 + cos(2.0*pi*ts/365.0)/2.0)

    cdef double cutoff = params.dyn_dist_cutoff

    cdef double thresh = 0.01

    links = network.to_links
    wards = network.nodes
    plinks = network.play

    cdef int i = 0
    cdef double * wards_day_foi = get_double_array_ptr(wards.day_foi)
    cdef double * wards_night_foi = get_double_array_ptr(wards.night_foi)
    cdef double night_foi

    p = p.start("setup")
    for i in range(1, network.nnodes+1):
        wards_day_foi[i] = 0.0
        wards_night_foi[i] = 0.0

    p = p.stop()

    if IMPORTS:
        p = p.start("imports")
        imported = import_infection(network=network, infections=infections,
                                    play_infections=play_infections,
                                    params=params, rng=rngs[0],
                                    population=population)

        print(f"Day: {timestep} Imports: expected {params.daily_imports} "
              f"actual {imported}")
        p = p.stop()

    cdef int N_INF_CLASSES = len(infections)
    cdef double scl_foi_uv = 0.0
    cdef double contrib_foi = 0.0
    cdef double beta = 0.0
    cdef double play_at_home_scl = 0.0

    cdef int num_threads = nthreads
    cdef unsigned long [::1] rngs_view = rngs
    cdef binomial_rng* r = _get_binomial_ptr(rngs[0])

    cdef int j = 0
    cdef int k = 0
    cdef int l = 0
    cdef int inf_ij = 0
    cdef double weight = 0.0
    cdef double distance = 0.0
    cdef double * links_weight = get_double_array_ptr(links.weight)
    cdef int * links_ifrom = get_int_array_ptr(links.ifrom)
    cdef int * links_ito = get_int_array_ptr(links.ito)
    cdef int ifrom = 0
    cdef int ito = 0
    cdef int staying, moving, play_move, end_p
    cdef double * links_distance = get_double_array_ptr(links.distance)
    cdef double frac = 0.0
    cdef double cumulative_prob = 0
    cdef double prob_scaled
    cdef double too_ill_to_move

    cdef int * wards_begin_p = get_int_array_ptr(wards.begin_p)
    cdef int * wards_end_p = get_int_array_ptr(wards.end_p)

    cdef double * plinks_distance = get_double_array_ptr(plinks.distance)
    cdef double * plinks_weight = get_double_array_ptr(plinks.weight)
    cdef int * plinks_ifrom = get_int_array_ptr(plinks.ifrom)
    cdef int * plinks_ito = get_int_array_ptr(plinks.ito)

    cdef double * wards_denominator_d = get_double_array_ptr(wards.denominator_d)
    cdef double * wards_denominator_n = get_double_array_ptr(wards.denominator_n)
    cdef double * wards_denominator_p = get_double_array_ptr(wards.denominator_p)
    cdef double * wards_denominator_pd = get_double_array_ptr(wards.denominator_pd)

    cdef double * links_suscept = get_double_array_ptr(links.suscept)
    cdef double * wards_play_suscept = get_double_array_ptr(wards.play_suscept)

    cdef double * wards_day_inf_prob = get_double_array_ptr(wards.day_inf_prob)
    cdef double * wards_night_inf_prob = get_double_array_ptr(wards.night_inf_prob)

    cdef int * wards_label = get_int_array_ptr(wards.label)

    cdef int * infections_i
    cdef int * play_infections_i

    cdef int * is_dangerous_array

    cdef int nnodes_plus_one = network.nnodes + 1
    cdef int nlinks_plus_one = network.nlinks + 1

    cdef binomial_rng* pr   # pointer to parallel rng
    cdef int thread_id

    cdef foi_buffer * day_buffers = allocate_foi_buffers(num_threads)
    cdef foi_buffer * day_buffer
    cdef foi_buffer * night_buffers = allocate_foi_buffers(num_threads)
    cdef foi_buffer * night_buffer

    cdef int cSELFISOLATE = 0

    if SELFISOLATE:
        cSELFISOLATE = 1
        is_dangerous_array = get_int_array_ptr(is_dangerous)

    cdef openmp.omp_lock_t lock
    openmp.omp_init_lock(&lock)

    p = p.start("loop_over_classes")
    for i in range(0, N_INF_CLASSES):
        contrib_foi = params.disease_params.contrib_foi[i]
        beta = params.disease_params.beta[i]
        scl_foi_uv = contrib_foi * beta * uvscale
        too_ill_to_move = params.disease_params.too_ill_to_move[i]

        # number of people staying gets bigger as
        # PlayAtHome increases
        play_at_home_scl = <double>(params.dyn_play_at_home *
                                    too_ill_to_move)

        infections_i = get_int_array_ptr(infections[i])
        play_infections_i = get_int_array_ptr(play_infections[i])

        if contrib_foi > 0:
            p = p.start(f"work_{i}")
            with nogil, parallel(num_threads=1):
                thread_id = cython.parallel.threadid()
                pr = _get_binomial_ptr(rngs_view[thread_id])
                day_buffer = &(day_buffers[thread_id])
                night_buffer = &(night_buffers[thread_id])
                day_buffer[0].count = 0
                night_buffer[0].count = 0

                for j in prange(1, nlinks_plus_one, schedule="static"):
                    # deterministic movements (e.g. to work)
                    inf_ij = infections_i[j]
                    if inf_ij > 0:
                        weight = links_weight[j]
                        ifrom = links_ifrom[j]
                        ito = links_ito[j]

                        #if inf_ij > weight:
                        #    print(f"inf[{i}][{j}] {inf_ij} > links[j].weight "
                        #        f"{weight}")

                        if links_distance[j] < cutoff:
                            if cSELFISOLATE:
                                frac = is_dangerous_array[ito] / (
                                                    wards_denominator_d[ito] +
                                                    wards_denominator_p[ito])

                                if frac > thresh:
                                    staying = infections_i[j]
                                else:
                                    # number staying - this is G_ij
                                    staying = _ran_binomial(pr,
                                                            too_ill_to_move,
                                                            inf_ij)
                            else:
                                # number staying - this is G_ij
                                staying = _ran_binomial(pr,
                                                        too_ill_to_move,
                                                        inf_ij)

                            #if staying < 0:
                            #    print(f"staying < 0")

                            # number moving, this is I_ij - G_ij
                            moving = inf_ij - staying

                            if staying > 0:
                                add_to_buffer(day_buffer, ifrom,
                                              staying * scl_foi_uv,
                                              &(wards_day_foi[0]), &lock)
                            #wards_day_foi[ifrom] += staying * scl_foi_uv

                            # Daytime Force of
                            # Infection is proportional to
                            # number of people staying
                            # in the ward (too ill to work)
                            # this is the sum for all G_ij (including g_ii
                            if moving > 0:
                                add_to_buffer(day_buffer, ito,
                                              moving * scl_foi_uv,
                                              &(wards_day_foi[0]), &lock)
                            #wards_day_foi[ito] += moving * scl_foi_uv

                            # Daytime FOI for destination is incremented (including self links, I_ii)
                        else:
                            # outside cutoff
                            if inf_ij > 0:
                                add_to_buffer(day_buffer, ifrom,
                                              inf_ij * scl_foi_uv,
                                              &(wards_day_foi[0]), &lock)
                            #wards_day_foi[ifrom] += inf_ij * scl_foi_uv

                        if inf_ij > 0:
                            add_to_buffer(night_buffer, ifrom,
                                          inf_ij * scl_foi_uv,
                                          &(wards_night_foi[0]), &lock)
                        #wards_night_foi[ifrom] += inf_ij * scl_foi_uv

                        # Nighttime Force of Infection is
                        # prop. to the number of Infected individuals
                        # in the ward
                        # This I_ii in Lambda^N

                    # end of if inf_ij (are there any new infections)
                # end of infectious class loop

                openmp.omp_set_lock(&lock)
                add_from_buffer(day_buffer, &(wards_day_foi[0]))
                add_from_buffer(night_buffer, &(wards_night_foi[0]))
                openmp.omp_unset_lock(&lock)
            # end of parallel section
            p = p.stop()

            p = p.start(f"play_{i}")
            with nogil, parallel(num_threads=1):
                thread_id = cython.parallel.threadid()
                pr = _get_binomial_ptr(rngs_view[thread_id])
                day_buffer = &(day_buffers[thread_id])
                day_buffer[0].count = 0

                for j in prange(1, nnodes_plus_one, schedule="static"):
                    # playmatrix loop FOI loop (random/unpredictable movements)
                    inf_ij = play_infections_i[j]
                    if inf_ij > 0:
                        wards_night_foi[j] += inf_ij * scl_foi_uv

                        staying = _ran_binomial(pr, play_at_home_scl, inf_ij)

                        #if staying < 0:
                        #    print(f"staying < 0")

                        moving = inf_ij - staying

                        cumulative_prob = 0.0
                        k = wards_begin_p[j]

                        end_p = wards_end_p[j]

                        while (moving > 0) and (k < end_p):
                            # distributing people across play wards
                            if plinks_distance[k] < cutoff:
                                weight = plinks_weight[k]
                                ifrom = plinks_ifrom[k]
                                ito = plinks_ito[k]

                                prob_scaled = weight / (1.0 - cumulative_prob)
                                cumulative_prob = cumulative_prob + weight

                                play_move = _ran_binomial(pr, prob_scaled, moving)

                                if cSELFISOLATE:
                                    frac = is_dangerous_array[ito] / (
                                                    wards_denominator_d[ito] +
                                                    wards_denominator_p[ito])

                                    if frac > thresh:
                                        staying = staying + play_move
                                    else:
                                        add_to_buffer(day_buffer, ito,
                                                      play_move * scl_foi_uv,
                                                      &(wards_day_foi[0]),
                                                      &lock)
                                        #wards_day_foi[ito] += play_move * scl_foi_uv
                                else:
                                    add_to_buffer(day_buffer, ito,
                                                  play_move * scl_foi_uv,
                                                  &(wards_day_foi[0]),
                                                  &lock)
                                    #wards_day_foi[ito] += play_move * scl_foi_uv

                                moving = moving - play_move
                            # end of if within cutoff

                            k = k + 1
                        # end of while loop

                        wards_day_foi[j] += (moving + staying) * scl_foi_uv
                    # end of if inf_ij (there are new infections)

                # end of loop over all nodes
                openmp.omp_set_lock(&lock)
                add_from_buffer(day_buffer, &(wards_day_foi[0]))
                openmp.omp_unset_lock(&lock)
            # end of parallel
            p = p.stop()
        # end of params.disease_params.contrib_foi[i] > 0:
    p = p.stop()
    # end of loop over all disease classes

    free_foi_buffers(&(day_buffers[0]), num_threads)
    free_foi_buffers(&(night_buffers[0]), num_threads)

    cdef int * infections_i_plus_one
    cdef int * play_infections_i_plus_one
    cdef double disease_progress = 0.0

    p = p.start("recovery")
    for i in range(N_INF_CLASSES-2, -1, -1):
        # recovery, move through classes backwards (loop down to 0)
        infections_i = get_int_array_ptr(infections[i])
        infections_i_plus_one = get_int_array_ptr(infections[i+1])
        play_infections_i = get_int_array_ptr(play_infections[i])
        play_infections_i_plus_one = get_int_array_ptr(play_infections[i+1])
        disease_progress = params.disease_params.progress[i]

        with nogil, parallel(num_threads=num_threads):
            thread_id = cython.parallel.threadid()
            pr = _get_binomial_ptr(rngs_view[thread_id])

            for j in prange(1, nlinks_plus_one, schedule="static"):
                inf_ij = infections_i[j]

                if inf_ij > 0:
                    l = _ran_binomial(pr, disease_progress, inf_ij)

                    if l > 0:
                        infections_i_plus_one[j] += l
                        infections_i[j] -= l

            for j in prange(1, nnodes_plus_one, schedule="static"):
                inf_ij = play_infections_i[j]

                if inf_ij > 0:
                    l = _ran_binomial(pr, disease_progress, inf_ij)

                    if l > 0:
                        play_infections_i_plus_one[j] += l
                        play_infections_i[j] -= l

        # end of parallel section
    # end of recovery loop
    p = p.stop()

    advance_infprob_omp(network=network, infections=infections,
                        play_infections=play_infections,
                        rngs=rngs, nthreads=nthreads,
                        profiler=profiler)

    advance_fixed_omp(network=network, infections=infections,
                      play_infections=play_infections,
                      rngs=rngs, nthreads=nthreads,
                      profiler=profiler)

    advance_play_omp(network=network, infections=infections,
                     play_infections=play_infections,
                     rngs=rngs, nthreads=nthreads,
                     profiler=profiler)

    p.stop()
