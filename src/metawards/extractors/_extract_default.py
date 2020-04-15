
__all__ = ["extract_default"]


def extract_default(nthreads: int = 1, setup=False, **kwargs):
    """This returns the default list of 'output_XXX' functions that
       are called in sequence for each iteration of the model run.
       These functions are used to output data to files for
       future processing

       Parameters
       ----------
       nthreads: int
         The number of threads that will be used for each function.
         If this is 1, then the serial versions of the functions will
         be returned, else the parallel (OpenMP) versions will be
         returned
       setup: bool
         Whether or not to return the functions used to setup the
         space and output files for the output_XXX functions returned by
         this iterator. This is called once at the start of a run
         to return the functions that must be called to setup the
         model

       Returns
       -------
       funcs: List[function]
         The list of functions that ```extract_data``` will call in sequence
    """

    if setup:
        from ._output_default import setup_output_default
        funcs = [setup_output_default]

    elif nthreads is None or nthreads == 1:
        from ._output_default import output_default
        funcs = [output_default]

    else:
        from ._output_default import output_default_omp
        funcs = [output_default_omp]

    return funcs
