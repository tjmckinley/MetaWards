#!/bin/env/python3
#cython: linetrace=False
# MUST ALWAYS DISABLE AS WAY TOO SLOW FOR ITERATE

cimport cython

from libc.math cimport sqrt
from libc.stdlib cimport malloc, free
cimport openmp

from .._network import Network
from .._parameters import Parameters
from .._outputfiles import OutputFiles
from .._population import Population

from ..utils._profiler import Profiler, NullProfiler
from ..utils._workspace import Workspace

from ..utils._get_array_ptr cimport get_int_array_ptr, get_double_array_ptr

__all__ = ["setup_output_default", "output_default", "output_default_omp"]


cdef struct _inf_buffer:
    int count
    int *index
    int *infected


cdef _inf_buffer* _allocate_inf_buffers(int nthreads,
                                        int buffer_size=1024) nogil:
    cdef int size = buffer_size
    cdef int n = nthreads

    cdef _inf_buffer *buffers = <_inf_buffer *> malloc(n * sizeof(_inf_buffer))

    for i in range(0, n):
        buffers[i].count = 0
        buffers[i].index = <int *> malloc(size * sizeof(int))
        buffers[i].infected = <int *> malloc(size * sizeof(int))

    return buffers


cdef void _free_inf_buffers(_inf_buffer *buffers, int nthreads) nogil:
    cdef int n = nthreads

    for i in range(0, n):
        free(buffers[i].index)
        free(buffers[i].infected)

    free(buffers)


cdef void _reset_inf_buffer(_inf_buffer *buffers, int nthreads) nogil:
    cdef int n = nthreads
    cdef int i = 0

    for i in range(0, n):
        buffers[i].count = 0


cdef void _add_from_buffer(_inf_buffer *buffer, int *wards_infected) nogil:
    cdef int i = 0
    cdef int count = buffer[0].count

    for i in range(0, count):
        wards_infected[buffer[0].index[i]] += buffer[0].infected[i]

    buffer[0].count = 0


cdef inline void _add_to_buffer(_inf_buffer *buffer, int index, int value,
                                int *wards_infected,
                                openmp.omp_lock_t *lock,
                                int buffer_size=1024) nogil:
    cdef int count = buffer[0].count

    buffer[0].index[count] = index
    buffer[0].infected[count] = value
    buffer[0].count = count + 1

    if buffer[0].count >= buffer_size:
        openmp.omp_set_lock(lock)
        _add_from_buffer(buffer, wards_infected)
        openmp.omp_unset_lock(lock)
        buffer[0].count = 0


# struct to hold all of the variables that will be reduced across threads
cdef struct _red_variables:
    double sum_x
    double sum_y
    double sum_x2
    double sum_y2
    int n_inf_wards
    int total_new
    int inf_tot
    int pinf_tot
    int is_dangerous
    int susceptibles


cdef void _reset_reduce_variables(_red_variables * variables,
                                  int nthreads) nogil:
    cdef int i = 0
    cdef int n = nthreads

    for i in range(0, n):
        variables[i].sum_x = 0
        variables[i].sum_y = 0
        variables[i].sum_x2 = 0
        variables[i].sum_y2 = 0
        variables[i].n_inf_wards = 0
        variables[i].total_new = 0
        variables[i].inf_tot = 0
        variables[i].pinf_tot = 0
        variables[i].is_dangerous = 0
        variables[i].susceptibles = 0


cdef _red_variables* _allocate_red_variables(int nthreads) nogil:
    """Allocate space for thread-local reduction variables for each
       of the 'nthreads' threads. Note that we need this as
       cython won't allow reduction in parallel blocks (only loops)
    """
    cdef int n = nthreads

    cdef _red_variables *variables = <_red_variables *> malloc(
                                                n * sizeof(_red_variables))


    _reset_reduce_variables(variables, n)

    return variables


cdef void _free_red_variables(_red_variables *variables) nogil:
    """Free the memory held by the reduction variables"""
    free(variables)


cdef void _reduce_variables(_red_variables *variables, int nthreads) nogil:
    """Reduce all of the thread-local totals in 'variables' for
       the 'nthreads' threads into the values in variables[0]
    """
    cdef int i = 0
    cdef int n = nthreads

    if n > 1:
        for i in range(1, n):
            variables[0].sum_x += variables[i].sum_x
            variables[0].sum_y += variables[i].sum_y
            variables[0].sum_x2 += variables[i].sum_x2
            variables[0].sum_y2 += variables[i].sum_y2
            variables[0].n_inf_wards += variables[i].n_inf_wards
            variables[0].total_new += variables[i].total_new
            variables[0].inf_tot += variables[i].inf_tot
            variables[0].pinf_tot += variables[i].pinf_tot
            variables[0].is_dangerous += variables[i].is_dangerous
            variables[0].susceptibles += variables[i].susceptibles


# Global variables that are used to cache information that is needed
# from one iteration to the next - this is safe as metawards will
# only run one model run at a time per process
cdef int _buffer_nthreads = 0
cdef _inf_buffer * _total_new_inf_ward_buffers = <_inf_buffer*>0
cdef _inf_buffer * _total_inf_ward_buffers = <_inf_buffer*>0
cdef _red_variables * _redvars = <_red_variables*>0

_files = None


def setup_output_default(network: Network,
                         output_dir: OutputFiles,
                         nthreads: int,
                         **kwargs):
    """This is the setup function that corresponds with
       :meth:`~metawards.extractors.output_default`.
    """
    global _buffer_nthreads

    if _buffer_nthreads != nthreads:
        global _total_new_inf_ward_buffers
        global _total_inf_ward_buffers
        global _redvars

        if _buffer_nthreads != 0:
            _free_red_variables(_redvars)
            _free_inf_buffers(_total_new_inf_ward_buffers, nthreads)
            _free_inf_buffers(_total_inf_ward_buffers, nthreads)

        _redvars = _allocate_red_variables(nthreads)
        _total_new_inf_ward_buffers = _allocate_inf_buffers(nthreads)
        _total_inf_ward_buffers = _allocate_inf_buffers(nthreads)
        _buffer_nthreads = nthreads

    global _files

    _files = []
    _files.append(output_dir.open("WorkInfections.dat"))
    _files.append(output_dir.open("NumberWardsInfected.dat"))
    _files.append(output_dir.open("MeanXY.dat"))
    _files.append(output_dir.open("PlayInfections.dat"))
    _files.append(output_dir.open("TotalInfections.dat"))
    _files.append(output_dir.open("VarXY.dat"))
    _files.append(output_dir.open("Dispersal.dat"))


def output_default_omp(network: Network, population: Population,
                       output_dir: OutputFiles,
                       workspace: Workspace,
                       infections, play_infections,
                       nthreads: int, profiler: Profiler,
                       **kwargs):
    """This is the default output function that must be called
       every iteration as it is responsible for accumulating
       the core data each day, which is used to report a summary
       to the main output file. This is the parallel version
       of this function.

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
       infections
         Space to hold the 'work' infections
       play_infections
         Space to hold the 'play' infections
       nthreads: int
         The number of threads to use to help extract the data
       profiler: Profiler
         The profiler used to profile this function
       kwargs
         Extra argumentst that are ignored by this function
    """
    from cython.parallel import parallel, prange

    p = profiler.start("extract_data")

    links = network.to_links
    wards = network.nodes

    cdef int N_INF_CLASSES = len(infections)

    assert len(infections) == len(play_infections)

    workspace.zero_all()

    cdef int timestep = population.day

    global _files
    _files[0].write("%d " % timestep)
    _files[1].write("%d " % timestep)
    _files[3].write("%d " % timestep)

    global _total_inf_ward_buffers
    global _total_new_inf_ward_buffers
    global _redvars

    cdef int * inf_tot = get_int_array_ptr(workspace.inf_tot)
    cdef int * pinf_tot = get_int_array_ptr(workspace.pinf_tot)
    cdef int * total_inf_ward = get_int_array_ptr(workspace.total_inf_ward)
    cdef int * total_new_inf_ward = get_int_array_ptr(
                                                workspace.total_new_inf_ward)
    cdef int * n_inf_wards = get_int_array_ptr(workspace.n_inf_wards)

    cdef int total = 0
    cdef int total_new = 0
    cdef int recovereds = 0
    cdef int susceptibles = 0
    cdef int latent = 0

    cdef double x = 0.0
    cdef double y = 0.0

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

    cdef int pinf = 0

    cdef int num_threads = nthreads
    cdef int thread_id = 0
    cdef int ifrom = 0
    cdef int newinf = 0
    cdef int nlinks_plus_one = network.nlinks + 1
    cdef int nnodes_plus_one = network.nnodes + 1

    cdef openmp.omp_lock_t lock
    openmp.omp_init_lock(&lock)

    cdef _inf_buffer * total_new_inf_ward_buffer
    cdef _inf_buffer * total_inf_ward_buffer
    cdef _red_variables * redvar

    p = p.start("loop_over_classes")

    for i in range(0, N_INF_CLASSES):
        n_inf_wards[i] = 0
        inf_tot[i] = 0
        pinf_tot[i] = 0

        _reset_reduce_variables(_redvars, num_threads)
        _reset_inf_buffer(_total_inf_ward_buffers, num_threads)
        _reset_inf_buffer(_total_new_inf_ward_buffers, num_threads)

        infections_i = get_int_array_ptr(infections[i])
        play_infections_i = get_int_array_ptr(play_infections[i])

        with nogil, parallel(num_threads=num_threads):
            thread_id = cython.parallel.threadid()
            total_inf_ward_buffer = &(_total_inf_ward_buffers[thread_id])
            total_new_inf_ward_buffer = \
                                &(_total_new_inf_ward_buffers[thread_id])
            redvar = &(_redvars[thread_id])

            for j in prange(1, nlinks_plus_one, schedule="static"):
                ifrom = links_ifrom[j]

                if i == 0:
                    redvar[0].susceptibles += <int>(links_suscept[j])

                    if infections_i[j] != 0:
                        _add_to_buffer(total_new_inf_ward_buffer,
                                       ifrom, infections_i[j],
                                       &(total_new_inf_ward[0]), &lock)
                        #total_new_inf_ward[links_ifrom[j]] += infections_i[j]

                if infections_i[j] != 0:
                    redvar[0].inf_tot += infections_i[j]
                    _add_to_buffer(total_inf_ward_buffer,
                                   ifrom, infections_i[j],
                                   &(total_inf_ward[0]), &lock)
                    #total_inf_ward[links_ifrom[j]] += infections_i[j]
            # end of loop over links

            # cannot reduce in parallel, so manual reduction
            openmp.omp_set_lock(&lock)
            _add_from_buffer(total_new_inf_ward_buffer,
                             &(total_new_inf_ward[0]))
            _add_from_buffer(total_inf_ward_buffer,
                             &(total_inf_ward[0]))
            openmp.omp_unset_lock(&lock)

            # loop over wards (nodes)
            for j in prange(1, nnodes_plus_one, schedule="static"):
                if i == 0:
                    redvar[0].susceptibles += <int>(wards_play_suscept[j])

                    if play_infections_i[j] > 0:
                        total_new_inf_ward[j] += play_infections_i[j]

                    if total_new_inf_ward[j] != 0:
                        newinf = total_new_inf_ward[j]
                        x = wards_x[j]
                        y = wards_y[j]
                        redvar[0].sum_x += newinf * x
                        redvar[0].sum_y += newinf * y
                        redvar[0].sum_x2 += newinf * x * x
                        redvar[0].sum_y2 += newinf * y * y
                        redvar[0].total_new += newinf

                if play_infections_i[j] > 0:
                    pinf = play_infections_i[j]
                    redvar[0].pinf_tot += pinf
                    total_inf_ward[j] += pinf

                if (i < N_INF_CLASSES-1) and total_inf_ward[j] > 0:
                    redvar[0].n_inf_wards += 1
            # end of loop over nodes
        # end of parallel

        # can now reduce across all threads (don't need to lock as each
        # thread maintained its own running total)
        _reduce_variables(_redvars, num_threads)

        inf_tot[i] = _redvars[0].inf_tot
        pinf_tot[i] = _redvars[0].pinf_tot
        n_inf_wards[i] = _redvars[0].n_inf_wards

        total_new += _redvars[0].total_new
        susceptibles += _redvars[0].susceptibles

        sum_x += _redvars[0].sum_x
        sum_y += _redvars[0].sum_y
        sum_x2 += _redvars[0].sum_x2
        sum_y2 += _redvars[0].sum_y2

        _reset_reduce_variables(_redvars, num_threads)

        _files[0].write("%d " % inf_tot[i])
        _files[1].write("%d " % n_inf_wards[i])
        _files[3].write("%d " % pinf_tot[i])

        if i == 1:
            latent += inf_tot[i] + pinf_tot[i]
        elif (i < N_INF_CLASSES-1) and (i > 1):
            total += inf_tot[i] + pinf_tot[i]
        else:
            recovereds += inf_tot[i] + pinf_tot[i]
    # end of loop over i
    p = p.stop()

    p = p.start("write_to_files")
    if total_new > 1:  # CHECK - this should be > 1 rather than > 0
        mean_x = sum_x / total_new
        mean_y = sum_y / total_new

        var_x = (sum_x2 - sum_x*mean_x) / (total_new - 1)
        var_y = (sum_y2 - sum_y*mean_y) / (total_new - 1)

        dispersal = sqrt(var_x + var_y)
        _files[2].write("%d %f %f\n" % (timestep, mean_x, mean_y))
        _files[5].write("%d %f %f\n" % (timestep, var_x, var_y))
        _files[6].write("%d %f\n" % (timestep, dispersal))
    else:
        _files[2].write("%d %f %f\n" % (timestep, 0.0, 0.0))
        _files[5].write("%d %f %f\n" % (timestep, 0.0, 0.0))
        _files[6].write("%d %f\n" % (timestep, 0.0))

    _files[0].write("\n")
    _files[1].write("\n")
    _files[3].write("\n")
    _files[4].write("%d \n" % total)
    _files[4].flush()

    p = p.stop()

    print(workspace.inf_tot)
    print(workspace.pinf_tot)

    print(f"S: {susceptibles}    ", end="")
    print(f"E: {latent}    ", end="")
    print(f"I: {total}    ", end="")
    print(f"R: {recovereds}    ", end="")
    print(f"IW: {n_inf_wards[0]}   ", end="")
    print(f"TOTAL POPULATION {susceptibles+latent+total+recovereds}")

    if population is not None:
        population.susceptibles = susceptibles
        population.total = total
        population.recovereds = recovereds
        population.latent = latent
        population.n_inf_wards = n_inf_wards[0]

    p.stop()

    return total + latent


def output_default_serial(network: Network, population: Population,
                          output_dir: OutputFiles, workspace: Workspace,
                          infections, play_infections,
                          profiler: Profiler, **kwargs):
    """This is the default output function that must be called
       every iteration as it is responsible for accumulating
       the core data each day, which is used to report a summary
       to the main output file. This is the serial version
       of this function.

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
       infections
         Space to hold the 'work' infections
       play_infections
         Space to hold the 'play' infections
       nthreads: int
         The number of threads to use to help extract the data
       profiler: Profiler
         The profiler used to profile this function
       kwargs
         Extra argumentst that are ignored by this function
    """
    kwargs["nthreads"] = 1
    output_default_omp(network=network, population=population,
                       output_dir=output_dir, workspace=workspace,
                       infections=infections,
                       play_infections=play_infections,
                       profiler=profiler, **kwargs)


def output_default(nthreads: int, **kwargs):
    """This is the default output function that must be called
       every iteration as it is responsible for accumulating
       the core data each day, which is used to report a summary
       to the main output file. This is the serial version
       of this function.

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
       infections
         Space to hold the 'work' infections
       play_infections
         Space to hold the 'play' infections
       nthreads: int
         The number of threads to use to help extract the data
       profiler: Profiler
         The profiler used to profile this function
       kwargs
         Extra argumentst that are ignored by this function
    """
    if nthreads == 1:
        output_default_serial(**kwargs)
    else:
        output_default_omp(nthreads=nthreads, **kwargs)
