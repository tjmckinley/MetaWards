
__all__ = ["iterate_weekend"]


def iterate_weekend(stage, **kwargs):
    """This returns the default list of 'advance_XXX' functions that
       are called in sequence for each weekend iteration of the model run.

       Parameters
       ----------
       stage: str
         The stage at which this iterator is operating
         (this has to change both the "foi" and "infect"
          stages)

       Returns
       -------
       funcs: List[function]
         The list of functions that ```iterate``` will call in sequence
    """
    if stage == "foi":
        from ._advance_foi_work_to_play import advance_foi_work_to_play
        from ._advance_recovery import advance_recovery
        return [advance_foi_work_to_play, advance_recovery]

    elif stage == "infect":
        from ._advance_infprob import advance_infprob
        from ._advance_work_to_play import advance_work_to_play
        from ._advance_play import advance_play

        return [advance_infprob, advance_work_to_play, advance_play]

    else:
        from ._iterate_default import iterate_default
        return iterate_default(stage=stage, **kwargs)
