
__all__ = ["mix_core"]


def mix_core(nthreads: int = 1, setup=False, **kwargs):
    """This returns the default list of 'merge_XXX' functions that
       are called in sequence to merge data from multiple demographics
       together

       Parameters
       ----------
       nthreads: int
         The number of threads that will be used for each function.
         If this is 1, then the serial versions of the functions will
         be returned, else the parallel (OpenMP) versions will be
         returned
       setup: bool
         Whether or not to return the functions used to setup the
         space and output files for the merge_XXX functions returned by
         this mixer. This is called once at the start of a run
         to return the functions that must be called to setup the
         mixers.

       Returns
       -------
       funcs: List[function]
         The list of functions that ```merge``` will call in sequence
    """

    funcs = []

    if setup:
        return []

    else:
        from ._merge_core import merge_core
        funcs.append(merge_core)

    return funcs
