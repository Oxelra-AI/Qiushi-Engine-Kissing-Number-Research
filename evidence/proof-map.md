# Proofs and finite inputs

Each row connects a lower bound to its exact count and verification tasks.
The [reports](../reports/README.md) prove the geometric reductions;
the [reproduction guide](../reproducibility/README.md) explains how to run the tasks.

| Dimension | Count | Verification tasks |
|---:|---|---|
| 32 | `131072 + 128*1676 + 2*32*31 = 347584` | `dimension32`, `supports32-37` |
| 33 | `131072 + 128*1803 + 2*33*32 = 363968` | `codes-primary`, `codes-independent`, `support-exchanges` |
| 34 | `131072 + 128*1960 + 2*34*33 = 384196` | `codes-primary`, `codes-independent`, `support-exchanges` |
| 35 | `409548 - 128 + 256 = 409676` | `hadamard35-36` |
| 36 | `484568 - 384 + 576 = 484760` | `hadamard35-36` |
| 37 | `131072 + 128*2845 + 2*37*36 - 3*128 + 512 = 498024` | `supports32-37` |
| 38 | `591612 + 2*144 = 591900` | `dimension38` |
| 39 | `327680 + 128*3383 + 2*39*38 = 763668` | `codes-primary`, `codes-independent`, `code-lineage` |
| 43 | `1092000 + 116235*12 + 9180*6 + 495*24 + 12 = 2553792` | `section43`, `section43-matrix` |
| 45 | `7377408 + 9*298 = 7380090` | `qr-ambient`, `section45`, `section45-parent` |

## Defining inputs

### Dimension 32

Replace intersecting weight-eight supports by a larger compatible support family of size 1676.

- [codes/data/d32_supports_binary.txt](../constructions/codes/data/d32_supports_binary.txt)
- [codes/data/d33_kernel.txt](../constructions/codes/data/d33_kernel.txt)
- [codes/data/d33_representatives.txt](../constructions/codes/data/d33_representatives.txt)
- [codes/verify_replacements.py](../constructions/codes/verify_replacements.py)

### Dimension 33

Find 1803 weight-eight supports whose pairwise intersections are at most four.

- [codes/data/d33_supports.txt](../constructions/codes/data/d33_supports.txt)
- [codes/data/d33_kernel.txt](../constructions/codes/data/d33_kernel.txt)
- [codes/data/d33_representatives.txt](../constructions/codes/data/d33_representatives.txt)
- [codes/verify.py](../constructions/codes/verify.py)
- [codes/verify_independent.py](../constructions/codes/verify_independent.py)
- [codes/independent.cpp](../constructions/codes/independent.cpp)
- [codes/reference_checker.py](../constructions/codes/reference_checker.py)
- [codes/data/exchanges/d33_parent.txt](../constructions/codes/data/exchanges/d33_parent.txt)
- [codes/data/exchanges/exchanges.json](../constructions/codes/data/exchanges/exchanges.json)
- [codes/verify_exchanges.py](../constructions/codes/verify_exchanges.py)

### Dimension 34

Find 1960 weight-eight supports whose pairwise intersections are at most four.

- [codes/data/d34_supports.txt](../constructions/codes/data/d34_supports.txt)
- [codes/data/d34_kernel.txt](../constructions/codes/data/d34_kernel.txt)
- [codes/data/d34_representatives.txt](../constructions/codes/data/d34_representatives.txt)
- [codes/verify.py](../constructions/codes/verify.py)
- [codes/verify_independent.py](../constructions/codes/verify_independent.py)
- [codes/independent.cpp](../constructions/codes/independent.cpp)
- [codes/reference_checker.py](../constructions/codes/reference_checker.py)
- [codes/data/exchanges/d34_parent.txt](../constructions/codes/data/exchanges/d34_parent.txt)
- [codes/data/exchanges/exchanges.json](../constructions/codes/data/exchanges/exchanges.json)
- [codes/verify_exchanges.py](../constructions/codes/verify_exchanges.py)

### Dimension 35

Replace one 128-point sign bundle by 256 compatible signed points.

- [codes/hadamard/data/top_code.json](../constructions/codes/hadamard/data/top_code.json)
- [codes/hadamard/data/d35_supports.txt](../constructions/codes/hadamard/data/d35_supports.txt)
- [codes/hadamard/data/d35_construction.json](../constructions/codes/hadamard/data/d35_construction.json)
- [codes/hadamard/verify.py](../constructions/codes/hadamard/verify.py)
- [codes/hadamard/data/generators.json](../constructions/codes/hadamard/data/generators.json)
- [codes/hadamard/search.py](../constructions/codes/hadamard/search.py)

### Dimension 36

Replace three 128-point sign bundles by 576 compatible signed points.

- [codes/hadamard/data/top_code.json](../constructions/codes/hadamard/data/top_code.json)
- [codes/hadamard/data/d36_supports.txt](../constructions/codes/hadamard/data/d36_supports.txt)
- [codes/hadamard/data/d36_construction.json](../constructions/codes/hadamard/data/d36_construction.json)
- [codes/hadamard/verify.py](../constructions/codes/hadamard/verify.py)
- [codes/hadamard/data/generators.json](../constructions/codes/hadamard/data/generators.json)
- [codes/hadamard/search.py](../constructions/codes/hadamard/search.py)

### Dimension 37

Combine a 2845-support family with a replacement of three sign bundles by 512 points.

- [codes/data/d37_supports_binary.txt](../constructions/codes/data/d37_supports_binary.txt)
- [codes/data/d37_signed_patch.json](../constructions/codes/data/d37_signed_patch.json)
- [codes/data/d33_kernel.txt](../constructions/codes/data/d33_kernel.txt)
- [codes/data/d33_representatives.txt](../constructions/codes/data/d33_representatives.txt)
- [codes/verify_replacements.py](../constructions/codes/verify_replacements.py)

### Dimension 38

Add 144 antipodal norm-48 lines to the empty equator of the published 591612-point construction.

- [d38/base-data/axis_keep.txt](../constructions/d38/base-data/axis_keep.txt)
- [d38/base-data/axis_rotation.txt](../constructions/d38/base-data/axis_rotation.txt)
- [d38/base-data/axis_rotation_D.txt](../constructions/d38/base-data/axis_rotation_D.txt)
- [d38/base-data/class_labels.txt](../constructions/d38/base-data/class_labels.txt)
- [d38/base-data/dim14_directions.txt](../constructions/d38/base-data/dim14_directions.txt)
- [d38/base-data/golay_basis.txt](../constructions/d38/base-data/golay_basis.txt)
- [d38/base-data/triples.txt](../constructions/d38/base-data/triples.txt)
- [d38/added-lines.txt](../constructions/d38/added-lines.txt)
- [tools/verify_dimension38.py](../tools/verify_dimension38.py)

### Dimension 39

Combine 3383 weight-eight supports with ten compatible sign-code cosets of total size 327680.

- [codes/data/d39_supports.txt](../constructions/codes/data/d39_supports.txt)
- [codes/data/d39_kernel.txt](../constructions/codes/data/d39_kernel.txt)
- [codes/data/d39_representatives.txt](../constructions/codes/data/d39_representatives.txt)
- [codes/verify.py](../constructions/codes/verify.py)
- [codes/verify_independent.py](../constructions/codes/verify_independent.py)
- [codes/independent.cpp](../constructions/codes/independent.cpp)
- [codes/reference_checker.py](../constructions/codes/reference_checker.py)
- [codes/data/exchanges/d39_parent.txt](../constructions/codes/data/exchanges/d39_parent.txt)
- [codes/data/exchanges/exchanges.json](../constructions/codes/data/exchanges/exchanges.json)
- [codes/verify_exchanges.py](../constructions/codes/verify_exchanges.py)

### Dimension 43

Choose a different embedded D5 section; its orbit and design-moment identities determine a 2553792-point section.

- [sections/d43/data/CQ48a.html](../constructions/sections/d43/data/CQ48a.html)
- [sections/d43/data/certificate.json](../constructions/sections/d43/data/certificate.json)
- [sections/d43/data/comparison-section.txt](../constructions/sections/d43/data/comparison-section.txt)
- [sections/d43/data/parent-section.txt](../constructions/sections/d43/data/parent-section.txt)
- [sections/d43/verify.py](../constructions/sections/d43/verify.py)
- [sections/d43/verify_matrix.py](../constructions/sections/d43/verify_matrix.py)

### Dimension 45

Change the parent anchor sector in the QR neighbour, obtain 298 finite witnesses, and transfer them through an exact moment inequality.

- [sections/qr/data/gram.json](../constructions/sections/qr/data/gram.json)
- [sections/d45/data/compact.json](../constructions/sections/d45/data/compact.json)
- [sections/d45/data/gram.json](../constructions/sections/d45/data/gram.json)
- [sections/d45/data/record.json](../constructions/sections/d45/data/record.json)
- [sections/qr/verify.py](../constructions/sections/qr/verify.py)
- [sections/qr/qr_code.py](../constructions/sections/qr/qr_code.py)
- [sections/d45/verify.py](../constructions/sections/d45/verify.py)
- [sections/d45/data/dual.json](../constructions/sections/d45/data/dual.json)
- [sections/d45/data/parent.json](../constructions/sections/d45/data/parent.json)
- [sections/d45/data/parent-vectors.jsonl](../constructions/sections/d45/data/parent-vectors.jsonl)
- [sections/d45/verify_parent.py](../constructions/sections/d45/verify_parent.py)
