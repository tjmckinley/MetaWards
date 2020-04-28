# Package setup copied from
# https://github.com/FedericoStra/cython-package-example
# Thanks - this was really helpful :-)

import os
import versioneer
from setuptools import setup, Extension
import distutils.sysconfig
import distutils.ccompiler
from glob import glob
import tempfile
import subprocess
import shutil
import sys

try:
    from Cython.Build import cythonize
    have_cython = True
except Exception:
    have_cython = False

# First, get the compiler that (I think) distutils will use
# - I will need this to add options etc.
compiler = distutils.ccompiler.new_compiler()
distutils.sysconfig.customize_compiler(compiler)


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

    with open(os.devnull, 'w') as fnull:
        exit_code = 1
        for flag in ["-fopenmp", "-openmp"]:
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


openmp_flag = get_openmp_flag()

if openmp_flag is None:
    print(f"You cannot compile MetaWards using a C compiler that doesn't "
          f"support OpenMP. The compiler {compiler.compiler_so[0]} "
          f"does not support OpenMP. See the installation instructions "
          f"on the web for more information and fixes.")
    sys.exit(-1)

cflags = f"-O3 {openmp_flag}"

nbuilders = int(os.getenv("CYTHON_NBUILDERS", 2))

if nbuilders < 1:
    nbuilders = 1

print(f"Number of builders equals {nbuilders}")

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
                                libraries=libraries))

for pyx in iterator_pyx_files:
    _, name = os.path.split(pyx)
    name = name[0:-4]
    module = f"metawards.iterators.{name}"

    extensions.append(Extension(module, [pyx], define_macros=define_macros,
                                libraries=libraries))

for pyx in extractor_pyx_files:
    _, name = os.path.split(pyx)
    name = name[0:-4]
    module = f"metawards.extractors.{name}"

    extensions.append(Extension(module, [pyx], define_macros=define_macros,
                                libraries=libraries))

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
