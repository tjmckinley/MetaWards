
from .._network import Network

__all__ = ["mix_none_single_population"]


def mix_none_single_population(stage: str, network, **kwargs):
    """This mixer will mix demographics assuming no
       infection between demographics, but assuming
       that they are all part of the same population,
       and so normalising by the total number of individuals
       across all demographics
    """
    if isinstance(network, Network):
        return []
    elif stage == "foi":
        from ._interaction_matrix import InteractionMatrix
        from ._merge_matrix_single_population \
            import merge_matrix_single_population

        matrix = InteractionMatrix.diagonal(network.num_demographics())
        network.demographics.interaction_matrix = matrix

        return [merge_matrix_single_population]
    else:
        from ._mix_default import mix_default
        return mix_default(stage=stage, network=network, **kwargs)
