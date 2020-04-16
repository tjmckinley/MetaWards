
from .._network import Network
from ._profiler import Profiler, NullProfiler
from .._population import Population
from .._outputfiles import OutputFiles
from ._workspace import Workspace

__all__ = ["extract_data"]


def extract_data(network: Network, population: Population,
                 workspace: Workspace, output_dir: OutputFiles,
                 infections, play_infections, rngs, get_output_functions,
                 nthreads: int, profiler: Profiler = None):
    """Extract data from the network and write this to the specified
       output directory. Like :meth:`~metawards.utils.iterate` this
       uses a dynamic set of functions that can be utilised to
       customise what is output dynamically throughout the model
       run.

       Parameters
       ----------
       network: Network
         The network over which the model is being run
       population: Population
         The population experiencing the model outbreak
       workspace: Workspace
         A scratch-space that can be used to accumulate data while
         it is being extracted
       output_dir: OutputFiles
         The output directory to which to write all files
       infections
         Space to hold all of the 'work' infections
       play_infections
         Space to hold all of the 'play' infections
       rngs
         Thread-safe random number generators (one per thread)
       get_output_functions
         A function that should return the list of output functions
         that are called in sequence to write the output data.
         See :meth:`~metawards.extractors.extract_default` for an
         example of a suitable function
       nthreads: int
         The number of threads over which to parallelise extracting
         the output
       profiler: Profiler
         The profiler used to profile extracting the output
    """
    if profiler is None:
        profiler = NullProfiler()

    p = profiler.start("extract_data")

    output_functions = get_output_functions(population=population,
                                            nthreads=nthreads)

    for output_function in output_functions:
        output_function(network=network,
                        population=population,
                        workspace=workspace,
                        output_dir=output_dir,
                        infections=infections,
                        play_infections=play_infections,
                        rngs=rngs, nthreads=nthreads,
                        profiler=p)

    p.stop()