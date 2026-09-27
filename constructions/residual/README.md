# Partial fibres in dimension 18

`d18/data/certificate.json` specifies 2,048 partial-fibre points and 832 holes
over the fixed 5,350-point core. The verifier reconstructs all 8,230 points,
checks distinctness and norms, and examines every unordered pair exactly in
$\mathbf Q(\sqrt3)$.

```bash
python d18/verify.py --output /tmp/residual-d18.json --chunk 128
```

NumPy is required. `--chunk` controls the memory used for pairwise checking;
it does not change the finite certificate. The 8,230-point result is retained
as a historical construction.
