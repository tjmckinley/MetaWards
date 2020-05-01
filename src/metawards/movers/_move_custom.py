
__all__ = ["move_custom",
           "mover_needs_setup",
           "build_custom_mover"]


def mover_needs_setup(mover):
    """Return whether or not the passed mover function has
       a "setup" argument, and thus needs to be setup before
       it can be used
    """
    import inspect
    return "setup" in inspect.signature(mover).parameters


def build_custom_mover(custom_function, parent_name="__main__"):
    """Build and return a custom mover from the passed
       function. This will wrap 'extract_mover' around
       the function to double-check that the custom
       function is doing everything correctly

       Parameters
       ----------
       custom_function
         This can either be a function, which will be wrapped and
         returned, or it can be a string. If it is a string then
         we will attempt to locate or import the function associated
         with that string. The search order is;

         1. Is this 'metawards.movers.custom_function'?
         2. Is this 'custom_function' that is already imported'?
         3. Is this a file name in the current path, if yes then
            find the function in that file (either the first function
            called 'extractXXX' or the specified function if
            custom_function is in the form module::function)

        parent_name: str
          This should be the __name__ of the calling function, e.g.
          call this function as build_custom_mover(func, __name__)

        Returns
        -------
        extractor
          The wrapped mover that is suitable for using in the move
          function.
    """
    if isinstance(custom_function, str):
        print(f"Importing a custom mover from {custom_function}")

        # we need to find the function
        import metawards.movers

        # is it metawards.movers.{custom_function}
        try:
            func = getattr(metawards.movers, custom_function)
            return build_custom_mover(func)
        except Exception:
            pass

        # do we have the function in the current namespace?
        import sys
        try:
            func = getattr(sys.modules[__name__], custom_function)
            return build_custom_mover(func)
        except Exception:
            pass

        # how about the __name__ namespace of the caller
        try:
            func = getattr(sys.modules[parent_name], custom_function)
            return build_custom_mover(func)
        except Exception:
            pass

        # how about the __main__ namespace (e.g. if this was loaded
        # in a script)
        try:
            func = getattr(sys.modules["__main__"], custom_function)
            return build_custom_mover(func)
        except Exception:
            pass

        # can we import this function as a file - need to check that
        # the user hasn't written this as module::function
        if custom_function.find("::") != -1:
            parts = custom_function.split("::")
            func_name = parts[-1]
            func_module = "::".join(parts[0:-1])
        else:
            func_name = None
            func_module = custom_function

        from ..utils._import_module import import_module

        module = import_module(func_module)

        if module is None:
            # we cannot find the extractor
            print(f"Cannot find the mover '{custom_function}'."
                  f"Please make sure this is spelled correctly and "
                  f"any python modules/files needed are in the "
                  f"PYTHONPATH or current directory")
            raise ImportError(f"Could not import the mover "
                              f"'{custom_function}'")

        if func_name is None:
            # find the first function that starts with 'move'
            import inspect
            for name, value in inspect.getmembers(module):
                if name.startswith("move"):
                    if hasattr(value, "__call__"):
                        # this is a function
                        return build_custom_mover(getattr(module, name))

            print(f"Could not find any function in the module "
                  f"{custom_function} that has a name that starts "
                  f"with 'move'. Please manually specify the "
                  f"name using the '{custom_function}::your_function syntax")

            raise ImportError(f"Could not import the mover "
                              f"{custom_function}")

        else:
            if hasattr(module, func_name):
                return build_custom_mover(getattr(module, func_name))

            print(f"Could not find the function {func_name} in the "
                  f"module {func_module}. Check that the spelling "
                  f"is correct and that the right version of the module "
                  f"is being loaded.")
            raise ImportError(f"Could not import the mover "
                              f"{custom_function}")

    if not hasattr(custom_function, "__call__"):
        print(f"Cannot build a mover for {custom_function} "
              f"as it is missing a __call__ function, i.e. it is "
              f"not a function.")
        raise ValueError(f"You can only build custom movers for "
                         f"actual functions... {custom_function}")

    print(f"Building a custom mover for {custom_function}")

    return lambda **kwargs: move_custom(custom_function=custom_function,
                                        **kwargs)


def move_custom(custom_function, setup=False, **kwargs):
    """This returns the default list of 'go_XXX' functions that
       are called in sequence to move the population between
       different demographics.

       This mover provides a custom mover that uses
       'custom_function' passed from the user. This
       mover makes sure that 'custom_function' does everything
       it should

       Parameters
       ----------
       custom_function
         A custom user-supplied function that returns the
         functions that the user would like to be called for
         each step.
       setup: bool
         Whether or not to return the functions used to setup the
         space and input for the go_XXX functions returned by
         this mover. This is called once at the start of a run
         to return the functions that must be called to setup the
         movers. Note that most movers shouldn't need any setup.

       Returns
       -------
       funcs: List[function]
         The list of functions that ```extract``` will call in sequence
    """

    if setup:
        kwargs["setup"] = setup

        if mover_needs_setup(custom_function):
            custom_funcs = custom_function(**kwargs)
        else:
            custom_funcs = None

    else:
        custom_funcs = custom_function(**kwargs)

    return custom_funcs
