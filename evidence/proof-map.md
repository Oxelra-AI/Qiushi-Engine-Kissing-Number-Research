# Proofs and finite inputs

Each row connects a lower bound to its exact count and verification tasks.
The [reports](../reports/README.md) prove the geometric reductions;
the [reproduction guide](../reproducibility/README.md) explains how to run the tasks.

| Dimension | Count | Verification tasks |
|---:|---|---|
| 25 | `197579 - 552 - 2 + 552 + 2 + 1 = 197580` | `dimension25` |
| 27 | `196560 - 2090 - 311 + 3*2258 + 2*311 + 12 = 201567` | `dimension27` |
| 32 | `131072 + 128*1676 + 2*32*31 = 347584` | `dimension32`, `supports32-37` |
| 33 | `131072 + 128*1803 + 2*33*32 = 363968` | `codes-primary`, `codes-independent`, `support-exchanges` |
| 34 | `131072 + 128*1960 + 2*34*33 = 384196` | `codes-primary`, `codes-independent`, `support-exchanges` |
| 35 | `409548 - 128 + 256 = 409676` | `hadamard35-36` |
| 36 | `484568 - 384 + 576 = 484760` | `hadamard35-36` |
| 37 | `131072 + 128*2845 + 2*37*36 - 3*128 + 512 = 498024` | `supports32-37` |
| 38 | `591612 + 2*144 = 591900` | `dimension38` |
| 39 | `327680 + 128*3383 + 2*39*38 = 763668` | `codes-primary`, `codes-independent`, `code-lineage` |
| 43 | `1092000 + 116235*12 + 9180*6 + 495*24 + 12 = 2553792` | `section43`, `section43-matrix` |
| 45 | `7377408 + 9*298 = 7380090` | `qr-ambient`, `section45`, `section45-parent`, `section45-statistics` |
| 49 | `52416000 + 2*7077 + 2 = 52430156` | `p48-current` |
| 50 | `52416000 + 2*21231 + 6 = 52458468` | `p48-current` |
| 51 | `52416000 + 2*42459 + 12 = 52500930` | `p48-current` |
| 52 | `52416000 + 2*84874 + 24 = 52585772` | `p48-current` |
| 53 | `52416000 + 2*141328 + 40 = 52698696` | `p48-current` |
| 54 | `52416000 + 2*253851 + 72 = 52923774` | `p48-current` |
| 55 | `52416000 + 2*442507 + 126 = 53301140` | `p48-current` |

## Structural calculations

The paper proves the parameterized statements and their equality cases.
These programs reconstruct the finite inputs, compute exact certificates,
and test the associated selection rules.

| Mathematical result | Program or independent checks |
|---|---|
| Two necessary repairs in the specified 25-dimensional motion | [Motion obstructions](../constructions/d25/verify_motion_obstructions.py); replay `motion25-obstructions` |
| Sharp reuse and finite chord-boundary criteria | [Rational and algebraic tests](../tests/test_motion_lifting_structure.py) |
| Matching-optimal compatible subexchanges and sharp transverse transfer | [Replacement checks](../tests/test_replacement_principles.py) |
| Exact capacities for all twelve-coordinate complete-type boundaries | [Reusable solver](../constructions/codes/hadamard/boundary.py), [all 512 type relations and the ten 37-dimensional divisions](../tests/test_transverse_type_capacity.py) |
| Endpoint contacts and next-shell obstruction in the fixed 38-dimensional base | [Shell contacts](../constructions/d38/verify_contacts.py); replay `shell38-contacts` |
| Eight fixed coordinate-section counts from an embedded E8 | [Exact moment ranks and Weyl correspondence](../constructions/sections/d43/verify_coordinate_family.py); replay `section43-coordinate-family`; [independent determinant and rejection tests](../tests/test_e8_coordinate_sections.py) |
| Signed anchor identities and the fixed-anchor optimum | [Parent graph](../constructions/sections/d45/verify_parent.py), [independent codegrees and corruption tests](../tests/test_anchor_graph.py) |
| Exact conditional-expectation selection from finite image pools | [Coverage algorithm](../constructions/p48/coverage.py), [exhaustive small-pool tests](../tests/test_finite_coverage.py) |

## Defining inputs

### Dimension 25

Move 552 retained shell points together, adjoin one point, and replace two individual caps by normalized integer vectors.

- [d25/baseline-heads.json](../constructions/d25/baseline-heads.json)
- [d25/repair-points.json](../constructions/d25/repair-points.json)
- [d25/construction.tex](../constructions/d25/construction.tex)
- [d25/verify_baseline.py](../constructions/d25/verify_baseline.py)
- [d25/verify_extension.py](../constructions/d25/verify_extension.py)
- [d25/golay.py](../constructions/d25/golay.py)
- [d25/leech.py](../constructions/d25/leech.py)
- [d25/check_rejections.py](../constructions/d25/check_rejections.py)
- [tools/verify_dimension25.py](../tools/verify_dimension25.py)

### Dimension 27

Keep the published 2258-head first layer and enlarge its compatible second layer from 310 to 311 owners.

- [d27/data/heads27_Y.npy](../constructions/d27/data/heads27_Y.npy)
- [d27/data/heads27_layer2_line.npy](../constructions/d27/data/heads27_layer2_line.npy)
- [d27/data/heads27_layer2_u.npy](../constructions/d27/data/heads27_layer2_u.npy)
- [d27/data/heads27_side.npy](../constructions/d27/data/heads27_side.npy)
- [d27/lib/golay.py](../constructions/d27/lib/golay.py)
- [d27/lib/leech.py](../constructions/d27/lib/leech.py)
- [tools/verify_dimension27.py](../tools/verify_dimension27.py)

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

Change the parent anchor sector in the QR neighbour and recover its complete
298-point target fibre. Norm-eight signature restrictions sharpen the moment
certificate to an identity, determining the projected count exactly.

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
- [sections/d45/verify_statistics.py](../constructions/sections/d45/verify_statistics.py)

### Dimension 49

Extend the compatible P48p mother class to 7077 lines and select automorphism images with a large union.

- [p48/data/P48p.html](../constructions/p48/data/P48p.html)
- [p48/data/p48p_gram.npy](../constructions/p48/data/p48p_gram.npy)
- [p48/data/p48p_gens.npy](../constructions/p48/data/p48p_gens.npy)
- [p48/data/class_p48_7077.npy](../constructions/p48/data/class_p48_7077.npy)
- [p48/verify.py](../constructions/p48/verify.py)

### Dimension 50

Extend the compatible P48p mother class to 7077 lines and select automorphism images with a large union.

- [p48/data/P48p.html](../constructions/p48/data/P48p.html)
- [p48/data/p48p_gram.npy](../constructions/p48/data/p48p_gram.npy)
- [p48/data/p48p_gens.npy](../constructions/p48/data/p48p_gens.npy)
- [p48/data/class_p48_7077.npy](../constructions/p48/data/class_p48_7077.npy)
- [p48/verify.py](../constructions/p48/verify.py)
- [p48/data/dim50_group_elems.npy](../constructions/p48/data/dim50_group_elems.npy)

### Dimension 51

Extend the compatible P48p mother class to 7077 lines and select automorphism images with a large union.

- [p48/data/P48p.html](../constructions/p48/data/P48p.html)
- [p48/data/p48p_gram.npy](../constructions/p48/data/p48p_gram.npy)
- [p48/data/p48p_gens.npy](../constructions/p48/data/p48p_gens.npy)
- [p48/data/class_p48_7077.npy](../constructions/p48/data/class_p48_7077.npy)
- [p48/verify.py](../constructions/p48/verify.py)
- [p48/data/dim51_group_elems.npy](../constructions/p48/data/dim51_group_elems.npy)

### Dimension 52

Extend the compatible P48p mother class to 7077 lines and select automorphism images with a large union.

- [p48/data/P48p.html](../constructions/p48/data/P48p.html)
- [p48/data/p48p_gram.npy](../constructions/p48/data/p48p_gram.npy)
- [p48/data/p48p_gens.npy](../constructions/p48/data/p48p_gens.npy)
- [p48/data/class_p48_7077.npy](../constructions/p48/data/class_p48_7077.npy)
- [p48/verify.py](../constructions/p48/verify.py)
- [p48/data/dim52_group_elems.npy](../constructions/p48/data/dim52_group_elems.npy)

### Dimension 53

Extend the compatible P48p mother class to 7077 lines and select automorphism images with a large union.

- [p48/data/P48p.html](../constructions/p48/data/P48p.html)
- [p48/data/p48p_gram.npy](../constructions/p48/data/p48p_gram.npy)
- [p48/data/p48p_gens.npy](../constructions/p48/data/p48p_gens.npy)
- [p48/data/class_p48_7077.npy](../constructions/p48/data/class_p48_7077.npy)
- [p48/verify.py](../constructions/p48/verify.py)
- [p48/data/dim53_group_elems.npy](../constructions/p48/data/dim53_group_elems.npy)

### Dimension 54

Extend the compatible P48p mother class to 7077 lines and select automorphism images with a large union.

- [p48/data/P48p.html](../constructions/p48/data/P48p.html)
- [p48/data/p48p_gram.npy](../constructions/p48/data/p48p_gram.npy)
- [p48/data/p48p_gens.npy](../constructions/p48/data/p48p_gens.npy)
- [p48/data/class_p48_7077.npy](../constructions/p48/data/class_p48_7077.npy)
- [p48/verify.py](../constructions/p48/verify.py)
- [p48/data/dim54_group_elems.npy](../constructions/p48/data/dim54_group_elems.npy)

### Dimension 55

Extend the compatible P48p mother class to 7077 lines and select automorphism images with a large union.

- [p48/data/P48p.html](../constructions/p48/data/P48p.html)
- [p48/data/p48p_gram.npy](../constructions/p48/data/p48p_gram.npy)
- [p48/data/p48p_gens.npy](../constructions/p48/data/p48p_gens.npy)
- [p48/data/class_p48_7077.npy](../constructions/p48/data/class_p48_7077.npy)
- [p48/verify.py](../constructions/p48/verify.py)
- [p48/data/dim55_group_elems.npy](../constructions/p48/data/dim55_group_elems.npy)
