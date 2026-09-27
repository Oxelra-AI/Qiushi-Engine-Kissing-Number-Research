# Origins of the constructions

The constructions combine lattice liftings, signed codes and exact section counts.
This account identifies the mathematical inputs and the new finite objects.

## Construction families

**Coordinated shell motion.** The 197,580-point construction in dimension 25
starts from Kravatskiy's fixed 197,579-point head data. Qiushi Engine moves
a complete 552-point partner layer, introduces one new point and replaces
two individual caps by normalized integer vectors. Convexity controls the
unchanged equatorial contacts; integer and Arb checks certify the remaining
strict inequalities. The original coordinates and their license are retained
in [the construction directory](../constructions/d25/).

**Leech liftings.** The earlier 25- and 27-dimensional constructions use
496-point blocks and a small tail geometry. The latest 27-dimensional
construction instead retains the public first layer in
[Lindow's contribution](https://github.com/alexlegeartis/KissingNumbers/pull/1)
and improves the compatible second layer. The new finite object is the
311-owner witness, with label-class sizes $(105,103,103)$, replacing the
310-owner choice and giving 201,567 points.

**Supports and signs.** The initial representation attaches all even-parity
sign patterns to each weight-eight support. Replacing conflicting supports
improves the support code. Later work changes the sign sets themselves:
discarding an entire support is sometimes unnecessary, since a smaller
signed subset can coexist with useful points on an intersecting support.
The 35–37-dimensional constructions record the exact deletions and additions
needed for this distinction.
The free-zone replacement principle is developed in
[Takhanov–Yun, §V](https://arxiv.org/html/2606.03299v1).
The 51-block weight-four source in dimension 36 is the twelve-coordinate
case of [Kalbfleisch–Stanton, Theorem 7](https://msp.org/pjm/1968/26-1/pjm-v26-n1-p15-p.pdf).
Qiushi's constructions select transverse supports, apply paired Hadamard
maps and place the resulting signed codes in explicit ERS coordinate regions;
the boundary checks establish net gains of 128, 192 and 128 in dimensions
35, 36 and 37 respectively.

**Equatorial augmentation.** The latest 38-dimensional construction starts
from a public layered configuration with no equatorial points. Its
24-dimensional equatorial subspace admits compatible norm-48 directions.
Searching a compatibility graph produces an antipodal line set; the explicit 144-line
witness gives the additional 288 points. Both layers use the Golay basis
supplied with the base construction, so their cross-products are checked
in a common coordinate system.

**P48p caps.** The earlier high-dimensional family and the new 7,077-line
family share a lifting principle. The new work enlarges the finite head
class and selects its automorphism images jointly. Overlapping lines are
assigned once, so the relevant statistic is the union size, not the sum of
the image sizes. The lifting uses the known minimum and shell size of
$P_{48p}$ and the explicitly supplied class and automorphism matrices.

**Lattice sections and moments.** A section is governed by the geometry of
its embedding, not just by its abstract Gram type. Dimension 43 exploits
this distinction inside an embedded $E_8$. Dimension 45 changes the parent
anchor sector in the QR neighbour, obtains a larger finite witness set, and
converts that set to a lower bound through a rational moment inequality.
The two constructions use design moments to avoid enumerating the full
ambient minimal shell.
The embedded $E_8$ parent is part of the cross-section framework of
[Dorofeev–Sun–Wang, v4](https://arxiv.org/abs/2607.20359v4).
The new $D_5$ count uses its specified embedding and a target-preserving
43-orbit moment system. Historical numerical comparisons cite the earlier
Sun–Wang v3, which explicitly reports the two comparison counts.

**Partial fibres and parity.** The historical 18-dimensional construction
keeps a 5,350-point core, adds 2,048 points from partial fibres and fills
832 compatible holes. Parity characters control which fibre subsets may
coexist; a finite angle palette turns the remaining geometric conditions
into exact compatibility checks. The resulting 8,230-point construction
and its pairwise verification are retained with the later research on
partial fibres.

## Discovery, construction and proof

Search programs propose supports, signed vectors, line families or embedded sections. The
mathematical argument explains why the accepted finite object produces a
kissing configuration. Verification programs check the object and its
required identities. Fixed certificates therefore give short, reproducible
checks of constructions found through much longer searches.

Qiushi Engine autonomously conducted the construction searches, mathematical
analysis and computational verification. Sources for the lattices, codes and
construction principles are cited alongside the results. The
[optical-platform study](https://arxiv.org/abs/2604.27092) describes the
system's autonomous experimental research.

## Data and references

- [results.json](../constructions/catalog/results.json) gives one current lower bound per
  main dimension, a count identity, its contribution and supporting receipts.
- [artifacts.json](../constructions/catalog/artifacts.json) identifies original finite inputs
  and source records by SHA-256 digest.
- [comparison-sources.json](../constructions/catalog/comparison-sources.json) fixes the
  source and date of each external numerical comparison.

Source digests identify the original input files. The repository manifest
identifies the distributed copies, whose explanatory paths have been made
relative to this repository.
