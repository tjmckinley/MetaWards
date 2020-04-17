
__all__ = ["iterate_working_week"]

from ._iterate_core import iterate_core
from ._iterate_weekday import iterate_weekday
from ._iterate_weekend import iterate_weekend
from ._iterate_default import iterator_needs_setup

from .._population import Population


def iterate_working_week(population: Population,
                         setup=False, **kwargs):
    """This returns the default list of 'advance_XXX' functions that
       are called in sequence for each iteration of the model run.
       This iterator understands the concept of a traditional working week,
       namely Monday-Friday is a work day, while Saturday and
       Sunday are weekends

       Parameters
       ----------
       population: Population
         The population experiencing the outbreak. This includes
         information about the day and date of the outbreak
       setup: bool
         Whether or not to return the functions used to setup the
         space and input for the advance_XXX functions returned by
         this iterator. This is called once at the start of a run
         to return the functions that must be called to setup the
         model

       Returns
       -------
       funcs: List[function]
         The list of functions that ```iterate``` will call in sequence
    """

    kwargs["population"] = population
    kwargs["setup"] = setup

    if setup:
        # Return the functions needed to initialise this iterator
        funcs = iterate_core(**kwargs)

        # Does 'iterate_weekday' need to be setup?
        if iterator_needs_setup(iterate_weekday):
            funcs += iterate_weekday(**kwargs)

        # Does 'iterate_weekend' need to be setup?
        if iterator_needs_setup(iterate_weekend):
            funcs += iterate_weekend(**kwargs)

    else:
        # is this a weekday or a weekend?
        if population.date is None:
            # have to guess from the day - assume day zero was a Monday
            day = population.day % 7
            # 0-4 is a weekday, 5 and 6 are weekend
            is_weekend = (day >= 5)
        else:
            day = population.date.weekday()
            # 0-4 is a weekday, 5 and 6 are weekend
            is_weekend = (day >= 5)

        if is_weekend:
            funcs = iterate_core(**kwargs) + iterate_weekend(**kwargs)
        else:
            funcs = iterate_core(**kwargs) + iterate_weekday(**kwargs)

    return funcs
