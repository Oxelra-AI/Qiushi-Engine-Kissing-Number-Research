# Exact coordinates for independent verification

The [complete coordinate release](https://github.com/Oxelra-AI/Qiushi-Engine-Kissing-Number-Research/releases/tag/section-vectors-2026-10-11)
contains both full point sets, in gzip CSV and compact binary form. These are
ordinary Cartesian coordinates, not lattice coefficients. Both exports use **48
integer columns**: the points lie in specified subspaces of dimensions 43 and
45, respectively. An orthonormal change of basis is unnecessary for checking
norms and pairwise inner products.

| Construction | Complete row count | Squared norm of each exported row | Maximum inner product of distinct rows | Unit normalization |
| --- | ---: | ---: | ---: | --- |
| 43D | 2,553,792 | 576 | 288 | divide by 24 |
| 45D | 7,380,090 | 4,416 | 2,208 | divide by $8\sqrt{69}$ |

## Downloads

- **43D:** [CSV](https://github.com/Oxelra-AI/Qiushi-Engine-Kissing-Number-Research/releases/download/section-vectors-2026-10-11/section43.csv.gz),
  [binary](https://github.com/Oxelra-AI/Qiushi-Engine-Kissing-Number-Research/releases/download/section-vectors-2026-10-11/section43.i8.gz).
- **45D:** [CSV](https://github.com/Oxelra-AI/Qiushi-Engine-Kissing-Number-Research/releases/download/section-vectors-2026-10-11/section45.csv.gz),
  [binary](https://github.com/Oxelra-AI/Qiushi-Engine-Kissing-Number-Research/releases/download/section-vectors-2026-10-11/section45.i8.gz).

CSV has 48 comma-separated integers per line and no header. Binary has the
same rows in the same order, as 48 signed 8-bit integers per row, with no header.
All points were checked for their exact norms, subspace and lattice/fibre
membership, and distinctness. The three positive fibres in 45D each contain
2,460,030 points. The release includes the per-dimension verification results.

These files support an independent all-pairs check. Our export validation
checks membership in the proved construction, rather than rerunning all pairs.

## Reproducing the complete exports

The fast implementation needs SageMath with fpylll, NumPy, a C++17 compiler,
Boost headers, OpenMP, and gzip (or pigz). From the repository root:

```sh
g++ -O3 -std=c++17 -fopenmp constructions/sections/export_vectors_native.cpp -o export-vectors
g++ -O3 -std=c++17 constructions/sections/vector_data_csv.cpp -o vector-data-csv
sage -python constructions/sections/prepare_fast.py --dimension 43 --output geometry43.json
./export-vectors geometry43.json vectors43 16 8
cat vectors43/part-*.i8 > section43.i8
sage -python constructions/sections/verify_vector_binary.py \
  --dimension 43 --input section43.i8 --output section43-verification.json
./vector-data-csv section43.i8 | gzip > section43.csv.gz
```

Replace 43 by 45 for the second construction. The last two native arguments
are the worker count and the number of tail coordinates used to split the
enumeration. Row order may vary; the mathematical point set does not.

The native search uses long-double bounds to generate candidates and integer
arithmetic to retain the required norm. The separate checker establishes exact
lattice/fibre membership and uniqueness for every row. Together with the proved
cardinalities, this certifies that the exports contain the complete point sets.

## Exact-rational reference implementation

[`export_vectors.py`](export_vectors.py) also gives a slower, entirely rational
enumeration of the same sets. It is useful for checking the enumeration logic
and for small trials.

Use a Python interpreter with SageMath available. From the repository root:

```sh
sage -python constructions/sections/export_vectors.py \
  --dimension 43 --output section43.csv.gz
sage -python constructions/sections/export_vectors.py \
  --dimension 45 --output section45.csv.gz
```

On installations where SageMath is imported directly by Python, replace
`sage -python` with that Python interpreter. No additional solver is required.
The gzip CSV files have no header. A companion `.csv.gz.json` file records the
coordinate convention, row count, normalization, orthogonal subspace and
whether enumeration finished. Existing files are not overwritten.

For a bounded first run, use a different output name:

```sh
sage -python constructions/sections/export_vectors.py \
  --dimension 45 --output section45-sample.csv.gz --limit 16 --max-nodes 10000
```

`--limit` and `--max-nodes` produce partial files. A result is marked
`complete: true` only after exhausting the search tree and obtaining the
proved row count. Stopping after a specified number of points is not a
completeness check. The exporter checks each output norm; a separate pairwise
checker can test uniqueness and the inner-product bounds in the table.

## 43D: the orthogonal section

Let $G$ and $T_5$ be the ambient Gram matrix and the first five section rows in
[`d43/data/parent-section.txt`](d43/data/parent-section.txt). Enumerate exactly

$$
\{z\in\mathbb Z^{48}:zGz^t=6,\quad T_5Gz^t=0\}.
$$

The integer Cartesian basis $B$ in
[`d43/data/euclidean-basis.json`](d43/data/euclidean-basis.json) satisfies
$BB^t=96G$. The exported row is $zB$; its squared norm is 576 and it is
orthogonal to every row of $T_5B$. Dividing by 24 gives unit vectors. Both
signs of every antipodal pair are included in a complete export.

The basis is taken, with its MIT attribution, from the fixed upstream
[`sphere-packing` source](https://github.com/wcgbg/sphere-packing/blob/a0bc7f51444e42c3cbae0d2a910039cd50013500/sphere_packing/lattices/p48nm.cc).
The exporter checks its exact Gram matrix against the published section data.

## 45D: three positive fibres and orthogonal projection

Use $G$ from [`d45/data/gram.json`](d45/data/gram.json) and $T$ from
[`d45/data/compact.json`](d45/data/compact.json). Here

$$
H=TGT^t=8I_3-2J_3,\qquad H^{-1}=(I_3+J_3)/8.
$$

Enumerate $zGz^t=6$ with $y=zGT^t$ equal to **one of $e_1,e_2,e_3$**.
Do not include the negative signatures. Its orthogonal projection, expressed
in the ambient lattice basis, is

$$
p=z-yH^{-1}T,
\qquad pGp^t=23/4.
$$

The integer basis $B$ already supplied in
[`d45/data/parent.json`](d45/data/parent.json) satisfies $BB^t=12G$.
For $y=e_i$, export

$$
nB,\qquad n=8z-(e_i+\mathbf1)T.
$$

These rows have squared norm 4,416 and are orthogonal to $TB$. Their unit
normalization is $nB/(8\sqrt{69})$. The three fibres give disjoint projected
point sets. This is the full construction defined in the paper, not a subset
of the 298 witness vectors. Those witnesses belong to a different fibre;
the 2,256 parent endpoints are also not the final point set.

## Enumeration and reproducibility

The program forms a saturated integer kernel $K$ of $TG$ (using $T_5$ in
43D), so every relevant ambient row has a unique representation $z=w+aK$,
$a\in\mathbb Z^d$. In 43D, $w=0$. In 45D, the three representatives $w$
are the supplied rows $W$ satisfying $WGT^t=I_3$.

With $Q=KGK^t$ and $\ell=KGw^t$, the shell equation becomes

$$
(a-c)Q(a-c)^t=R,\qquad
c=-Q^{-1}\ell,\qquad R=6-wGw^t+\ell^tQ^{-1}\ell.
$$

Here $R=6$ in 43D and $R=23/4$ in 45D. Unimodular Gram reduction changes
the basis, not the enumerated set. An exact rational $LDL^t$ factorization
then gives integer search intervals using integer square roots. No floating
tolerance, heuristic pruning or stored witness list determines inclusion.

The focused tests can be run with:

```sh
python -B -m unittest discover -s tests -p test_section_vector_export.py -v
```

The small-form tests require only Python's standard library. The geometry
test additionally requires SageMath and checks both Cartesian bases, saturated
kernels, reduced forms, affine centres and projection scales.
