# Lattice sections, design moments and finite witnesses

Both constructions start from a 48-dimensional extremal even unimodular
lattice. Its 52416000 minimal vectors have squared norm six and form a
spherical 11-design. The design property makes low-degree polynomial sums
available without enumerating that shell. Specifying a section gives a
finite set of integral projection signatures, and the unknown numbers of
shell vectors in those fibres satisfy exact rational moment equations.

The two dimensions use this information differently. Dimension 43 asks
for an exact count of a perpendicular shell. Dimension 45 asks for a
lower bound on three fibres that form a kissing configuration after
projection. Both objectives are linear functions of the fibre counts,
so neither requires those counts to be determined individually.

## Dimension 43: choosing an embedded section

The target was a large perpendicular part of an extremal 48-dimensional shell. A $D_5$ Gram matrix and its determinant do not determine that population. The successful construction uses a particular $D_5$ sitting inside an embedded $E_8$ in $P_{48n}$.

The parent root system gives a complete finite projection domain. Weyl averaging provides an explanatory count of 2,553,792, including twelve exceptional roots. A smaller subgroup preserving the specified child compresses the exact moment calculation to 43 orbits. A rational certificate then determines that child's count.

This distinguishes two uses of symmetry. The signature domain has a useful abstract group action; it is unnecessary to assume that each such transformation extends to an automorphism of the ambient lattice. The argument averages the equations and the target statistic.

The mother $E_8$ supplies substantially more information than an isolated
$D_5$. Norm and root-product constraints leave 26641 possible signatures,
including the 240 exceptional embedded roots. Weyl averaging gives five
nonexceptional orbit multiplicities

$$1092000,\quad116235,\quad9180,\quad495,\quad63/4.$$

The $D_5$ orthogonal space meets those orbits in $1,12,6,24,0$
signatures and contains twelve exceptional roots. Its averaged population is

$$1092000+12(116235)+6(9180)+24(495)+12=2553792.$$

To establish the specified embedding's count, the computation retains
the target under a smaller symmetry group. With moment equations $Av=b$
and target $c^Tv$, a rational vector $w$ satisfying $A^Tw=c$ proves
$c^Tv=w^Tb$. This is an exact identity even when the full fibre
distribution is underdetermined. The stored certificate gives
$w^Tb=2553792$.

The discovery calculation used modular linear algebra to select
independent moment rows before constructing a rational certificate.
The public reconstruction instead starts from standard $E_8$ coordinates
and rebuilds the domain, subgroup orbits, moments and target. The
[matrix checker](../../constructions/sections/d43/verify_matrix.py)
then provides a separate short check of the rational identities.

The complete domain is part of the argument. The right side of the
moment system describes the full shell; the perpendicular condition
belongs in the objective, rather than in a prior removal of other
signature columns. This distinction explains why parent-section
information can determine a child count while an incomplete projection
system can suggest unattainable counts.


## Dimension 45: selecting a statistic that can be witnessed

Three section vectors have Gram matrix $H=8I_3-2J_3$. Signatures are
$y=(x\cdot t_1,x\cdot t_2,x\cdot t_3)$, and $f(y)$ denotes their
fibre multiplicity. The complete finite domain has 239 signatures;
after antipodal identification and removal of known exceptions, there
are 116 nonnegative variables and 161 rational moment equations.

The decisive counting expression is

$$f(e_1)+f(e_2)+f(e_3)\ge7377408+9f(-2,-2,3).$$

It changes what must be found. A set of distinct vectors in the last
fibre supplies a lower bound for its multiplicity, and every additional
witness contributes nine points to the projected count. The multiplier
and nonnegative slack are rational and checked against the regenerated
moment system. No numerical optimization is needed to use the final
inequality.

An earlier Pless-lattice route found a fibre containing 292 explicit vectors, giving

$$
7377408+9(292)=7380036.
$$

The later route used a norm-eight anchor $p$ in an odd-coordinate sector of a quadratic-residue neighbour. Its complete 2,256-point parent set forms 1,128 pairs $\{x,p-x\}$ centred at $p/2$. These pairs are the vertices of a graph, reducing searches for different section fibres to common-neighbour computations. The graph has degree 368; the selected nonadjacent pair has 70 common neighbours, giving a 298-vector fibre and the count 7,380,090. The supplied [parent data and checker](../../constructions/sections/d45/verify_parent.py) reconstruct exactly the section and witness set in the final certificate.

## Reusing a complete parent set

For a fixed $p$, the parent set is $A_p=\{x:x^2=6,\ x\cdot p=4\}$.
Since $x\pm p$ have squared norm at least six, the integral product
$x\cdot p$ lies between $-4$ and $4$. The polynomial
$P(t)=t^2(t^2-1)(t^2-4)(t^2-9)$ vanishes at the seven inner values.
Its shell sum, obtained from moments through degree eight, is 90961920.
As $P(4)=20160$ and the shell is antipodal,
$|A_p|=90961920/(2\cdot20160)=2256$. Thus a list of 2256 distinct
valid endpoints is complete, not merely a sample of an unknown parent set.

Pairing $x$ with $p-x$ produces 1128 graph vertices. Products one and
three define adjacency; replacing an endpoint changes its product $t$
to $4-t$, preserving adjacency. For the selected nonadjacent vertices
represented by $r,s$, use the section $(-s,s-p,p-r)$. Each vertex
adjacent to $r$ but not to $s$ has a unique endpoint $a$ with
$r\cdot a=3$; then $w=p-a$ is a norm-six vector of signature
$(-2,-2,3)$. This proves the correspondence behind the count $368-70$.

The anchor search also changed its geometric domain. In integer
numerator coordinates $p=y/\sqrt{12}$, the selected parent has absolute
shape $(3^6,1^{42})$, hence $y^2=96$. It belongs to the odd-coordinate
part of the neighbour. Earlier integral-sector searches and the
$(7,1^{47})$ trial family did not yield this parent. The improvement
therefore combines a new anchor with reuse of the same graph method.

## From witnesses to the full projected configuration

For signatures $e_1,e_2,e_3$, the removed projection has squared norm
$1/4$, and cross-products between different signatures are $1/8$.
The remaining vectors have squared norm $23/4$ and different-point
products at most $23/8$. Their normalized union is therefore a
45-dimensional kissing configuration. The 298 witnesses and moment
inequality give

$$7377408+9(298)=7380090.$$

The graph search supplies 298 explicit witnesses. A parity argument proves that the specific quadratic-residue neighbour has minimum six. The complete 239-signature domain determines a 161-row rational moment system and a dual inequality. Its rational multiplier is supplied for direct checking against the regenerated system. Nonnegative slack bounds the required statistic even when individual fibre sizes remain undetermined.

The [ambient reconstruction](../../constructions/sections/qr/verify.py),
[moment verification](../../constructions/sections/d45/verify.py) and
[parent reconstruction](../../constructions/sections/d45/verify_parent.py)
use the same Gram matrix and recover the same final witness set.
Together they connect the published code-theoretic inputs, the actual
lattice, the search representation and the final lower bound.
