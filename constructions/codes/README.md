# Supports, sign codes and local replacements

The final code-based results cover dimensions 32–37 and 39. The construction
uses weight-eight supports, binary sign codes and, in dimensions 35–37,
local signed replacements.

`data/claims.json` specifies the three-layer inputs in dimensions 33, 34,
37, 38 and 39. The 38-dimensional code is retained to document the support
exchange and the shortening relation between the sign codes in dimensions
38 and 39; the final 38-dimensional result is the
[Leech equatorial extension](../d38/README.md).
`verify.py` checks all pair types, and `verify_independent.py` compiles a
separate C++17 implementation in a temporary directory. The 32-dimensional
support family and the 35–37-dimensional replacements have the additional
checks below.

From `constructions/codes/`, run:

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
The resulting bounds are $K(32)\ge347584$, $K(35)\ge409676$,
$K(36)\ge484760$ and $K(37)\ge498024$.

The Python checks require the standard library; the independent check also
requires a C++17 compiler. `generate.py` streams the original three-layer
coordinates from the claims file. Coordinate order and sign conventions are
specified by the checked finite inputs.
