
__all__ = ["iterate_default"]


def iterate_default(nthreads: int = 1, **kwargs):
    """This returns the default list of 'advance_XXX' functions that
       are called in sequence for each iteration of the model run.

       Parameters
       ----------
       nthreads: int
         The number of threads that will be used for each function.
         If this is 1, then the serial versions of the functions will
         be returned, else the parallel (OpenMP) versions will be
         returned

       Returns
       -------
       funcs: List[function]
         The list of functions that ```iterate``` will call in sequence
    """

    if nthreads == 1:
        from ._advance_foi import advance_foi
        from ._advance_recovery import advance_recovery
        from ._advance_infprob import advance_infprob
        from ._advance_fixed import advance_fixed
        from ._advanced_play import advance_play

        funcs = [advance_foi,
                 advance_recovery,
                 advance_infprob,
                 advance_fixed,
                 advance_play]
    else:
        from ._advance_foi import advance_foi_omp
        from ._advance_recovery import advance_recovery_omp
        from ._advance_infprob import advance_infprob_omp
        from ._advance_fixed import advance_fixed_omp
        from ._advanced_play import advance_play_omp

        funcs = [advance_foi_omp,
                 advance_recovery_omp,
                 advance_infprob_omp,
                 advance_fixed_omp,
                 advance_play_omp]

    return funcs
