# Equatorial completion of a lifted Leech shell

The problem is to enlarge a lifted configuration without losing its
efficient reuse of mother-shell directions. The head and tail coordinates
control different parts of each inner product. An empty equator is useful
only if its new directions are compatible with every head already used.

The earlier dimension-38 construction combined 3,077 supports with eleven dense-code cosets and gave 576,892 points. The public 591,612-point Leech construction changed the geometry: all 98,280 minimal lines were carried on cap triples in fourteen tail dimensions. Its original equator was empty.

The new completion uses equatorial directions from the norm-48 shell.
The lattice itself guarantees their compatibility with every lifted
minimal direction. The remaining problem is to choose new lines that
are mutually compatible. A 142-line witness gave 591,896 points,
followed by a 144-line witness giving 591,900.

## Why the second shell provides room

A mixed point has head $u/\sqrt{48}$, where $u$ has squared norm 32,
and a tail of squared length $1/3$. Its head is shorter than a unit
mother-shell point. For a unit equatorial direction $z$, the condition
against $c=u/\sqrt{32}$ is therefore

$$|z\cdot c|\le\sqrt{3/8},$$

not the stricter $1/2$ required for direct insertion into the unit mother
shell. A norm-48 vector $v$ represents $z=v/\sqrt{48}$, and the bound
becomes the integer inequality $|v\cdot u|\le24$. The lifting creates
this additional angular space; selecting a different shell uses it.

In fact, no search through the old shell is needed to establish this bound.
Since the lattice has minimum squared norm 32 and $v\pm u\ne0$,

$$32\le\|v\pm u\|^2=80\pm2v\cdot u,$$

so $|v\cdot u|\le24$ for every minimal vector $u$. Thus the geometric
constraint involving 196,560 old points is automatic once membership in
the same lattice and squared norm 48 are established.

Candidate generation and selection now have separate tasks. Generate
integer vectors of squared norm 48 satisfying the three lattice congruences
in the report, and retain the representative whose first nonzero coordinate
is positive. Two candidate lines conflict exactly when their absolute
product exceeds 24. An independent set in this finite graph supplies two
equatorial points per line; the objective is its cardinality. Joint
replacement can change several selected lines at once, with each newly
selected line paying only for the union of its old neighbours. The final
144-line set is checked by its norms, lattice membership and mutual
products. Direct products against the old shell provide a second check
of the cross-shell lemma, rather than an additional search constraint.

## The complete construction

The mother configuration partitions the 98280 Leech lines into 644 classes.
Each class is paired with a zero-sum triangle in a 1932-point tail code.
Two head signs and three tail labels give six points per line. A rotated
copy of the tail code contributes 1932 pure-tail points. The added equator
is disjoint from both layers and orthogonal to the pure tails. Hence

$$6(98280)+1932+2(144)=591900.$$

The new input is the 144-line equatorial set. The partition, tail geometry
and rational rotation come from the attributed public construction in
[the source record](../provenance.md). The report derives all pair types;
the verifier reconstructs and checks the complete finite base before
checking the new lines. These fixed inputs uniquely specify the complete
591,900-point configuration.

## Coordinate realization and exact checks

The base shell and new lines initially used different Golay conventions. Checking them in the same published basis resolved the discrepancy. The result is determined by the final 144 rows and the two exact product bounds.

This basis alignment is mathematical: an arbitrary relabelling of code
coordinates need not preserve the given class and line arrays. The
certificate fixes one Golay generator and a canonical line ordering.
[The verifier](../../tools/verify_dimension38.py) rebuilds the three shell
types, checks all classes and tail triangles, checks the rational rotation,
and then compares each added line with the entire shell and with every
other added line. The two product maxima are both 24. These checks expose
the exact contacts at the threshold while preserving the simple layered
proof for the full 591900-point configuration.
