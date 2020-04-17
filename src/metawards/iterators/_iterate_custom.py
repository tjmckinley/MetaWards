
__all__ = ["iterate_custom", "build_custom_iterator"]

from ._iterate_core import iterate_core
from ._iterate_default import iterator_needs_setup


def build_custom_iterator(custom_function):
    """Build and return a custom iterator from the passed
       function. This will wrap 'iterate_custom' around
       the function to double-check that the custom
       function is doing everything correctly
    """
    return lambda **kwargs: iterate_custom(custom_function=custom_function,
                                           **kwargs)


def iterate_custom(custom_function,
                   setup=False, **kwargs):
    """This returns the default list of 'advance_XXX' functions that
       are called in sequence for each iteration of the model run.
       This iterator provides a custom iterator that uses
       'custom_function' passed from the user. This iterator makes
       sure that 'setup' is called correctly and that the functions
       needed by 'iterate_core' are called first.

       Parameters
       ----------
       custom_function
         A custom user-supplied function that returns the
         functions that the user would like to be called for
         each step
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

    kwargs["setup"] = setup

    if setup:
        # Return the functions needed to initialise this iterator
        core_funcs = iterate_core(**kwargs)

        if iterator_needs_setup(custom_function):
            custom_funcs = custom_function(**kwargs)
        else:
            custom_funcs = None

    else:
        core_funcs = iterate_core(**kwargs)
        custom_funcs = custom_function(**kwargs)

    # make sure that the core functions are called, and that
    # their call is before the custom function (unless the user
    # has moved them, which we hope was for a good reason!)
    if core_funcs is None or len(core_funcs) == 0:
        if custom_funcs is None:
            return []
        else:
            return custom_funcs

    elif custom_funcs is None or len(custom_funcs) == 0:
        return core_funcs

    else:
        for i in range(len(core_funcs)-1, -1, -1):
            # move backwards so that the first custom function
            # is prepended last
            if core_funcs[i] not in custom_funcs:
                custom_funcs.insert(0, core_funcs[i])

        print(custom_funcs)

        return custom_funcs
