
from .._network import Network

__all__ = ["mix_none_multi_population"]


def mix_none_multi_population(stage: str, network, **kwargs):
    """This mixer will is equivalent to mix_none, in that
       it will not allow infections to be mixed between
       demographics, and it will normalise by the number
       of individuals in each demographic. This is equivalent
       to each demographic being a completely
       separate and non-interacting population
    """
    if isinstance(network, Network):
        return []
    elif stage == "foi":
        from ._interaction_matrix import InteractionMatrix
        from ._merge_matrix_multi_population \
            import merge_matrix_multi_population

        matrix = InteractionMatrix.diagonal(network.num_demographics())
        network.demographics.interaction_matrix = matrix

        return [merge_matrix_multi_population]
    else:
        from ._mix_default import mix_default
        return mix_default(stage=stage, network=network, **kwargs)
