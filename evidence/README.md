# Verification

The geometric proofs are developed in the [reports](../reports/README.md).
The [proof map](proof-map.md) connects each dimension to its counting formula,
finite inputs and verification tasks.
The [result catalogue](../constructions/catalog/results.json) identifies each
finite construction and its counting formula. The
[artifact index](../constructions/catalog/artifacts.json) records the input files.

[verification.json](verification.json) records the complete computational replay:
the checks performed, their exact input identities, environment and outcomes.
The inputs and algorithms can be rerun with `make verify`; the
[reproduction guide](../reproducibility/README.md) explains the individual checks.

The repository [manifest](../manifest.json) covers all distributed files.
`make integrity` checks that a downloaded copy agrees with that manifest.
