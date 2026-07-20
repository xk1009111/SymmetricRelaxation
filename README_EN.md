# Cell Relaxation Tool — 细胞退火工具

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

> **[中文版](README_CN.md)**

A Python implementation of the **symmetric relaxation (annealing) algorithm** for entire 2D cellular networks. This is a focused version extracted from the complete [CellSymRelax](https://github.com/) project, containing only the core relaxation (annealing) functionality — Voronoi generation, vertex equilibration, ellipse fitting, and data export. All proliferation, topological transformation, and other extended features have been removed.

Based on:

- Xu K., Weng L., Wang Z., Lian Y., Huang B. (2026). *A symmetric relaxation method for entire two-dimensional cellular networks and its implications*. (arXiv: XuSR20260616)
- Xu K. (2021). *A geometry-based relaxation algorithm for equilibrating a trivalent polygonal network in two dimensions and its implications*. Philosophical Magazine, 101(14), 1632-1653.

---

## Features

### Voronoi Network Generation
Generate trimmed Voronoi networks:
- **Hexagon random-disordered Voronoi (n×n)** — Randomly perturb the coordinates of seed points in a regular hexagonal grid, with perturbation range confined within the hexagon, controlled by parameter *k* (0 = regular hexagons, 1 = high disorder).
- **Uniform Random Voronoi** — Based on uniformly random points.

### Symmetric Relaxation (Annealing)
Equilibrate both inner and marginal vertices via geometric symmetry:

- **Inner vertices** — Driven by central angle symmetry of associated cells, with optional interior angle symmetry (targeting 120° interior angles).
- **Marginal vertices** — Moved along boundary edges, targeting 90° for marginal angles; also influenced by central angle symmetry.
- **Configurable** — Relaxation factor (vertex movement speed), edge vertex participation toggle, and interior angle square-sum guard.

### Ellipse Fitting
- **R-LMG** (via `conicfit`) — High-precision geometric fitting, preferred for triangles and quadrilaterals.
- **Algebraic Least Squares** (numpy SVD) — Fast fitting for polygons with 5+ sides.
- Automatic fallback between methods based on fitting quality (area ratio ≤ 5).

### Data Export
Export results to Excel (`.xlsx`):
- **Ellipse & Cell perimeter and area** — Center, semi-axes, angle, cell perimeter, cell area, cell layer info (outermost = layer 1, incrementing inward).
- **Edge Angle Data** — Interior angles, adjacent edge lengths per vertex.
- **ME/MA Statistics** — Marginal edge lengths and marginal angles for boundary cells.

### Visualization
- Real-time cell network display with color-coded layers.
- Display optimal rays with centroid-vertex connections and triangles formed by three rays at each vertex.
- Ellipse overlay for fitted cells.
- Image export to EPS (vector) and PNG formats.

---

## Requirements

- **Python 3.8+** (recommended 3.10+)
- Python packages: see [requirements.txt](requirements.txt)
- **R** language environment (for R-LMG ellipse fitting via `rpy2`), optional but recommended
- R packages: `conicfit`, `sp`, `shotGroups`

---

## Installation

### Quick Start (one-command setup)

**Windows:**
```bash
setup.bat
```

**Linux / macOS:**
```bash
chmod +x setup.sh
./setup.sh
```

The script will automatically:
1. Check your Python installation.
2. Install all Python packages via `pip install -r requirements.txt`.
3. Detect the bundled `R_Dist/` portable directory and configure it.
4. Fall back to system R if not found.
5. **Automatically download and install R** if still not found (Windows/macOS).
6. Install required R packages (`conicfit`, `sp`, `shotGroups`).

### Manual Setup

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Install R and required R packages
#    Install R from https://www.r-project.org/, then:
#    Rscript -e "install.packages(c('conicfit', 'sp', 'shotGroups'))"

# 3. Run
python only_annealing_main.py
```

### Build EXE (PyInstaller)

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "CellAnnealing" ^
    --add-data "annealing;annealing" ^
    --add-data "cell;cell" ^
    --add-data "utillib;utillib" ^
    --add-data "randomSet;randomSet" ^
    --add-data "initVoronoi.py;." ^
    --hidden-import "scipy.spatial" ^
    --hidden-import "scipy.optimize" ^
    --hidden-import "openpyxl" ^
    --hidden-import "pyenvelope" ^
    only_annealing_main.py
# Output: dist/CellAnnealing.exe
```

> After building, place `R_Dist/` next to the EXE to enable R-LMG fitting.

---

## Project Structure

```
only_annealing/
├── only_annealing_main.py      # Main entry point (Tkinter GUI)
├── requirements.txt            # Python dependencies
├── setup.bat                   # Windows one-click setup script
├── setup.sh                    # Linux/macOS one-click setup script
├── build_exe.bat               # PyInstaller build script
├── .gitignore
├── .gitattributes
├── LICENSE                     # MIT License
├── README.md                   # English documentation
├── README_CN.md                # Chinese documentation
│
├── initVoronoi.py              # Voronoi network initialization
│
├── annealing/                  # Relaxation (annealing) algorithms
│   ├── AnnealingGUI.py         # Annealer core (parameterized)
│   └── annealerUtil.py         # Annealing utility functions
│
├── cell/                       # Core cell data & statistics
│   ├── CellData.py             # Cell data management
│   └── annealing_statistics.py # Annealing statistics
│
├── randomSet/                  # Random Voronoi initialization
│   └── randomInitVoronoi.py
│
└── utillib/                    # Utility libraries
    ├── mylib.py                # Core data structures (Cell, Point, Line, etc.)
    ├── fittinglib.py           # Ellipse fitting (R-LMG + least squares)
    ├── exportUtils.py          # Excel export utilities
    └── layerMarker.py          # Cell layer marking
```

---

## R Environment

The `setup.bat` / `setup.sh` scripts handle R automatically with the following priority:

| Priority | Source | Detection Method |
|---|---|---|
| 1 (best) | System R | `R_HOME` environment variable or `R` in PATH |
| 2 | Bundled `R_Dist/` | `R_Dist/bin/R` exists locally |
| 3 (fallback) | Auto-download | Script downloads and installs R automatically |

If no R environment is found, ellipse fitting falls back to pure Python (numpy/scipy least squares), which remains fully functional but may produce slightly different results for triangles and quadrilaterals.

> **Note:** `R_Dist/` is excluded from git (see `.gitignore`). Run `setup.bat` after cloning to configure R, or copy `R_Dist/` from a complete distribution.

---

## Usage

> **Note:** When running the annealing program on a regular computer, the number of cells is recommended not to exceed 400, otherwise it will be very slow or crash; after closing the graphical visualization interface, the cell limit can be moderately increased.

```bash
python only_annealing_main.py
```

The GUI provides:
1. **Voronoi Initialization** — Configure network type and parameters, then generate.
2. **Annealing** — Set relaxation factor, marginal vertex participation, and interior angle square-sum guard, then run single/multiple iterations.
3. **Optimal Rays** — Display optimal rays with centroid-vertex connections and triangles formed by three rays at each vertex.
4. **Ellipse Fitting** — Fit ellipses to all cells and overlay on display.
5. **Data Export** — Save geometric and topological parameters of all cells to three Excel files.
6. **Image Export** — Save current view as EPS or PNG via the matplotlib toolbar.

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

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## Contributors

## Project Lead & Core Algorithm Designer
- **Kai Xu (许凯)** — Project initiator, lead designer of all core algorithms, code architecture planning and design. Developed the Chinese-English bilingual GUI with the assistance of Trae.

## Core Technical Contributors
- **Guowei Shi (史国威)** — Implemented the initial foundational code and original simulated annealing prototype.
- **Lifan Weng (翁力凡), Zihan Wang (王子涵), Yuyang Lian (连钰洋), Bin Huang (黄斌)** — Conducted subsequent code refactoring, computational performance optimization, GUI functional improvement and supplementary internationalization support.

---

## Contact

**Kai Xu**
- Email: kaixu@jmu.edu.cn (primary) / kxu2013@gmail.com (secondary)
- ORCID: [0000-0002-1341-1525](https://orcid.org/0000-0002-1341-1525)
- Affiliation: Fisheries College / College of Computer Engineering, Jimei University, Xiamen, China

For questions, bug reports, or collaboration inquiries, please contact the corresponding author.