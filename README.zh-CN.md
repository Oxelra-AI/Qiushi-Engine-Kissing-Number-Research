# Qiushi Engine：接吻数新下界的自主发现

[English](README.md) · [中文报告](reports/zh/main.pdf) · [英文报告](reports/en/main.pdf) · [成果](research/results.md) · [研究脉络](research/README.zh-CN.md) · [复现](reproducibility/README.md)

**72小时连续长程自主科研，全程公开直播。**

Qiushi Engine 自主数学研究取得 **10 个维数的接吻数新下界**，覆盖 **32–39、43、45维**。

云栖大会期间，浙江大学联合阿里云开展了72小时自主科研直播，
从北京时间2026年9月22日08:00持续至9月25日08:00。
Qiushi Engine 自主研读文献、提出并检验构造、调整研究方向、验证数学对象，
将持续探索的科研过程向公众展开。
[《杭州日报》](https://hznews.hangzhou.com.cn/kejiao/content/2026-09/23/content_9314105.htm)将此次活动报道为
国内首次以全程公开直播方式，让AI连续72小时自主挑战开放前沿数学问题。
活动介绍见[直播说明](research/livestream.md)。

科学发现需要在答案与路径尚不明确时，决定下一步研究什么。
在这次挑战中，Qiushi Engine 围绕一个开放的数学目标，贯通编码理论、格几何与
组合数学，通过持续自主研究形成新的构造与证明。

研究的关键认识在于：即使一个构型已受到严密约束，改变各部分的组织方式，仍可能
打开新的增长空间。联合替换使无法逐个加入的点能够共同进入构型；另一格壳提供
新的相容方向；精确矩关系则使小规模见证能够揭示庞大构型的点数。
这些发现体现了不同数学结构之间的联系所带来的创造空间。
报告展开其中的思想与论证，开放数据与程序让读者能够重建、检验并继续发展这些成果。

## 数学成果

接吻数问题问的是：多少个相同大小的球能够同时接触中心球，而彼此不重叠？
归一化后，接吻构型等价于两两内积不超过二分之一的单位向量集。
下表每一行都给出一个点数更大的构型，从而提高相应维数的接吻数下界。
公开比较值记录于2026年9月24日至25日，相应[固定来源](constructions/catalog/comparison-sources.json)与数据一同提供。

| 维数 | 下界 | 公开比较值 | 增加 |
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

## 逐维探索与发现

每个维度都有独立的研究叙述，从所面对的数学问题出发，讲清候选如何产生、约束为何阻碍
改进、中间构造如何形成，以及最终方法如何解决问题。33维的十个新支持如何共享九个阻挡？
36维的符号搜索如何变成四色设计？45维成功构造的四面体几何又如何联系不同候选族？

[32](research/dimensions/32.zh-CN.md) · [33](research/dimensions/33.zh-CN.md) · [34](research/dimensions/34.zh-CN.md) · [35](research/dimensions/35.zh-CN.md) · [36](research/dimensions/36.zh-CN.md) · [37](research/dimensions/37.zh-CN.md) · [38](research/dimensions/38.zh-CN.md) · [39](research/dimensions/39.zh-CN.md) · [43](research/dimensions/43.zh-CN.md) · [45](research/dimensions/45.zh-CN.md)

[研究总览](research/README.zh-CN.md)说明各维度之间的联系，并提供中英文逐维文档。
文档直接连接具体构造、保存的交换及重建程序，让研究思路与数学对象相互对应。

## 构造思想

在分层码中，一组新支持的价值取决于它们共同排斥哪些旧支持：同一旧支持只需删除一次。
联合优化这一代价，可以获得逐个插入无法得到的净增益。配对 Hadamard 变换进一步把
权四符号码转移为相容的权八构型，并将其嵌入满足边界条件的局部坐标区域，得到35至37维的
局部改进。其中，35维的局部码达到了所用十一坐标模型的容量上界。

38维的研究利用 Leech 格提升构型留下的赤道空间。相容的新方向来自极小壳之外的范数48壳层；
选出的144条反极直线提供288个新点。证明同时控制这些方向的内部内积以及它们与全部提升点的
交叉内积，得到591900点构型。

43维和45维将球面设计的矩恒等式用于格截面计数，把涉及52416000个格向量的计数问题
化为有限的有理恒等式。嵌入的 $E_8$ 截面确定 $D_5$ 子截面正交壳的规模，给出2553792点。
45维则建立关于选定纤维的矩不等式，使其中每个见证对下界作出正贡献；共同邻点搜索得到
298个见证，从而推出 $7377408+9\times298=7380090$。

| 维数 | 数据与验证 | 数学研究脉络 |
|---|---|---|
| 32–37, 39 | [支持与局部符号替换](constructions/codes/) | [支持与局部符号替换](research/trajectory/codes.md) |
| 38 | [赤道补充](constructions/d38/) | [赤道补充](research/trajectory/equatorial.md) |
| 43, 45 | [格截面与设计矩](constructions/sections/) | [格截面与设计矩](research/trajectory/sections.md) |

[研究报告](reports/README.md)按上述顺序展开数学论证；
[研究脉络](research/README.zh-CN.md)连接构造原理、搜索选择、中间对象与最终结果。
有限数据附有坐标约定和数学来源。

## 阅读与复现

| 阅读目的 | 入口 |
|---|---|
| 理解结果、几何证明与各构造的关系 | [中文报告](reports/zh/main.pdf) · [English report](reports/en/main.pdf) |
| 理解构造如何形成 | [逐维探索与发现](research/README.zh-CN.md) |
| 检查精确输入及证明条件 | [验证说明](evidence/README.md) |
| 配置环境并运行程序 | [复现指南](reproducibility/README.md) |
| 查看数据与来源 | [构造目录](constructions/catalog/results.json) · [来源说明](research/provenance.md) |

准备含 NumPy、SymPy、SageMath 的 Python 环境和 C++17 编译器后，运行：

```sh
make list
make verify
```

复算结果写入仓库旁新建的目录。执行 `make reports` 编译双语 PDF；
`make source-en`、`make source-zh` 生成可独立编译的 LaTeX 工程。
具体依赖和命令见[复现指南](reproducibility/README.md)。

```text
reports/           中英文报告：PDF、LaTeX、参考文献与图形
research/          逐维探索与发现、共同数学方法与来源
constructions/     精确数据、构造族和验证程序
evidence/          验证结果及其与证明的关系
reproducibility/   环境依赖与运行说明
tools/             报告编译、复算及文件检查
tests/             数据与文档一致性测试
```

## 作者

杨书行、赵瑞、吴俊尧、汪易泽、陈福家、朱凯昊、李文浩、李子晨、
李亚琪、洪沈展、潘宇昂、杨俊杰、邓韬文、密金城、陈红胜*、杨怡豪*。

浙江大学信息与电子工程学院 · Qiushi Engine 求是引擎团队，中国杭州

*通讯作者：陈红胜（hansomchen@zju.edu.cn）；杨怡豪（yangyihao@zju.edu.cn）。

Qiushi Engine 的自主实验研究见
[自主光学实验平台论文](https://arxiv.org/abs/2604.27092)。

[引用](CITATION.cff) · [许可](LICENSE) · [第三方材料](constructions/third-party.md)
