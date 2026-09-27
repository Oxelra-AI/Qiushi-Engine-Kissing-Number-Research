# Original oriented-block P48 construction

This package preserves the first seven high-dimensional constructions. The
618,653 integer rows in `data/blocks.txt` form 63 disjoint oriented blocks.
This is the sole copy of the complete finite block witness.

```bash
python verify.py --output /tmp/p48-original.json
```

The command compiles the C++17 finite checker in a temporary directory,
checks shell membership, distinctness and all within-block products, then
checks the specified Pless-code neighbour and its theta-series shell count.
The minimum-distance and weight-enumerator theorems used in the ambient proof
are cited in `verify_ambient.py`.

The resulting bounds for dimensions 49–55 are 52425977, 52445822, 52475564,
52534909, 52613892, 52771283 and 53034779. The later 7,077-line cap construction
is stored in the parent `p48/` directory; the two families use different finite
objects and count formulas.
