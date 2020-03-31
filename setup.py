# Package setup copied from
# https://github.com/FedericoStra/cython-package-example
# Thanks - this was really helpful :-)

import os
from setuptools import setup, find_packages, Extension
from Cython.Build import cythonize

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
    Extension("metawards._run_model", ["src/metawards/_run_model.pyx"]),
    Extension("metawards._workspace", ["src/metawards/_workspace.pyx"]),
    Extension("metawards._build_wards_network", ["src/metawards/_build_wards_network.pyx"]),
    Extension("metawards._add_wards_network_distance", ["src/metawards/_add_wards_network_distance.pyx"]),
    Extension("metawards._get_min_max_distances", ["src/metawards/_get_min_max_distances.pyx"]),
    Extension("metawards._reset_everything", ["src/metawards/_reset_everything.pyx"]),
    Extension("metawards._rescale_matrix", ["src/metawards/_rescale_matrix.pyx"]),
    Extension("metawards._recalculate_denominators", ["src/metawards/_recalculate_denominators.pyx"]),
    Extension("metawards._move_population", ["src/metawards/_move_population.pyx"]),
    Extension("metawards._fill_in_gaps", ["src/metawards/_fill_in_gaps.pyx"]),
    Extension("metawards._build_play_matrix", ["src/metawards/_build_play_matrix.pyx"]),
]

CYTHONIZE = bool(int(os.getenv("CYTHONIZE", 0)))

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
