
from typing import Union as _Union
from typing import Callable as _Callable

from .._network import Network
from .._networks import Networks
from .._population import Population
from .._infections import Infections
from ._profiler import Profiler

__all__ = ["run_level"]


def run_level(stage: str,
              network: _Union[Network, Networks],
              population: Population,
              infections: Infections,
              iterator: _Callable[..., None],
              extractor: _Callable[..., None],
              mixer: _Callable[..., None],
              mover: _Callable[..., None],
              rngs, nthreads, profiler: Profiler) -> None:
    """Run the model for the specified stage of the day. Valid stages
       are;

       * "initialise": model initialisation. Called once before the
                       whole model run is performed
       * "setup": day setup. Called once at the start of the day.
                  Should be used to import new seeds, move populations
                  between demographics, move infected individuals
                  through disease stages etc. There is no calculation
                  performed at this stage.
       * "foi": foi calculation. Called to recalculate the force of infection
                (foi) for each ward in the network (and subnetworks).
                This is calculated based on the populations in each state
                in each ward in each demographic
       * "infect": Called to advance the outbreak by calculating
                   the number of new infections
       * "analyse": Called at the end of the day to merge and analyse
                    the data and extrac the results
       * "finalise": Called at the end of the model run to finalise
                     any outputs or produce overall summary files

       Parameters
       ----------
       network: Network or Networks
         The network(s) to be modelled
       population: Population
         The population experiencing the outbreak
       infections: Infections
         Space to record the infections through the day
       iterator: function
         Iterator used to obtain the function used to advance
         the outbreak
       extractor: function
         Extractor used to analyse the data and output results
       mixer: function
         Mixer used to mix and merge data between different demographics
       mover: function
         Mover used to move populations between demographics
       rngs: list[random number generate pointers]
         Pointers to the random number generators to use for each thread
       nthreads: int
         The number of threads to use to run the model
       profiler: Profiler
         The profiler used to profile the calculation

       Returns
       -------
       None
    """

    stages = ["initialise", "setup", "foi", "infect", "analyse" , "finalise"]

    if stage not in stages:
        raise ValueError(
                f"Cannot recognise the stage {stage}. Available stages "
                f"are {stages}")

    kwargs = {"stage": stage,
              "network": network,
              "population": population,
              "infections": infections,
              "rngs": rngs,
              "nthreads": nthreads,
              "profiler": profiler}

    if iterator is not None:
        iterator(**kwargs)

    if mover is not None:
        mover(**kwargs)

    if mixer is not None:
        mixer(**kwargs)

    if extractor is not None:
        extractor(**kwargs)
