
from .._population import Population

__all__ = ["output_final_report"]


def output_final_report(population: Population) -> None:
    """Call in the "finalise" stage to output the final
       report of the population trajectory to
       'results.csv'
    """
