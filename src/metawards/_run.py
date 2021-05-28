from __future__ import annotations

from typing import Union as _Union
from typing import List as _List
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._disease import Disease
    from ._demographics import Demographics
    from ._demographic import Demographic
    from ._parameters import Parameters
    from ._wards import Wards
    from ._ward import Ward
    from ._variableset import VariableSet, VariableSets

    from datetime import date


__all__ = ["run", "find_mw_exe", "find_mw_include", "find_mw_lib",
           "get_reticulate_command"]


def _write_to_file(obj: any, filename: str, dir: str = ".", bzip: bool = False,
                   dry_run: bool = False) -> str:
    """Write the passed object to a file called 'filename' in
       directory 'dir', returning the
       relative path to that file
    """
    import os

    if dry_run:
        return filename

    filename = os.path.join(dir, filename)

    if hasattr(obj, "to_json"):
        return obj.to_json(filename, auto_bzip=bzip)
    else:
        raise IOError(f"Cannot convert {obj} to a file!")

    return filename


def _rmdir(directory):
    """Function modified from one copied from 'mitch' on stackoverflow
       https://stackoverflow.com/questions/13118029/deleting-folders-in-python-recursively
    """
    if directory is None:
        return

    from pathlib import Path
    directory = Path(directory)

    # first, check for removing important directories such as $HOME or root
    if directory == Path.home():
        raise FileExistsError(f"We WILL NOT remove your "
                              f"home directory ${directory}")

    if directory == Path("/"):
        raise FileExistsError(f"We WILL NOT remove the root directory "
                              f"{directory}")

    # get the directory containing '$HOME'
    if directory == Path.home().parent:
        raise FileExistsError(f"We WILL NOT remove the users/home "
                              f"directory {directory}")

    if not directory.is_dir():
        directory.unlink()
        return

    for item in directory.iterdir():
        if item.is_dir():
            _rmdir(item)
        else:
            item.unlink()

    directory.rmdir()


def _is_executable(filename):
    import os
    if not os.path.exists(filename):
        return None

    if os.path.isdir(filename):
        return None

    # determining if this is executable
    # on windows is really difficult, so just
    # assume it is...
    return filename


def _find_metawards(dirname):
    import os
    m = _is_executable(os.path.join(dirname, "metawards"))

    if m:
        return m

    m = _is_executable(os.path.join(dirname, "metawards.exe"))

    if m:
        return m

    m = _is_executable(os.path.join(dirname, "Scripts", "metawards"))

    if m:
        return m

    m = _is_executable(os.path.join(dirname, "Scripts", "metawards.exe"))

    if m:
        return m

    m = _is_executable(os.path.join(dirname, "bin", "metawards"))

    if m:
        return m

    m = _is_executable(os.path.join(dirname, "bin", "metawards.exe"))

    if m:
        return m

    return None


def _find_metawards_include(dirname):
    import os

    # this is from a metawards installation
    m = os.path.abspath(os.path.join(dirname, "include", "metawards"))

    if os.path.exists(m):
        return m

    # this is from a metawards source run (used for testing)
    m = os.path.abspath(os.path.join(dirname, "src", "metawards"))

    if os.path.exists(m):
        return m

    return None


def _find_metawards_lib(dirname):
    import os
    import glob

    m = glob.glob(os.path.join(dirname, "lib", "libmetawards_*"))

    if m is None:
        m = []

    if len(m) >= 1:
        m = os.path.dirname(os.path.abspath(m[0]))
        return m

    m = glob.glob(os.path.join(dirname, "libmetawards_*"))

    if m is None:
        m = []

    if len(m) >= 1:
        m = os.path.dirname(os.path.abspath(m[0]))
        return m

    m = glob.glob(os.path.join(dirname, "lib*", "metawards_random.*"))

    if m is None:
        m = []

    if len(m) >= 1:
        m = os.path.dirname(os.path.abspath(m[0]))
        return m

    m = glob.glob(os.path.join(dirname, "metawards_random.*"))

    if m is None:
        m = []

    if len(m) >= 1:
        m = os.path.dirname(os.path.abspath(m[0]))
        return m

    return None


def find_mw_lib():
    """Try to find the directory containing the MetaWards libraries
       (e.g. metawards_random).

       This raises an exception if the libraries cannot be found.
       It returns the full path to the library directory
    """
    import metawards as _metawards
    import os as _os
    import sys as _sys

    # Search through the path based on where the metawards module
    # has been installed.
    modpath = _metawards.__file__

    metawards = None

    # Loop only 100 times - this should break before now,
    # We are not using a while loop to avoid an infinite loop
    for i in range(0, 100):
        metawards = _find_metawards_lib(modpath)

        if metawards:
            break

        newpath = _os.path.dirname(modpath)

        if newpath == modpath:
            break

        modpath = newpath

    if metawards is not None:
        return metawards

    # Search from sys.prefix
    modpath = _sys.prefix

    # Loop only 100 times - this should break before now,
    # We are not using a while loop to avoid an infinite loop
    for i in range(0, 100):
        metawards = _find_metawards_lib(modpath)

        if metawards:
            break

        newpath = _os.path.dirname(modpath)

        if newpath == modpath:
            break

        modpath = newpath

    if metawards is not None:
        return metawards

    # This could have been put in the hostedtoolcache folder...
    p = _os.path.abspath(_os.path.join(_os.path.dirname(_metawards.__file__),
                                       "..", "hostedtoolcache"))

    if _os.path.exists(p):
        for dirpath, dirnames, filenames in _os.walk(p):
            for filename in [f for f in filenames if (f.endswith(".lib") or
                                                      (f.endswith(".a")))]:
                if filename.find("metawards") != -1:
                    metawards = dirpath

    if metawards is None:
        from .utils._console import Console
        Console.error(
            "Cannot find the metawards library directory, when starting from "
            f"{_metawards.__file__}. Please could you "
            "find it and then post an issue on the "
            "GitHub repository (https://github.com/metawards/MetaWards) "
            "as this may indicate a bug in the code.")
        raise RuntimeError("Cannot locate the metawards library directory")

    return metawards


def find_mw_include():
    """Try to find the directory containing the MetaWards include files.
       This raises an exception if the include files cannot be found.
       It returns the full path to the include files
    """
    import metawards as _metawards
    import os as _os
    import sys as _sys

    # Search through the path based on where the metawards module
    # has been installed.
    modpath = _metawards.__file__

    metawards = None

    # Loop only 100 times - this should break before now,
    # We are not using a while loop to avoid an infinite loop
    for i in range(0, 100):
        metawards = _find_metawards_include(modpath)

        if metawards:
            break

        newpath = _os.path.dirname(modpath)

        if newpath == modpath:
            break

        modpath = newpath

    if metawards is not None:
        return metawards

    # Search from sys.prefix
    modpath = _sys.prefix

    # Loop only 100 times - this should break before now,
    # We are not using a while loop to avoid an infinite loop
    for i in range(0, 100):
        metawards = _find_metawards_include(modpath)

        if metawards:
            break

        newpath = _os.path.dirname(modpath)

        if newpath == modpath:
            break

        modpath = newpath

    if metawards is None:
        from .utils._console import Console
        Console.error(
            "Cannot find the metawards include directory, when starting from "
            f"{_metawards.__file__}. Please could you "
            "find it and then post an issue on the "
            "GitHub repository (https://github.com/metawards/MetaWards) "
            "as this may indicate a bug in the code.")
        raise RuntimeError("Cannot locate the metawards include directory")

    return metawards


def find_mw_exe():
    """Try to find the MetaWards executable. This should be findable
       if MetaWards has been installed. This raises an exception
       if it cannot be found. It returns the full path to the
       executable
    """
    import metawards as _metawards
    import os as _os
    import sys as _sys

    # Search through the path based on where the metawards module
    # has been installed.
    modpath = _metawards.__file__

    metawards = None

    # Loop only 100 times - this should break before now,
    # We are not using a while loop to avoid an infinite loop
    for i in range(0, 100):
        metawards = _find_metawards(modpath)

        if metawards:
            break

        newpath = _os.path.dirname(modpath)

        if newpath == modpath:
            break

        modpath = newpath

    if metawards is not None:
        return metawards

    # Search from sys.prefix
    modpath = _sys.prefix

    # Loop only 100 times - this should break before now,
    # We are not using a while loop to avoid an infinite loop
    for i in range(0, 100):
        metawards = _find_metawards(modpath)

        if metawards:
            break

        newpath = _os.path.dirname(modpath)

        if newpath == modpath:
            break

        modpath = newpath

    if metawards is None:
        # We couldn't find it that way - try another route...
        dirpath = _os.path.join(_os.path.dirname(_sys.executable))

        for option in [_os.path.join(dirpath, "metawards.exe"),
                       _os.path.join(dirpath, "metawards"),
                       _os.path.join(dirpath, "Scripts", "metawards.exe"),
                       _os.path.join(dirpath, "Scripts", "metawards")]:
            if _os.path.exists(option):
                metawards = option
                break

    if metawards is None:
        # last attempt - is 'metawards' in the PATH?
        from shutil import which
        metawards = which("metawards")

    if metawards is None:
        from .utils._console import Console
        Console.error(
            "Cannot find the metawards executable. Please could you find "
            "it and add it to the PATH. Or please post an issue on the "
            "GitHub repository (https://github.com/metawards/MetaWards) "
            "as this may indicate a bug in the code.")
        raise RuntimeError("Cannot locate the metawards executable")

    return metawards


def get_reticulate_command():
    """Print the reticulate command that you need to type
       to be able to use the Python in which MetaWards is
       installed
    """
    import os as _os
    import sys as _sys
    pyexe = _os.path.abspath(_sys.executable)
    return f"reticulate::use_python(\"{pyexe}\", required=TRUE)"


def run(help: bool = None,
        version: bool = None,
        dry_run: bool = None,
        silent: bool = False,
        auto_load: bool = False,
        config: str = None,
        input: _Union[str, VariableSet, VariableSets] = None,
        line: int = None,
        repeats: int = None,
        seed: int = None,
        additional: _Union[str, _List[str]] = None,
        output: str = None,
        disease: _Union[str, Disease] = None,
        model: _Union[str, Wards, Ward] = None,
        demographics: _Union[str, Demographics, Demographic] = None,
        start_date: _Union[str, date] = None,
        start_day: int = None,
        parameters: _Union[str, Parameters] = None,
        repository: str = None,
        population: int = None,
        nsteps: int = None,
        user_variables: _Union[str, VariableSet] = None,
        iterator: str = None,
        extractor: str = None,
        mixer: str = None,
        mover: str = None,
        star_as_E: bool = None,
        star_as_R: bool = None,
        disable_star: bool = None,
        UV: float = None,
        debug: bool = None,
        debug_level: int = None,
        outdir_scheme: str = None,
        nthreads: int = None,
        nprocs: int = None,
        hostfile: str = None,
        cores_per_node: int = None,
        auto_bzip: bool = None,
        no_auto_bzip: bool = None,
        force_overwrite_output: bool = None,
        profile: bool = None,
        no_profile: bool = None,
        mpi: bool = None,
        scoop: bool = None) -> _Union[str, 'pandas.DataFrame']:
    """Run a MetaWards simulation

       Parameters
       ----------
       silent: bool
         Run without printing the output to the screen
       dry_run: bool
         Don't run anything - just print what will be run
       help: bool
         Whether or not to print the full help
       version: bool
         Whether or not to print the metawards version info
       output: str
         The name of the directory in which to write the output. If this
         is not set, then a new, random-named directory will be used.
       force_overwrite_output: bool
         Force overwriting the output directory - this will remove any
         existing directory before running
       auto_load: bool
         Whether or not to automatically load and return a pandas dataframe
         of the output/results.csv.bz2 file. If pandas is available then
         this defaults to True, otherwise False
       disease: Disease or str
         The disease to model (or the filename of the json file containing
         the disease, or name of the disease)
       model: Ward, Wards or str
         The network wards to run (of the filename of the json file
         containing the network, or name of the network))

       There are many more parameters, based on the arguments to
       metawards --help.

       Please set "help" to True to print out a full list of
       help for all of the arguments

        Returns
        -------
        results: str or pandas.DataFrame
          The file containing the output results (output/results.csv.bz2),
          or, if auto_load is True, the pandas.DataFrame containing
          those results
    """
    import sys
    import os
    import tempfile
    from .utils._console import Console

    metawards = find_mw_exe()

    args = []

    tmpdir = None

    theme = "simple"
    no_progress = True
    no_spinner = True

    if help:
        args.append("--help")
        output = None
    elif version:
        args.append("--version")
        output = None
    else:
        if output is None and not dry_run:
            output = tempfile.mkdtemp(prefix="output_", dir=".")
            force_overwrite_output = True

        if force_overwrite_output:
            args.append("--force-overwrite-output")
        else:
            if output is None:
                output = "output"

            while os.path.exists(output):
                import metawards as _metawards
                print(f"Output directory {output} exists.")
                output = _metawards.input("Please choose a new directory: ",
                                          default="error")

                if output is None:
                    return 0

                output = output.strip()
                if len(output) == 0:
                    return 0

                if output.lower() == "error":
                    Console.error("You need to delete the directory or set "
                                  "'force_overwrite_output' to TRUE")
                    return -1

        try:
            if config is not None:
                args.append(f"--config {config}")

            if input is not None:
                if not isinstance(input, str):
                    if tmpdir is None:
                        tmpdir = tempfile.mkdtemp(prefix="input_", dir=".")

                    input = _write_to_file(input, "input.dat", dir=tmpdir,
                                           bzip=False, dry_run=dry_run)

                args.append(f"--input {input}")

            if line is not None:
                args.append(f"--line {int(line)}")

            if repeats is not None:
                args.append(f"--repeats {int(repeats)}")

            if seed is not None:
                args.append(f"--seed {int(seed)}")

            if additional is not None:
                if isinstance(additional, list):
                    additional = "\\n".join(additional)
                elif not isinstance(additional, str):
                    additional = str(int(additional))

                if "\"" in additional:
                    if sys.platform.startswith("win"):
                        additional.replace("\"", "'")
                        args.append(f"--additional \"{additional}\"")
                    else:
                        args.append(f"--additional '{additional}'")
                else:
                    args.append(f"--additional \"{additional}\"")

            if output is not None:
                args.append(f"--output {output}")

            if disease is not None:
                if not isinstance(disease, str):
                    if tmpdir is None:
                        tmpdir = tempfile.mkdtemp(prefix="input_", dir=".")

                    disease = _write_to_file(disease, "disease.json",
                                             dir=tmpdir,
                                             bzip=False, dry_run=dry_run)

                args.append(f"--disease {disease}")

            if model is not None:
                from ._ward import Ward
                from ._wards import Wards

                if isinstance(model, Ward):
                    m = Wards()
                    m.add(model)
                    model = m

                if not isinstance(model, str):
                    if tmpdir is None:
                        tmpdir = tempfile.mkdtemp(prefix="input_", dir=".")

                    model = _write_to_file(model, "model.json", dir=tmpdir,
                                           bzip=True, dry_run=dry_run)

                args.append(f"--model {model}")

            if demographics is not None:
                from ._demographic import Demographic
                from ._demographics import Demographics

                if isinstance(demographics, Demographic):
                    d = Demographics()
                    d.add(demographics)
                    demographics = demographics

                if not isinstance(demographics, str):
                    if tmpdir is None:
                        tmpdir = tempfile.mkdtemp(prefix="input_", dir=".")

                    demographics = _write_to_file(demographics,
                                                  "demographics.json",
                                                  dir=tmpdir,
                                                  bzip=False,
                                                  dry_run=dry_run)

                args.append(f"--demographics {demographics}")

            if start_date is not None:
                from datetime import date
                if isinstance(start_date, date):
                    start_date = date.isoformat()

                args.append(f"--start-date {start_date}")

            if start_day is not None:
                args.append(f"--start-day {int(start_day)}")

            if parameters is not None:
                if not isinstance(parameters, str):
                    if tmpdir is None:
                        tmpdir = tempfile.mkdtemp(prefix="input_", dir=".")

                    parameters = _write_to_file(parameters, "parameters.dat",
                                                dir=tmpdir, bzip=False,
                                                dry_run=dry_run)

                args.append(f"--parameters {parameters}")

            if repository is not None:
                args.append(f"--repository {repository}")

            if population is not None:
                args.append(f"--population {int(population)}")

            if nsteps is not None:
                args.append(f"--nsteps {int(nsteps)}")

            if user_variables is not None:
                if not isinstance(user_variables, str):
                    if tmpdir is None:
                        tmpdir = tempfile.mkdtemp(prefix="input_", dir=".")

                    user_variables = _write_to_file(user_variables,
                                                    "user_variables.dat",
                                                    dir=tmpdir,
                                                    bzip=False,
                                                    dry_run=dry_run)

                args.append(f"--user {user_variables}")

            if iterator is not None:
                args.append(f"--iterator {iterator}")

            if extractor is not None:
                args.append(f"--extractor {extractor}")

            if mixer is not None:
                args.append(f"--mixer {mixer}")

            if mover is not None:
                args.append(f"--mover {mover}")

            if star_as_E:
                args.append("--star-as-E")
            elif star_as_R:
                args.append("--star-as-R")
            elif disable_star:
                args.append("--disable-star")

            if UV is not None:
                args.append(f"--UV {UV}")

            if theme is not None:
                args.append(f"--theme {theme}")

            if no_spinner:
                args.append("--no-spinner")

            if no_progress:
                args.append("--no-progress")

            if debug:
                args.append("--debug")

                if debug_level is not None:
                    args.append(f"--debug-level {debug_level}")

            if outdir_scheme is not None:
                args.append(f"--outdir-scheme {outdir_scheme}")

            if nthreads is not None:
                args.append(f"--nthreads {int(nthreads)}")

            if nprocs is not None:
                args.append(f"--nprocs {int(nprocs)}")

            if hostfile is not None:
                args.append(f"--hostfile {hostfile}")

            if cores_per_node is not None:
                args.append(f"--cores-per-node {int(cores_per_node)}")

            if auto_bzip:
                args.append("--auto-bzip")
            elif no_auto_bzip:
                args.append("--no-auto-bzip")

            if profile:
                args.append("--profile")
            elif no_profile:
                args.append("--no-profile")

            if mpi:
                args.append("--mpi")

            if scoop:
                args.append("--scoop")

        except Exception as e:
            Console.error(f"[ERROR] Error interpreting the arguments"
                          f"[ERROR] {e.__class__}: {e}")
            _rmdir(tmpdir)
            raise
            return -1

    cmd = f"{metawards} {' '.join(args)}"

    if dry_run:
        Console.info(f"[DRY-RUN] {cmd}")
        return_val = 0
    else:
        if output is not None:
            Console.info(
                f"Writing output to directory {os.path.abspath(output)}")

        Console.info(f"[RUNNING] {cmd}")

        try:
            if sys.platform.startswith("win"):
                # shlex.split doesn't work, but the command can
                # be passed as a single string
                args = cmd
            else:
                import shlex
                args = shlex.split(cmd)

            import subprocess

            # We have to specify all of the pipes (stdin, stdout, stderr)
            # as below as otherwise we will break metawards on Windows
            # (especially needed to allow metawards to run under
            #  reticulate via metawards$run. Without these specified
            #  we end up with Windows File Errors)
            with subprocess.Popen(args,
                                  stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT,
                                  bufsize=1, encoding="utf8",
                                  errors="ignore",
                                  text=True) as PROC:
                while True:
                    line = PROC.stdout.readline()

                    if not line:
                        break

                    if not silent:
                        try:
                            sys.stdout.write(line)
                            sys.stdout.flush()
                        except UnicodeEncodeError:
                            # We get frequent unicode errors when run
                            # within RStudio. It is best just to ignore them
                            pass
                        except Exception as e:
                            Console.error(f"WRITE ERROR: {e.__class__} : {e}")

                return_val = PROC.poll()

                if return_val is None:
                    # get None if everything OK on Windows
                    # (sometimes windows returns 0 as None, which
                    #  breaks things!)
                    return_val = 0

        except Exception as e:
            Console.error(f"[ERROR] {e.__class__}: {e}")
            return_val = -1

    if tmpdir is not None:
        _rmdir(tmpdir)

    if dry_run:
        return

    if output is None:
        return

    if return_val == 0:
        results = os.path.join(output, "results.csv")

        if not os.path.exists(results):
            results += ".bz2"

        if auto_load:
            try:
                import pandas
            except ImportError:
                Console.error("Cannot import pandas:\n{e}")
                auto_load = False

        if auto_load is None:
            try:
                import pandas
                auto_load = True
            except ImportError:
                auto_load = False

        if auto_load:
            import pandas as pd
            return pd.read_csv(results)
        else:
            return results
    else:
        output_file = os.path.join(output, "console.log.bz2")

        Console.error(f"Something went wrong with the run. Please look "
                      f"at {output_file} for more information")
        return None
