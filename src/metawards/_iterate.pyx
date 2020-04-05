#!/bin/env/python3
#cython: boundscheck=False
#cython: cdivision=True
#cython: initializedcheck=False
#cython: cdivision_warnings=False
#cython: wraparound=False
#cython: binding=False
#cython: initializedcheck=False
#cython: nonecheck=False
#cython: overflowcheck=False


from libc.stdlib cimport malloc, free

cimport cython
from libc.math cimport cos, pi
from  ._rate_to_prob cimport rate_to_prob

from cython.parallel import parallel, prange
cimport openmp

from ._network import Network
from ._parameters import Parameters
from ._profiler import Profiler, NullProfiler
from ._import_infection import import_infection
from ._array import create_int_array, create_double_array

from ._ran_binomial cimport _ran_binomial, _get_binomial_ptr, binomial_rng

__all__ = ["iterate"]


cdef struct foi_buffer:
    int count
    int *index
    double *foi


cdef foi_buffer* allocate_foi_buffers(int nthreads, int buffer_size=1024) nogil:
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
                               openmp.omp_lock_t *lock) nogil:
    cdef int count = buffer[0].count

    buffer[0].index[count] = index
    buffer[0].foi[count] = value
    buffer[0].count = count + 1

    if buffer[0].count >= 1024:
        openmp.omp_set_lock(lock)
        add_from_buffer(buffer, wards_foi)
        openmp.omp_unset_lock(lock)
        buffer[0].count = 0


cdef double * _get_double_array_ptr(double_array):
    cdef double [::1] a = double_array
    return &(a[0])


cdef int * _get_int_array_ptr(int_array):
    cdef int [::1] a = int_array
    return &(a[0])


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
    cdef double * wards_day_foi = _get_double_array_ptr(wards.day_foi)
    cdef double * wards_night_foi = _get_double_array_ptr(wards.night_foi)
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
    cdef play_at_home_scl = 0.0

    cdef int num_threads = nthreads
    cdef unsigned long [::1] rngs_view = rngs
    cdef binomial_rng* r = _get_binomial_ptr(rngs[0])

    cdef int j = 0
    cdef int k = 0
    cdef int l = 0
    cdef int inf_ij = 0
    cdef double weight = 0.0
    cdef double distance = 0.0
    cdef double * links_weight = _get_double_array_ptr(links.weight)
    cdef int * links_ifrom = _get_int_array_ptr(links.ifrom)
    cdef int * links_ito = _get_int_array_ptr(links.ito)
    cdef int ifrom = 0
    cdef int ito = 0
    cdef int staying, moving, play_move, end_p
    cdef double * links_distance = _get_double_array_ptr(links.distance)
    cdef double frac = 0.0
    cdef double cumulative_prob = 0
    cdef double prob_scaled
    cdef double too_ill_to_move

    cdef int * wards_begin_p = _get_int_array_ptr(wards.begin_p)
    cdef int * wards_end_p = _get_int_array_ptr(wards.end_p)

    cdef double * plinks_distance = _get_double_array_ptr(plinks.distance)
    cdef double * plinks_weight = _get_double_array_ptr(plinks.weight)
    cdef int * plinks_ifrom = _get_int_array_ptr(plinks.ifrom)
    cdef int * plinks_ito = _get_int_array_ptr(plinks.ito)

    cdef double * wards_denominator_d = _get_double_array_ptr(wards.denominator_d)
    cdef double * wards_denominator_n = _get_double_array_ptr(wards.denominator_n)
    cdef double * wards_denominator_p = _get_double_array_ptr(wards.denominator_p)
    cdef double * wards_denominator_pd = _get_double_array_ptr(wards.denominator_pd)

    cdef double * links_suscept = _get_double_array_ptr(links.suscept)
    cdef double * wards_play_suscept = _get_double_array_ptr(wards.play_suscept)

    cdef int * wards_label = _get_int_array_ptr(wards.label)

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
        is_dangerous_array = _get_int_array_ptr(is_dangerous)

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

        infections_i = _get_int_array_ptr(infections[i])
        play_infections_i = _get_int_array_ptr(play_infections[i])

        if contrib_foi > 0:
            p = p.start(f"work_{i}")
            with nogil, parallel(num_threads=num_threads):
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
            for j in range(1, network.nnodes+1):
                # playmatrix loop FOI loop (random/unpredictable movements)
                inf_ij = play_infections_i[j]
                if inf_ij > 0:
                    wards_night_foi[j] += inf_ij * scl_foi_uv

                    staying = _ran_binomial(r, play_at_home_scl, inf_ij)

                    if staying < 0:
                        print(f"staying < 0")

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
                            cumulative_prob += weight

                            play_move = _ran_binomial(r, prob_scaled, moving)

                            if cSELFISOLATE:
                                frac = is_dangerous_array[ito] / (
                                                wards_denominator_d[ito] +
                                                wards_denominator_p[ito])

                                if frac > thresh:
                                    staying += play_move
                                else:
                                    wards_day_foi[ito] += play_move * scl_foi_uv
                            else:
                                wards_day_foi[ito] += play_move * scl_foi_uv

                            moving -= play_move
                        # end of if within cutoff

                        k += 1
                    # end of while loop

                    wards_day_foi[j] += (moving + staying) * scl_foi_uv
                # end of if inf_ij (there are new infections)

            # end of loop over all nodes
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
        infections_i = _get_int_array_ptr(infections[i])
        infections_i_plus_one = _get_int_array_ptr(infections[i+1])
        play_infections_i = _get_int_array_ptr(play_infections[i])
        play_infections_i_plus_one = _get_int_array_ptr(play_infections[i+1])
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

    cdef double length_day = params.length_day
    cdef double rate, inf_prob

    # i is set to 0 now as we are only dealing now with new infections
    i = 0
    infections_i = _get_int_array_ptr(infections[i])
    play_infections_i = _get_int_array_ptr(play_infections[i])

    p = p.start("fixed")
    with nogil, parallel(num_threads=num_threads):
        thread_id = cython.parallel.threadid()
        pr = _get_binomial_ptr(rngs_view[thread_id])

        for j in prange(1, nlinks_plus_one, schedule="static"):
            # actual new infections for fixed movements
            inf_prob = 0

            ifrom = links_ifrom[j]
            ito = links_ito[j]
            distance = links_distance[j]

            if distance < cutoff:
                # distance is below cutoff (reasonable distance)
                # infect in work ward
                if wards_day_foi[ito] > 0:
                    # daytime infection of link j
                    if cSELFISOLATE:
                        frac = is_dangerous_array[ito] / (
                                                wards_denominator_d[ito] +
                                                wards_denominator_p[ito])

                        if frac > thresh:
                            inf_prob = 0.0
                        else:
                            rate = (length_day * wards_day_foi[ito]) / (
                                                wards_denominator_d[ito] +
                                                wards_denominator_pd[ito])

                            inf_prob = rate_to_prob(rate)
                    else:
                        rate = (length_day * wards_day_foi[ito]) / (
                                                wards_denominator_d[ito] +
                                                wards_denominator_pd[ito])

                        inf_prob = rate_to_prob(rate)

                # end of if wards.day_foi[ito] > 0
            # end of if distance < cutoff
            elif wards_day_foi[ifrom] > 0:
                # if distance is too large then infect in home ward with day FOI
                rate = (length_day * wards_day_foi[ifrom]) / (
                                                wards_denominator_d[ifrom] +
                                                wards_denominator_pd[ifrom])

                inf_prob = rate_to_prob(rate)

            if inf_prob > 0.0:
                # daytime infection of workers
                l = _ran_binomial(pr, inf_prob, <int>(links_suscept[j]))

                if l > 0:
                    # actual infection
                    #print(f"InfProb {inf_prob}, susc {links.suscept[j]}, l {l}")
                    infections_i[j] += l
                    links_suscept[j] -= l

            if wards_night_foi[ifrom] > 0:
                # nighttime infection of workers
                rate = (1.0 - length_day) * (wards_night_foi[ifrom]) / (
                                                wards_denominator_n[ifrom] +
                                                wards_denominator_p[ifrom])

                inf_prob = rate_to_prob(rate)

                l = _ran_binomial(pr, inf_prob, <int>(links_suscept[j]))

                #if l > links_suscept[j]:
                #    print(f"l > links[{j}].suscept {links_suscept[j]} nighttime")

                if l > 0:
                    # actual infection
                    # print(f"NIGHT InfProb {inf_prob}, susc {links.suscept[j]}, {l}")
                    infections_i[j] += l
                    links_suscept[j] -= l
            # end of wards.night_foi[ifrom] > 0  (nighttime infections)
        # end of loop over all network links
    # end of parallel section
    p = p.stop()

    cdef int suscept = 0
    cdef double dyn_play_at_home = params.dyn_play_at_home

    p = p.start("play")
    with nogil, parallel(num_threads=num_threads):
        thread_id = cython.parallel.threadid()
        pr = _get_binomial_ptr(rngs_view[thread_id])

        for j in prange(1, nnodes_plus_one, schedule="static"):
            # playmatrix loop
            inf_prob = 0.0

            suscept = <int>wards_play_suscept[j]

            #if suscept < 0:
            #    print(f"play_suscept is less than 0 ({suscept}) "
            #        f"problem {j}, {wards_label[j]}")

            staying = _ran_binomial(pr, dyn_play_at_home, suscept)

            moving = suscept - staying

            cumulative_prob = 0.0

            # daytime infection of play matrix moves
            for k in range(wards_begin_p[j], wards_end_p[j]):
                if plinks_distance[k] < cutoff:
                    ito = plinks_ito[k]

                    if wards_day_foi[ito] > 0.0:
                        weight = plinks_weight[k]
                        prob_scaled = weight / (1.0-cumulative_prob)
                        cumulative_prob = cumulative_prob + weight

                        if cSELFISOLATE:
                            frac = is_dangerous_array[ito] / (
                                                    wards_denominator_p[ito] +
                                                    wards_denominator_d[ito])

                            if frac > thresh:
                                inf_prob = 0.0
                                play_move = 0
                            else:
                                play_move = _ran_binomial(pr, prob_scaled, moving)
                                frac = (length_day * wards_day_foi[ito]) / (
                                                    wards_denominator_pd[ito] +
                                                    wards_denominator_d[ito])

                                inf_prob = rate_to_prob(frac)
                        else:
                            play_move = _ran_binomial(pr, prob_scaled, moving)
                            frac = (length_day * wards_day_foi[ito]) / (
                                                    wards_denominator_pd[ito] +
                                                    wards_denominator_d[ito])

                            inf_prob = rate_to_prob(frac)

                        l = _ran_binomial(pr, inf_prob, play_move)

                        moving = moving - play_move

                        if l > 0:
                            # infection
                            #print(f"PLAY: InfProb {inf_prob}, susc {play_move}, "
                            #      f"l {l}")
                            #print(f"daytime play_infections[{i}][{j}] += {l}")
                            play_infections_i[j] += l
                            wards_play_suscept[j] -= l

                    # end of DayFOI if statement
                # end of Dynamics Distance if statement
            # end of loop over links of wards[j]

            if (staying + moving) > 0:
                # infect people staying at home
                frac = (length_day * wards_day_foi[j]) / (
                                            wards_denominator_pd[j] +
                                            wards_denominator_d[j])

                inf_prob = rate_to_prob(frac)

                l = _ran_binomial(pr, inf_prob, staying+moving)

                if l > 0:
                    # another infections, this time from home
                    #print(f"staying home play_infections[{i}][{j}] += {l}")
                    play_infections_i[j] += l
                    wards_play_suscept[j] -= l

            # nighttime infections of play movements
            night_foi = wards_night_foi[j]
            if night_foi > 0.0:
                frac = ((1.0 - length_day) * night_foi) / (
                                wards_denominator_n[j] + wards_denominator_p[j])

                inf_prob = rate_to_prob(frac)

                l = _ran_binomial(pr, inf_prob, <int>(wards_play_suscept[j]))

                if l > 0:
                    # another infection
                    #print(f"nighttime play_infections[{i}][{j}] += {l}")
                    play_infections_i[j] += l
                    wards_play_suscept[j] -= l
        # end of loop over wards (nodes)
    # end of parallel
    p = p.stop()

    p.stop()
