
from ._network import Network
from ._parameters import Parameters

__all__ = ["infect_additional_seeds", "load_additional_seeds",
           "seed_infection_at_node", "seed_all_wards"]


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
