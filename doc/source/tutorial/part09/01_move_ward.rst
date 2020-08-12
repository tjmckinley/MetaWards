========================
Creating intricate moves
========================

Up to now you have used the top-level go functions (e.g.
:func:`~metawards.movers.go_isolate`, :func:`~metawards.movers.go_stage`
and :func:`~metawards.movers.go_to`) to perform more complex
moves of individuals between demographics and/or disease stages.

These go functions are built on top of lower-level function
:func:`~metawards.movers.go_ward`. This is a generic go function that
can move individuals between any and all combinations of
demographics, disease stages, wards (for players), ward-links
(for workers) and :class:`~metawards.PersonType` (worker or player).

It uses :class:`~metawards.movers.MoveGenerator` to define the move.
This is a generator that generates all of the moves to perform
based on the arguments to its constructor.

