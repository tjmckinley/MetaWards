#!/bin/env/python3
#cython: linetrace=False
# MUST ALWAYS DISABLE AS WAY TOO SLOW FOR ITERATE

from .._nodes import Nodes
from .._links import Links

from ._get_array_ptr cimport get_double_array_ptr, get_int_array_ptr

__all__ = ["scale_node_susceptibles", "scale_link_susceptibles"]


def scale_node_susceptibles(nodes: Nodes, ratio: any = None,
                            work_ratio: any = None, play_ratio: any = None):
    """Scale the number of susceptibles in the passed Nodes
        by the passed scale ratios. These can be values, e.g.
        ratio = 2.0 will scale the total number of susceptibles
        in each ward by 2.0. They can also be lists of values,
        where ward[i] will be scaled by ratio[i]. They can also
        be dictionaries, e.g. ward[i] scaled by ratio[i]

        Parameters
        ----------
        nodes: Nodes
            The nodes whose susceptible population will be scaled
        ratio: None, float, list or dict
            The amount by which to scale the total population of
            susceptibles - evenly scales the work and play populations
        work_ratio: None, float, list or dict
            Scale only the work population of susceptibles
        play_ratio: None, float, list or dict
            Scale only the play population of susceptibles

        Returns
        -------
        None
    """

    if ratio is not None:
        work_ratio = ratio
        play_ratio = ratio

    if play_ratio is None:
        return

    if nodes is None or len(nodes) == 0:
        return

    try:
        play_ratio = float(play_ratio)
    except Exception:
        pass

    cdef double * nodes_play_suscept = get_double_array_ptr(
                                                nodes.play_suscept)
    cdef double * nodes_save_play_suscept = get_double_array_ptr(
                                                nodes.save_play_suscept)

    cdef int i = 0
    cdef int nnodes_plus_one = len(nodes)   # this will already
                                            # be the 1-indexed size

    cdef double v = 0.0

    if isinstance(play_ratio, float):
        if play_ratio == 1.0:
            return

        # scale all equally
        v = play_ratio

        with nogil:
            for i in range(1, nnodes_plus_one):
                nodes_play_suscept[i] *= v
                nodes_save_play_suscept[i] *= v

    elif isinstance(play_ratio, dict):
        # scale only the specified nodes
        for key, value in play_ratio.items():
            v = value
            nodes_play_suscept[key] *= v
            nodes_save_play_suscept[key] *= v

    elif isinstance(play_ratio, list):
        if len(play_ratio) != len(nodes) - 1:
            raise ValueError(
                f"The list of play_ratio scale factors ({len(play_ratio)}) "
                f"must equal the number of nodes ({len(nodes)-1})")

        for i in range(1, nnodes_plus_one):
            v = play_ratio[i]
            nodes_play_suscept[i] *= v
            nodes_save_play_suscept[i] *= v

    else:
        raise NotImplementedError(
                f"Cannot scale the nodes by a {play_ratio.__class__}")


def scale_link_susceptibles(links: Links, ratio: any):
    """Scale the number of susceptibles in the passed Links
        by the passed scale ratio. This can be a value, e.g.
        ratio = 2.0 will scale the total number of susceptibles
        by 2.0. This can also be lists of values,
        where ward[i] will be scaled by ratio[i]. They can also
        be dictionaries, e.g. ward[i] scaled by ratio[i]

        Parameters
        ----------
        ratio: None, float, list or dict
            The amount by which to scale the total population of
            susceptibles - evenly scales the work and play populations

        Returns
        -------
        None
    """

    if ratio is None:
        return

    if links is None or len(links) == 0:
        return

    try:
        ratio = float(ratio)
    except Exception:
        pass

    cdef double * links_weight = get_double_array_ptr(links.weight)
    cdef double * links_suscept = get_double_array_ptr(links.suscept)
    cdef int * links_ifrom = get_int_array_ptr(links.ifrom)

    cdef int i = 0
    cdef int nlinks_plus_one = len(links)  # already 1-indexed size
    cdef int ifrom = 0
    cdef double v = 0.0

    if isinstance(ratio, float):
        if ratio == 1.0:
            return

        # scale all equally
        v = ratio

        with nogil:
            for i in range(1, nlinks_plus_one):
                links_weight[i] *= v
                links_suscept[i] *= v

    elif isinstance(ratio, dict):
        # scale only links originating from specific nodes
        for i in range(1, nlinks_plus_one):
            ifrom = links_ifrom[i]

            v = ratio.get(ifrom, 1.0)

            if v != 1.0:
                links_weight[i] *= v
                links_suscept[i] *= v

    elif isinstance(ratio, list):
        # scale the links originating from the specified nodes
        # (the size of this list has already been checked in
        # the nodes equivalent of this function)
        for i in range(1, nlinks_plus_one):
            ifrom = links_ifrom[i]

            v = ratio[ifrom]

            if v != 1.0:
                links_weight[i] *= v
                links_suscept[i] *= v
