# 二维细胞网络的对称松弛方法

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

> **[English](README.md)**

本项目是用于**整个二维细胞网络的对称松弛算法**的 Python 实现，基于以下研究：

- 许凯，黄斌，翁力凡，王子涵，连钰洋 (2026). *整个二维细胞网络的对称松弛方法及其意义*. (arXiv: XuSR20260616)
- Xu K. (2021). *A geometry-based relaxation algorithm for equilibrating a trivalent polygonal network in two dimensions and its implications*. Philosophical Magazine, 101(14), 1632-1653.

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

---

## 概述

本工具包提供以下功能：

- 生成具有可控不规则度的裁剪 Voronoi 网络。
- 通过对称松弛过程平衡内部顶点和边缘顶点。
- 复现关键经验定律：von Neumann-Mullins、Aboav-Weaire 和 Lewis 定律。

---

## 功能特性

### 正六边形无规化

使用可调节的不规则参数 **k** 生成 Voronoi 网络（k=0 为正六边形，k=1 为高度无序）。

### 松弛方法

- **内部顶点**：由关联细胞的中心角对称性和内角约束驱动，目标角度 120°。
- **边缘顶点**：沿边界边移动，目标角度 90°。

### 几何分析

- 每个细胞的椭圆拟合（conicfit / 最小二乘法）。
- 计算形状指数、边长、内角、面积/周长变化。

### 定律验证

- 带几何校正项的 **von Neumann-Mullins** 定律。
- 适用于边缘细胞的 **修正 Aboav-Weaire** 定律。
- 基于椭圆最大内接多边形（EMIP）假说的 **Lewis** 定律。

---

## 算法概述

松弛过程通过逐步将顶点向目标位置移动来平衡三价多边形网络。每个顶点的运动由**两种几何对称性**控制：

### 1. 中心角对称性（细胞层面）

对于一个 n 边细胞，从其质心到各顶点的射线之间的理想夹角应为 **2π/n**，与正 n 边形一致。这种对称性驱动细胞趋向椭圆最大内接多边形（EMIP）形状，并主导遵循 von Neumann-Mullins 定律的面积变化。

### 2. 角度对称性（顶点层面）

在每个顶点处，相接边之间的内角应理想地相等。对于内部顶点（三个细胞交汇），目标为 **120°**；对于边缘顶点（两个细胞在边界交汇），目标为 **90°**。这种对称性确保局部力平衡，并与自然组织（如紫菜叶状体，Xu & He 2026）中观察到的几何形态吻合。

每个顶点同时受两种对称性影响，但由于内部顶点和边缘顶点具有不同的拓扑环境，两者的相对权重存在根本性差异。

---

## 详细顶点运动原理

### 内部顶点：由中心角对称性主导

内部顶点被三个完整细胞包围，其主要作用是优化内部的全局空间填充，同时以局部角度平衡作为次要约束。

#### 主要机制 - 中心角对称性（细胞层面）

1. 计算细胞的质心 **O**。
2. 从 **O** 出发，测量到细胞所有顶点的方向角 θ_i。
3. 应用最小二乘拟合，找到一组从 **O** 出发的 **n** 条射线，使得：
   - 相邻射线之间恰好间隔 **2π/n**。
   - 拟合射线与实际顶点方向之间的角度偏差平方和最小。
4. 从每个细胞中选出指向顶点 **V** 的拟合射线。三条选出的射线（每个细胞一条）构成一个三角形。
5. 该三角形的**质心**即为顶点 **V** 的目标位置。

该机制迫使每个细胞向其 EMIP 演化，这是复现 Lewis 定律和 Aboav-Weaire 定律的关键。

#### 次要约束 - 角度对称性（顶点层面）

在应用移动之前，算法会检查：

- 如果移动 **V** 会增加其三个内角的平方和，则取消移动。
- 如果 **V** 已经位于三条最优射线构成的三角形内，则跳过移动。

该角度约束作为调节器，防止中心角优化过度扭曲局部角度，温和地将内角驱动至 **120°**。

> **总结**：内部顶点主要由细胞层面的中心角对称性驱动（全局形状优化），而顶点层面的角度对称性作为软校正来强制实现 120°。前者是面积变化的主要引擎，后者微调局部几何形态。

---

### 边缘顶点：由角度对称性主导

边缘顶点位于网络边界上，仅与两个细胞相邻，拥有两条边界边和一条内部边。由于缺少第三个细胞，无法应用基于三角形的中心角方法。

#### 主要机制 - 角度对称性（顶点层面）

目标是通过将两个边界角驱动至 **90°** 来平滑边界：

1. 识别两个边界角中较小的那个（内部边与每条边界边之间的夹角）。
2. 沿该较小角对应的边界边，将顶点向该边的中点移动。
3. 这直接减小了两个边界角之间的差异，使其收敛至约 90°。

#### 次要机制 - 与同细胞内部顶点中心角对称性的耦合

尽管边缘顶点不使用中心角对称性来计算自身目标，但其运动与同一边缘细胞中内部顶点的中心角驱动松弛紧密耦合。两种类型的顶点（内部和边缘）通过共享的细胞几何形态相互约束，交替的松弛步骤确保细胞整体向 EMIP 演化，同时保持边界平滑。

### 内部顶点 vs. 边缘顶点运动对比

| 方面    | 内部顶点                              | 边缘顶点                                        |
| ----- | --------------------------------- | ------------------------------------------- |
| 主导对称性 | 中心角（细胞层面）                         | 角度对称性（顶点层面）                                 |
| 目标角度  | 120°（三细胞交汇）                       | 90°（双细胞边界交汇）                                |
| 目标位置  | 三条最优射线构成三角形的质心                    | 较小角对应边界边的中点                                 |
| 次要约束  | 禁止增加角度平方和的移动；若已在三角形内则跳过；内角 < 180° | 若边界角差低于阈值则跳过（n≥4 为 20°，n=3 为 60°）；内角 < 180° |

---

## 环境要求

- **Python 3.8+**
- Python 包：详见 [requirements.txt](requirements.txt)
- **R** 语言环境（通过 `rpy2` 进行椭圆拟合）
- R 包：`conicfit`、`sp`、`shotGroups`（从 CRAN 安装）

---

## 安装

### 快速开始（一键安装）

运行自动安装脚本，一次性安装所有 Python 和 R 依赖：

**Windows：**

```bash
setup.bat
```

**Linux / macOS：**

```bash
chmod +x setup.sh && ./setup.sh
```

该脚本会自动执行以下操作：

1. 检查 Python 安装。
2. 通过 `pip install -r requirements.txt` 安装所有 Python 包。
3. 检测项目自带的 **R_Dist/** 目录，自动配置环境。
4. 如果 R_Dist 不存在，回退使用系统 R。
5. 如果没有任何 R 环境，**自动下载安装 R**（Windows/macOS），或指引安装（Linux）。
6. 安装所需的 R 包（`conicfit`、`sp`、`shotGroups`）。

### 手动安装（分步说明）

#### 1. 克隆仓库

```bash
git clone https://github.com/your-username/Formal_Cell_Change.git
cd Formal_Cell_Change
```

#### 2. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

#### 3. 安装 R 及所需 R 包

从 [https://www.r-project.org/](https://www.r-project.org/) 安装 R，然后打开 R 控制台运行：

```R
install.packages(c("conicfit", "sp", "shotGroups"))
```

#### 4. 运行

```bash
python unifiedMain.py
```

---

## 项目结构

```
Formal_Cell_Change/
├── unifiedMain.py              # 主入口（Tkinter GUI）
├── proliferation.py            # 细胞增殖模式
├── topologicalChange.py        # 拓扑变换模式
├── initVoronoi.py              # Voronoi 网络初始化
├── ellipseFitting.py           # 椭圆拟合工具
├── myRandom.py                 # 随机网络生成器
├── test_beta_type.py           # Beta 类型测试脚本
│
├── cell/                       # 核心细胞数据与统计
│   ├── CellData.py
│   └── annealing_statistics.py
│
├── annealing/                  # 退火（松弛）算法
│   ├── Annealing.py
│   ├── AnnealingGUI.py
│   └── annealerUtil.py
│
├── topological/                # 拓扑变换
│   ├── Topological.py
│   ├── TopologicalGUI.py
│   └── TopologicalUtil.py
│
├── split/                      # 细胞分裂
│   ├── Split.py
│   ├── SplitGUI.py
│   └── splitUtil.py
│
├── randomSet/                  # 随机 Voronoi 初始化
│   └── randomInitVoronoi.py
│
├── utillib/                    # 工具库
│   ├── mylib.py                # 核心数据结构（Cell, Point, Line 等）
│   ├── fittinglib.py           # 圆锥曲线拟合（R 接口）
│   ├── exportUtils.py          # Excel 导出工具
│   ├── commonlib.py            # 通用工具
│   └── layerMarker.py          # 图层标记
│
├── MyThread.py                 # 自定义线程支持
│
├── requirements.txt            # Python 依赖
├── setup.bat                   # Windows 一键安装脚本
├── setup.sh                    # Linux/macOS 一键安装脚本
├── README_CN.md                # 本文件
├── LICENSE                     # MIT 许可证
└── .gitignore                  # Git 忽略规则
```

---

## 使用方法

运行主 GUI 应用程序：

```bash
python unifiedMain.py
```

GUI 提供以下功能按钮：

- **初始化 (Init)** - 初始化 Voronoi 网络
- **退火（单步/批量）(Anneal)** - 执行松弛迭代
- **分裂 (Split)** - 激活细胞增殖模式
- **拓扑变换 (Topological Change)** - 启用拓扑变换
- **导出 (Export)** - 将结果保存至 Excel

---

## 引用

如果在学术工作中使用此代码，请引用：

```
Xu K., Weng L., Wang Z., Lian Y., Huang B. (2026). A symmetric relaxation
method for entire two-dimensional cellular networks and its implications.
arXiv: XuSR20260616.
```

```
Xu K. (2021). A geometry-based relaxation algorithm for equilibrating a
trivalent polygonal network in two dimensions and its implications.
Philosophical Magazine, 101(14), 1632-1653.
```

---

## 联系方式

许凯 (Kai Xu)**

- 邮箱：kaixu@jmu.edu.cn（主要）/ kxu2013@gmail.com
- ORCID：[0000-0002-1341-1525](https://orcid.org/0000-0002-1341-1525)
- 单位：集美大学水产学院 / 计算机工程学院，厦门，中国

如有问题、报告 bug 或合作咨询，请联系通讯作者。
