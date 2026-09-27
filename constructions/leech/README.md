# Leech block liftings

The finite inputs give the historical bounds $K(25)\ge197058$ and
$K(27)\ge200540$. They consist of a Golay generator, five 496-point blocks,
and exact three-dimensional tails over $\mathbf Q(\sqrt2,\sqrt3)$.

```bash
python verify.py --output /tmp/leech.json
python verify_independent.py --output /tmp/leech-independent.json
python check_tails.py --output /tmp/leech-tails.json
```

The first checker uses Python integer and rational arithmetic. The independent
checker uses NumPy and SymPy. `generate.py --dimension 25 --output points.jsonl`
streams exact coordinates; choose dimension 27 for the second construction.
The stronger two-layer 27-dimensional construction is in `../d27/`.
