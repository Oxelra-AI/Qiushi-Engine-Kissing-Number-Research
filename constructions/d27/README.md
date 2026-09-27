# Two-layer construction in dimension 27

The frozen configuration has **201,567 points**. It retains the 2,258
first-layer heads of the public 201,566-point construction and uses 311
compatible second-layer owners in place of 310. Its count is

\[
196560-2090-311+3(2258)+2(311)+12=201567.
\]

`data/` contains the four integer arrays. `lib/` contains the public
Golay/Leech generator used to fix their coordinate convention. The two-layer
construction is due to A. Kravatskiy; the 201,566-point reference package
credits B. Lindow's joint reoptimization. This collection records Qiushi's
subsequent 311-owner configuration, with the inherited first layer identified
explicitly.

From the repository root:

```sh
python3 tools/verify_dimension27.py --data constructions/d27/data \
  --library constructions/d27/lib --output ../dimension27-verification.json
```

The verifier reconstructs the Leech shell, checks both deletion sets and all
head-pair inequalities, and proves the remaining algebraic inequalities
exactly. It does not invoke the reference package's verifier.

All points have squared norm 4; distinct points have inner product at most
2. The second-layer/axis maximum is **2**, attained for an axis contact.
`verification.json` is the saved execution record for these exact inputs.

The [research account](../../research/dimensions/27.md) gives the candidate
graph and binary optimization. `search.py --output NEW_DIRECTORY` rebuilds
the 3,125 candidates and 261,474 edges, and checks the saved 311-owner
selection. Its optional `--seconds` mode requires OR-Tools.
