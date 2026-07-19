# 修复日志

## 修复日期：2026-07-19

### 修复内容概述

本次修复解决了以下问题：

1. **界面字体统一设置**：所有控件字体最小为18号，包括坐标显示
2. **工具栏按钮优化**：从emoji图标改为文字按钮，支持框选放大、移动、重置视图、保存
3. **Voronoi图显示优化**：坐标轴字号改为18号，删除默认标题
4. **图片保存权限问题**：默认保存路径改为桌面，避免权限问题
5. **英文翻译换行调整**：多个长短语添加换行，避免拥挤
6. **数值输入框宽度调整**：统一调整为6字符宽度
7. **参数名称更新**：退火速率改为退火因子 (γ)
8. **布局优化**：n和k参数分开到两行，工具栏按钮padding更紧凑

---

### 修复详情

#### 1. 界面字体统一设置

**文件**：`only_annealing_main.py`

**问题**：界面字体大小不一致，部分控件字体过小

**修复**：修改 `_f()` 和 `_apply_font_scale()` 方法，确保所有控件字体最小为18号
```python
def _f(self, base_size, attrs=()):
    s = self.font_scale.get()
    scaled = max(18, int(round(18 * s)))
    return (self._default_font, scaled) + tuple(attrs)
```

#### 2. 工具栏按钮重构

**文件**：`only_annealing_main.py`

**问题**：matplotlib工具栏按钮样式不可控，按钮偏小，悬浮提示文字太小

**修复**：
- 创建自定义Tkinter工具栏框架
- 替换为文字按钮：框选放大、移动、重置视图、保存
- 设置按钮字体为18号，padding更紧凑
- 添加坐标显示标签（18号字体）

#### 3. Voronoi图显示优化

**文件**：`only_annealing_main.py`

**问题**：坐标轴字号太小，标题显示"cell visualization"

**修复**：
- 设置 `ax.tick_params(labelsize=18)`
- 删除 `ax.set_title()` 调用

#### 4. 图片保存路径修复

**文件**：`only_annealing_main.py`

**问题**：保存图片到主目录时提示需要管理员权限

**修复**：修改默认保存路径为桌面
```python
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
initial_dir = desktop_path if os.path.exists(desktop_path) else os.path.expanduser("~")
```

#### 5. 英文翻译换行调整

**文件**：`utillib/i18n.py`

**问题**：长英文短语显示拥挤

**修复**：
- `hexagon random-disordered Voronoi (n×n)` → `hexagon random-disordered\nVoronoi (n×n)`
- `Include Marginal Vertices in Annealing:` → `Include Marginal Vertices\nin Annealing:`

#### 6. 参数名称更新

**文件**：`utillib/i18n.py`

**问题**："退火速率"术语不准确

**修复**：
- 中文：`退火速率 (0~1):` → `退火因子 (γ):`
- 英文：`Annealing Rate (0~1):` → `Relaxation factor (γ):`

#### 7. 布局优化

**文件**：`only_annealing_main.py`

**问题**：n和k参数挤在同一行，工具栏按钮间距过大

**修复**：
- 创建独立的 `row2` 框架，将k参数移到第二行
- 工具栏按钮padding从 `padx=8, pady=4` 改为 `padx=4, pady=2`
- 按钮间距从 `padx=4` 改为 `padx=2`

---

### 影响的文件列表

| 文件 | 修改类型 |
|------|----------|
| `only_annealing_main.py` | 主要修改 |
| `utillib/i18n.py` | 翻译更新 |

---

### 验证结果

- [x] 所有控件字体最小为18号
- [x] 工具栏按钮正常显示（框选放大、移动、重置视图、保存）
- [x] 坐标显示字号为18号
- [x] Voronoi图坐标轴字号为18号，无标题
- [x] 图片可保存到桌面（无权限问题）
- [x] 英文翻译换行显示正常
- [x] n和k参数分开到两行
- [x] 工具栏按钮空间紧凑

---

## 修复日期：2026-07-17

### 修复内容概述

本次修复解决了以下问题：

1. **额外弹出窗口问题**：程序启动时出现多个空窗口
2. **字体异常变大问题**：Windows 高 DPI 环境下字体显示异常
3. **参数传递问题**：随机扰动模式下 k 值和种子数无法修改
4. **界面切换问题**：无法从"随机扰动"切换到"均匀随机"模式

---

### 修复详情

#### 1. Windows DPI 感知设置

**文件**：`only_annealing_main.py`

**问题**：Windows 高 DPI 显示器下，Tkinter 窗口自动缩放导致字体变大

**修复**：在导入 tkinter 之前添加 DPI 感知设置
```python
if sys.platform == 'win32':
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
```

#### 2. 提前初始化 Tk 根窗口

**文件**：`only_annealing_main.py`

**问题**：matplotlib 导入时可能创建额外的 Tk 根窗口

**修复**：在导入 matplotlib 之前创建 Tk 根窗口并设置全局缩放
```python
root = tk.Tk()
root.withdraw()
root.tk.call('tk', 'scaling', 1.0)
```

#### 3. 移除未使用的 plt 导入

**文件**：`cell/CellData.py`

**问题**：导入 `matplotlib.pyplot as plt` 但未使用，导致创建额外窗口

**修复**：移除未使用的导入语句

#### 4. 参数传递修复

**文件**：`only_annealing_main.py`、`initVoronoi.py`

**问题**：参数通过字典传递，导致参数值无法正确更新

**修复**：
- 修改 `ViroinitData` 函数签名，接受直接参数
- 在调用处直接读取 Entry 控件的值
- 修改 `getCells` 函数，确保参数正确转换和传递

#### 5. 界面切换修复

**文件**：`only_annealing_main.py`

**问题**：使用 StringVar 绑定 Radiobutton 导致界面切换失效

**修复**：
- 移除 StringVar 绑定
- 使用 `current_mode` 变量追踪当前模式
- 创建独立的 `_switch_to_grid()` 和 `_switch_to_random()` 方法

#### 6. Matplotlib 配置修复

**文件**：`only_annealing_main.py`

**问题**：使用 `plt` 导致额外窗口

**修复**：
- 移除 `import matplotlib.pyplot as plt`
- 改用 `import matplotlib` 和 `matplotlib.rcParams`
- 使用 `Figure()` 代替 `plt.figure()`
- 将 toolbar 从 `'toolmanager'` 改为 `'toolbar2'`

---

### 影响的文件列表

| 文件 | 修改类型 |
|------|----------|
| `only_annealing_main.py` | 主要修改 |
| `cell/CellData.py` | 移除未使用的导入 |
| `initVoronoi.py` | 参数传递修复 |
| `fix_patch.diff` | 已更新 |

---

### 验证结果

- [x] 程序启动只显示一个主窗口
- [x] 字体大小正常（Windows 高 DPI 环境）
- [x] 随机扰动模式下 k 值和种子数可修改
- [x] 可在"随机扰动"和"均匀随机"模式间切换
- [x] 图片保存功能正常
