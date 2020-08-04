===============
Local Lockdowns
===============

In the :doc:`last chapter <07_cutoff>` it was implied that the parameters
for equation 1, and the action of the ``cutoff`` parameter, were global,
and applied to all wards equally. If this was true, then it would make
it difficult for ``metawards`` to model ward-specific behaviour, such
as local lockdowns, or differences in local behaviour.
In reality, ``metawards`` provides support for ward-specific values of
the scaling and cutoff parameters.

Limiting movement at a local level
----------------------------------

Every ward can have its own value
of the cutoff parameter. Movement between two wards is only permitted
if the distance between wards is less than the minimum of the
cutoff distance of each ward, and the value of
:meth:`Parameters.dyn_dist_cutoff <metawards.Parameters.dyn_dist_cutoff>`,
e.g. if this condition is true;

3. :math:`D_\text{ij} < \text{min}( C_i, C_j, C_\text{global} )`

where;

* :math:`D_\text{ij}` is the distance between the centres of wards
  :math:`i` and :math:`j`,
* :math:`C_i` is the local cutoff parameter for ward :math:`i`,
* :math:`C_j` is the local cutoff parameter for ward :math:`j`, and
* :math:`C_\text{global}` is the global cutoff distance set via
  :meth:`Parameters.dyn_dist_cutoff <metawards.Parameters.dyn_dist_cutoff>`

Scaling FOI at a local level
----------------------------

Every ward can have its own value of the FOI scaling parameter. In reality,
equation 1 is actually;

4. :math:`F(w) = S \times S_l(w) \times U(t) \times \sum_s [ C_s \beta_s N_s(w) ]`

where;

* :math:`S_l(w)` is the local scaling factor for ward :math:`w`. This acts
  together with :math:`S`, :math:`U(t)` and :math:`C_s` to give you a lot
  of control over how infectious individuals at each disease stage in each
  ward contribute to the ward's FOI.



