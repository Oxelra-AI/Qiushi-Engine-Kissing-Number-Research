# Supports, sign codes and local replacement

## The mathematical problem

The common starting point is the three-layer construction of
[Edel, Rains and Sloane](https://doi.org/10.37236/1360). A binary sign code
gives a dense layer, a family of eight-element supports gives a middle layer,
and the roots provide a fixed sparse layer. Each support normally carries
128 sign patterns. Once the code distance and support intersections meet
their thresholds, every pair of spherical points is controlled and the count is

$$N=|T|+128|\mathcal B|+2n(n-1).$$

The dense layer, supports and signs are separate mathematical choices.
Changing one support adds 128 points, whereas changing the signs on a small
group of supports can improve the count without increasing the support family.
This distinction leads to two constructive problems: profitable joint exchanges
and larger signed point sets inside a region with a controlled boundary.

## Joint support selection

The early constructions in dimensions 33, 34, 37, 38, and 39 used the ERS layers with improved constant-weight supports and dense sign codes. Joint exchanges measured the union of the old conflicts, allowing several inserted supports to share deletion costs.
The [exchange records](../../constructions/codes/data/exchanges/exchanges.json) retain the complete parent families and the removed and inserted supports, so each final transition can be reconstructed.

For a candidate support $b$, let $F(b)$ be the old supports meeting it in
more than four positions. A mutually compatible candidate set $Y$ has net
gain $|Y|-|\bigcup_{b\in Y}F(b)|$. Thus a useful candidate can have several
conflicts when those conflicts are shared by other selected candidates.
Counting each candidate's cost separately would discard this possibility.
In a finite candidate pool, binary selection and deletion variables express
the same problem exactly; the report gives its constraints and objective.

The terminal exchanges saved for dimensions 33 and 34 replace nine supports
by ten and six by seven, reaching 1803 and 1960. The saved 37-dimensional
exchange replaces 37 by 40 and reaches 2843. These are individual transitions
inside a longer search, while the complete final support lists define the
mathematical objects. The checker reconstructs each union of conflicts and
then checks every pair in the new family.

The next change relaxed the complete parity bundle on a support. Small signed codes could fill a controlled region more efficiently. A matched Hadamard map turned transverse four-subsets into signed weight-eight vectors, giving the 256-point replacement in dimension 35 and the 576-point replacement in dimension 36.

Support search produced the 1,676-word family in dimension 32 and improved the dimension-37 family from 2,843 to 2,845 supports. The latter alone changes the count from 497,640 to 497,896. Applying local replacement to this larger family removes three 128-point bundles and inserts 512 points, producing 498,024.
The dimension-37 input includes its 32 transverse four-subsets and six coordinate pairs; applying all sixteen sign patterns regenerates exactly the stored 512 vectors.

## Why the local boundary can be separated

The free-zone replacement principle appears in
[Takhanov–Yun, §V, Definition 5 and Lemma 4](https://arxiv.org/html/2606.03299v1).
Here it is applied to the weight-eight ERS middle layer, with a paired
Hadamard transfer supplying the replacement vectors.

In dimensions 35 and 36, choose a coordinate region $W$ and remove the
supports wholly contained in it. Every retained support meets $W$ in at
most four positions. Consequently, *any* weight-eight signed vector on
$W$ has safe products with the retained middle layer. The dense and root
layers impose the same universal bounds as before. The search therefore
reduces to finding an internally compatible signed code $Q$ on $W$, with
gain $|Q|-128b$, where $b$ is the number of removed supports.

The regions have eleven and twelve coordinates and contain respectively
one and three old supports. This is more informative than a search through
all signed vectors: it identifies why local changes can be made without
disturbing the rest of the large configuration.

## Constructing the signed code

The Hadamard map on a coordinate pair sends $(\varepsilon,0)$ to
$(\varepsilon,\varepsilon)$ and $(0,\varepsilon)$ to
$(\varepsilon,-\varepsilon)$. A weight-four support meeting each pair
at most once becomes weight eight. Norms and inner products are both
multiplied by two. Pairwise intersections at most two in the source,
together with all sixteen signs per support, therefore imply the required
product bound of four in the image.

Two finite source constructions supply the pairs of records:

| Result | Source family | Matchings examined | Retained supports | Signed points |
|---|---|---:|---:|---:|
| Dimension 35 | 30 blocks of $S(3,4,10)$ | 945 | 16 | 256 |
| Dimension 36 | 51 blocks from two one-factorizations of $K_6$ | 10395 | 36 | 576 |

The first family covers each triple once. The second has 45 blocks formed
from same-colour edges in the two six-coordinate halves and six internal
blocks. It is the twelve-coordinate case of
[Kalbfleisch–Stanton, Theorem 7](https://msp.org/pjm/1968/26-1/pjm-v26-n1-p15-p.pdf),
also used in Takhanov–Yun's Construction 1. Their intersection properties
are proved in the report.
[The constructive search](../../constructions/codes/hadamard/search.py)
rebuilds both families, enumerates the matchings and regenerates exactly
the signed sets in the certificates. The more compact
[generators](../../constructions/codes/hadamard/data/generators.json)
specify the retained supports directly. Thus the package preserves both
the method for finding these objects and their shortest reconstruction.

For dimension 36 there is also a direct description. Use one colour of
the one-factorization as the coordinate pairing in both halves. Each of
the other four colours contributes nine cross blocks, all transverse to
that pairing. Their sixteen sign patterns give $4\cdot9\cdot16=576$
points. The reconstruction program checks that this four-colour
description gives exactly the stored construction.

The eleven-coordinate model has a sharp bound: each signed weight-eight
vector extends to eight full sign strings, while each full sign string
extends at most one compatible vector. Therefore $8|Q|\le2^{11}$ and
$|Q|\le256$. The dimension-35 replacement attains this value. Twelve
coordinates permit intersections of size four within a common sign
string, allowing the larger construction used in dimension 36.

## Combining the mechanisms

Dimensions 32, 33 and 34 use respectively 1676, 1803 and 1960 supports
with the 131072-word Cheng–Sloane dense layer. Dimension 39 uses 3383
supports and ten cosets of a rank-15 kernel. Its 45 cross-coset distance
minima equal ten, giving a 327680-word dense layer. The package preserves
the generators, representatives and shortening relations.

Dimension 37 combines two gains: thirteen more supports than the public
comparison contribute 1664 points, then a 512-point signed set replaces
three 128-point bundles and contributes another 128. Its final count is
498024. The 35- and 36-dimensional gains, 128 and 192, instead come
entirely from local signed replacements. This explains both the common
construction and the different contribution of each dimension.

## Coordinate reconstruction

In the 37-dimensional data, support strings are read from left to right with coordinates starting at one, while integer masks use bit positions. These descriptions agree under $i\mapsto38-i$ when both coordinate systems start at one, or $i\mapsto37-i$ when the right-hand side is a zero-based bit index. This coordinate map identifies the support family and its signed replacement in the same ambient space.
