# Equatorial extension in dimension 38

The construction adds 144 antipodal lines, hence 288 points, to the public
591,612-point cap-and-axis configuration:

\[
6(98280)+1932+2(144)=591900.
\]

`base-data/` fixes the public Golay basis, the class partition, the
fourteen-dimensional directions and the rational axis rotation.
`added-lines.txt` is Qiushi's frozen 144-line extension. The basis is part of
the certificate: a different coordinate realization of the Leech lattice
cannot be substituted without an explicit isometry.

From the repository root:

```sh
python3 tools/verify_dimension38.py --base-data constructions/d38/base-data \
  --lines constructions/d38/added-lines.txt --output ../dimension38-verification.json
```

The verifier reconstructs the minimal shell in the specified basis, checks
the partition, cap directions and rational rotation, verifies the three
Golay congruences placing all 144 new vectors in the same Leech lattice,
then checks every added
line against the complete shell and every other added line. The two relevant
integer-product maxima are both 24. Rotation arithmetic uses Python integers;
its denominator is too large for an unqualified fixed-width multiplication.

`verification.json` is the saved execution record. The calculation uses data
from the public construction and does not run its verifier.
