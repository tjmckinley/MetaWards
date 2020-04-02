
cimport cython
from libc.math cimport sqrt

from ._network import Network
from ._parameters import Parameters
from ._profiler import Profiler, NullProfiler
from ._population import Population
from ._workspace import Workspace


@cython.boundscheck(False)
@cython.wraparound(False)
def extract_data(network: Network, infections, play_infections,
                 timestep: int, files, workspace: Workspace,
                 population: Population, is_dangerous=None,
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

    N_INF_CLASSES = len(infections)
    MAXSIZE = network.nnodes + 1

    assert len(infections) == len(play_infections)

    if SELFISOLATE and (is_dangerous is None):
        raise AssertionError("You must pass in the 'is_dangerous' array "
                             "if SELFISOLATE is True")

    workspace.zero_all()

    files[0].write("%d " % timestep)
    files[1].write("%d " % timestep)
    files[3].write("%d " % timestep)

    cdef int [::1] inf_tot = workspace.inf_tot
    cdef int [::1] pinf_tot = workspace.pinf_tot
    cdef int [::1] total_inf_ward = workspace.total_inf_ward
    cdef int [::1] total_new_inf_ward = workspace.total_new_inf_ward
    cdef int [::1] n_inf_wards = workspace.n_inf_wards

    cdef int total = 0
    cdef int total_new = 0

    cdef int recovereds = 0
    cdef int susceptibles = 0
    cdef int latent = 0

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
    cdef double [::1] links_suscept = links.suscept
    cdef int [::1] links_ifrom = links.ifrom
    cdef int [::1] links_ito = links.ito

    cdef int [::1] infections_i, play_infections_i

    cdef double [::1] wards_play_suscept = wards.play_suscept
    cdef double [::1] wards_x = wards.x
    cdef double [::1] wards_y = wards.y

    cdef int [::1] is_dangerous_array

    if SELFISOLATE:
        is_dangerous_array = is_dangerous

    p = p.start("loop_over_classes")

    for i in range(0, N_INF_CLASSES):
        # do we need to initialise total_new_inf_wards and
        # total_inf_wards to 0?

        infections_i = infections[i]
        play_infections_i = play_infections[i]

        for j in range(1, network.nlinks+1):
            if i == 0:
                susceptibles += <int>(links_suscept[j])
                total_new_inf_ward[links_ifrom[j]] += infections_i[j]

            if infections_i[j] != 0:
                if SELFISOLATE:
                    if (i > 4) and (i < 10):
                        is_dangerous[links_ito[j]] += infections_i[j]

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
                #print(f"pinf[{i}][{j}] > 0: {play_infections[i][j]}")
                pinf = play_infections_i[j]
                pinf_tot[i] += pinf
                total_inf_ward[j] += pinf

                if SELFISOLATE:
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
        mean_x = <double>sum_x / <double>total_new
        mean_y = <double>sum_y / <double>total_new

        var_x = <double>(sum_x2 - sum_x*mean_x) / <double>(total_new - 1)
        var_y = <double>(sum_y2 - sum_y*mean_y) / <double>(total_new - 1)

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

        if population.population != population.initial:
            print(f"DISAGREEMENT WITH POPULATION COUNT! {population.initial} "
                  f"versus {population.population}!")

    p.stop()

    return total + latent
