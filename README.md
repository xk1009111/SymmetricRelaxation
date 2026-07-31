# Symmetric Relaxation of 2D Cellular Networks

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

> **[中文版](README_CN.md)**

A Python implementation of symmetric relaxation algorithms for entire 2D cellular networks, as described in:

- Xu K.,Huang B, Weng L., Wang Z., Lian Y (2026). *A symmetric relaxation method for entire two-dimensional cellular networks and its implications*. (arXiv: XuSR20260616)
- Xu K. (2021). *A geometry-based relaxation algorithm for equilibrating a trivalent polygonal network in two dimensions and its implications*. Philosophical Magazine, 101(14), 1632-1653.

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Overview

This package provides tools to:

- Generate trimmed Voronoi networks with controllable irregularity.
- Equilibrate both inner and marginal vertices via a symmetric relaxation process.
- Reproduce key empirical laws: von Neumann-Mullins, Aboav-Weaire, and Lewis.

---

## Features

### Regular Hexagon Disordering

Generate Voronoi networks with a prescribed irregularity parameter **k** (0 = regular hexagons, 1 = high disorder).

### Relaxation Methods

- **Inner vertices**: governed by central angle symmetry of associated cells and interior angle constraint (targeting 120°).
- **Marginal vertices**: moved along boundary edges, targeting 90° for two-cell vertices.

### Geometric Analysis

- Ellipse fitting (conicfit / least squares) for each cell.
- Compute shape index, edge length, interior angle, area/perimeter changes.

### Law Validation

- **von Neumann-Mullins** with geometric correction term.
- **Modified Aboav-Weaire** for marginal cells.
- **Lewis law** via ellipse maximum inscribed polygon (EMIP) hypothesis.

---

## Algorithm Overview

The relaxation process equilibrates a trivalent polygonal network by moving vertices stepwise toward target positions. The motion of each vertex is governed by **two geometric symmetries**:

### 1. Central Angle Symmetry (Cell Level)

For an n-sided cell, the ideal angles between rays from its centroid to its vertices should be **2π/n**, as in a regular n-gon. This symmetry drives cells toward ellipse maximum inscribed polygon (EMIP) shapes and is responsible for area changes obeying the von Neumann-Mullins law.

### 2. Angle Symmetry (Vertex Level)

At each vertex, the interior angles between incident edges should ideally be equal. For inner vertices (three cells meet), the target is **120°**; for marginal vertices (two cells meet on the boundary), the target is **90°**. This symmetry ensures local force balance and matches observed geometries in natural tissues (e.g., *Pyropia* thalli, Xu & He 2026).

Although every vertex is influenced by both symmetries, the relative weights differ fundamentally between inner and marginal vertices due to their distinct topological environments.

---

## Detailed Vertex Motion Principle

### Inner Vertices: Dominated by Central Angle Symmetry

An inner vertex is surrounded by three complete cells. Its primary role is to optimise the global space filling of the interior, while maintaining local angle equilibration as a secondary constraint.

#### Primary mechanism - Central angle symmetry (cell level)

1. Compute the cell's centroid **O**.
2. From **O**, measure the directions (angles θ_i) to all vertices of the cell.
3. Apply least squares fitting to find a set of **n** rays starting at **O** such that:
   - Adjacent rays are separated by exactly **2π/n**.
   - The sum of squared angular deviations between the fitted rays and the actual vertex directions is minimised.
4. From each cell, select the fitted ray that points towards the vertex **V**. The three selected rays (one per cell) form a triangle.
5. The **centroid of this triangle** is the target position for **V**.

This mechanism forces each cell to evolve toward its EMIP, which is the key to reproducing Lewis's law and Aboav-Weaire's law.

#### Secondary constraint - Angle symmetry (vertex level)

Before applying a move, the algorithm checks:

- If moving **V** would increase the sum of squares of its three interior angles, the move is cancelled.
- If **V** already lies within the triangle formed by the three optimal rays, the move is skipped.

This angle constraint acts as a regulator that prevents the central angle optimisation from over-distorting local angles. It gently drives interior angles toward **120°**.

> **In summary**: Inner vertices are primarily driven by cell-level central angle symmetry (global shape optimisation), while vertex-level angle symmetry serves as a soft correction to enforce 120°. The former is the main engine for area changes; the latter fine-tunes the local geometry.

---

### Marginal Vertices: Dominated by Angle Symmetry

Marginal vertices lie on the network boundary and are adjacent to only two cells. They have two boundary edges and one internal edge. Because the third cell is missing, the triangle-based central angle approach cannot be applied.

#### Primary mechanism - Angle symmetry (vertex level)

The goal is to smooth the boundary by driving the two boundary angles toward **90°**:

1. Identify the smaller of the two boundary angles (between the internal edge and each boundary edge).
2. Move the vertex along the boundary edge corresponding to that smaller angle toward the midpoint of that edge.
3. This directly reduces the disparity between the two boundary angles, converging them to ~90°.

#### Secondary mechanism - Coupling with central-angle symmetry of co-cell inner vertices

Although a marginal vertex does not use central-angle symmetry to compute its own target, its movement is tightly coupled with the central-angle-driven relaxation of the inner vertices belonging to the same marginal cell. The two types of vertices - inner and marginal - are mutually constrained through the shared cell geometry. Their alternating relaxation steps ensure that the cell as a whole moves toward its EMIP while its boundary remains smooth.

### Comparison: Inner vs. Marginal Vertex Motion

| Aspect               | Inner Vertex                                                                                             | Marginal Vertex                                                                                     |
| -------------------- | -------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| Dominant symmetry    | Central angle (cell level)                                                                               | Angle symmetry (vertex level)                                                                       |
| Target angle         | 120° (three-cell junction)                                                                               | 90° (two-cell boundary junction)                                                                    |
| Target position      | Centroid of triangle from three optimal rays                                                             | Midpoint of boundary edge with smaller angle                                                        |
| Secondary constraint | Forbid moves that increase sum of squared angles; skip if already inside triangle; interior angle < 180° | Skip if boundary angle difference below threshold (20° for n≥4, 60° for n=3); interior angle < 180° |

---

## Requirements

- **Python 3.8+**
- Python packages: see [requirements.txt](requirements.txt)
- **R** language environment (for ellipse fitting via `rpy2`)
- R packages: `conicfit`, `sp`, `shotGroups` (install from CRAN)

---

## Installation

### Quick Start (one-command setup)

Run the automated setup script to install all Python and R dependencies at once:

**Windows:**

```bash
setup.bat
```

**Linux / macOS:**

```bash
chmod +x setup.sh
./setup.sh
```

The script will:

1. Check your Python installation.
2. Install all Python packages via `pip install -r requirements.txt`.
3. Detect the bundled **R_Dist/** directory automatically and configure it.
4. If R_Dist is not found, fall back to the system R installation.
5. If no R is found, **automatically download and install R** (Windows/macOS) or guide you through installation (Linux).
6. Install the required R packages (`conicfit`, `sp`, `shotGroups`).

### Manual Setup (step by step)

#### 1. Clone the repository

```bash
git clone https://github.com/your-username/Formal_Cell_Change.git
cd Formal_Cell_Change
```

#### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

#### 3. Install R and required R packages

Install R from [https://www.r-project.org/](https://www.r-project.org/), then open an R console and run:

```R
install.packages(c("conicfit", "sp", "shotGroups"))
```

#### 4. Run

```bash
python unifiedMain.py
```

---

## Project Structure

```
Formal_Cell_Change/
├── unifiedMain.py              # Main entry point (Tkinter GUI)
├── proliferation.py            # Cell proliferation mode
├── topologicalChange.py        # Topological change mode
├── initVoronoi.py              # Voronoi network initialization
├── ellipseFitting.py           # Ellipse fitting utilities
├── myRandom.py                 # Random network generator
├── test_beta_type.py           # Beta type test script
│
├── cell/                       # Core cell data & statistics
│   ├── CellData.py
│   └── annealing_statistics.py
│
├── annealing/                  # Annealing (relaxation) algorithms
│   ├── Annealing.py
│   ├── AnnealingGUI.py
│   └── annealerUtil.py
│
├── topological/                # Topological transformation
│   ├── Topological.py
│   ├── TopologicalGUI.py
│   └── TopologicalUtil.py
│
├── split/                      # Cell splitting
│   ├── Split.py
│   ├── SplitGUI.py
│   └── splitUtil.py
│
├── randomSet/                  # Random Voronoi initialization
│   └── randomInitVoronoi.py
│
├── utillib/                    # Utility libraries
│   ├── mylib.py                # Core data structures (Cell, Point, Line, etc.)
│   ├── fittinglib.py           # Conic fitting (R interface)
│   ├── exportUtils.py          # Excel export utilities
│   ├── commonlib.py            # Common utilities
│   └── layerMarker.py          # Layer marking
│
├── MyThread.py                 # Custom threading support
│
├── requirements.txt            # Python dependencies
├── setup.bat                   # Windows one-click setup script
├── setup.sh                    # Linux/macOS one-click setup script
├── README.md                   # This file
├── LICENSE                     # MIT License
└── .gitignore                  # Git ignore rules
```

---

## Usage

Run the main GUI application:

```bash
python unifiedMain.py
```

The GUI provides buttons for:

- **Init** - Initialize a Voronoi network
- **Anneal (Step/Batch)** - Perform relaxation iterations
- **Split** - Activate cell proliferation mode
- **Topological Change** - Enable topological transformations
- **Export** - Save results to Excel

---

## Citation

If you use this code in academic work, please cite:

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

## Contact

**Kai Xu**

- Email: kaixu@jmu.edu.cn (primary) / kxu2013@gmail.com
- ORCID: [0000-0002-1341-1525](https://orcid.org/0000-0002-1341-1525)
- Affiliation: Fisheries College / College of Computer Engineering, Jimei University, Xiamen, China

For questions, bug reports, or collaboration inquiries, please contact the corresponding author.
