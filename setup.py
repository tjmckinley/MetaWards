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


extensions = [
    Extension("metawards._test", ["src/metawards/_test.pyx"]),
    Extension("metawards._nodes", ["src/metawards/_nodes.pyx"]),
    Extension("metawards._tolinks", ["src/metawards/_tolinks.pyx"]),
    Extension("metawards._metawards", ["src/metawards/_metawards.pyx"]),
    Extension("metawards._run_model", ["src/metawards/_run_model.pyx"]),
    Extension("metawards._workspace", ["src/metawards/_workspace.pyx"])
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
)
