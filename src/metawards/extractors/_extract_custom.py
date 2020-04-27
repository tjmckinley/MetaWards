
__all__ = ["extract_custom",
           "build_custom_extractor"]


def build_custom_extractor(custom_function, parent_name="__main__"):
    """Build and return a custom extractor from the passed
       function. This will wrap 'extract_custom' around
       the function to double-check that the custom
       function is doing everything correctly

       Parameters
       ----------
       custom_function
         This can either be a function, which will be wrapped and
         returned, or it can be a string. If it is a string then
         we will attempt to locate or import the function associated
         with that string. The search order is;

         1. Is this 'metawards.extractors.custom_function'?
         2. Is this 'custom_function' that is already imported'?
         3. Is this a file name in the current path, if yes then
            find the function in that file (either the first function
            called 'extractXXX' or the specified function if
            custom_function is in the form module::function)

        parent_name: str
          This should be the __name__ of the calling function, e.g.
          call this function as build_custom_extractor(func, __name__)

        Returns
        -------
        extractor
          The wrapped extractor that is suitable for using in the extract
          function.
    """
    print(custom_function)

    if isinstance(custom_function, str):
        print(f"Importing a custom extractor from {custom_function}")

        # we need to find the function
        import metawards.extractors

        # is it metawards.extractors.{custom_function}
        try:
            func = getattr(metawards.extractors, custom_function)
            return build_custom_extractor(func)
        except Exception:
            pass

        # do we have the function in the current namespace?
        import sys
        try:
            func = getattr(sys.modules[__name__], custom_function)
            return build_custom_extractor(func)
        except Exception:
            pass

        # how about the __name__ namespace of the caller
        try:
            func = getattr(sys.modules[parent_name], custom_function)
            return build_custom_extractor(func)
        except Exception:
            pass

        # how about the __main__ namespace (e.g. if this was loaded
        # in a script)
        try:
            func = getattr(sys.modules["__main__"], custom_function)
            return build_custom_extractor(func)
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

        try:
            import importlib
            module = importlib.import_module(func_module)
        except SyntaxError as e:
            print(f"\nSyntax error when importing {func_module}")
            print(f"{e.__class__.__name__}:{e}")
            print(f"Line {e.lineno}.{e.offset}:{(e.offset-1)*' '} |")
            print(f"Line {e.lineno}.{e.offset}:{(e.offset-1)*' '}\\|/")
            print(f"Line {e.lineno}.{e.offset}: {e.text}\n")
            module = None
        except Exception:
            module = None

        if module is None:
            try:
                import importlib.util
                import os

                if os.path.exists(func_module):
                    pyfile = func_module
                else:
                    pyfile = f"{func_module}.py"

                spec = importlib.util.spec_from_file_location(
                                                func_module,
                                                pyfile)

                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                print(f"Loaded iterator from {pyfile}")
            except SyntaxError as e:
                print(f"\nSyntax error when reading {pyfile}")
                print(f"{e.__class__.__name__}:{e}")
                print(f"Line {e.lineno}.{e.offset}:{(e.offset-1)*' '} |")
                print(f"Line {e.lineno}.{e.offset}:{(e.offset-1)*' '}\\|/")
                print(f"Line {e.lineno}.{e.offset}: {e.text}\n")
            except Exception:
                pass

        if module is None:
            # we cannot find the extractor
            print(f"Cannot find the extractor '{custom_function}'."
                  f"Please make sure this is spelled correctly and "
                  f"any python modules/files needed are in the "
                  f"PYTHONPATH or current directory")
            raise ImportError(f"Could not import the extractor "
                              f"'{custom_function}'")

        if func_name is None:
            # find the first function that starts with 'extract'
            import inspect
            for name, value in inspect.getmembers(module):
                if name.startswith("extract"):
                    if hasattr(value, "__call__"):
                        # this is a function
                        return build_custom_extractor(getattr(module, name))

            print(f"Could not find any function in the module "
                  f"{custom_function} that has a name that starts "
                  f"with 'extract'. Please manually specify the "
                  f"name using the '{custom_function}::your_function syntax")

            raise ImportError(f"Could not import the extractor "
                              f"{custom_function}")

        else:
            if hasattr(module, func_name):
                return build_custom_extractor(getattr(module, func_name))

            print(f"Could not find the function {func_name} in the "
                  f"module {func_module}. Check that the spelling "
                  f"is correct and that the right version of the module "
                  f"is being loaded.")
            raise ImportError(f"Could not import the extractor "
                              f"{custom_function}")

    if not hasattr(custom_function, "__call__"):
        print(f"Cannot build an extractor for {custom_function} "
              f"as it is missing a __call__ function, i.e. it is "
              f"not a function.")
        raise ValueError(f"You can only build custom extractors for "
                         f"actual functions... {custom_function}")

    print(f"Building a custom extractor for {custom_function}")

    return lambda **kwargs: extract_custom(custom_function=custom_function,
                                           **kwargs)


def extract_custom(custom_function,
                   setup=False, **kwargs):
    """This returns the default list of 'output_XXX' functions that
       are called in sequence to extract data after each iteration
       of the model run.

       This extractor provides a custom extractor that uses
       'custom_function' passed from the user. This extractor makes
       sure that 'setup' is called correctly and that the functions
       needed by 'extract_core' are called first.

       Parameters
       ----------
       custom_function
         A custom user-supplied function that returns the
         functions that the user would like to be called for
         each step.
       setup: bool
         Whether or not to return the functions used to setup the
         space and input for the output_XXX functions returned by
         this extractor. This is called once at the start of a run
         to return the functions that must be called to setup the
         output. Note that most extractors don't need any setup.

       Returns
       -------
       funcs: List[function]
         The list of functions that ```extract``` will call in sequence
    """

    kwargs["setup"] = setup

    from ._extract_core import extract_core
    from ._extract_default import extractor_needs_setup

    if setup:
        # Return the functions needed to initialise this extractor
        core_funcs = extract_core(**kwargs)

        if extractor_needs_setup(custom_function):
            custom_funcs = custom_function(**kwargs)
        else:
            custom_funcs = None

    else:
        core_funcs = extract_core(**kwargs)
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

        return custom_funcs
