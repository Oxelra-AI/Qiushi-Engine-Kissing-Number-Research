# How the constructions were discovered

[中文](README.zh-CN.md) · [Results](results.md) · [Reports](../reports/README.md)

A successful construction does not reveal the route to it. These accounts
follow Qiushi Engine's autonomous mathematical investigation: how a problem
was represented, which obstacles the calculations exposed, what choices
opened a more productive search, and how the resulting objects led to proofs.

## Ten dimensional accounts

The accounts preserve intermediate constructions, concrete search observations
and the mathematical reasons for changing a method. Saved support exchanges,
design generators, lattice vectors and rational identities connect the
narrative to objects that can be reconstructed.

<!-- BEGIN DIMENSION_ACCOUNTS -->
| Dimension | Research account | Lower bound |
|---:|---|---:|
| 32 | [Joint replacement grows a support code](dimensions/32.md) | 347,584 |
| 33 | [Ten new supports share nine old blockers](dimensions/33.md) | 363,968 |
| 34 | [Five-subset constraints resolve a large candidate pool](dimensions/34.md) | 384,196 |
| 35 | [A transferred design attains local capacity](dimensions/35.md) | 409,676 |
| 36 | [Four colours yield a 576-point replacement](dimensions/36.md) | 484,760 |
| 37 | [A larger support code admits a tailored signed patch](dimensions/37.md) | 498,024 |
| 38 | [The next lattice shell fills an unoccupied equator](dimensions/38.md) | 591,900 |
| 39 | [Support growth retains the dense sign layer](dimensions/39.md) | 763,668 |
| 43 | [A parent section reveals a better subsection](dimensions/43.md) | 2,553,792 |
| 45 | [A small fibre controls a large configuration](dimensions/45.md) | 7,380,090 |
<!-- END DIMENSION_ACCOUNTS -->

## Connections across dimensions

**Shared conflicts change the value of a candidate.** In dimensions 32, 33,
34 and 39, a support need not be admissible on its own to be useful. Joint
choice prices the union of old conflicts. The final 33-dimensional exchange
has twenty individually counted conflicts but only nine old supports to
remove. Five-subset packing constraints make the candidates' mutual
compatibility explicit, as the 34-dimensional search demonstrates.

**A controlled boundary makes a smaller problem possible.** The signed
searches in dimensions 35 and 36 exposed coordinate regions where the
surrounding configuration imposes a uniform intersection bound. A Hadamard
map then brought weight-four designs into the weight-eight problem.
Dimension 35 attains its eleven-coordinate capacity; dimension 36 has a
direct four-colour construction. Dimension 37 requires a different selection
because only part of its twelve-coordinate region is free of outside conflicts.

**Changing the ambient construction can reveal unused space.** The
38-dimensional research moved from ERS supports to a larger Leech lifting.
Its unoccupied equator admits vectors from the next lattice shell. A minimum-norm
argument makes all cross-shell products safe, leaving a smaller selection
problem among the new directions themselves.

**A large count can be controlled by the right small object.** In dimension
43, parent-section moments determine the orthogonal shell of a selected
subsection. In dimension 45, the moments instead give an inequality with a
positive coefficient on a searchable fibre. The first route extracts a
count from an embedding; the second turns explicit witnesses into a lower
bound and common-neighbour graphs into a discovery tool.

These connections guided different choices rather than prescribing one
search for every dimension. A support code, a local signed set, a shell
direction and a lattice embedding expose different ways to enlarge a
kissing configuration.

## Shared derivations and exact objects

The dimensional accounts explain the individual investigations. The shared
accounts below develop the mathematical framework used by related dimensions.
The [reports](../reports/README.md) provide full geometric arguments, and
the [reproduction guide](../reproducibility/README.md) gives the execution paths.

<!-- BEGIN RESEARCH_FAMILIES -->
| Dimensions | Shared mathematical development | Data and programs |
|---|---|---|
| 32–37, 39 | [Supports and signed replacements](trajectory/codes.md) | [Supports and signed replacements](../constructions/codes/) |
| 38 | [Equatorial completion](trajectory/equatorial.md) | [Equatorial completion](../constructions/d38/) |
| 43, 45 | [Lattice sections and moments](trajectory/sections.md) | [Lattice sections and moments](../constructions/sections/) |
<!-- END RESEARCH_FAMILIES -->

<!-- BEGIN ADDITIONAL_HISTORY -->

<!-- END ADDITIONAL_HISTORY -->

[Mathematical sources](provenance.md) · [Research livestream](livestream.md)
