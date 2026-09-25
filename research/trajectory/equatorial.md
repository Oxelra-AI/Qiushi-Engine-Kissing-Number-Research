# Equatorial completion of a lifted Leech shell

The problem is to enlarge a lifted configuration without losing its
efficient reuse of mother-shell directions. The head and tail coordinates
control different parts of each inner product. An empty equator is useful
only if its new directions are compatible with every head already used.

The earlier dimension-38 construction combined 3,077 supports with eleven dense-code cosets and gave 576,892 points. The public 591,612-point Leech construction changed the geometry: all 98,280 minimal lines were carried on cap triples in fourteen tail dimensions. Its original equator was empty.

The new completion searched for equatorial directions in the norm-48 shell instead of trying to reuse another minimal line. Products with all norm-32 shell vectors had to be at most 24 in absolute value; the same threshold controlled products between selected new lines. A 142-line witness gave 591,896 points, followed by a 144-line witness giving 591,900.

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

For a finite candidate set, first test this inequality against all 196560
mother-shell vectors, and keep one representative per antipodal line.
Two retained lines conflict exactly when their absolute product exceeds
24. An independent set in this graph supplies two equatorial points per
line. Mother-shell filtering can be reused throughout the subset search,
and every selected line has equal weight in the final objective.

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
checking the new lines. The final object is not dependent on a successful
repetition of the original search.

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
