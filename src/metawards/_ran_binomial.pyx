

from ._ran_binomial cimport _construct_gsl_rng, _ran_binomial, \
                            _seed_ran_binomial, _delete_gsl_rng, \
                            _get_gsl_ptr


__all__ = ["ran_binomial", "seed_ran_binomial", "delete_ran_binomial"]


# The plan with this file is to move to an inline cdef that just
# calls the gsl_ran_binomial function directly. Moving away from
# pygsl (and indeed probably gsl) as this is too heavyweight an
# import just to use a random binomial generator. The signature
# of this function in the code will remain though...


def seed_ran_binomial(seed: int = None):
    """Seed and return the random binomial generator. This returns
       the object that you should pass to ran_binomial to generate
       random numbers drawn from a binomial distribution
    """
    if seed is None:
        import random
        seed = random.randint(10000, 99999999)

    print(f"Using random number seed: {seed}")
    rng = _construct_gsl_rng()
    print(f"Constructed {rng}")
    _seed_ran_binomial(rng, seed)
    print(f"Seeded...")

    cdef gsl_rng* r = _get_gsl_ptr(rng)

    # test seeding of the random number generator by drawing and printing
    # 5 random numbers - this is temporary, and only used to
    # facilitate comparison to the original C code
    for i in range(1,6):
        x = _ran_binomial(r, 0.5, 100)
        print(f"random number {i} equals {x}")

    return rng


def ran_binomial(rng, p: float, n: int):
    """Return a random number drawn from the binomial distribution
       [p,n] (see gsl_ran_binomial for documentation)
    """
    cdef gsl_rng *r = _get_gsl_ptr(rng)
    return _ran_binomial(r, p, n)


def delete_ran_binomial(rng):
    """Delete the passed random number generator.

       WARNING: It will not be safe to use this generator after
                you have deleted it!
    """
    _delete_gsl_rng(rng)
