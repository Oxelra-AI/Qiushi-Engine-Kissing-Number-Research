# Complete point configurations

These files contain complete configurations, not just seeds or witness subsets.
The [coordinate release](https://github.com/Oxelra-AI/Qiushi-Engine-Kissing-Number-Research/releases/tag/configuration-vectors-2026-10-12)
provides the additional datasets requested for independent verification.
The [43D and 45D guide](sections/VECTORS.md) links the earlier complete exports.

## Dimensions 32--39

Each row is an ordinary integer Cartesian direction. Normalize **each row by
its own Euclidean norm**. The 39D sign layer and the rotated axes in 38D have
different norms from the other points in their configurations.

| Dimension | Rows | Coordinate columns | Squared norms | CSV | Binary |
| ---: | ---: | ---: | --- | --- | --- |
| 32 | 347,584 | 32 | 32 | [CSV](https://github.com/Oxelra-AI/Qiushi-Engine-Kissing-Number-Research/releases/download/configuration-vectors-2026-10-12/configuration32.csv.gz) | [int8](https://github.com/Oxelra-AI/Qiushi-Engine-Kissing-Number-Research/releases/download/configuration-vectors-2026-10-12/configuration32.i8.gz) |
| 33 | 363,968 | 33 | 32 | [CSV](https://github.com/Oxelra-AI/Qiushi-Engine-Kissing-Number-Research/releases/download/configuration-vectors-2026-10-12/configuration33.csv.gz) | [int8](https://github.com/Oxelra-AI/Qiushi-Engine-Kissing-Number-Research/releases/download/configuration-vectors-2026-10-12/configuration33.i8.gz) |
| 34 | 384,196 | 34 | 32 | [CSV](https://github.com/Oxelra-AI/Qiushi-Engine-Kissing-Number-Research/releases/download/configuration-vectors-2026-10-12/configuration34.csv.gz) | [int8](https://github.com/Oxelra-AI/Qiushi-Engine-Kissing-Number-Research/releases/download/configuration-vectors-2026-10-12/configuration34.i8.gz) |
| 35 | 409,676 | 35 | 32 | [CSV](https://github.com/Oxelra-AI/Qiushi-Engine-Kissing-Number-Research/releases/download/configuration-vectors-2026-10-12/configuration35.csv.gz) | [int8](https://github.com/Oxelra-AI/Qiushi-Engine-Kissing-Number-Research/releases/download/configuration-vectors-2026-10-12/configuration35.i8.gz) |
| 36 | 484,760 | 36 | 32 | [CSV](https://github.com/Oxelra-AI/Qiushi-Engine-Kissing-Number-Research/releases/download/configuration-vectors-2026-10-12/configuration36.csv.gz) | [int8](https://github.com/Oxelra-AI/Qiushi-Engine-Kissing-Number-Research/releases/download/configuration-vectors-2026-10-12/configuration36.i8.gz) |
| 37 | 498,024 | 37 | 32 | [CSV](https://github.com/Oxelra-AI/Qiushi-Engine-Kissing-Number-Research/releases/download/configuration-vectors-2026-10-12/configuration37.csv.gz) | [int8](https://github.com/Oxelra-AI/Qiushi-Engine-Kissing-Number-Research/releases/download/configuration-vectors-2026-10-12/configuration37.i8.gz) |
| 38 | 591,900 | 52 (rank 38) | 48; $16D^2$ on axes | [CSV](https://github.com/Oxelra-AI/Qiushi-Engine-Kissing-Number-Research/releases/download/configuration-vectors-2026-10-12/configuration38.csv.gz) | [int64](https://github.com/Oxelra-AI/Qiushi-Engine-Kissing-Number-Research/releases/download/configuration-vectors-2026-10-12/configuration38.i64.gz) |
| 39 | 763,668 | 39 | 32 or 39 | [CSV](https://github.com/Oxelra-AI/Qiushi-Engine-Kissing-Number-Research/releases/download/configuration-vectors-2026-10-12/configuration39.csv.gz) | [int8](https://github.com/Oxelra-AI/Qiushi-Engine-Kissing-Number-Research/releases/download/configuration-vectors-2026-10-12/configuration39.i8.gz) |

All files are gzip-compressed, without a header. CSV and binary contain the
same rows in the same order. Binary is row-major signed int8, except for 38D,
which uses little-endian signed int64. Each `configurationN.json` release asset
records the complete row count, normalization, layers and export checks.
The checks establish exact source membership, norms, distinctness and complete
counts; they are not a new full pairwise verification.

For example:

```python
import gzip
import numpy as np

with gzip.open("configuration39.i8.gz", "rb") as stream:
    directions = np.frombuffer(stream.read(), dtype=np.int8).reshape(-1, 39)
```

For integer directions $a,b$, put $p=a\cdot b$, $A=a\cdot a$, $B=b\cdot b$.
The exact kissing condition is

$$p\leq0\quad\text{or}\quad4p^2\leq AB.$$

For equal norms it reduces to $2p\leq A$. Convert entries to Python integers
or another sufficiently wide integer type before forming these expressions;
in particular, **38D axis products do not fit in int64 or exact float32**.

### The 38D integer embedding

Let $D=157057717643854109$ and let $R/D$ be the released rational tail rotation.
The orthogonal embedding

$$ (x,y)\longmapsto(x,y/\sqrt2,y/\sqrt2) $$

maps the original 38-dimensional space into a 38-dimensional subspace of
$\mathbb R^{52}$. After positive rescaling of each row, the complete points are:

- caps: $(\pm u,v,v)$, squared norm 48;
- rotated axes: $(0,dR^{\mathsf T},dR^{\mathsf T})$, squared norm $16D^2$;
- added equatorial points: $(\pm s,0,0)$, squared norm 48.

The axes are divided by $4D$ for unit normalization; the other rows are divided
by $\sqrt{48}$. This retains exactly the angles of the published construction.
The last two 14-coordinate blocks coincide. The release also supplies an exact
rank-38 check with nonzero integer minors.

### Reproduce these exports

From the repository root, using Python with NumPy:

```sh
python constructions/codes/export_vectors.py --dimension 39 --output-dir vectors39 --csv
python constructions/d38/export_vectors.py --output-dir vectors38
```

Replace 39 by any dimension from 32 through 37 for the other code constructions.
The 38D exporter uses its own lattice construction, not the historical ERS
intermediate construction.
