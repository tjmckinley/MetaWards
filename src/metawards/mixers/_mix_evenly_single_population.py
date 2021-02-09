
from .._network import Network

__all__ = ["mix_evenly_single_population"]


def mix_evenly_single_population(stage: str, network, **kwargs):
    """This mixer will evenly mix all demographics, assuming
       that they are all part of the same population. This
       will give equal results as if all demographics are
       part of the same network
    """
    if isinstance(network, Network):
        return []
    elif stage == "foi":
        from ._interaction_matrix import InteractionMatrix
        from ._merge_matrix_single_population \
            import merge_matrix_single_population

        matrix = InteractionMatrix.ones(network.num_demographics())
        network.demographics.interaction_matrix = matrix

        return [merge_matrix_single_population]
    else:
        from ._mix_default import mix_default
        return mix_default(stage=stage, network=network, **kwargs)
