# Qiushi Engine: Large-Scale Autonomous Discovery of Kissing Number Constructions

**Preprint:** [arXiv:2609.35051](https://arxiv.org/abs/2609.35051) · [arXiv PDF](https://arxiv.org/pdf/2609.35051) · [BibTeX](CITATION.bib). Version 1 submitted on 28 September 2026, under Information Theory (cs.IT).

[中文](README.zh-CN.md) · [Paper](paper/main.pdf) · [English report](reports/en_full/main.pdf) · [中文报告](reports/zh_full/main.pdf) · [Results](research/results.md) · [Research](research/README.md) · [Reproduce](reproducibility/README.md)

[Download the complete project](https://github.com/Oxelra-AI/Qiushi-Engine-Kissing-Number-Research/releases/download/structural-study-2026-09-28.1/Qiushi-Engine-Kissing-Number-Research-complete.zip) · [Third release: structural results and research materials](https://github.com/Oxelra-AI/Qiushi-Engine-Kissing-Number-Research/releases/tag/structural-study-2026-09-28.1)

Qiushi Engine's autonomous mathematical research yields new kissing-number lower bounds in **19 dimensions: 25, 27, 32–39, 43, 45 and 49–55**.
The system carried out the construction searches, mathematical analysis
and computational verification presented in this study.

The [Apsara livestream report](reports/README.md#apsara-conference-livestream-report)
covers dimensions 32–39, 43 and 45. The [complete research report](reports/en_full/main.pdf)
also includes dimensions 25, 27 and 49–55.

During the Apsara Conference, Zhejiang University and Alibaba Cloud organized
a 72-hour research livestream, from 08:00 on 22 September to 08:00 on
25 September 2026, China Standard Time. Qiushi Engine autonomously studied
the literature, proposed and tested constructions, revised its research
direction and verified the resulting mathematical objects. The broadcast
opened this sustained research process to public observation.
[Hangzhou Daily](https://hznews.hangzhou.com.cn/kejiao/content/2026-09/23/content_9314105.htm)
described the event as China's first public livestream in which AI pursued
an open mathematical problem autonomously for 72 consecutive hours.
See the [livestream overview](research/livestream.md).

Improving a large kissing configuration can require moving hundreds of
points together, replacing a combinatorial design, or recasting a count
of millions of vectors as a small system of identities. Qiushi Engine
pursued these different routes within one autonomous investigation,
changing the mathematical representation when a fixed search became limiting.

The central question is where a tightly constrained configuration still
has room to change. Coordinated motion preserves a contact layer while
opening space at its boundary; joint replacements share deletion costs;
another lattice shell supplies compatible directions. For lattice sections,
exact moments determine a target count or convert small witness sets into
large lower bounds. The resulting constructions also yield structural
results: a sharp capacity bound for a local signed-code model and an
embedding theorem that forces a section count. The paper develops these
statements; the research accounts explain how the system found them, and
the data and programs make the constructions reproducible.

## Mathematical results

A kissing number asks how many equal spheres can touch a central sphere
without overlapping one another. After normalization, a configuration is a
set of unit vectors with pairwise inner products at most one half.
Each row below gives a larger configuration and hence an improved lower bound.
Public comparison retrieval dates: 2026-09-24 to 2026-09-27. [Fixed sources](constructions/catalog/comparison-sources.json) accompany the table.

| Dimension | Lower bound | Public comparison | Increase |
|---:|---:|---:|---:|
| 25 | 197,580 | 197,579 | +1 |
| 27 | 201,567 | 201,566 | +1 |
| 32 | 347,584 | 346,944 | +640 |
| 33 | 363,968 | 362,048 | +1,920 |
| 34 | 384,196 | 381,124 | +3,072 |
| 35 | 409,676 | 409,548 | +128 |
| 36 | 484,760 | 484,568 | +192 |
| 37 | 498,024 | 496,232 | +1,792 |
| 38 | 591,900 | 591,612 | +288 |
| 39 | 763,668 | 756,116 | +7,552 |
| 43 | 2,553,792 | 2,545,056 | +8,736 |
| 45 | 7,380,090 | 7,379,838 | +252 |
| 49 | 52,430,156 | 52,430,140 | +16 |
| 50 | 52,458,468 | 52,458,418 | +50 |
| 51 | 52,500,930 | 52,500,816 | +114 |
| 52 | 52,585,772 | 52,585,516 | +256 |
| 53 | 52,698,696 | 52,698,222 | +474 |
| 54 | 52,923,774 | 52,922,906 | +868 |
| 55 | 53,301,140 | 53,299,730 | +1,410 |

The dimension-32 comparison is derived by applying the ERS construction to
Lysenstøen's 1,671-word code listed in [Brouwer's table](https://aeb.win.tue.nl/codes/Andw.html#d8.8):
$2^{17}+128\cdot1671+2\cdot32\cdot31=346944$.

## Follow the discoveries

Each dimensional account follows a different mathematical question through
candidate generation, obstacles, intermediate constructions and the final
result. Read how ten supports share nine blockers in dimension 33, how a
four-colour design replaces a difficult signed search in dimension 36,
or how the geometry of a tetrahedron guides the 45-dimensional search.

[25](research/dimensions/25.md) · [27](research/dimensions/27.md) · [32](research/dimensions/32.md) · [33](research/dimensions/33.md) · [34](research/dimensions/34.md) · [35](research/dimensions/35.md) · [36](research/dimensions/36.md) · [37](research/dimensions/37.md) · [38](research/dimensions/38.md) · [39](research/dimensions/39.md) · [43](research/dimensions/43.md) · [45](research/dimensions/45.md) · [49](research/dimensions/49.md) · [50](research/dimensions/50.md) · [51](research/dimensions/51.md) · [52](research/dimensions/52.md) · [53](research/dimensions/53.md) · [54](research/dimensions/54.md) · [55](research/dimensions/55.md)

The [research overview](research/README.md) connects these accounts and
provides the corresponding Chinese versions. The accounts link directly
to the finite objects that preserve the constructions and their saved exchanges.

## Mathematical ideas

### Move a contact layer without breaking its internal geometry

In dimension 25, a coordinated motion of 552 contact points preserves their
transverse components and all internal distances. Convexity controls the
unchanged equator. The released space admits one new point, with only two
local contacts requiring repair, giving 197,580 points. For this insertion
and motion family, two cap changes are also necessary. More generally,
the motion's fixed-boundary constraints admit a finite exact test on a circle.

### Choose directions and reuse labels together

In dimension 27, second-layer selection and tail labels are optimized together.
The original 310 directions cannot be extended by direct insertion, but joint
reselection and recolouring among 3,125 candidates accommodate 311 directions,
giving 201,567 points.

### Count shared deletions once

In a layered code, the benefit of adding several supports depends on their
shared conflicts: the supports removed to admit the whole family are counted
only once. Optimizing this joint cost enlarges the constant-weight codes
in dimensions 32–34, 37 and 39. When the candidate pool is internally
compatible, a maximum matching computes the optimal subexchange exactly.

### Transfer a design into a local signed replacement

Paired Hadamard maps transfer weight-four signed codes into compatible
weight-eight configurations. Their placement in suitable coordinate regions
gives the local improvements in dimensions 35–37, including a sharp capacity
bound for the eleven-coordinate model used in dimension 35. The construction
extends to a family of $32t^2(t-1)$ signed vectors in $4t$ coordinates,
attaining the capacity of its transverse $2+2$ model for every $t\ge2$.
In twelve coordinates, arbitrary restrictions by complete pair types have
an exact matching formula and an explicit optimal construction.

### Let the lattice minimum control every cross-shell pair

In dimension 38, the lifted Leech configuration leaves an equatorial space
whose useful directions lie outside the minimal shell. A compatible set of
144 antipodal lines from the norm-48 shell supplies 288 additional points.
The lattice minimum bounds all norm-48/norm-32 products automatically;
the remaining choice is among the new directions themselves. This gives
591,900 points.

### Recover a large count from a small statistic

For dimensions 43 and 45, spherical-design moments replace a count over
52,416,000 lattice vectors with finite rational relations. An embedded
$\sqrt3 E_8$ section determines the cardinality of the orthogonal shell of the specified $D_5$ subsystem and gives
2,553,792 points. More generally, one polynomial fixes the counts for
eight nested coordinate sections: the parent embedding determines these
populations in every extremal even unimodular lattice of rank 48 containing it.
In dimension 45, additional section-vector constraints
turn the moment inequality into an exact count identity. A fibre of size
$368-c$ corresponds to a neighbourhood difference, where $c$ counts common
neighbours in an anchor graph. Its signed Gram matrix imposes spectral and
parity restrictions; the supplied graph attains its minimum $c=70$, giving
exactly $7,377,408+9\times298=7,380,090$ points.

### Enlarge a class, then choose its images for their union

Dimensions 49–55 share a compatible $P_{48p}$ class enlarged to 7,077 lines.
Each dimension uses a different number of automorphism images. Their union,
rather than the sum of their sizes, measures the available gain. Assigning
each repeated direction once and pairing the resulting classes with root
tails gives seven new bounds from the same construction principle.
Within this paired architecture, the pure tails force the lifting heights
and exclude repeated assignment of a head. The optimization is exactly
maximum image coverage; a finite-pool selection rule gives a computable
guarantee without enumerating the full isometry group.

The [construction-principle overview](paper/README.md#construction-principles)
connects all nineteen dimensions to their general statements and checks.

| Dimensions | Data and verification | Mathematical development |
|---|---|---|
| 25 | [Coordinated shell motion](constructions/d25/) | [Coordinated shell motion](research/trajectory/motion.md) |
| 27 | [Labelled Leech liftings](constructions/d27/) | [Labelled Leech liftings](research/trajectory/leech.md) |
| 32–37, 39 | [Supports and signed replacements](constructions/codes/) | [Supports and signed replacements](research/trajectory/codes.md) |
| 38 | [Equatorial completion](constructions/d38/) | [Equatorial completion](research/trajectory/equatorial.md) |
| 49–55 | [Automorphism-image liftings](constructions/p48/) | [Automorphism-image liftings](research/trajectory/p48.md) |
| 43, 45 | [Lattice sections and moments](constructions/sections/) | [Lattice sections and moments](research/trajectory/sections.md) |

The [reports](reports/README.md) develop the mathematical arguments in this
order. The [research account](research/README.md) connects the principles,
search choices, intermediate objects and final constructions. Coordinate
conventions and mathematical sources accompany the finite data.

## Read and reproduce

| To understand | Start here |
|---|---|
| Main theorems, proofs and structural results | [Mathematical paper](paper/main.pdf) · [LaTeX source](paper/main.tex) |
| Results, geometric arguments and their relationship | [English report](reports/en_full/main.pdf) · [中文报告](reports/zh_full/main.pdf) |
| How the constructions developed | [Research account](research/README.md) |
| Each result's finite inputs and proof checks | [Proof map](evidence/proof-map.md) · [Verification](evidence/README.md) |
| Dependencies and execution | [Reproduction guide](reproducibility/README.md) |
| Data and source attribution | [Construction catalogue](constructions/catalog/results.json) · [Sources](research/provenance.md) |

The verification suite uses Python with NumPy, SymPy, SageMath and
`python-flint`, together with a C++17 compiler. To list and run the checks:

```sh
make list
make verify
```

The verification run writes its results to a new directory beside the repository.
`make paper` compiles the mathematical paper to `paper/main.pdf`.
`make source-paper` exports only the LaTeX sources needed to compile the paper.
The [finite-data supplement](reports/en_full/certificates.zip) is available separately.
`make reports` checks and preserves the published livestream PDFs;
`make source-en` and `make source-zh` package their self-contained LaTeX projects.
`make reports-full` builds the complete study in `reports/en_full/` and `reports/zh_full/`;
`make source-full-en` and `make source-full-zh` package its sources separately.

See the [full instructions](reproducibility/README.md).

```text
reports/           English and Chinese reports: PDF, LaTeX, bibliography, figures
paper/             Mathematical paper: statements, proofs and structural consequences
research/          Per-dimension discovery accounts, shared methods and sources
constructions/     Exact data, construction families and verification programs
evidence/          Recorded verification and its relation to the proofs
reproducibility/   Dependencies and execution instructions
tools/             Report builds, reproduction and integrity checks
tests/             Data and document consistency tests
```

The paper [*Large-Scale Autonomous Discovery of Kissing Number Constructions*](paper/main.pdf)
develops the construction principles, capacity bounds and section-count
theorems underlying the nineteen-dimensional study.

## Authors

Shuxing Yang, Rui Zhao, Junyao Wu, Yize Wang, Fujia Chen, Kaihao Zhu,
Wenhao Li, Zichen Li, Yaqi Li, Shenzhan Hong, Yuang Pan, Junjie Yang,
Taowen Deng, Jincheng Mi, Hongsheng Chen*, Yihao Yang*.

College of Information Science and Electronic Engineering, Zhejiang University · Qiushi Engine Team, Hangzhou, China

*Correspondence: Hongsheng Chen (hansomchen@zju.edu.cn); Yihao Yang (yangyihao@zju.edu.cn).

For Qiushi Engine's autonomous experimental research, see the
[optical-platform study](https://arxiv.org/abs/2604.27092).

Please cite the [arXiv preprint](https://arxiv.org/abs/2609.35051) when using this study.
[BibTeX](CITATION.bib) · [Citation metadata](CITATION.cff) · [License](LICENSE) · [Third-party materials](constructions/third-party.md)
