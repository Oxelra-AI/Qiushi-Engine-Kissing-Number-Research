# Complete Cartesian directions in dimensions 49–55

[Download the complete files](../VECTORS.md#dimensions-49--55).

The complete files contain ordinary integer Cartesian coordinates, including
the retained equator, all cap points and all pure tails. **Normalize each row
by its own Euclidean length.** Unlike the 43D/45D section files, these files
have three squared norms: 144 for equatorial rows, 192 for caps and 48 for
pure tails. The JSON companion gives the exact row ranges.

| Intrinsic dimension | Rows | Cartesian columns | File |
| ---: | ---: | ---: | --- |
| 49 | 52,430,156 | 51 | `configuration49.i8.gz` |
| 50 | 52,458,468 | 57 | `configuration50.i8.gz` |
| 51 | 52,500,930 | 57 | `configuration51.i8.gz` |
| 52 | 52,585,772 | 60 | `configuration52.i8.gz` |
| 53 | 52,698,696 | 63 | `configuration53.i8.gz` |
| 54 | 52,923,774 | 72 | `configuration54.i8.gz` |
| 55 | 53,301,140 | 72 | `configuration55.i8.gz` |

After gzip decompression, `.i8` is a headerless row-major signed-int8 array.
All entries lie in `[-12,12]`. Widen to at least int32 before multiplying or
taking dot products. Extra coordinate columns are redundant; the point sets
have the intrinsic dimensions in the table.

## Exact coordinate map

The supplied [`cartesian-basis.json`](data/cartesian-basis.json) contains
integer matrices `F,B` satisfying

$$
FGF^t=6I_{48},\qquad B=GF^t,\qquad BB^t=6G.
$$

Thus a norm-six catalogue coefficient row `z` has Cartesian head `h=2zB`
of squared norm 144. For each tail root `r`, use these concatenated blocks:

| Tail root squared norm | Tail Cartesian row `v` | Squared norm |
| ---: | --- | ---: |
| 1 | `(4r,4r,4r)` | 48 |
| 2 | `(2r,2r,4r)` | 48 |
| 8 | `(r,r,2r)` | 48 |

Retained equatorial rows are `(±h,0)`. A selected head line assigned to `v`
replaces its two equatorial rows by all four `(±h,±v)` combinations, with
independent signs. The pure tails are `(0,±v)`. Repeated coordinate blocks
do not increase the tail rank. This is exactly the normalized construction
proved in the [lifting derivation](../../research/trajectory/p48.md).

## Reproduction

Use a SageMath Python providing NumPy and fpylll for preparation and export:

```sh
sage -python constructions/p48/prepare_shell.py \
  --blocks 20 30 40 --loops 3 --output p48p-geometry.json
g++ -O3 -std=c++17 -fopenmp \
  constructions/sections/export_vectors_native.cpp -o export-vectors
./export-vectors p48p-geometry.json mother-shell 16 7
sage -python constructions/p48/index_shell.py \
  --shards mother-shell --output p48p-canonical-lines.i8
sage -python constructions/p48/export_vectors.py \
  --shell p48p-canonical-lines.i8 \
  --basis constructions/p48/data/cartesian-basis.json --output full
python constructions/p48/verify_vector_binary.py \
  --shell p48p-canonical-lines.i8 \
  --basis constructions/p48/data/cartesian-basis.json \
  --directory full --report full-coordinate-verification.json
```

The native search proposes candidates using long-double bounds, retains only
exact Gram-norm-six rows, and emits both signs. The independent indexer checks
all antipodal pairs and norms, then sorts and verifies 26,208,000 distinct
lines. Their 52,416,000 vectors match the proved complete mother-shell size.
The Cartesian exporter checks every used line against that complete index,
the exact basis identity, every generated norm, all block counts and the
published totals. Distinctness follows from the injective head map, disjoint
assigned classes and the three distinct point types. The separate checker
requires NumPy and SymPy and reconstructs every exported row from the finite
inputs, also checking the exact intrinsic ranks.
