# Lifting a 7,077-line class in the P48p lattice

`data/` contains the catalogue Gram matrix and automorphisms, the frozen
7,077-line class and the chosen automorphism images. Distinct tail directions
are assigned to disjoint parts of these images. If their union contains
\(S\) minimal lines and the tail code contains \(t_k\) points, the lifting has

\[
N_{48+k}=52\,416\,000+2S+t_k.
\]

| Dimension | Union size \(S\) | Tail size | Construction size |
| ---: | ---: | ---: | ---: |
| 49 | 7,077 | 2 | 52,430,156 |
| 50 | 21,231 | 6 | 52,458,468 |
| 51 | 42,459 | 12 | 52,500,930 |
| 52 | 84,874 | 24 | 52,585,772 |
| 53 | 141,328 | 40 | 52,698,696 |
| 54 | 253,851 | 72 | 52,923,774 |
| 55 | 442,507 | 126 | 53,301,140 |

Run from the repository root:

```sh
python3 constructions/p48/verify.py --output ../p48-verification.json
```

The verifier checks the catalogue-to-array match, exact positive definiteness,
unimodularity, automorphism identities, all class products, all image unions,
tail ranks and pair inequalities. It retains the published P48p minimum 6 and
52,416,000-point shell as mathematical premises. It does not enumerate that
entire shell. `verification.json` records the recomputation for the supplied
inputs.

The [shared derivation](../../research/trajectory/p48.md) includes the
complete pair classification and class-extension search. The seven
[dimensional accounts](../../research/README.md) describe the individual
tail systems and selected families. `search.py --output NEW_DIRECTORY`
checks the eight additions and reproduces the exact union decomposition;
optional image-pool parameters enable further search.
