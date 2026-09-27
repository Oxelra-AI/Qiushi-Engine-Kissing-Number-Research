# Why the axial addition supplies exactly one point

Keep the two poles, $P=(-2n,0)$, and the moved block
$W=(r+an,b)$ of the 197580-point construction fixed. Here $r\perp n$,
$a=\sqrt3/2+\sqrt2/4$, and $b=(\sqrt6-2)/4>0$.

**Claim.** In the plane spanned by $(n,0)$ and the last coordinate,
the only norm-2 point compatible with these fixed points is the already
present $Q=(\sqrt3n,-1)$.

Write a possible point as $x=(\alpha n,\beta)$.
The poles imply $|\beta|\le1$; $P$ implies $\alpha\ge-1$.
Since $\alpha^2+\beta^2=4$, the negative branch is excluded and
$\alpha=\sqrt{4-\beta^2}$.
Compatibility with any one of the moved points requires

\[
f(\beta):=a\sqrt{4-\beta^2}+b\beta\le2.
\]

But $f''(\beta)=-4a/(4-\beta^2)^{3/2}<0$ on $[-1,1]$,
while $f(-1)=2$ and $f(1)=2+2b$.
Strict concavity gives
$f(\beta)>2+b(\beta+1)>2$ for $-1<\beta<1$.
The endpoint $1$ also fails, leaving only $\beta=-1$ and
$\alpha=\sqrt3$.

Thus this fixed axial plane cannot supply another distinct point.
Further gains must use a nonzero perpendicular component, another compatible
block, or a change of the presently fixed points. The argument imposes no
upper bound on configurations using those additional freedoms.
