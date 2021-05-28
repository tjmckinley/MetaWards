# Package setup copied from
# https://github.com/FedericoStra/cython-package-example
# Thanks - this was really helpful :-)

from distutils.errors import LinkError
import os
import versioneer
from setuptools import setup, Extension
import distutils.sysconfig
import distutils.ccompiler
from distutils import log
import multiprocessing
import subprocess
from glob import glob
import platform
import tempfile
import shutil
import sys

try:
    from Cython.Build import cythonize
    have_cython = True
except Exception:
    have_cython = False

_system_input = input

# has the user asked for a build?
is_build = False

for arg in sys.argv[1:]:
    lower = arg.lower()
    if arg in ["build", "bdist_wheel", "build_py"]:
        is_build = True
        break


def setup_package():
    # First, set some flags regarding the distribution
    IS_MAC = False
    IS_LINUX = False
    IS_WINDOWS = False
    MACHINE = platform.machine()

    openmp_flags = ["-fopenmp"]

    if platform.system() == "Darwin":
        IS_MAC = True
        if is_build:
            print(f"\nCompiling on a Mac ({MACHINE})")

    elif platform.system() == "Windows":
        IS_WINDOWS = True
        openmp_flags.insert(0, "/openmp")   # MSVC flag
        if is_build:
            print(f"\nCompiling on Windows ({MACHINE})")

    elif platform.system() == "Linux":
        IS_LINUX = True
        if is_build:
            print(f"\nCompiling on Linux ({MACHINE})")

    else:
        if is_build:
            print(f"Unrecognised platform {platform.system()}. Assuming Linux")
        IS_LINUX = True

    # Get the compiler that (I think) distutils will use
    # - I will need this to add options etc.
    compiler = distutils.ccompiler.new_compiler()
    distutils.sysconfig.customize_compiler(compiler)

    user_openmp_flag = os.getenv("OPENMP_FLAG", None)

    if user_openmp_flag is not None:
        openmp_flags.insert(user_openmp_flag, 0)

    # override 'input' so that defaults can be used when this is run in batch
    # or CI/CD
    def input(prompt: str, default="y"):
        """Wrapper for 'input' that returns 'default' if it detected
        that this is being run from within a batch job or other
        service that doesn't have access to a tty
        """
        import sys

        try:
            if sys.stdin.isatty():
                return _system_input(prompt)
            else:
                print(f"Not connected to a console, so having to use "
                      f"the default ({default})")
                return default
        except Exception as e:
            print(f"Unable to get the input: {e.__class__} {e}")
            print(f"Using the default ({default}) instead")
            return default

    # Check if compiler support openmp (and find the correct openmp flag)
    def get_openmp_flag():
        openmp_test = \
            r"""
            #include <omp.h>
            #include <stdio.h>

            int main(int argc, char **argv)
            {
                int nthreads, thread_id;

                #pragma omp parallel private(nthreads, thread_id)
                {
                    thread_id = omp_get_thread_num();
                    nthreads = omp_get_num_threads();
                    printf("I am thread %d of %d\n", thread_id, nthreads);
                }

                return 0;
            }
            """

        tmpdir = tempfile.mkdtemp()
        curdir = os.getcwd()
        os.chdir(tmpdir)
        filename = r'openmp_test.c'

        with open(filename, 'w') as file:
            file.write(openmp_test)
            file.flush()

        openmp_compile_flag = None
        openmp_link_flags = []

        if user_openmp_flag:
            openmp_flags.insert(0, user_openmp_flag)

        print("\nChecking if the compiler supports openmp...\n")

        log_threshold = log.set_threshold(log.FATAL)

        for flag in openmp_flags:
            try:
                print(f"Checking if the compiler supports openmp flag {flag}")
                # Compiler and then link using each openmp flag...
                compiler.compile(sources=["openmp_test.c"],
                                 extra_postargs=[flag])

                objects = ["openmp_test" + compiler.obj_extension]

                link_flags = [flag]

                try:
                    compiler.link_executable(objects, "test_openmp",
                                             extra_postargs=[flag])
                except Exception:
                    # We are likely missing the path to the libomp library - get this path
                    print(
                        "\nCould not link - trying again, specifying the path to libomp")

                    compiler_dir = os.path.dirname(compiler.compiler_so[0])
                    libomp = glob(f"{compiler_dir}/../lib*/libomp*")

                    if len(libomp) == 0:
                        raise LinkError("Cannot find libomp for linking!")

                    libomp = os.path.abspath(libomp[0])
                    print(f"libomp = {libomp}\n")
                    libpath = os.path.dirname(libomp)

                    try:
                        link_flags = [flag, f"-L{libpath}",
                                      f"-Wl,-rpath,{libpath}", "-lomp"]
                        compiler.link_executable(objects, "test_openmp",
                                                 extra_postargs=[flag]+link_flags)
                    except Exception as e:
                        print("\nFailed to link, likely because the OpenMP\n"
                              "library can't be found. Make sure that\n"
                              "this library is in your LD_LIBRARY_PATH\n")
                        raise e

                try:
                    subprocess.check_output('./test_openmp')
                except Exception as e:
                    print("\nFailed to run test_openmp executable. This\n"
                          "suggests that even if we can compile with OpenMP\n"
                          "that we can't run the code.")
                    raise e

                openmp_compile_flag = flag
                openmp_link_flags = link_flags
                print(
                    f"Compiler supports openmp using flag {flag}. Excellent!\n")
                break
            except Exception as e:
                print(e)
                print(f"Compiler doesn't appear to support flag {flag}.")
                print("No problem - you can ignore the above error message.\n")

        log.set_threshold(log_threshold)

        # clean up
        os.chdir(curdir)
        shutil.rmtree(tmpdir)

        if openmp_compile_flag is None:
            return None
        else:
            return [openmp_compile_flag, openmp_link_flags]

    if is_build:
        openmp_flags = get_openmp_flag()
    else:
        openmp_flags = None

    include_dirs = ["src/metawards"]

    if is_build and (openmp_flags is None):
        print(f"\nYour compiler {compiler.compiler_so[0]} does not support "
              f"OpenMP with any of the known OpenMP flags {openmp_flags}. "
              f"If you know which flag to use can you specify it using "
              f"the environent variable OPENMP_FLAG. Otherwise, we will "
              f"have to compile the serial version of the code.")

        if IS_MAC:
            print("\nThis is common on Mac, as the default compiler does not "
                  "support OpenMP. If you want to compile with OpenMP then "
                  "install llvm via homebrew, e.g. 'brew install llvm', see "
                  "https://embeddedartistry.com/blog/2017/02/24/installing-llvm-clang-on-osx/")

            print("\nRemember then to choose that compiler by setting the "
                  "CC environment variable, or passing it on the 'make' line, "
                  "e.g. 'CC=/opt/homebrew/opt/llvm/bin/clang make'")
        elif IS_LINUX or IS_WINDOWS:
            print("\nStrange, as OpenMP is normally supported on Windows and Linux.")
            print("This suggests that there may be something wrong with the compiler.")

        result = input("\nDo you want compile without OpenMP? (y/n) ",
                       default="y")

        if result is None or result.strip().lower()[0] != "y":
            sys.exit(-1)

        include_dirs.append("src/metawards/disable_openmp")

    cflags = []
    lflags = []

    if not IS_WINDOWS:
        cflags.append("-O3")

    if openmp_flags:
        cflags.append(openmp_flags[0])
        lflags += openmp_flags[1]

        print(f"\nCFLAGS = {' '.join(cflags)}")
        print(f"LFLAGS = {' '.join(lflags)}\n")

    nbuilders = int(os.getenv("CYTHON_NBUILDERS", 2))

    if nbuilders < 1:
        nbuilders = 1

    if is_build:
        print(f"Number of builders equals {nbuilders}\n")

    compiler_directives = {"language_level": 3, "embedsignature": True,
                           "boundscheck": False, "cdivision": True,
                           "initializedcheck": False,
                           "cdivision_warnings": False,
                           "wraparound": False, "binding": False,
                           "nonecheck": False, "overflowcheck": False}

    if os.getenv("CYTHON_LINETRACE", 0):
        if is_build:
            print("Compiling with Cython line-tracing support - will be SLOW")
        define_macros = [("CYTHON_TRACE", "1")]
        compiler_directives["linetrace"] = True
    else:
        define_macros = []

    # Thank you Priyaj for pointing out this little documented feature - finally
    # I can build the random code into a library!
    # https://www.edureka.co/community/21524/setuptools-shared-libary-cython-wrapper-linked-shared-libary
    ext_lib_path = "src/metawards/ran_binomial"
    sources = ["mt19937.c", "distributions.c"]

    ext_libraries = [['metawards_random', {
        'sources': [os.path.join(ext_lib_path, src)
                    for src in sources],
        'include_dirs': [],
        'macros': [],
    }]]

    def no_cythonize(extensions, **_ignore):
        # https://cython.readthedocs.io/en/latest/src/userguide/source_files_and_compilation.html#distributing-cython-modules
        for extension in extensions:
            sources = []
            for sfile in extension.sources:
                path, ext = os.path.splitext(sfile)
                if ext in (".pyx", ".py"):
                    if extension.language == "c++":
                        ext = ".cpp"
                    else:
                        ext = ".c"
                    sfile = path + ext
                sources.append(sfile)
            extension.sources[:] = sources
        return extensions

    utils_pyx_files = glob("src/metawards/utils/*.pyx")
    iterator_pyx_files = glob("src/metawards/iterators/*.pyx")
    extractor_pyx_files = glob("src/metawards/extractors/*.pyx")
    mixer_pyx_files = glob("src/metawards/mixers/*.pyx")
    mover_pyx_files = glob("src/metawards/movers/*.pyx")

    libraries = ["metawards_random"]

    extensions = []

    for pyx in utils_pyx_files:
        _, name = os.path.split(pyx)
        name = name[0:-4]
        module = f"metawards.utils.{name}"

        extensions.append(Extension(module, [pyx], define_macros=define_macros,
                                    libraries=libraries,
                                    extra_compile_args=cflags,
                                    extra_link_args=lflags,
                                    include_dirs=include_dirs))

    for pyx in iterator_pyx_files:
        _, name = os.path.split(pyx)
        name = name[0:-4]
        module = f"metawards.iterators.{name}"

        extensions.append(Extension(module, [pyx], define_macros=define_macros,
                                    libraries=libraries,
                                    extra_compile_args=cflags,
                                    extra_link_args=lflags,
                                    include_dirs=include_dirs))

    for pyx in extractor_pyx_files:
        _, name = os.path.split(pyx)
        name = name[0:-4]
        module = f"metawards.extractors.{name}"

        extensions.append(Extension(module, [pyx], define_macros=define_macros,
                                    libraries=libraries,
                                    extra_compile_args=cflags,
                                    extra_link_args=lflags,
                                    include_dirs=include_dirs))

    for pyx in mixer_pyx_files:
        _, name = os.path.split(pyx)
        name = name[0:-4]
        module = f"metawards.mixers.{name}"

        extensions.append(Extension(module, [pyx], define_macros=define_macros,
                                    libraries=libraries,
                                    extra_compile_args=cflags,
                                    extra_link_args=lflags,
                                    include_dirs=include_dirs))

    for pyx in mover_pyx_files:
        _, name = os.path.split(pyx)
        name = name[0:-4]
        module = f"metawards.movers.{name}"

        extensions.append(Extension(module, [pyx], define_macros=define_macros,
                                    libraries=libraries,
                                    extra_compile_args=cflags,
                                    extra_link_args=lflags,
                                    include_dirs=include_dirs))

    CYTHONIZE = bool(int(os.getenv("CYTHONIZE", 0)))

    if not have_cython:
        CYTHONIZE = False

    if CYTHONIZE:
        extensions = cythonize(extensions,
                               compiler_directives=compiler_directives,
                               nthreads=nbuilders)
    else:
        extensions = no_cythonize(extensions)

    with open("requirements.txt") as fp:
        install_requires = fp.read().strip().split("\n")

    with open("requirements-dev.txt") as fp:
        dev_requires = fp.read().strip().split("\n")

    if IS_WINDOWS:
        import sys
        v = sys.version_info

        mw_random_lib = glob(
            f"build/*{v.major}.{v.minor}/metawards_random.lib")

        if len(mw_random_lib) == 0:
            if not is_build:
                print("WARNING: CANNOT FIND metawards_random.lib!")
        elif len(mw_random_lib) > 1:
            mw_random_lib = [mw_random_lib[0]]

        libs_dir = os.path.abspath(os.path.join(sys.prefix, "libs"))

        if not is_build:
            print(f"Installing {mw_random_lib} to {libs_dir}")
    else:
        import sys
        v = sys.version_info
        mw_random_lib = glob(
            f"build/*{v.major}.{v.minor}/libmetawards_random.a")

        if len(mw_random_lib) == 0:
            if not is_build:
                print("WARNING: CANNOT FIND metawards_random.lib!")
        elif len(mw_random_lib) > 1:
            mw_random_lib = [mw_random_lib[0]]

        libs_dir = "lib"

    if not os.path.exists("build"):
        os.mkdir("build")

    print(os.listdir("build"))
    for p in os.listdir("build"):
        print(p)
        print(os.listdir(os.path.join("build", p)))

    print(f"\n** mw_random_lib: {mw_random_lib} libs_dir: {libs_dir}")

    setup(
        version=versioneer.get_version(),
        cmdclass=versioneer.get_cmdclass(),
        ext_modules=extensions,
        install_requires=install_requires,
        libraries=ext_libraries,
        extras_require={
            "dev": dev_requires,
            "docs": ["sphinx", "sphinx-rtd-theme"]
        },
        entry_points={
            "console_scripts": [
                "metawards = metawards.app.run:cli",
                "metawards-plot = metawards.scripts.plot:cli",
                "metawards-install = metawards.scripts.install:cli",
                "metawards-python = metawards.scripts.pyexe:cli",
                "metawards-jupyter = metawards.scripts.jupexe:cli",
                "metawards-reticulate = metawards.scripts.retexe:cli",
                "metawards-update = metawards.scripts.update:cli"
            ]
        },
        data_files=[("share/metawards/requirements",
                     ["requirements.txt", "requirements-optional.txt"]),
                    ("include/metawards/ran_binomial",
                     glob("src/metawards/ran_binomial/*.h")),
                    (libs_dir, mw_random_lib)]
    )


if __name__ == "__main__":
    # Freeze to support parallel compilation when using spawn instead of fork
    # (thanks to pandas for showing how to do this in their setup.py)
    multiprocessing.freeze_support()
    setup_package()
