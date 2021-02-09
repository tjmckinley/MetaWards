
from .._network import Network

__all__ = ["mix_evenly_multi_population"]


def mix_evenly_multi_population(stage: str, network, **kwargs):
    """This mixer will evenly mix all demographics using
       a matrix of [1] using merge_matrix_multi_population.
       Each population is separate, and will mix with a
       probability based on the number of individuals
       in each demographic
    """
    if isinstance(network, Network):
        return []
    elif stage == "foi":
        from ._interaction_matrix import InteractionMatrix
        from ._merge_matrix_multi_population \
            import merge_matrix_multi_population

        matrix = InteractionMatrix.ones(network.num_demographics())
        network.demographics.interaction_matrix = matrix

        return [merge_matrix_multi_population]
    else:
        from ._mix_default import mix_default
        return mix_default(stage=stage, network=network, **kwargs)
