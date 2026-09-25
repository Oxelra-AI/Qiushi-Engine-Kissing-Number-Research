# Supports, sign codes and local replacements

`data/claims.json` specifies the five original three-layer constructions.
The kernel generators, coset representatives and weight-eight support lists
are finite inputs. `verify.py` checks all pair types; `verify_independent.py`
compiles a separate C++17 implementation in a temporary directory.

```bash
python verify.py --output /tmp/codes.json
python verify_independent.py --output /tmp/codes-independent.json
python check_code_lineage.py --output /tmp/code-lineage.json
python verify_replacements.py --output /tmp/support-replacements.json
python verify_exchanges.py --output /tmp/support-exchanges.json
python hadamard/verify.py --output /tmp/hadamard.json
python hadamard/search.py
```

`verify_replacements.py` checks the 1,676-support construction in dimension 32 and
the 2,845-support construction with a 512-point signed replacement in
dimension 37. It regenerates the 512 signed vectors from the six coordinate
pairs and 32 transverse four-subsets and checks equality with the stored
vector set. `verify_exchanges.py` checks the complete parents, removed and
inserted supports, and final witnesses for the five terminal exchanges in
dimensions 33, 34, 37, 38 and 39. `hadamard/` contains the exact signed replacements in dimensions
35 and 36. Its `search.py` constructs a 30-block Steiner quadruple system
and a 51-block code from one-factorizations, then enumerates all 945 and
10,395 coordinate matchings. The resulting 256 and 576 signed vectors
coincide with the certificates. The main Hadamard verifier also runs this
reconstruction, together with the compact generators in `data/generators.json`.
The latest bounds in these four dimensions are 347584, 409676,
484760 and 498024 respectively.

The Python checks require the standard library; the independent check also
requires a C++17 compiler. `generate.py` streams the original three-layer
coordinates from the claims file. Coordinate order and sign conventions are
specified by the checked finite inputs.
