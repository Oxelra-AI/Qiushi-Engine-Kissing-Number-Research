# Qiushi Engine: New Lower Bounds for Kissing Numbers

[中文](README.zh-CN.md) · [English report](reports/en/main.pdf) · [中文报告](reports/zh/main.pdf) · [Results](research/results.md) · [Research](research/README.md) · [Reproduce](reproducibility/README.md)

**72 hours of continuous autonomous research, shared in a public livestream.**

Qiushi Engine's autonomous mathematical research yields new kissing-number lower bounds in **10 dimensions: 32–39, 43 and 45**.

During the Apsara Conference, Zhejiang University and Alibaba Cloud organized
a 72-hour research livestream, from 08:00 on 22 September to 08:00 on
25 September 2026, China Standard Time. Qiushi Engine autonomously studied
the literature, proposed and tested constructions, revised its research
direction and verified the resulting mathematical objects. The broadcast
opened this sustained research process to public observation.
[Hangzhou Daily](https://xjnnet.com/baoliao/2026-09-23/81691.html)
described the event as China's first public livestream in which AI pursued
an open mathematical problem autonomously for 72 consecutive hours.
See the [livestream overview](research/livestream.md).

The mathematical question is how to enlarge a highly constrained spherical
configuration. The research develops joint code exchanges, signed local
replacements, compatible directions from another lattice shell, and exact
counts for lattice sections. The reports explain why these changes work;
the accompanying data and programs reconstruct and verify the finite objects
on which the proofs depend.

## Mathematical results

A kissing number asks how many equal spheres can touch a central sphere
without overlapping one another. After normalization, a configuration is a
set of unit vectors with pairwise inner products at most one half.
Each row below gives a larger configuration and hence an improved lower bound.
Public comparisons were recorded on 24–25 September 2026;
[fixed sources](constructions/catalog/comparison-sources.json) accompany the table.

| Dimension | Lower bound | Public comparison | Increase |
|---:|---:|---:|---:|
| 32 | 347,584 | 346,432 | +1,152 |
| 33 | 363,968 | 362,048 | +1,920 |
| 34 | 384,196 | 381,124 | +3,072 |
| 35 | 409,676 | 409,548 | +128 |
| 36 | 484,760 | 484,568 | +192 |
| 37 | 498,024 | 496,232 | +1,792 |
| 38 | 591,900 | 591,612 | +288 |
| 39 | 763,668 | 756,116 | +7,552 |
| 43 | 2,553,792 | 2,545,056 | +8,736 |
| 45 | 7,380,090 | 7,379,838 | +252 |

## Mathematical ideas

In a layered code, the benefit of adding several supports depends on their
shared conflicts: the supports removed to admit the whole family are counted
only once. Optimizing this joint cost enlarges the constant-weight codes.
Paired Hadamard maps then transfer weight-four signed codes into compatible
weight-eight configurations. Their placement in suitable coordinate regions
gives the local improvements in dimensions 35–37, including a sharp capacity
bound for the eleven-coordinate model used in dimension 35.

In dimension 38, the lifted Leech configuration leaves an equatorial space
whose useful directions lie outside the minimal shell. A compatible set of
144 antipodal lines from the norm-48 shell supplies 288 additional points.
The argument controls both the internal products of the new directions and
their products with the entire lifted configuration, giving 591,900 points.

For dimensions 43 and 45, spherical-design moments replace a count over
52,416,000 lattice vectors with finite rational identities. An embedded
$E_8$ section determines the orthogonal shell of a $D_5$ subsection and gives
2,553,792 points. In dimension 45, a moment inequality assigns a positive
contribution to each vector in a selected fibre. Common-neighbour searches
produce 298 such witnesses, yielding $7,377,408+9\times298=7,380,090$.

| Dimensions | Data and verification | Mathematical development |
|---|---|---|
| 32–37, 39 | [Supports and signed replacements](constructions/codes/) | [Supports and signed replacements](research/trajectory/codes.md) |
| 38 | [Equatorial completion](constructions/d38/) | [Equatorial completion](research/trajectory/equatorial.md) |
| 43, 45 | [Lattice sections and moments](constructions/sections/) | [Lattice sections and moments](research/trajectory/sections.md) |

The [reports](reports/README.md) develop the mathematical arguments in this
order. The [research account](research/README.md) connects the principles,
search choices, intermediate objects and final constructions. Coordinate
conventions and mathematical sources accompany the finite data.

## Read and reproduce

| To understand | Start here |
|---|---|
| Results, geometric arguments and their relationship | [English report](reports/en/main.pdf) · [中文报告](reports/zh/main.pdf) |
| How the constructions developed | [Research account](research/README.md) |
| Exact inputs and proof checks | [Verification](evidence/README.md) |
| Dependencies and execution | [Reproduction guide](reproducibility/README.md) |
| Data and source attribution | [Construction catalogue](constructions/catalog/results.json) · [Sources](research/provenance.md) |

With Python providing NumPy, SymPy and SageMath, and a C++17 compiler:

```sh
make list
make verify
```

The verification run writes its results to a new directory beside the repository.
`make reports` builds the bilingual PDFs; `make source-en` and `make source-zh`
produce self-contained LaTeX projects. See the [full instructions](reproducibility/README.md).

```text
reports/           English and Chinese reports: PDF, LaTeX, bibliography, figures
research/          Mathematical development and sources
constructions/     Exact data, construction families and verification programs
evidence/          Recorded verification and its relation to the proofs
reproducibility/   Dependencies and execution instructions
tools/             Report builds, reproduction and integrity checks
tests/             Data and document consistency tests
```

## Authors

Shuxing Yang, Rui Zhao, Junyao Wu, Yize Wang, Fujia Chen, Kaihao Zhu,
Wenhao Li, Zichen Li, Yaqi Li, Shenzhan Hong, Yuang Pan, Junjie Yang,
Taowen Deng, Jincheng Mi, Hongsheng Chen*, Yihao Yang*.

College of Information Science and Electronic Engineering, Zhejiang University · Qiushi Engine Team, Hangzhou, China

*Correspondence: Hongsheng Chen (hansomchen@zju.edu.cn); Yihao Yang (yangyihao@zju.edu.cn).

For Qiushi Engine's autonomous experimental research, see the
[optical-platform study](https://arxiv.org/abs/2604.27092).

[Citation](CITATION.cff) · [License](LICENSE) · [Third-party materials](constructions/third-party.md)
