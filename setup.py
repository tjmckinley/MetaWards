# Package setup copied from
# https://github.com/FedericoStra/cython-package-example
# Thanks - this was really helpful :-)

import os
import versioneer
from setuptools import setup, Extension
import distutils.sysconfig
import distutils.ccompiler
from glob import glob
import platform
import tempfile
import subprocess
import shutil
import sys

try:
    from Cython.Build import cythonize
    have_cython = True
except Exception:
    have_cython = False

# First, set some flags regarding the distribution
IS_MAC = False
IS_LINUX = False
IS_WINDOWS = False
MACHINE = platform.machine()

if platform.system() == "Darwin":
    IS_MAC = True
    print(f"\nCompiling on a Mac ({MACHINE})")

elif platform.system() == "Windows":
    IS_WINDOWS = True
    print(f"\nCompiling on Windows ({MACHINE})")

elif platform.system() == "Linux":
    IS_LINUX = True
    print(f"\nCompiling on Linux ({MACHINE})")

else:
    print(f"Unrecognised platform {platform.system()}. Assuming Linux")
    IS_LINUX = True

# Get the compiler that (I think) distutils will use
# - I will need this to add options etc.
compiler = distutils.ccompiler.new_compiler()
distutils.sysconfig.customize_compiler(compiler)

openmp_flags = ["-fopenmp", "-openmp"]
user_openmp_flag = os.getenv("OPENMP_FLAG", None)


# Check if compiler support openmp (and find the correct openmp flag)
def get_openmp_flag():
    openmp_test = \
        r"""
        #include <omp.h>
        #include <stdio.h>

        int main()
        {
            int nthreads, thread_id;

            #pragma omp parallel private(nthreads, thread_id)
            {
                thread_id = omp_get_thread_num();
                nthreads = omp_get_num_threads();
                printf("I am thread %d of %d\n", thread_id, nthreads);
            }
        }
        """

    tmpdir = tempfile.mkdtemp()
    curdir = os.getcwd()
    os.chdir(tmpdir)
    filename = r'openmp_test.c'

    with open(filename, 'w') as file:
        file.write(openmp_test)
        file.flush()

    openmp_flag = None

    if user_openmp_flag:
        openmp_flags.insert(0, user_openmp_flag)

    with open(os.devnull, 'w') as fnull:
        exit_code = 1
        for flag in openmp_flags:
            try:
                # Compiler and then link using each openmp flag...
                cmd = compiler.compiler_so + [flag, filename,
                                              "-c"]
                exit_code = subprocess.call(cmd, stdout=fnull, stderr=fnull)
            except Exception:
                pass

            if exit_code == 0:
                openmp_flag = flag
                break

    # clean up
    os.chdir(curdir)
    shutil.rmtree(tmpdir)

    return openmp_flag


disable_openmp = os.getenv("METAWARDS_DISABLE_OPENMP", None)

if disable_openmp:
    openmp_flag = None
else:
    openmp_flag = get_openmp_flag()

include_dirs = []

if openmp_flag is None:
    if disable_openmp:
        print("You have disabled OpenMP")
    else:
        print(f"\nYour compiler {compiler.compiler_so[0]} does not support "
              f"OpenMP with any of the known OpenMP flags {openmp_flags}. "
              f"If you know which flag to use can you specify it using "
              f"the environent variable OPENMP_FLAG. Otherwise, we will "
              f"have to compile the serial version of the code.")

        if IS_MAC:
            print(f"\nThis is common on Mac, as the default compiler does not "
                  f"support OpenMP. If you want to compile with OpenMP then "
                  f"install llvm via homebrew, e.g. 'brew install llvm', see "
                  f"https://embeddedartistry.com/blog/2017/02/24/installing-llvm-clang-on-osx/")

            print(f"\nRemember then to choose that compiler by setting the "
                  f"CC environment variable, or passing it on the 'make' line, "
                  f"e.g. 'CC=/usr/local/opt/llvm/bin/clang make'")

        print(f"\nAlternatively, set the environment variable "
              f"METAWARDS_DISABLE_OPENMP to compile without OpenMP "
              f"support, e.g. 'METAWARDS_DISABLE_OPENMP=1 make'")

        sys.exit(-1)

    include_dirs.append("src/metawards/disable_openmp")

cflags = "-O3"

if openmp_flag:
    cflags = f"{cflags} {openmp_flag}"

nbuilders = int(os.getenv("CYTHON_NBUILDERS", 2))

if nbuilders < 1:
    nbuilders = 1

print(f"Number of builders equals {nbuilders}\n")

compiler_directives = {"language_level": 3, "embedsignature": True,
                       "boundscheck": False, "cdivision": True,
                       "initializedcheck": False, "cdivision_warnings": False,
                       "wraparound": False, "binding": False,
                       "nonecheck": False, "overflowcheck": False}

if os.getenv("CYTHON_LINETRACE", 0):
    print("Compiling with Cython line-tracing support - will be SLOW")
    define_macros = [("CYTHON_TRACE", "1")]
    compiler_directives["linetrace"] = True
else:
    define_macros = []


# Thank you Priyaj for pointing out this little documented feature - finally
# I can build the random code into a library!
# https://www.edureka.co/community/21524/setuptools-shared-libary-cython-wrapper-linked-shared-libary
ext_lib_path = "src/metawards/ran_binomial"
sources = ["mt19937.c", "distributions.c"]

ext_libraries = [['metawards_random', {
                  'sources': [os.path.join(ext_lib_path, src) for src in sources],
                  'include_dirs': [],
                  'macros': [],
                  }]]


# https://cython.readthedocs.io/en/latest/src/userguide/source_files_and_compilation.html#distributing-cython-modules
def no_cythonize(extensions, **_ignore):
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

libraries = ["metawards_random"]

extensions = []

for pyx in utils_pyx_files:
    _, name = os.path.split(pyx)
    name = name[0:-4]
    module = f"metawards.utils.{name}"

    extensions.append(Extension(module, [pyx], define_macros=define_macros,
                                libraries=libraries,
                                include_dirs=include_dirs))

for pyx in iterator_pyx_files:
    _, name = os.path.split(pyx)
    name = name[0:-4]
    module = f"metawards.iterators.{name}"

    extensions.append(Extension(module, [pyx], define_macros=define_macros,
                                libraries=libraries,
                                include_dirs=include_dirs))

for pyx in extractor_pyx_files:
    _, name = os.path.split(pyx)
    name = name[0:-4]
    module = f"metawards.extractors.{name}"

    extensions.append(Extension(module, [pyx], define_macros=define_macros,
                                libraries=libraries,
                                include_dirs=include_dirs))

CYTHONIZE = bool(int(os.getenv("CYTHONIZE", 0)))

if not have_cython:
    CYTHONIZE = False

os.environ['CFLAGS'] = cflags

if CYTHONIZE:
    # only using 1 cythonize thread as multiple threads caused a fork bomb
    # on github
    extensions = cythonize(extensions, compiler_directives=compiler_directives,
                           nthreads=1)
else:
    extensions = no_cythonize(extensions)

with open("requirements.txt") as fp:
    install_requires = fp.read().strip().split("\n")

with open("requirements-dev.txt") as fp:
    dev_requires = fp.read().strip().split("\n")

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
           "metawards-plot = metawards.app.plot:cli"
        ]
    }
)
