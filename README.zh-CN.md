# Qiushi Engine：接吻数构造的大规模自主发现

[English](README.md) · [论文](paper/main.pdf) · [中文报告](reports/zh_full/main.pdf) · [英文报告](reports/en_full/main.pdf) · [成果](research/results.md) · [研究脉络](research/README.zh-CN.md) · [复现](reproducibility/README.md)

Qiushi Engine 自主数学研究取得 **19 个维数的接吻数新下界**，覆盖 **25、27、32–39、43、45、49–55维**。
本研究的构造搜索、数学分析与计算验证由 Qiushi Engine 自主开展。

[大会直播报告](reports/README.md#apsara-conference-livestream-report)汇集32–39、43、45维的十项成果；
[完整研究报告](reports/zh_full/main.pdf)同时纳入25、27、49–55维。

云栖大会期间，浙江大学联合阿里云开展了72小时自主科研直播，
从北京时间2026年9月22日08:00持续至9月25日08:00。
Qiushi Engine 自主研读文献、提出并检验构造、调整研究方向、验证数学对象，
将持续探索的科研过程向公众展开。
[《杭州日报》](https://hznews.hangzhou.com.cn/kejiao/content/2026-09/23/content_9314105.htm)将此次活动报道为
国内首次以全程公开直播方式，让AI连续72小时自主挑战开放前沿数学问题。
活动介绍见[直播说明](research/livestream.md)。

扩大一个庞大的接吻构型，可能需要同时移动数百个点、替换一个组合设计，或将数千万个
向量的计数转化为一个小规模恒等式系统。Qiushi Engine 在持续自主研究中探索这些不同
路线，在固定搜索遇到限制时改变问题的数学表示。

贯穿研究的问题是：一个受到严密约束的构型，究竟还有哪些部分可以改变？协同移动保持
接触层的内部几何，同时在边界释放空间；联合替换利用共享的删除代价；另一格壳提供
相容的新方向。对于格截面，精确矩关系能够确定目标计数，或将小规模见证集转化为
大构型的下界。这些构造还带来具体的结构性结论，包括局部符号码模型的尖锐容量界，
以及由嵌入结构决定截面点数的定理。论文展开这些命题，研究脉络说明系统如何发现它们，
数据与程序则让读者能够重建和检验相应构造。

## 数学成果

接吻数问题问的是：多少个相同大小的球能够同时接触中心球，而彼此不重叠？
归一化后，接吻构型等价于两两内积不超过二分之一的单位向量集。
下表每一行都给出一个点数更大的构型，从而提高相应维数的接吻数下界。
公开比较值的核查日期：2026-09-24至2026-09-27。相应[固定来源](constructions/catalog/comparison-sources.json)与数据一同提供。

| 维数 | 下界 | 公开比较值 | 增加 |
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

32维比较值由[Brouwer码表](https://aeb.win.tue.nl/codes/Andw.html#d8.8)所载Lysenstøen的1671字码代入ERS构造得到：
$2^{17}+128\cdot1671+2\cdot32\cdot31=346944$。

## 逐维探索与发现

每个维度都有独立的研究叙述，从所面对的数学问题出发，讲清候选如何产生、约束为何阻碍
改进、中间构造如何形成，以及最终方法如何解决问题。33维的十个新支持如何共享九个阻挡？
36维的符号搜索如何变成四色设计？45维成功构造的四面体几何又如何联系不同候选族？

[25](research/dimensions/25.zh-CN.md) · [27](research/dimensions/27.zh-CN.md) · [32](research/dimensions/32.zh-CN.md) · [33](research/dimensions/33.zh-CN.md) · [34](research/dimensions/34.zh-CN.md) · [35](research/dimensions/35.zh-CN.md) · [36](research/dimensions/36.zh-CN.md) · [37](research/dimensions/37.zh-CN.md) · [38](research/dimensions/38.zh-CN.md) · [39](research/dimensions/39.zh-CN.md) · [43](research/dimensions/43.zh-CN.md) · [45](research/dimensions/45.zh-CN.md) · [49](research/dimensions/49.zh-CN.md) · [50](research/dimensions/50.zh-CN.md) · [51](research/dimensions/51.zh-CN.md) · [52](research/dimensions/52.zh-CN.md) · [53](research/dimensions/53.zh-CN.md) · [54](research/dimensions/54.zh-CN.md) · [55](research/dimensions/55.zh-CN.md)

[研究总览](research/README.zh-CN.md)说明各维度之间的联系，并提供中英文逐维文档。
文档直接连接具体构造、保存的交换及重建程序，让研究思路与数学对象相互对应。

## 构造思想

### 移动接触层，保持内部几何

25维的突破来自552个接触点的协同移动。保持横向分量不变，使块内距离在移动中保持；
凸性统一控制与未动赤道的关系。新增点占据由此释放的位置，仅需修复两个局部接触，
便得到197580点构型。

### 共同选择方向与复用标签

27维将第二提升层的选择与尾部标签共同优化。原有310个方向不能直接扩充，
但在3125个相容候选中联合重选与重着色，可以容纳311个方向，得到201567点。

### 共享的删除代价只计算一次

在分层码中，一组新支持的价值取决于它们共同排斥哪些旧支持：同一旧支持只需删除一次。
联合优化这一代价，可以获得逐个插入无法得到的净增益，扩大32–34、37、39维的常重码。

### 将组合设计转移为局部符号替换

配对 Hadamard 变换把
权四符号码转移为相容的权八构型，并将其嵌入满足边界条件的局部坐标区域，得到35至37维的
局部改进。其中，35维的局部码达到了所用十一坐标模型的容量上界。

### 用格最小范数统一控制跨壳相容性

38维的研究利用 Leech 格提升构型留下的赤道空间。相容的新方向来自极小壳之外的范数48壳层；
格最小范数自动控制范数48向量与全部范数32向量的交叉内积，剩下的选择只需满足新方向间的相容性。
选出的144条反极直线提供288个新点，得到591900点构型。

### 用小统计量确定大构型的点数

43维和45维将球面设计的矩恒等式用于格截面计数，把涉及52416000个格向量的计数问题
化为有限的有理关系。嵌入的 $\sqrt3 E_8$ 截面确定指定 $D_5$ 子系统正交壳的规模，给出2553792点。
45维则建立关于选定纤维的矩不等式，使其中每个见证对下界作出正贡献；共同邻点搜索得到
298个见证，从而推出 $7377408+9\times298=7380090$。

### 扩大母类，再按并集选择它的像

49至55维共用一个扩充到7077条直线的 $P_{48p}$ 相容类。不同维度需要不同数量的自同构像，
目标是扩大像的并集，而非简单累加各像的规模。将重复方向只分配一次，再与对应尾根系组合，
同一数学机制便给出七个新下界。

| 维数 | 数据与验证 | 数学研究脉络 |
|---|---|---|
| 25 | [格壳协同变形](constructions/d25/) | [格壳协同变形](research/trajectory/motion.md) |
| 27 | [Leech 标签提升](constructions/d27/) | [Leech 标签提升](research/trajectory/leech.md) |
| 32–37, 39 | [支持与局部符号替换](constructions/codes/) | [支持与局部符号替换](research/trajectory/codes.md) |
| 38 | [赤道补充](constructions/d38/) | [赤道补充](research/trajectory/equatorial.md) |
| 49–55 | [自同构像提升](constructions/p48/) | [自同构像提升](research/trajectory/p48.md) |
| 43, 45 | [格截面与设计矩](constructions/sections/) | [格截面与设计矩](research/trajectory/sections.md) |

[研究报告](reports/README.md)按上述顺序展开数学论证；
[研究脉络](research/README.zh-CN.md)连接构造原理、搜索选择、中间对象与最终结果。
有限数据附有坐标约定和数学来源。

## 阅读与复现

| 阅读目的 | 入口 |
|---|---|
| 阅读主定理、证明与结构性结论 | [数学论文](paper/main.pdf) · [LaTeX 源码](paper/main.tex) |
| 理解结果、几何证明与各构造的关系 | [中文报告](reports/zh_full/main.pdf) · [English report](reports/en_full/main.pdf) |
| 理解构造如何形成 | [逐维探索与发现](research/README.zh-CN.md) |
| 查看各项结果的精确输入与证明检查 | [证明与数据对应表](evidence/proof-map.md) · [验证说明](evidence/README.md) |
| 配置环境并运行程序 | [复现指南](reproducibility/README.md) |
| 查看数据与来源 | [构造目录](constructions/catalog/results.json) · [来源说明](research/provenance.md) |

验证程序使用含 NumPy、SymPy、SageMath 和 `python-flint` 的 Python 环境，
以及 C++17 编译器。列出并运行检查：

```sh
make list
make verify
```

复算结果写入仓库旁新建的目录。`make paper` 编译论文，生成 `paper/main.pdf`。
`make source-paper` 仅导出编译论文所需的 LaTeX 源码。
[有限数据补充包](reports/en_full/certificates.zip)单独提供。
`make reports` 检查并保留已发表的直播版双语 PDF；
`make source-en`、`make source-zh` 打包对应的独立 LaTeX 工程。
`make reports-full` 在 `reports/en_full/` 和 `reports/zh_full/` 编译完整研究报告；
`make source-full-en`、`make source-full-zh` 单独打包其源码。

具体依赖和命令见[复现指南](reproducibility/README.md)。

```text
reports/           中英文报告：PDF、LaTeX、参考文献与图形
paper/             数学论文：命题、证明与结构性结论
research/          逐维探索与发现、共同数学方法与来源
constructions/     精确数据、构造族和验证程序
evidence/          验证结果及其与证明的关系
reproducibility/   环境依赖与运行说明
tools/             报告编译、复算及文件检查
tests/             数据与文档一致性测试
```

[论文《接吻数构造的大规模自主发现》](paper/main.pdf)（*Large-Scale Autonomous Discovery of Kissing Number Constructions*）
展开十九维研究中的构造原理、容量界与截面计数定理。

## 作者

杨书行、赵瑞、吴俊尧、汪易泽、陈福家、朱凯昊、李文浩、李子晨、
李亚琪、洪沈展、潘宇昂、杨俊杰、邓韬文、密金城、陈红胜*、杨怡豪*。

浙江大学信息与电子工程学院 · Qiushi Engine 求是引擎团队，中国杭州

*通讯作者：陈红胜（hansomchen@zju.edu.cn）；杨怡豪（yangyihao@zju.edu.cn）。

Qiushi Engine 的自主实验研究见
[自主光学实验平台论文](https://arxiv.org/abs/2604.27092)。

[引用](CITATION.cff) · [许可](LICENSE) · [第三方材料](constructions/third-party.md)
