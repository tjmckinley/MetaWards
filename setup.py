# Package setup copied from
# https://github.com/FedericoStra/cython-package-example
# Thanks - this was really helpful :-)

import os
import versioneer
from setuptools import setup, Extension

try:
    from Cython.Build import cythonize
    have_cython = True
except Exception:
    have_cython = False

cflags = '-O3 -march=native -Wall -fopenmp'

random_sources = ["src/metawards/ran_binomial/mt19937.c",
                  "src/metawards/ran_binomial/distributions.c"]


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

# Currently each file compiles to its own module. Ideally I'd like
# them all to compile into a single module library, but this doesn't
# work (get the error "ImportError: dynamic module does not define
# init function" and the answers on stackoverflow didn't work.
# If anyone can help please do :-)


extensions = [
    Extension("metawards._nodes", ["src/metawards/_nodes.pyx"]),
    Extension("metawards._links", ["src/metawards/_links.pyx"]),
    Extension("metawards.utils._run_model",
              ["src/metawards/utils/_run_model.pyx"]),
    Extension("metawards.utils._workspace",
              ["src/metawards/utils/_workspace.pyx"]),
    Extension("metawards.utils._build_wards_network",
              ["src/metawards/utils/_build_wards_network.pyx"]),
    Extension("metawards.utils._add_wards_network_distance",
              ["src/metawards/utils/_add_wards_network_distance.pyx"]),
    Extension("metawards.utils._get_min_max_distances",
              ["src/metawards/utils/_get_min_max_distances.pyx"]),
    Extension("metawards.utils._reset_everything",
              ["src/metawards/utils/_reset_everything.pyx"]),
    Extension("metawards.utils._rescale_matrix",
              ["src/metawards/utils/_rescale_matrix.pyx"]),
    Extension("metawards.utils._recalculate_denominators",
              ["src/metawards/utils/_recalculate_denominators.pyx"]),
    Extension("metawards.utils._move_population",
              ["src/metawards/utils/_move_population.pyx"]),
    Extension("metawards.utils._fill_in_gaps",
              ["src/metawards/utils/_fill_in_gaps.pyx"]),
    Extension("metawards.utils._build_play_matrix",
              ["src/metawards/utils/_build_play_matrix.pyx"]),
    Extension("metawards.utils._array", ["src/metawards/utils/_array.pyx"]),
    Extension("metawards.utils._iterate",
              ["src/metawards/utils/_iterate.pyx"]+random_sources),
    Extension("metawards.utils._iterate_weekend",
              ["src/metawards/utils/_iterate_weekend.pyx"]),
    Extension("metawards.utils._extract_data",
              ["src/metawards/utils/_extract_data.pyx"]),
    Extension("metawards.utils._extract_data_for_graphics",
              ["src/metawards/utils/_extract_data_for_graphics.pyx"]),
    Extension("metawards.utils._import_infection",
              ["src/metawards/utils/_import_infection.pyx"]+random_sources),
    Extension("metawards.utils._ran_binomial",
              ["src/metawards/utils/_ran_binomial.pyx"]+random_sources),
    Extension("metawards.utils._assert_sane_network",
              ["src/metawards/utils/_assert_sane_network.pyx"]),
    Extension("metawards.utils._parallel",
              ["src/metawards/utils/_parallel.pyx"]),
]

# disable bounds checking and wraparound globally as the code already
# checks for this and doesn't use negative indexing. It can be
# turned on as needed in the modules
for e in extensions:
    e.cython_directives = {"boundscheck": False, "wraparound": False}

CYTHONIZE = bool(int(os.getenv("CYTHONIZE", 0)))

if not have_cython:
    CYTHONIZE = False

os.environ['CFLAGS'] = cflags

if CYTHONIZE:
    compiler_directives = {"language_level": 3, "embedsignature": True}
    extensions = cythonize(extensions, compiler_directives=compiler_directives)
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
    extras_require={
        "dev": dev_requires,
        "docs": ["sphinx", "sphinx-rtd-theme"]
    },
    entry_points={
        "console_scripts": [
           "metawards = metawards.app.run:cli"
        ]
    }
)
