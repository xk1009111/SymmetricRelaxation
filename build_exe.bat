@echo off
chcp 65001 >nul
title 构建细胞退火工具 EXE

echo ============================================
echo  细胞退火工具 - PyInstaller 打包脚本
echo ============================================
echo.

REM 切换到脚本所在目录
cd /d "%~dp0"

REM 安装依赖（如已安装可跳过）
echo [1/3] 检查并安装依赖...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo 安装依赖失败，请检查网络连接或手动安装。
    pause
    exit /b 1
)

REM 安装 PyInstaller
echo [2/3] 检查 PyInstaller...
pip install pyinstaller
if %errorlevel% neq 0 (
    echo 安装 PyInstaller 失败。
    pause
    exit /b 1
)

REM 执行打包
echo [3/3] 开始打包...
echo.
echo 正在打包为单文件 EXE（无控制台窗口）...
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

if %errorlevel% equ 0 (
    echo.
    echo ============================================
    echo  ✓ 打包成功！
    echo   输出文件: dist\CellAnnealing.exe
    echo ============================================
) else (
    echo.
    echo  × 打包失败，请检查错误信息。
)

pause
