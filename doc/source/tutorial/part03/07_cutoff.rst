====================
Restricting movement
====================

The flexibility of ``metawards`` means that there are multiple different
ways you could choose to model a lockdown.

To understand how, we must look at how ``metawards`` calculates the
*force of infection* (FOI) of each ward. The FOI of a ward is used
to calculate the infection rate, which determines the rate by which
individuals in a ward become infected.

Force of infection
-------------------

The *force of infection* (FOI) is calculated for each ward individually,
using the equation;

:math:`\text{FOI}(\text{ward}) = \text{scale_uv} * \text{UV}(t) * \sum_\text{stages} [ \text{contrib_foi}_\text{stage} * \beta_\text{stage} * N_\text{stage}(\text{ward}) ]`

where;

* :math:`\text{FOI}(\text{ward})` is the FOI calculated for a specific ward
* :math:`\text{scale_uv}` is a constant scaling parameter, set via :meth:`Population.scale_uv <metawards.Population.scale_uv>`
* :math:`\text{UV}(t)` is a seasonal scaling parameter calculated for the specified day :math:`t`
* :math:`\sum_\text{stages}` is the sum over all disease stages
* :math:`\text{contrib_foi}_\text{stage}` is the disease parameter :math:`\text{contrib_foi}` for the specified :math:`\text{stage}`
* :math:`\beta_\text{stage}` is the disease parameter :math:`\beta` for the specified :math:`\text{stage}`, and
* :math:`N_\text{stage}(\text{ward})` is the number of infected individuals at the specified disease stage in this specific ward

