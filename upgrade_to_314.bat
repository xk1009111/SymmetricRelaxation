@echo off
REM ==================================================
REM  Cell Annealing Tool - Upgrade to Python 3.14 (uv)
REM  Pure-ASCII script: safe under any console codepage.
REM ==================================================
setlocal

cd /d "%~dp0"

echo ============================================
echo  Upgrade to Python 3.14 (managed by uv)
echo ============================================
echo.

REM ---- Step 1: Install Python 3.14.6 (skip if present) ----
echo [1/5] Installing Python 3.14.6 via uv...
uv python install 3.14.6
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install Python 3.14.6. Make sure uv is installed and online.
    pause
    exit /b 1
)
echo [OK] Python 3.14.6 ready.
echo.

REM ---- Step 2: Backup old .venv (Python 3.8) ----
echo [2/5] Backing up old .venv (Python 3.8)...
if exist ".venv38.bak" (
    echo [skip] .venv38.bak already exists, skip backup.
) else if exist ".venv" (
    rename ".venv" ".venv38.bak"
    echo [OK] .venv renamed to .venv38.bak
) else (
    echo [info] No existing .venv found, will create a fresh one.
)
echo.

REM ---- Step 3: Create new .venv (Python 3.14.6) ----
echo [3/5] Creating new .venv with Python 3.14.6...
uv venv .venv --python 3.14.6
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create .venv.
    pause
    exit /b 1
)
echo [OK] .venv created.
echo.

REM ---- Step 4a: Install core dependencies (required) ----
echo [4a/5] Installing core deps: numpy scipy matplotlib openpyxl shapely pyenvelope
uv pip install --python ".venv\Scripts\python.exe" "numpy>=2.2" "scipy>=1.15" "matplotlib>=3.10" "openpyxl>=3.1" "shapely>=2.1" "pyenvelope>=0.1.0"
if %errorlevel% neq 0 (
    echo [ERROR] Core deps install failed. Paste the error above to me.
    pause
    exit /b 1
)
echo [OK] Core deps installed.
echo.

REM ---- Step 4b: Try install rpy2 (optional, failure is OK) ----
echo [4b/5] Trying to install rpy2 (optional; falls back to pure-Python if it fails)
uv pip install --python ".venv\Scripts\python.exe" "rpy2>=3.6.5"
if %errorlevel% neq 0 (
    echo [info] rpy2 not installed - likely no 3.14 Windows wheel.
    echo       Ellipse fitting will use pure Python/scipy. This is OK.
) else (
    echo [OK] rpy2 installed. R-LMG fitting available - needs R runtime.
)
echo.

REM ---- Step 5: Verify ----
echo [5/5] Verifying versions and core deps...
".venv\Scripts\python.exe" --version
echo ---
".venv\Scripts\python.exe" -c "import numpy,scipy,matplotlib,openpyxl,shapely,pyenvelope;print('numpy',numpy.__version__);print('scipy',scipy.__version__);print('matplotlib',matplotlib.__version__);print('openpyxl',openpyxl.__version__);print('shapely',shapely.__version__);print('pyenvelope OK')"
echo ---
echo rpy2 availability (detect only, no R init):
".venv\Scripts\python.exe" -c "import importlib.util as u;s=u.find_spec('rpy2');print('[OK] rpy2 installed' if s else '[info] rpy2 NOT installed, pure-Python fitting will be used')"
echo.

echo ============================================
echo  Done. Run the app with:
echo      ".venv\Scripts\python.exe" only_annealing_main.py
echo.
echo  Rollback to 3.8: delete .venv, rename .venv38.bak back to .venv
echo ============================================
pause
