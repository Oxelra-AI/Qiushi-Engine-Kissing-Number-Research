# Lattice sections, design moments and finite witnesses

An extremal even unimodular lattice of rank 48 has 52,416,000 minimal
vectors of squared norm six, forming an 11-design. Integrality and
minimum-norm bounds give a finite domain of projection signatures;
design moments give exact equations for their multiplicities.
Dimension 43 determines a perpendicular-shell count. Dimension 45
expresses a projected count through one fibre, then counts that fibre
by an anchor graph.

## Dimension 43: the embedding determines the count

The successful $D_5$ lies inside a specified $\sqrt3E_8$ in $P_{48n}$.
Its abstract Gram type and determinant alone do not determine how
many ambient minimal vectors are perpendicular to it.

A projection onto the parent has the form $\lambda/\sqrt3$ with
$\lambda\in E_8$. Apart from the 240 singleton exceptions $\lambda=3r$,
the minimum gives $|\lambda\cdot r|\le3$ for every root and
$\|\lambda\|^2\le18$. The complete domain has 26,641 signatures.
Its five nonexceptional norm orbits have Weyl-averaged multiplicities

$$1092000,\quad116235,\quad9180,\quad495,\quad63/4.$$

The $D_5$ orthogonal space meets these orbits in $1,12,6,24,0$
signatures and contains twelve exceptions, giving the average

$$1092000+12(116235)+6(9180)+24(495)+12=2553792.$$

For the specified child, the target-preserving subgroup
$\langle W(D_5),W(A_3),-I\rangle$ gives 43 orbits. Its moment system
$Av=b$ and target $c^Tv$ have a rational certificate

$$A^Tw=c,\qquad w^Tb=2553792.$$

Thus the count is exact even without determining individual fibres.
The group preserves the domain, moments and target; it need not act
on the ambient lattice. The result holds in every extremal even
unimodular rank-48 lattice containing the parent, for this child and
its Weyl conjugates. The [matrix checker](../../constructions/sections/d43/verify_matrix.py)
regenerates the rational identities. The full domain is essential:
orthogonality belongs in the target, not in prior deletion of columns.

The same domain determines the eight fixed coordinate cuts
$U_k=\iota(\sqrt3\operatorname{span}\{e_1,\ldots,e_k\})$.
With $m=8-k$, their perpendicular-shell counts are

$$1092000+18360m+464944\binom m2+11880\binom m3
+146880\binom m4+2520\binom m5+31680\binom m6.$$

Target-preserving orbit systems have full column rank, so their
actual orbit masses equal the Weyl-averaged masses. The
[family checker](../../constructions/sections/d43/verify_coordinate_family.py)
verifies the rank minors, moments and Weyl correspondence with the
specified $D_5$. This counts the eight fixed cuts and their conjugates,
not arbitrary sections or optimal cuts; $U_1$ is an axis, not a
$D_1$ root system.

## Dimension 45: from a lower certificate to an exact identity

For a section with Gram $H=8I_3-2J_3$, let
$f(y)=|\{x\in X:(x\cdot t_1,x\cdot t_2,x\cdot t_3)=y\}|$.
The original complete domain has 239 signatures, including eight
singleton exceptions. Removing the exceptions and pairing antipodes
leaves 116 variables in 161 moment equations. A rational multiplier gives

$$f(e_1)+f(e_2)+f(e_3)\ge7377408+9f(-2,-2,3).$$

The section also contains norm-eight vectors $t_i+t_j$. The minimum
forces $|y_i+y_j|\le4$, excluding 30 signatures and leaving 101 ordinary
antipodal orbits. Every positive slack term in the original certificate
lies on an excluded orbit. The inequality therefore sharpens to

$$f(e_1)+f(e_2)+f(e_3)=7377408+9f(-2,-2,3).$$

The [statistics checker](../../constructions/sections/d45/verify_statistics.py)
reconstructs both domains and checks this identity. It applies to every
extremal even unimodular rank-48 lattice containing the specified Gram,
without requiring a primitive section.

## The anchor graph counts the complete fibre

For $p^2=8$, put $A_p=\{x\in X:x\cdot p=4\}$.
The filter $P(t)=t^2(t^2-1)(t^2-4)(t^2-9)$ has shell sum 90961920,
while $P(4)=20160$ and $|x\cdot p|\le4$. Antipodality gives
$|A_p|=2256$. Thus 2256 distinct certified endpoints form a complete
parent set. Pairing $x$ with $p-x$ gives 1128 vertices; products one
or three define adjacency independently of the chosen endpoints.
Filtered degree-ten moments make every such graph 368-regular.

For nonadjacent vertices represented by $r,s$, the section
$(-s,s-p,p-r)$ has Gram $H$. Each vertex of
$N(\bar r)\setminus N(\bar s)$ has a unique endpoint $a$ with
$r\cdot a=3$, and $w=p-a$ has signature $(-2,-2,3)$.
Conversely that signature forces $p\cdot w=4$, $r\cdot w=1$ and
$s\cdot w=2$, recovering the endpoint. Hence the entire fibre has
size $368-c$, and the projected count is $7380720-9c$, where
$c=|N(\bar r)\cap N(\bar s)|$.

Choosing one endpoint per pair and centring at $p/2$ gives a signed
matrix $S$ with

$$S^2=88S+368I,\qquad
\operatorname{Spec}(S)=\{92^{(47)},(-4)^{(1081)}\}.$$

The signed common-neighbour identity makes all codegrees even, hence
all these projected counts divisible by 18. This is a signed spectrum,
not a two-eigenvalue claim for the unsigned graph.

The selected QR-neighbour anchor has numerator shape $(3^6,1^{42})$
at scale $1/\sqrt{12}$. Its unique minimum-codegree pair has $c=70$,
so the complete fibre has 298 points and the projected configuration
has exactly $7377408+9(298)=7380090$ points. This is optimal for that
fixed anchor and Gram, not over other anchors, lattices or Grams.
The earlier Pless-lattice route supplied 292 witnesses and the bound
7380036.

Projection of the three fibres leaves squared norm $23/4$ and products
at most $23/8$, so normalization gives a kissing configuration.
The [ambient reconstruction](../../constructions/sections/qr/verify.py),
[parent checker](../../constructions/sections/d45/verify_parent.py) and
[moment/projection checker](../../constructions/sections/d45/verify.py)
connect the specified lattice, complete fibre and lower bound.
