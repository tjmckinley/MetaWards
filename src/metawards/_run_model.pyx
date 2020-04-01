
from libc.math cimport sqrt, cos, pi, exp

import math

from ._network import Network
from ._parameters import Parameters
from ._workspace import Workspace
from ._population import Population

from typing import List
from array import array
import time

import os

__all__ = ["run_model"]


cdef double rate_to_prob(double rate):
    """Convert the return the probability associated with the passed
       infection rate
    """
    if rate < 1e-6:
        return rate - (rate*rate / 2.0)
    else:
        return 1.0 - exp(-rate)


def ran_binomial(rng, p: float, n: int):
    """Return a random number drawn from the binomial distribution
       [p,n] (see gsl_ran_binomial for documentation)
    """
    return rng.binomial(p, n)


def import_infection(network: Network, infections, play_infections,
                     params: Parameters, rng,
                     population: int):

    links = network.to_links
    wards = network.nodes

    frac = float(params.daily_imports) / float(population)

    total = 0

    for i in range(0, network.nnodes+1):
        to_seed = ran_binomial(rng, frac, int(wards.play_suscept[i]))

        if to_seed > 0:
            wards.play_suscept[i] -= to_seed
            play_infections[0][i] += to_seed
            total += to_seed

    for i in range(0, network.nlinks+1):
        # workers
        to_seed = ran_binomial(rng, frac, int(links.suscept[i]))

        if to_seed > 0:
            links.suscept[i] -= to_seed
            infections[0][i] += to_seed
            total += to_seed

    return total


def print_timings(timings):
    """Print out the timing information from timings"""
    print("\nTIMING")
    for timing in timings:
        # times in nanoseconds - convert to ms
        print(f"{timing[0]}: {timing[1]/1000000.0} ms")


def iterate(network: Network, infections, play_infections,
            params: Parameters, rng, timestep: int,
            population: int,
            is_dangerous=None,
            SELFISOLATE: bool = False,
            IMPORTS: bool = False):
    """Iterate the model forward one timestep (day) using the supplied
       network and parameters, advancing the supplied infections,
       and using the supplied random number generator (rng)
       to generate random numbers. This iterates for a normal
       (working) day (with predictable movements, mixed
       with random movements)

       If SELFISOLATE is True then you need to pass in
       is_dangerous, which should be an array("i", network.nnodes)
    """
    _start_total = time.time_ns()

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
    cdef double [::1] wards_day_foi = wards.day_foi
    cdef double [::1] wards_night_foi = wards.night_foi

    timings = []

    _start = time.time_ns()
    for i in range(1, network.nnodes+1):
        wards_day_foi[i] = 0.0
        wards_night_foi[i] = 0.0
    _end = time.time_ns()
    timings.append( ("SETUP", _end - _start) )

    if IMPORTS:
        _start = time.time_ns()
        imported = import_infection(network=network, infections=infections,
                                    play_infections=play_infections,
                                    params=params, rng=rng,
                                    population=population)

        print(f"Day: {timestep} Imports: expected {params.daily_imports} "
              f"actual {imported}")
        _end = time.time_ns()
        timings.append( ("IMPORTS", _end - _start) )


    cdef int N_INF_CLASSES = len(infections)
    cdef double scl_foi_uv = 0.0
    cdef double contrib_foi = 0.0
    cdef double beta = 0.0
    cdef play_at_home_scl = 0.0

    cdef int j = 0
    cdef int k = 0
    cdef int inf_ij = 0
    cdef double weight = 0.0
    cdef double [::1] links_weight = links.weight
    cdef int [::1] links_ifrom = links.ifrom
    cdef int [::1] links_ito = links.ito
    cdef int ifrom = 0
    cdef int ito = 0
    cdef int staying, moving, playmove
    cdef double [::1] links_distance = links.distance
    cdef double frac = 0.0
    cdef double cumulative_prob
    cdef double too_ill_to_move

    cdef int [::1] wards_begin_p = wards.begin_p
    cdef int [::1] wards_end_p = wards.end_p

    cdef double [::1] plinks_distance = plinks.distance
    cdef double [::1] plinks_weight = plinks.weight
    cdef int [::1] plinks_ifrom = plinks.ifrom
    cdef int [::1] plinks_ito = plinks.ito

    cdef double [::1] wards_denominator_d = wards.denominator_d
    cdef double [::1] wards_denominator_n = wards.denominator_n
    cdef double [::1] wards_denominator_p = wards.denominator_p
    cdef double [::1] wards_denominator_pd = wards.denominator_pd

    cdef double [::1] links_suscept = links.suscept
    cdef double [::1] wards_play_suscept = wards.play_suscept

    cdef int [::1] wards_label = wards.label

    cdef int [::1] infections_i, play_infections_i

    cdef int [::1] is_dangerous_array

    if SELFISOLATE:
        is_dangerous_array = is_dangerous

    for i in range(0, N_INF_CLASSES):
        contrib_foi = params.disease_params.contrib_foi[i]
        beta = params.disease_params.beta[i]
        scl_foi_uv = contrib_foi * beta * uvscale
        too_ill_to_move = params.disease_params.too_ill_to_move[i]

        # number of people staying gets bigger as
        # PlayAtHome increases
        play_at_home_scl = <float>(params.dyn_play_at_home *
                                   too_ill_to_move)

        infections_i = infections[i]
        play_infections_i = play_infections[i]

        if contrib_foi > 0:
            _start = time.time_ns()
            for j in range(1, network.nlinks+1):
                # deterministic movements (e.g. to work)
                inf_ij = infections_i[j]
                if inf_ij > 0:
                    weight = links_weight[j]
                    ifrom = links_ifrom[j]
                    ito = links_ito[j]

                    if inf_ij > <int>(weight):
                        print(f"inf[{i}][{j}] {inf_ij} > links[j].weight "
                              f"{weight}")

                    if links_distance[j] < cutoff:
                        if SELFISOLATE:
                            frac = <float>(is_dangerous_array[ito]) / <float>(
                                     wards_denominator_d[ito] +
                                     wards_denominator_p[ito])

                            if frac > thresh:
                                staying = infections_i[j]
                            else:
                                # number staying - this is G_ij
                                staying = ran_binomial(rng,
                                                       too_ill_to_move,
                                                       inf_ij)
                        else:
                            # number staying - this is G_ij
                            staying = ran_binomial(rng,
                                                   too_ill_to_move,
                                                   inf_ij)

                        if staying < 0:
                            print(f"staying < 0")

                        # number moving, this is I_ij - G_ij
                        moving = inf_ij - staying

                        wards_day_foi[ifrom] += staying * scl_foi_uv

                        # Daytime Force of
                        # Infection is proportional to
                        # number of people staying
                        # in the ward (too ill to work)
                        # this is the sum for all G_ij (including g_ii

                        wards_day_foi[ito] += moving * scl_foi_uv

                        # Daytime FOI for destination is incremented (including self links, I_ii)
                    else:
                        # outside cutoff
                        wards_day_foi[ifrom] += inf_ij * scl_foi_uv

                    wards_night_foi[ifrom] += inf_ij * scl_foi_uv

                    # Nighttime Force of Infection is
                    # prop. to the number of Infected individuals
                    # in the ward
                    # This I_ii in Lambda^N

                # end of if inf_ij (are there any new infections)
            # end of infectious class loop
            _end = time.time_ns()
            timings.append( (f"work_{i}", _end - _start) )

            _start = time.time_ns()
            for j in range(1, network.nnodes+1):
                # playmatrix loop FOI loop (random/unpredictable movements)
                inf_ij = play_infections_i[j]
                if inf_ij > 0:
                    wards_night_foi[j] += inf_ij * scl_foi_uv

                    staying = ran_binomial(rng, play_at_home_scl, inf_ij)

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

                            playmove = ran_binomial(rng, prob_scaled, moving)

                            if SELFISOLATE:
                                frac = is_dangerous_array[ito] / <float>(
                                                wards_denominator_d[ito] +
                                                wards_denominator_p[ito])

                                if frac > thresh:
                                    staying += playmove
                                else:
                                    wards_day_foi[ito] += playmove * scl_foi_uv
                            else:
                                wards_day_foi[ito] += playmove * scl_foi_uv

                            moving -= playmove
                        # end of if within cutoff

                        k += 1
                    # end of while loop

                    wards_day_foi[j] += (moving + staying) * scl_foi_uv
                # end of if inf_ij (there are new infections)

            # end of loop over all nodes
            _end = time.time_ns()
            timings.append( (f"play_{i}", _end - _start) )
        # end of params.disease_params.contrib_foi[i] > 0:
    # end of loop over all disease classes

    cdef int [::1] infections_i_plus_one, play_infections_i_plus_one
    cdef double disease_progress = 0.0

    _start_recovery = time.time_ns()
    for i in range(N_INF_CLASSES-2, -1, -1):  # loop down to 0
        # recovery, move through classes backwards
        infections_i = infections[i]
        infections_i_plus_one = infections[i+1]
        play_infections_i = play_infections[i]
        play_infections_i_plus_one = play_infections[i+1]
        disease_progress = params.disease_params.progress[i]

        for j in range(1, network.nlinks+1):
            inf_ij = infections_i[j]

            if inf_ij > 0:
                l = ran_binomial(rng, disease_progress, inf_ij)

                if l > 0:
                    infections_i_plus_one[j] += l
                    infections_i[j] -= l

            elif inf_ij != 0:
                print(f"inf_ij problem {i} {j} {inf_ij}")

        for j in range(1, network.nnodes+1):
            inf_ij = play_infections_i[j]

            if inf_ij > 0:
                l = ran_binomial(rng, disease_progress, inf_ij)

                if l > 0:
                    play_infections_i_plus_one[j] += l
                    play_infections_i[j] -= l

            elif inf_ij != 0:
                print(f"play_inf_ij problem {i} {j} {inf_ij}")
    # end of recovery loop
    _end_recovery = time.time_ns()
    timings.append(("recovery", _end_recovery-_start_recovery))

    cdef double length_day = params.length_day
    cdef double rate, inf_prob

    # i is set to 0 now as we are only dealing now with new infections
    i = 0
    infections_i = infections[i]
    play_infections_i = play_infections[i]

    _start_fixed = time.time_ns()
    for j in range(1, network.nlinks+1):
        # actual new infections for fixed movements
        inf_prob = 0

        distance = links_distance[j]

        if distance < cutoff:
            # distance is below cutoff (reasonable distance)
            # infect in work ward
            ifrom = links_ifrom[j]
            ito = links_ito[j]

            if wards_day_foi[ito] > 0:
                # daytime infection of link j
                if SELFISOLATE:
                    frac = is_dangerous_array[ito] / <float>(
                                            wards_denominator_d[ito] +
                                            wards_denominator_p[ito])

                    if frac > thresh:
                        inf_prob = 0.0
                    else:
                        rate = <float>(length_day *
                                       wards_day_foi[ito]) /   \
                               <float>(wards_denominator_d[ito] +
                                       wards_denominator_pd[ito])

                        inf_prob = rate_to_prob(rate)
                else:
                    rate = <float>(length_day *
                                   wards_day_foi[ito]) /   \
                           <float>(wards_denominator_d[ito] +
                                   wards_denominator_pd[ito])

                    inf_prob = rate_to_prob(rate)

            # end of if wards.day_foi[ito] > 0
        # end of if distance < cutoff
        elif wards_day_foi[ifrom] > 0:
            # if distance is too large then infect in home ward with day FOI
            rate = <float>(length_day * wards_day_foi[ifrom]) /  \
                   <float>(wards_denominator_d[ifrom] +
                           wards_denominator_pd[ifrom])

            inf_prob = rate_to_prob(rate)

        if inf_prob > 0.0:
            # daytime infection of workers
            l = ran_binomial(rng, inf_prob, <int>(links_suscept[j]))

            if l > 0:
                # actual infection
                #print(f"InfProb {inf_prob}, susc {links.suscept[j]}, l {l}")
                infections_i[j] += l
                links_suscept[j] -= l

        if wards_night_foi[ifrom] > 0:
            # nighttime infection of workers
            rate = (1.0 - length_day) * (wards_night_foi[ifrom]) /  \
                   <float>(wards_denominator_n[ifrom] +
                           wards_denominator_p[ifrom])

            inf_prob = rate_to_prob(rate)

            l = ran_binomial(rng, inf_prob, <int>(links_suscept[j]))

            if l > links_suscept[j]:
                print(f"l > links[{j}].suscept {links_suscept[j]} nighttime")

            if l > 0:
                # actual infection
                # print(f"NIGHT InfProb {inf_prob}, susc {links.suscept[j]}, {l}")
                infections_i[j] += l
                links_suscept[j] -= l
        # end of wards.night_foi[ifrom] > 0  (nighttime infections)
    # end of loop over all network links
    _end_fixed = time.time_ns()
    timings.append(("fixed", _end_fixed-_start_fixed))

    cdef int suscept = 0
    cdef double dyn_play_at_home = params.dyn_play_at_home

    _start_play = time.time_ns()
    for j in range(1, network.nnodes+1):
        # playmatrix loop
        inf_prob = 0.0

        suscept = <int>wards_play_suscept[j]

        if suscept < 0:
            print(f"play_suscept is less than 0 ({suscept}) "
                  f"problem {j}, {wards_label[j]}")

        staying = ran_binomial(rng, dyn_play_at_home, suscept)

        moving = suscept - staying

        cumulative_prob = 0.0

        # daytime infection of play matrix moves
        for k in range(wards_begin_p[j], wards_end_p[j]):
            if plinks_distance[k] < cutoff:
                ito = plinks_ito[k]

                if wards_day_foi[ito] > 0.0:
                    weight = plinks_weight[k]
                    prob_scaled = <float>weight / (1.0-cumulative_prob)
                    cumulative_prob += weight

                    if SELFISOLATE:
                        frac = <float>(is_dangerous_array[ito]) / <float>(
                                        wards_denominator_p[ito] +
                                        wards_denominator_d[ito])

                        if frac > thresh:
                            inf_prob = 0.0
                            play_move = 0
                        else:
                            play_move = ran_binomial(rng, prob_scaled, moving)
                            frac = <float>(length_day *
                                           wards_day_foi[ito]) / <float>(
                                             wards_denominator_pd[ito] +
                                             wards_denominator_d[ito])

                            inf_prob = rate_to_prob(frac)
                    else:
                        play_move = ran_binomial(rng, prob_scaled, moving)
                        frac = <float>(length_day *
                                        wards_day_foi[ito]) / <float>(
                                            wards_denominator_pd[ito] +
                                            wards_denominator_d[ito])

                        inf_prob = rate_to_prob(frac)

                    l = ran_binomial(rng, inf_prob, play_move)

                    moving -= play_move

                    if l > 0:
                        # infection
                        #print(f"PLAY: InfProb {inf_prob}, susc {playmove}, "
                        #      f"l {l}")
                        #print(f"daytime play_infections[{i}][{j}] += {l}")
                        play_infections_i[j] += l
                        wards_play_suscept[j] -= l

                # end of DayFOI if statement
            # end of Dynamics Distance if statement
        # end of loop over links of wards[j]

        if (staying + moving) > 0:
            # infect people staying at home
            frac = <float>(length_day * wards_day_foi[j]) / <float>(
                           wards_denominator_pd[j] +
                           wards_denominator_d[j])

            inf_prob = rate_to_prob(frac)

            l = ran_binomial(rng, inf_prob, staying+moving)

            if l > 0:
                # another infections, this time from home
                #print(f"staying home play_infections[{i}][{j}] += {l}")
                play_infections_i[j] += l
                wards_play_suscept[j] -= l

        # nighttime infections of play movements
        night_foi = wards_night_foi[j]
        if night_foi > 0.0:
            frac = <float>((1.0 - length_day) * night_foi) / <float>(
                            wards_denominator_n[j] + wards_denominator_p[j])

            inf_prob = rate_to_prob(frac)

            l = ran_binomial(rng, inf_prob, <int>(wards_play_suscept[j]))

            if l > 0:
                # another infection
                #print(f"nighttime play_infections[{i}][{j}] += {l}")
                play_infections_i[j] += l
                wards_play_suscept[j] -= l
    # end of loop over wards (nodes)
    _end_play = time.time_ns()
    timings.append(("play", _end_play-_start_play))

    _end_total = time.time_ns()
    timings.append(("TOTAL", _end_total - _start_total))
    print_timings(timings)


def iterate_weekend(network: Network, infections, play_infections,
                    params: Parameters, rng, timestep: int,
                    population: int,
                    is_dangerous = None, SELFISOLATE: bool = False,
                   ):
    """Iterate the model forward one timestep (day) using the supplied
       network and parameters, advancing the supplied infections,
       and using the supplied random number generator (rng)
       to generate random numbers. This iterates for a non-working
       (weekend) day (with only random movements)

       If SELFISOLATE is True then you need to pass in
       is_dangerous, which should be an array("i", network.nnodes)
    """
    raise AssertionError("Will write iterate_weekend later...")


def how_many_vaccinated(vac):
    raise AssertionError("how_many_vaccinated has not yet been written")


def vaccinate_same_id(network: Network, risk_ra, sort_ra,
                      infections, play_infections,
                      vac, params):
    raise AssertionError("vaccinate_same_id has not yet been written")


def infect_additional_seeds(network: Network, params: Parameters,
                            infections, play_infections,
                            additional_seeds, timestep: int):
    """Cause more infection from additional infection seeds"""
    wards = network.nodes

    for seed in additional_seeds:
        if seed[0] == timestep:
            if wards.play_suscept[seed[1]] < seed[2]:
                print(f"Not enough susceptibles in ward for seeding")
            else:
                wards.play_suscept[seed[1]] -= seed[2]
                #print(f"seeding play_infections[0][{seed[1]}] += {seed[2]}")
                play_infections[0][seed[1]] += seed[2]


def load_additional_seeds(filename: str):
    """Load additional seeds from the passed filename. This returns
       the added seeds
    """
    print(f"Loading additional seeds from {filename}...")

    with open(filename, "r") as FILE:
        line = FILE.readline()
        seeds = []

        while line:
            words = line.split()

            # yes, this is really the order of the seeds - "t num loc"
            # is in the file as "t loc num"
            seeds.append( (int(words[0]), int(words[2]), int(words[1])) )
            print(seeds[-1])
            line = FILE.readline()

    return seeds


def extract_data_for_graphics(network: Network, infections,
                              play_infections, workspace: Workspace,
                              FILE):
    """Extract data that will be used for graphical analysis"""
    links = network.to_links

    cdef int N_INF_CLASSES = len(infections)

    assert workspace.N_INF_CLASSES == N_INF_CLASSES
    assert workspace.MAXSIZE >= network.nnodes+1

    workspace.zero_all()

    cdef int i, j, inf_ij, pinf_ij, ifrom
    cdef int total = 0

    cdef int [::1] infections_i, play_infections_i
    cdef int [::1] inf_tot = workspace.inf_tot
    cdef int [::1] total_inf_ward = workspace.total_inf_ward
    cdef int [::1] total_infections = workspace.total_infections
    cdef int [::1] prevalence = workspace.prevalence
    cdef int [::1] links_ifrom = links.ifrom

    for i in range(0, N_INF_CLASSES):
        infections_i = infections[i]
        play_infections_i = play_infections[i]

        for j in range(1, network.nnodes+1):
            total_inf_ward[j] = 0

        for j in range(1, network.nlinks+1):
            inf_ij = infections_i[j]
            if inf_ij != 0:
                inf_tot[i] += inf_ij
                ifrom = links_ifrom[j]
                total_inf_ward[ifrom] += inf_ij
                if i < N_INF_CLASSES-1:
                    total_infections[ifrom] += inf_ij
                    total += inf_ij

        for j in range(1, network.nnodes+1):
            pinf_ij = play_infections_i[j]
            total_inf_ward[j] += pinf_ij
            if (pinf_ij != 0) and (i < N_INF_CLASSES-1):
                total_infections[j] += pinf_ij
                total += pinf_ij

            if i == 2:
                FILE.write("%d " % total_infections[j])   # incidence

                if i == N_INF_CLASSES - 1:
                    FILE.write("%d ", total_infections[j])  # prevalence

                if i == N_INF_CLASSES - 1:
                    prevalence[j] = total_infections[j]

    FILE.write("\n")

    return total

def extract_data(network: Network, infections, play_infections,
                 timestep: int, files, workspace: Workspace,
                 population: Population, is_dangerous=None,
                 SELFISOLATE: bool = False):
    """Extract data for timestep 'timestep' from the network and
       infections and write this to the output files in 'files'
       (these must have been opened by 'open_files'). You need
       to pass in a Workspace that has been set up for the
       passed network and parameters

       If SELFISOLATE is True then you need to pass in
       is_dangerous, which should be an array("i", network.nnodes)
    """
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

    return total + latent


def seed_infection_at_node(network: Network, params: Parameters,
                           seed: int, infections, play_infections):
    """Seed the infection at a specific ward"""
    wards = network.nodes
    links = network.to_links

    j = 0

    while (links.ito[j] != seed) or (links.ifrom[j] != seed):
        j += 1

    #print(f"j {j} link from {links.ifrom[j]} to {links.ito[j]}")

    if links.suscept[j] < params.initial_inf:
        wards.play_suscept[seed] -= params.initial_inf
        #print(f"seed at play_infections[0][{seed}] += {params.initial_inf}")
        play_infections[0][seed] += params.initial_inf

    infections[0][j] = params.initial_inf
    links.suscept[j] -= params.initial_inf


def seed_all_wards(network: Network, play_infections,
                   expected: int, population: int):
    """Seed the wards with an initial set of infections, assuming
       an 'expected' number of infected people out of a population
       of 'population'
    """
    wards = network.nodes

    frac = float(expected) / float(population)

    for i in range(0, network.nnodes+1):  # 1-index but also count at 0?
        temp = wards.denominator_n[i] + wards.denominator_p[i]
        to_seed = int(frac*temp + 0.5)
        wards.play_suscept[i] -= to_seed
        play_infections[0][i] += to_seed


def clear_all_infections(infections, play_infections):
    """Clears all infections (held in the list of array(int) in infections,
       and array(int) in play_infections) associated with the
       passed network
    """
    assert len(infections) == len(play_infections)

    for i in range(0, len(infections)):
        a = infections[i]
        for j in range(0, len(a)):
            a[j] = 0

        a = play_infections[i]
        for j in range(0, len(a)):
            a[j] = 0


def open_files(output_dir: str):
    """Opens all of the output files written to during the simulation,
       opening them all in the directory 'output_dir'

       This returns the file handles of all open files
    """
    files = []

    files.append( open(os.path.join(output_dir, "WorkInfections.dat"), "w") )
    files.append( open(os.path.join(output_dir, "NumberWardsInfected.dat"),
                       "w") )
    files.append( open(os.path.join(output_dir, "MeanXY.dat"), "w") )
    files.append( open(os.path.join(output_dir, "PlayInfections.dat"), "w") )
    files.append( open(os.path.join(output_dir, "TotalInfections.dat"), "w") )
    files.append( open(os.path.join(output_dir, "VarXY.dat"), "w") )
    files.append( open(os.path.join(output_dir, "Dispersal.dat"), "w") )

    return files


def run_model(network: Network,
              infections, play_infections,
              rng, s: int,
              output_dir: str=".",
              population: int=57104043,
              nsteps: int=None,
              MAXSIZE: int=10050,
              VACCINATE: bool = False,
              IMPORTS: bool = False,
              EXTRASEEDS: bool = True,
              WEEKENDS: bool = False):
    """Actually run the model... Real work happens here. The model
       will run until completion or until 'nsteps' have been
       completed (whichever happens first)
    """

    params = network.params

    if params is None:
        return Population(initial=population)

    to_seed = network.to_seed

    # create a workspace in which to run the model
    workspace = Workspace(network=network, params=params)

    # create a population object to monitor the outbreak
    population = Population(initial=population)

    int_t = "i"    # signed int64
    float_t = "d"  # double (float64)

    size = MAXSIZE   # suspect this will be the number of nodes

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    if not os.path.isdir(output_dir):
        raise AssertionError(f"The specified output directory ({output_dir}) "
                             f"does not appear to be a valid directory")

    EXPORT = open(os.path.join(output_dir, "ForMattData.dat"), "w")

    if VACCINATE:
        trigger = 0
        null_int = size * [0]
        null_float = size * [0.0]

        vac = array(int_t, null_int)
        #wards_ra = array(int_t, null_int)
        risk_ra = array(float_t, null_float)
        sort_ra = array(int_t, null_int)
        VACF = open(os.path.join(output_dir, "Vaccinated.dat", "w"))

    files = open_files(output_dir)

    clear_all_infections(infections=infections,
                         play_infections=play_infections)

    if s < 0:
        print(f"Negative value of s? {s}")
        to_seed = 0
    else:
        to_seed = to_seed[s]

    print(f"node_seed {to_seed}")

    if not IMPORTS:
        if s < 0:
            seed_all_wards(network=network,
                           play_infections=play_infections,
                           expected=params.daily_imports,
                           population=population.initial)
        else:
            seed_infection_at_node(network=network, params=params,
                                   seed=to_seed,
                                   infections=infections,
                                   play_infections=play_infections)

    cdef int timestep = 0  # start timestep of the model
                           # (day since infection starts)

    cdef int infecteds = extract_data(network=network, infections=infections,
                                      play_infections=play_infections,
                                      timestep=timestep, files=files,
                                      workspace=workspace,
                                      population=population)

    cdef int day = 0

    if WEEKENDS:
        day = 1  # day number of the week, 1-5 = weekday, 6-7 = weekend

    if EXTRASEEDS:
        additional_seeds = load_additional_seeds(
                                params.input_files.additional_seeding)

    while (infecteds != 0) or (timestep < 5):
        _start_total = time.time_ns()
        timings = []
        if EXTRASEEDS:
            _start = time.time_ns()
            infect_additional_seeds(network=network, params=params,
                                    infections=infections,
                                    play_infections=play_infections,
                                    additional_seeds=additional_seeds,
                                    timestep=timestep)
            _end = time.time_ns()
            timings.append(("additional seeds", _end - _start))

        if WEEKENDS:
            if day > 5:
                _start = time.time_ns()
                iterate_weekend(network=network, infections=infections,
                                play_infections=play_infections,
                                params=params, rng=rng, timestep=timestep,
                                population=population.initial)
                _end = time.time_ns()
                timings.append(("iterate weekend", _end-_start))
                print("weekend")
            else:
                _start = time.time_ns()
                iterate(network=network, infections=infections,
                        play_infections=play_infections,
                        params=params, rng=rng, timestep=timestep,
                        population=population.initial)
                _end = time.time_ns()
                timings.append(("iterate", _end-_start))
                print("normal day")

            if day == 7:
                day = 0

            day += 1
        else:
            _start = time.time_ns()
            iterate(network=network, infections=infections,
                    play_infections=play_infections,
                    params=params, rng=rng, timestep=timestep,
                    population=population.initial)
            _end = time.time_ns()
            timings.append(("iterate", _end-_start))

        print(f"\n {timestep} {infecteds}")

        _start = time.time_ns()
        infecteds = extract_data(network=network, infections=infections,
                                 play_infections=play_infections,
                                 timestep=timestep, files=files,
                                 workspace=workspace,
                                 population=population)
        _end = time.time_ns()
        timings.append(("extract_data", _end-_start))

        _start = time.time_ns()
        extract_data_for_graphics(network=network, infections=infections,
                                  play_infections=play_infections,
                                  workspace=workspace, FILE=EXPORT)
        _end = time.time_ns()
        timings.append(("extract_for_graphcs", _end-_start))

        timestep += 1

        if nsteps is not None:
            if timestep > nsteps:
                print(f"Exiting model run early at nsteps = {nsteps}")
                break

        if VACCINATE:
            _start = time.time_ns()
            #vaccinate_wards(network=network, wards_ra=wards_ra,
            #                infections=infections,
            #                play_infections=play_infections,
            #                vac=vac, params=params)

            if infecteds > params.global_detection_thresh:
                trigger = 1

            if trigger == 1:
                #vaccinate_county(network=network, risk_ra=risk_ra,
                #                 sort_ra=sort_ra,
                #                 infections=infections,
                #                 play_infections=play_infections,
                #                 vac=vac, params=params)

                vaccinate_same_id(network=network, risk_ra=risk_ra,
                                  sort_ra=sort_ra,
                                  infections=infections,
                                  play_infections=play_infections,
                                  vac=vac, params=params)

                if params.disease_params.contrib_foi[0] == 1.0:
                    N_INF_CLASSES = len(infections)
                    for j in range(0, N_INF_CLASSES-1):
                        params.disease_params.contrib_foi[j] = 0.2

            VACF.write("%d %d\n" % (timestep, how_many_vaccinated(vac)))
            _end = time.time_ns()
            timings.append(("vaccinate", _end-_start))

        # end of "IF VACCINATE"

        _end_total = time.time_ns()
        timings.append(("TOTAL", _end_total - _start_total))
        print("TOTAL ITERATION")
        print_timings(timings)
    # end of while loop

    EXPORT.close()

    if VACCINATE:
        VACF.close()

    for FILE in files:
        FILE.close()

    print(f"Infection died ... Ending at time {timestep}")

    return population
