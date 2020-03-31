# MetaWards

This is a Python port of the [MetaWards](https://github.com/ldanon/MetaWards)
package originally written by Leon Danon. This is currently a work in progress
and is not intended yet for production use. The port is kept in sync with
the original C code, with checks in place to ensure that the two codes
give identical results. This improves the robustness of both codes, as
it minimises the footprint to bugs that can evade both C and Python.

The aim of this port is to make it easier for others to contribute to the
program, to improve robustness by adding in unit and integration test,
and to also open up scope for further optimisation and parallelisation.

The package makes heavy use of [cython](https://cython.org) which is used
to compile bottleneck parts of the code to C. This enables this Python port
to run at approximately the same speed as the original C program.

There is still a lot of work to do, so please bear with us as we work to
make this package into a well-documented, easily usable application that
will help you to reproduce the model runs and analysis. Apologies in
advance if we are slow to respond to any issues - we are working at high
speed to get everything ready and aim to have most things completed by
the beginning of Easter. We appreciate people want to help. At this stage
adding more people won't speed things up, and we now have a team of
professional [Research Software Engineers](https://www.bristol.ac.uk/acrc/research-software-engineering/) working on this package.

## Data

The data and input parameters needed to use this package are stored in
the [MetaWardsData](https://github.com/chryswoods/MetaWardsData)
repository. Please make sure that you clone this repository to your
computer and supply the full path to that repository to the program
when it runs. There are three ways to do this;

1. Set the `METAWARDSDATA` environment variable to point to this directory,
   e.g. `export METAWARDSDATA=$HOME/GitHub/MetaWards`

2. Pass the `repository` variable to the input data classes
   [Disease](https://github.com/chryswoods/MetaWards/blob/devel/src/metawards/_disease.py), [InputFiles](https://github.com/chryswoods/MetaWards/blob/devel/src/metawards/_inputfiles.py) and [Parameters](https://github.com/chryswoods/MetaWards/blob/devel/src/metawards/_parameters.py)

3. Or simply make sure you clone into the directory `$HOME/GitHub/MetaWardsData`
   as this is the default path.

## References

These are the references behind the
[original C code](https://github.com/ldanon/MetaWards) are;

- _"Individual identity and movement networks for disease metapopulations"_
Matt J. Keeling, Leon Danon, Matthew C. Vernon, Thomas A. House
Proceedings of the National Academy of Sciences May 2010, 107 (19) 8866-8870; DOI: [10.1073/pnas.1000416107](https://doi.org/10.1073/pnas.1000416107)

- _"A spatial model of CoVID-19 transmission in England and Wales: early spread and peak timing"_
Leon Danon, Ellen Brooks-Pollock, Mick Bailey, Matt J Keeling
medRxiv 2020.02.12.20022566; doi: [10.1101/2020.02.12.20022566](https://doi.org/10.1101/2020.02.12.20022566)

## Dependancies

The code requires Python 3.7 or above and depends on
[pygsl](http://pygsl.sourceforge.net) and [cython](https://cython.org).

Only the `gsl_rng.binomial` function is used from GSL, so it is likely
that this requirement will soon be dropped. The link to GSL forces us
to use a GPL3 license for this Python package. Once we have replaced
the binomial function we will re-evaluate the license under which this
code is distributed.

## Installation

You can install the code from source by typing;

```
git clone https://github.com/chryswoods/MetaWards
cd MetaWards
python setup.py install
```

(assuming that `python` is version 3.7 or above)

You can run tests using pytest, e.g.

```
METAWARDSDATA="/path/to/MetaWardsData" pytest tests
```

You can also install via `pip` using

```
pip install metawards
```

## Running

Currently the Python port is under development so the simple front-end
script is not yet ready. At the moment, you can see how to use the software
by duplicating the code in [test_integration.py](https://github.com/chryswoods/MetaWards/blob/devel/tests/test_integration.py).

This test duplicates a run of the MetaWards C program that is bundled
in this repository that was run using;

```
metawards 15324 ncovparams.csv 0 1.0
```

The original C code, command line and expected output are in the
[original](https://github.com/chryswoods/MetaWards/tree/devel/original)
directory that is bundled in this repo.

### Running an ensemble

We will be integrating this Python port with
[https://docs.python.org/3.7/library/multiprocessing.html?highlight=process](multiprocessing) and
[dask](https://dask.org) to enable multiple models and seeds
to be run in parallel over distributed resources. The aim is to have
this parallel code working by the beginning of Easter.
