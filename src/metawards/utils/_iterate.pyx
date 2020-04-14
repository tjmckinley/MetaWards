#!/bin/env/python3
#cython: linetrace=False
# MUST ALWAYS DISABLE AS WAY TOO SLOW FOR ITERATE

from .._network import Network
from .._parameters import Parameters
from ._profiler import Profiler, NullProfiler
from ._import_infection import import_infection


from ..iterators._advance_play import advance_play_omp
from ..iterators._advance_fixed import advance_fixed_omp
from ..iterators._advance_infprob import advance_infprob_omp
from ..iterators._advance_recovery import advance_recovery_omp
from ..iterators._advance_foi import advance_foi_omp

__all__ = ["iterate"]


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

    links = network.to_links
    wards = network.nodes
    plinks = network.play

    if IMPORTS:
        p = p.start("imports")
        imported = import_infection(network=network, infections=infections,
                                    play_infections=play_infections,
                                    params=params, rng=rngs[0],
                                    population=population)

        print(f"Day: {timestep} Imports: expected {params.daily_imports} "
              f"actual {imported}")
        p = p.stop()

    advance_foi_omp(network=network, infections=infections,
                    play_infections=play_infections,
                    rngs=rngs, nthreads=nthreads,
                    day=timestep, profiler=p)

    advance_recovery_omp(network=network, infections=infections,
                         play_infections=play_infections,
                         rngs=rngs, nthreads=nthreads,
                         day=timestep, profiler=p)

    advance_infprob_omp(network=network, infections=infections,
                        play_infections=play_infections,
                        rngs=rngs, nthreads=nthreads,
                        day=timestep, profiler=p)

    advance_fixed_omp(network=network, infections=infections,
                      play_infections=play_infections,
                      rngs=rngs, nthreads=nthreads,
                      day=timestep, profiler=p)

    advance_play_omp(network=network, infections=infections,
                     play_infections=play_infections,
                     rngs=rngs, nthreads=nthreads,
                     day=timestep, profiler=p)

    p.stop()
