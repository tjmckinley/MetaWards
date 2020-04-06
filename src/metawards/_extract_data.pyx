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

cimport cython
from libc.math cimport sqrt

from cython.parallel import parallel, prange
cimport openmp

from ._network import Network
from ._parameters import Parameters
from ._profiler import Profiler, NullProfiler
from ._population import Population
from ._workspace import Workspace


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


cdef struct inf_buffer:
    int count
    int *index
    int *infected


cdef int buffer_size = 128  # the number of ints to hold in each thread buffer


cdef inf_buffer* allocate_inf_buffers(int nthreads) nogil:
    cdef int size = buffer_size
    cdef int n = nthreads

    cdef inf_buffer *buffers = <inf_buffer *> malloc(n * sizeof(inf_buffer))

    for i in range(0, nthreads):
        buffers[i].count = 0
        buffers[i].index = <int *> malloc(size * sizeof(int))
        buffers[i].infected = <int *> malloc(size * sizeof(int))

    return buffers


cdef void free_inf_buffers(inf_buffer *buffers, int nthreads) nogil:
    cdef int n = nthreads

    for i in range(0, nthreads):
        free(buffers[i].index)
        free(buffers[i].infected)

    free(buffers)


cdef void add_from_buffer(inf_buffer *buffer, int *wards_infected) nogil:
    cdef int i = 0
    cdef int count = buffer[0].count

    for i in range(0, count):
        wards_infected[buffer[0].index[i]] += buffer[0].infected[i]


cdef inline void add_to_buffer(inf_buffer *buffer, int index, int value,
                               int *wards_infected,
                               openmp.omp_lock_t *lock) nogil:
    cdef int count = buffer[0].count

    buffer[0].index[count] = index
    buffer[0].infected[count] = value
    buffer[0].count = count + 1

    if buffer[0].count >= buffer_size:
        openmp.omp_set_lock(lock)
        add_from_buffer(buffer, wards_infected)
        openmp.omp_unset_lock(lock)
        buffer[0].count = 0


def extract_data(network: Network, infections, play_infections,
                 timestep: int, files, workspace: Workspace,
                 population: Population, is_dangerous=None,
                 nthreads: int=None,
                 profiler: Profiler=None, SELFISOLATE: bool = False):
    """Extract data for timestep 'timestep' from the network and
       infections and write this to the output files in 'files'
       (these must have been opened by 'open_files'). You need
       to pass in a Workspace that has been set up for the
       passed network and parameters

       If SELFISOLATE is True then you need to pass in
       is_dangerous, which should be an array("i", network.nnodes)
    """
    if profiler is None:
        profiler = NullProfiler()

    p = profiler.start("extract_data")

    links = network.to_links
    wards = network.nodes

    cdef int N_INF_CLASSES = len(infections)
    cdef int MAXSIZE = network.nnodes + 1

    assert len(infections) == len(play_infections)

    if SELFISOLATE and (is_dangerous is None):
        raise AssertionError("You must pass in the 'is_dangerous' array "
                             "if SELFISOLATE is True")

    workspace.zero_all()

    files[0].write("%d " % timestep)
    files[1].write("%d " % timestep)
    files[3].write("%d " % timestep)

    cdef int * inf_tot = get_int_array_ptr(workspace.inf_tot)
    cdef int * pinf_tot = get_int_array_ptr(workspace.pinf_tot)
    cdef int * total_inf_ward = get_int_array_ptr(workspace.total_inf_ward)
    cdef int * total_new_inf_ward = get_int_array_ptr(workspace.total_new_inf_ward)
    cdef int * n_inf_wards = get_int_array_ptr(workspace.n_inf_wards)

    cdef int total = 0
    cdef int total_new = 0

    cdef int recovereds = 0
    cdef int susceptibles = 0
    cdef int latent = 0

    cdef double x, y
    cdef double sum_x = 0.0
    cdef double sum_y = 0.0
    cdef double sum_x2 = 0.0
    cdef double sum_y2 = 0.0
    cdef double mean_x = 0.0
    cdef double mean_y = 0.0
    cdef double var_x = 0.0
    cdef double var_y = 0.0
    cdef double dispersal = 0.0

    cdef int i, j
    cdef double * links_suscept = get_double_array_ptr(links.suscept)
    cdef int * links_ifrom = get_int_array_ptr(links.ifrom)
    cdef int * links_ito = get_int_array_ptr(links.ito)

    cdef int * infections_i
    cdef int * play_infections_i

    cdef double * wards_play_suscept = get_double_array_ptr(wards.play_suscept)
    cdef double * wards_x = get_double_array_ptr(wards.x)
    cdef double * wards_y = get_double_array_ptr(wards.y)

    cdef int * is_dangerous_array

    cdef int pinf = 0

    cdef int cSELFISOLATE = 0

    cdef int num_threads = nthreads
    cdef int nlinks_plus_one = network.nlinks + 1
    cdef int nnodes_plus_one = network.nnodes + 1

    cdef openmp.omp_lock_t lock
    openmp.omp_init_lock(&lock)


    if SELFISOLATE:
        is_dangerous_array = get_int_array_ptr(is_dangerous)
        cSELFISOLATE = 1

    p = p.start("loop_over_classes")

    for i in range(0, N_INF_CLASSES):
        # do we need to initialise total_new_inf_wards and
        # total_inf_wards to 0?
        n_inf_wards[i] = 0
        inf_tot[i] = 0
        pinf_tot[i] = 0

        infections_i = get_int_array_ptr(infections[i])
        play_infections_i = get_int_array_ptr(play_infections[i])

        with nogil, parallel(num_threads=num_threads):
            for j in prange(1, nlinks_plus_one, schedule="static"):
                if i == 0:
                    susceptibles += <int>(links_suscept[j])
                    total_new_inf_ward[links_ifrom[j]] += infections_i[j]

                if infections_i[j] != 0:
                    if cSELFISOLATE:
                        if (i > 4) and (i < 10):
                            is_dangerous_array[links_ito[j]] += infections_i[j]

                    inf_tot[i] += infections_i[j]
                    total_inf_ward[links_ifrom[j]] += infections_i[j]

        for j in range(1, network.nnodes+1):
            if i == 0:
                susceptibles += <int>(wards_play_suscept[j])
                if play_infections_i[j] > 0:
                    total_new_inf_ward[j] += play_infections_i[j]

                if total_new_inf_ward[j] != 0:
                    newinf = total_new_inf_ward[j]
                    x = wards_x[j]
                    y = wards_y[j]
                    sum_x += newinf * x
                    sum_y += newinf * y
                    sum_x2 += newinf * x * x
                    sum_y2 += newinf * y * y
                    total_new += newinf

            if play_infections_i[j] > 0:
                pinf = play_infections_i[j]
                pinf_tot[i] += pinf
                total_inf_ward[j] += pinf

                if cSELFISOLATE:
                    if (i > 4) and (i < 10):
                        is_dangerous_array[i] += pinf

            if (i < N_INF_CLASSES-1) and total_inf_ward[j] > 0:
                n_inf_wards[i] += 1

        files[0].write("%d " % inf_tot[i])
        files[1].write("%d " % n_inf_wards[i])
        files[3].write("%d " % pinf_tot[i])

        if i == 1:
            latent += inf_tot[i] + pinf_tot[i]
        elif (i < N_INF_CLASSES-1) and (i > 1):
            total += inf_tot[i] + pinf_tot[i]
        else:
            recovereds += inf_tot[i] + pinf_tot[i]

    p = p.stop()

    p = p.start("write_to_files")
    if total_new > 1:  # CHECK - this should be > 1 rather than > 0
        mean_x = sum_x / total_new
        mean_y = sum_y / total_new

        var_x = (sum_x2 - sum_x*mean_x) / (total_new - 1)
        var_y = (sum_y2 - sum_y*mean_y) / (total_new - 1)

        dispersal = sqrt(var_x + var_y)
        files[2].write("%d %f %f\n" % (timestep, mean_x, mean_y))
        files[5].write("%d %f %f\n" % (timestep, var_x, var_y))
        files[6].write("%d %f\n" % (timestep, dispersal))
    else:
        files[2].write("%d %f %f\n" % (timestep, 0.0, 0.0))
        files[5].write("%d %f %f\n" % (timestep, 0.0, 0.0))
        files[6].write("%d %f\n" % (timestep, 0.0))

    files[0].write("\n")
    files[1].write("\n")
    files[3].write("\n")
    files[4].write("%d \n" % total)
    files[4].flush()

    p = p.stop()

    print(f"S: {susceptibles}    ", end="")
    print(f"E: {latent}    ", end="")
    print(f"I: {total}    ", end="")
    print(f"R: {recovereds}    ", end="")
    print(f"IW: {n_inf_wards[0]}   ", end="")
    print(f"TOTAL POPULATION {susceptibles+total+recovereds}")

    if population is not None:
        population.susceptibles = susceptibles
        population.total = total
        population.recovereds = recovereds
        population.latent = latent
        population.n_inf_wards = n_inf_wards[0]

        #if population.population != population.initial:
        #    print(f"DISAGREEMENT WITH POPULATION COUNT! {population.initial} "
        #          f"versus {population.population}!")

    p.stop()

    return total + latent
