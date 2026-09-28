# A structured motion in dimension 25

The [25-dimensional account](../dimensions/25.md) develops a motion that
preserves the internal geometry of a 552-point contact layer. A deleted
Leech point and its retained partner have the same transverse component;
their segment supplies the horizontal part of the moving point. Convexity
then controls all unchanged equatorial contacts at once.

The new latitude is fixed by norm preservation and contact with the
additional point. More generally, parameters $(c,d)$ lie on a circle,
and each fixed boundary point imposes one closed half-plane. Feasibility
and minimum nonnegative deletion cost are attained among the circle's
boundary intersections and one reference point: at most $2m+1$ candidates
for $m$ constraints. On each intervening arc every inequality has constant
truth value, and moving to an endpoint cannot destroy a satisfied one.

For the specified inserted point $Q$, at least two cap changes are
necessary in this coordinated-motion family. One cap conflicts with $Q$
independently of the motion; if it were the only change, the retained
caps would force an arc on which a further cap conflicts. The supplied
two repairs attain this minimum. The [obstruction checker](../../constructions/d25/verify_motion_obstructions.py)
certifies the two strict inequalities used in this argument.

The [complete proof](../../constructions/d25/construction.tex),
[integer repairs](../../constructions/d25/repair-points.json) and
[verification programs](../../constructions/d25/) specify the construction.
The [Chinese account](../dimensions/25.zh-CN.md) follows the same argument.
