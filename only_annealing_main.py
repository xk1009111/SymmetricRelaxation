"""
细胞退火专用工具 - 仅保留退火核心功能
======================================
基于 unifiedMain.py 精简而来，移除了以下功能：
- T1 邻居交换 / T2 三角形消失 / T3 细胞增殖
- 网格演化（细胞增殖 + 二维泡沫）
- 拓扑变换
- 谱系追踪颜色标记
- 单细胞模式

仅保留：
1. 维诺图初始化（随机扰动 n×n / 均匀随机）
2. 细胞退火（含辅助线显示）
3. 椭圆拟合
4. 数据导出（椭圆数据 / 边角数据 / ME-MA 数据）
5. 细胞可视化

可直接通过 PyInstaller 打包为 exe。
"""
import os
import sys
import random
import math
import time
import shutil
import datetime
import warnings

# Windows DPI 感知设置（必须在导入 tkinter 之前）
if sys.platform == 'win32':
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

# 强制切换工作目录到脚本所在位置
current_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_dir)
sys.path.append(current_dir)

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog

# 初始化 Tk 根窗口（必须在导入 matplotlib 之前）
root = tk.Tk()
root.withdraw()
root.tk.call('tk', 'scaling', 1.0)

import matplotlib
matplotlib.use('TkAgg')
matplotlib.interactive(False)
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np

style = ttk.Style()
style.theme_use('clam')
style.configure('TButton', font=(('Microsoft YaHei' if sys.platform == 'win32' else 'Arial'), 18), padding=(20, 15))
style.configure('TLabel', font=(('Microsoft YaHei' if sys.platform == 'win32' else 'Arial'), 18))
style.configure('TFrame', font=(('Microsoft YaHei' if sys.platform == 'win32' else 'Arial'), 18))

# 导入核心模块
import initVoronoi as Viro
from annealing.AnnealingGUI import Annealer
import annealing.annealerUtil as anneal_util
from cell.CellData import CellData
import utillib.layerMarker as layerMarker
import utillib.exportUtils as exportUtils
import utillib.i18n as i18n
_ = i18n._

warnings.filterwarnings("ignore")

matplotlib.rcParams['toolbar'] = 'toolbar2'
matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False
matplotlib.rcParams['figure.dpi'] = 100
matplotlib.rcParams['font.size'] = 18

# ============================================================================
# 全局变量
# ============================================================================
cellData = None
annealer = None
cellSeed = None
param2 = None


# ============================================================================
# 工具函数
# ============================================================================

def get_ellipse(e_x, e_y, a, b, e_angle):
    """计算椭圆点"""
    angles_circle = np.arange(0, 2 * np.pi, 0.01)
    x, y = [], []
    for angles in angles_circle:
        or_x = a * math.cos(angles)
        or_y = b * math.sin(angles)
        length_or = math.sqrt(or_x * or_x + or_y * or_y)
        or_theta = math.atan2(or_y, or_x)
        new_theta = or_theta + e_angle
        new_x = e_x + length_or * math.cos(new_theta)
        new_y = e_y + length_or * math.sin(new_theta)
        x.append(new_x)
        y.append(new_y)
    return x, y


def ViroinitData(cell_seed_str, param_str, param2_str='0'):
    """维诺图初始化"""
    global param2, cellSeed

    cellSeed = cell_seed_str
    param = param_str
    param2 = param2_str

    print(f'[ViroinitData] param={param}, cellSeed={cellSeed}, param2={param2}')

    if not cellSeed.isdigit() or int(cellSeed) < 3:
        raise ValueError("种子值需为数字且大于3")

    param_float = float(param)
    if param_float < 0.0 or param_float > 1.0:
        raise ValueError("扰乱参数需介于0.0到1.0之间")

    param2_int = int(param2)
    if param2_int < 0 or param2_int > int((int(cellSeed) - 1) / 2):
        raise ValueError(f"边缘层数需在0到{int((int(cellSeed) - 1) / 2)}之间")

    cells = Viro.getCells(param, param2, cellSeed)

    for cell in cells:
        for i in range(0, len(cell.points)):
            cell.points[i] = cell.points[i].tolist()

    return cells


# ============================================================================
# 主界面类
# ============================================================================

class AnnealingGUI:
    """细胞退火专用图形界面"""

    def __init__(self, root):
        self.root = root
        self.root.title("细胞退火工具")
        self.root.geometry("1600x900")

        # 快照（用于回退）
        self.cells_snapshot = None

        # 字体缩放比例（1.0 = 100%）
        self.font_scale = tk.DoubleVar(value=1.0)
        # 存储所有 font= 参数引用 (widget, base_size, attrs_tuple)
        self._font_widgets = []
        self.font_scale.trace_add('write', lambda *_: self._apply_font_scale())

        # 系统默认字体
        if sys.platform == 'win32':
            self._default_font = 'Microsoft YaHei'
        else:
            self._default_font = 'Arial'

        # 创建主布局
        self._create_layout()

        # 初始化 matplotlib
        self._init_matplotlib()

    # ── 字体缩放辅助 ──
    def _f(self, base_size, attrs=()):
        """返回缩放后的字体：使用系统默认字体"""
        s = self.font_scale.get()
        scaled = max(18, int(round(18 * s)))
        return (self._default_font, scaled) + tuple(attrs)

    def _reg_font(self, widget, base_size, attrs=()):
        """注册控件（字体随缩放更新）。"""
        self._font_widgets.append((widget, base_size, attrs))

    def _apply_font_scale(self, *args):
        """将当前缩放比例应用到所有已注册控件。"""
        s = self.font_scale.get()
        for w, base, attrs in self._font_widgets:
            try:
                scaled = max(18, int(round(18 * s)))
                w.config(font=(self._default_font, scaled) + tuple(attrs))
            except Exception:
                pass

    def _change_font(self, delta=None, reset=False):
        """调整字体缩放比例。delta = ±0.1，reset = True 恢复 1.0。"""
        if reset:
            self.font_scale.set(1.0)
        else:
            new_val = round(self.font_scale.get() + delta, 1)
            new_val = max(0.5, min(2.0, new_val))  # 50% ~ 200%
            self.font_scale.set(new_val)
        self._apply_font_scale()
        pct = int(round(self.font_scale.get() * 100))
        try:
            self._font_size_label.config(text=f"{pct}%")
        except Exception:
            pass

    def _create_layout(self):
        """创建主布局"""
        # 左侧参数面板
        self.left_frame = tk.Frame(self.root, width=520, bg='#f0f0f0')
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        self.left_frame.pack_propagate(False)

        # 右侧显示区域
        self.right_frame = tk.Frame(self.root, bg='#f0f0f0')
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 右侧：画布 + 统计信息
        self.right_canvas_frame = tk.Frame(self.right_frame, bg='white')
        self.right_stats_frame = tk.Frame(self.right_frame, bg='#f0f0f0', width=350)
        self.right_stats_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(4, 2), pady=2)
        self.right_stats_frame.pack_propagate(False)
        self.right_canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(2, 4), pady=2)

        # === 左侧面板内容 ===
        # 标题和语言切换按钮
        title_frame = tk.Frame(self.left_frame, bg='#f0f0f0')
        title_frame.pack(pady=10, fill=tk.X)
        
        lbl_title = tk.Label(title_frame, text=_('main_panel_title'),
                 font=self._f(20, ('bold',)), bg='#f0f0f0')
        self._lbl_title = lbl_title
        lbl_title.pack(side=tk.LEFT, padx=5)
        self._reg_font(lbl_title, 20, ('bold',))

        # 语言切换按钮（放在标题旁边）
        self._lang_frame = tk.Frame(title_frame, bg='#f0f0f0')
        self._lang_frame.pack(side=tk.RIGHT, padx=5)
        
        lang_font_zh = (self._default_font, 18, 'bold') if i18n.get_current_language() == 'zh' else (self._default_font, 18)
        self._lang_label_zh = tk.Button(self._lang_frame, text="中文",
                                        font=lang_font_zh, fg='red', bg='#f0f0f0',
                                        relief=tk.FLAT, padx=0, pady=0,
                                        command=self._toggle_language)
        self._lang_label_zh.pack(side=tk.LEFT)
        
        self._lang_label_sep = tk.Label(self._lang_frame, text="/",
                                        font=(self._default_font, 18), fg='red', bg='#f0f0f0')
        self._lang_label_sep.pack(side=tk.LEFT)
        
        lang_font_en = (self._default_font, 18, 'bold') if i18n.get_current_language() == 'en' else (self._default_font, 18)
        self._lang_label_en = tk.Button(self._lang_frame, text="English",
                                        font=lang_font_en, fg='red', bg='#f0f0f0',
                                        relief=tk.FLAT, padx=0, pady=0,
                                        command=self._toggle_language)
        self._lang_label_en.pack(side=tk.LEFT)

        # ── 字体大小控制栏（固定在顶部） ──
        font_ctl = tk.Frame(self.left_frame, bg='#e8e8e8', height=32)
        font_ctl.pack(side=tk.TOP, fill=tk.X, padx=5, pady=(2, 2))
        font_ctl.pack_propagate(False)
        self._lbl_font = tk.Label(font_ctl, text=_('font_label'), bg='#e8e8e8',
                 font=self._f(14))
        self._lbl_font.pack(side=tk.LEFT, padx=(6, 2))
        self._reg_font(self._lbl_font, 14)
        btn_smaller = tk.Button(font_ctl, text="A−", font=self._f(14, ('bold',)),
                                relief=tk.FLAT, bg='#e8e8e8', padx=4, pady=0,
                                command=lambda: self._change_font(-0.1))
        btn_smaller.pack(side=tk.LEFT, padx=1)
        self._reg_font(btn_smaller, 14, ('bold',))
        btn_larger = tk.Button(font_ctl, text="A+", font=self._f(14, ('bold',)),
                               relief=tk.FLAT, bg='#e8e8e8', padx=4, pady=0,
                               command=lambda: self._change_font(0.1))
        btn_larger.pack(side=tk.LEFT, padx=1)
        self._reg_font(btn_larger, 14, ('bold',))
        self._font_size_label = tk.Label(font_ctl, text="100%", bg='#e8e8e8',
                                         font=self._f(14), width=5)
        self._font_size_label.pack(side=tk.LEFT, padx=(2, 6))
        self._reg_font(self._font_size_label, 14)
        self._font_reset_btn = tk.Button(font_ctl, text=_('font_reset'), font=self._f(14),
                  relief=tk.FLAT, bg='#e8e8e8', padx=4, pady=0,
                  command=lambda: self._change_font(reset=True))
        self._font_reset_btn.pack(side=tk.LEFT)
        self._reg_font(self._font_reset_btn, 14)

        # ── 滚动区域（垂直 + 水平滚动条） ──
        # 容器：外框 + 内 canvas
        scroll_container = tk.Frame(self.left_frame, bg='#f0f0f0')
        scroll_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        canvas_scroll = tk.Canvas(scroll_container, bg='#f0f0f0',
                                  width=500, highlightthickness=0)
        v_scrollbar = ttk.Scrollbar(scroll_container, orient="vertical",
                                    command=canvas_scroll.yview)
        h_scrollbar = ttk.Scrollbar(scroll_container, orient="horizontal",
                                    command=canvas_scroll.xview)
        self.scrollable_frame = tk.Frame(canvas_scroll, bg='#f0f0f0')

        self.scrollable_frame.bind("<Configure>",
            lambda e: canvas_scroll.configure(scrollregion=canvas_scroll.bbox("all")))
        canvas_scroll.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas_scroll.configure(yscrollcommand=v_scrollbar.set,
                                xscrollcommand=h_scrollbar.set)

        # 网格布局：canvas 占满，vbar 在右，hbar 在底
        canvas_scroll.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        scroll_container.grid_rowconfigure(0, weight=1)
        scroll_container.grid_columnconfigure(0, weight=1)

        # 绑定鼠标滚轮（垂直 + Shift=水平）
        def _on_mousewheel(event):
            try:
                if event.state & 0x1:  # Shift 按下 → 水平滚动
                    canvas_scroll.xview_scroll(-int(event.delta / 120), "units")
                else:
                    canvas_scroll.yview_scroll(-int(event.delta / 120), "units")
            except Exception:
                pass

        def _on_enter(event):
            canvas_scroll.bind_all("<MouseWheel>", _on_mousewheel)

        def _on_leave(event):
            canvas_scroll.unbind_all("<MouseWheel>")

        self.scrollable_frame.bind("<Enter>", _on_enter)
        self.scrollable_frame.bind("<Leave>", _on_leave)

        # === 细胞生成区域 ===
        self._create_cell_generation_section()

        # === 退火参数区域 ===
        self._create_annealing_section()

        # === 底部操作按钮 ===
        self._create_action_buttons()

        # === 右侧统计面板 ===
        self._create_stats_panel()

    def _create_cell_generation_section(self):
        """创建细胞生成参数区域"""
        gen_frame = tk.LabelFrame(self.scrollable_frame, text=_('voronoi_init'),
                                  font=self._f(16, ('bold',)), bg='#f0f0f0')
        self._gen_frame = gen_frame
        gen_frame.pack(fill=tk.X, padx=10, pady=5)
        self._reg_font(gen_frame, 16, ('bold',))

        type_frame = tk.Frame(gen_frame, bg='#f0f0f0')
        type_frame.pack(fill=tk.X, padx=8, pady=4)
        w_lbl_type = tk.Label(type_frame, text=_('voronoi_type'), bg='#f0f0f0',
                 font=self._f(14))
        w_lbl_type.pack(side=tk.LEFT)
        self._reg_font(w_lbl_type, 14)
        self._w_lbl_type = w_lbl_type

        type_row1 = tk.Frame(type_frame, bg='#f0f0f0')
        type_row1.pack(fill=tk.X)

        self.current_mode = 'grid'
        w_rb_grid = tk.Radiobutton(type_row1, text=_('voronoi_grid'), value="grid",
                       bg='#f0f0f0', font=self._f(14),
                       command=self._switch_to_grid)
        w_rb_grid.pack(side=tk.LEFT, padx=4)
        w_rb_grid.select()
        self._reg_font(w_rb_grid, 14)
        self._w_rb_grid = w_rb_grid

        type_row2 = tk.Frame(type_frame, bg='#f0f0f0')
        type_row2.pack(fill=tk.X)

        w_rb_random = tk.Radiobutton(type_row2, text=_('voronoi_random'), value="random",
                       bg='#f0f0f0', font=self._f(14),
                       command=self._switch_to_random)
        w_rb_random.pack(side=tk.LEFT, padx=4)
        self._reg_font(w_rb_random, 14)
        self._w_rb_random = w_rb_random

        # 参数区域容器
        self.params_container = tk.Frame(gen_frame, bg='#f0f0f0')
        self.params_container.pack(fill=tk.X, padx=8, pady=2)
        
        # 随机扰动 n×n 参数
        self.grid_frame = tk.Frame(self.params_container, bg='#f0f0f0')
        self.grid_frame.pack(fill=tk.X)
        row1 = tk.Frame(self.grid_frame, bg='#f0f0f0')
        row1.pack(fill=tk.X)
        w_lbl_seed = tk.Label(row1, text=_('voronoi_seed'), bg='#f0f0f0',
                 font=self._f(14))
        w_lbl_seed.pack(side=tk.LEFT)
        self._reg_font(w_lbl_seed, 14)
        self._w_lbl_seed = w_lbl_seed

        self.voronoi_seed = tk.StringVar(value="10")
        self.w_ent_seed = tk.Entry(row1, textvariable=self.voronoi_seed, width=6,
                 font=self._f(14))
        self.w_ent_seed.pack(side=tk.LEFT, padx=4)
        self._reg_font(self.w_ent_seed, 14)

        row2 = tk.Frame(self.grid_frame, bg='#f0f0f0')
        row2.pack(fill=tk.X)
        w_lbl_k = tk.Label(row2, text=_('voronoi_param'), bg='#f0f0f0',
                 font=self._f(14))
        w_lbl_k.pack(side=tk.LEFT)
        self._reg_font(w_lbl_k, 14)
        self._w_lbl_k = w_lbl_k
        self.voronoi_param = tk.StringVar(value="0.6")
        self.w_ent_param = tk.Entry(row2, textvariable=self.voronoi_param, width=6,
                 font=self._f(14))
        self.w_ent_param.pack(side=tk.LEFT, padx=4)
        self._reg_font(self.w_ent_param, 14)

        # 均匀随机维诺图参数（只保留种子点数）
        self.random_frame = tk.Frame(self.params_container, bg='#f0f0f0')
        row_r = tk.Frame(self.random_frame, bg='#f0f0f0')
        row_r.pack(fill=tk.X)
        w_lbl_rand_n = tk.Label(row_r, text=_('random_seed'), bg='#f0f0f0',
                 font=self._f(14))
        w_lbl_rand_n.pack(side=tk.LEFT)
        self._reg_font(w_lbl_rand_n, 14)
        self._w_lbl_rand_n = w_lbl_rand_n
        self.random_voronoi_seed = tk.StringVar(value="400")
        self.w_ent_rand_n = tk.Entry(row_r, textvariable=self.random_voronoi_seed, width=6,
                 font=self._f(14))
        self.w_ent_rand_n.pack(side=tk.LEFT, padx=4)
        self._reg_font(self.w_ent_rand_n, 14)

        # 初始化按钮
        self.init_btn = tk.Button(gen_frame, text=_('generate_voronoi'),
                                  command=self._init_system,
                                  font=self._f(14), bg='#2196F3', fg='white',
                                  padx=10, pady=4)
        self.init_btn.pack(pady=8)
        self._reg_font(self.init_btn, 14)

        # 初始显示随机扰动界面
        self._switch_to_grid()

    def _switch_to_grid(self):
        """切换到随机扰动模式"""
        self.current_mode = 'grid'
        self.grid_frame.pack(fill=tk.X)
        self.random_frame.pack_forget()
        self.params_container.update_idletasks()

    def _switch_to_random(self):
        """切换到均匀随机模式"""
        self.current_mode = 'random'
        self.grid_frame.pack_forget()
        self.random_frame.pack(fill=tk.X)
        self.params_container.update_idletasks()

    def _create_annealing_section(self):
        """创建退火参数区域"""
        anneal_frame = tk.LabelFrame(self.scrollable_frame, text=_('cell_annealer'),
                                     font=self._f(16, ('bold',)), bg='#f0f0f0')
        anneal_frame.pack(fill=tk.X, padx=10, pady=5)
        self._reg_font(anneal_frame, 16, ('bold',))
        self._anneal_frame = anneal_frame

        # 退火速率
        rate_frame = tk.Frame(anneal_frame, bg='#f0f0f0')
        rate_frame.pack(fill=tk.X, padx=8, pady=4)
        w_lbl_rate = tk.Label(rate_frame, text=_('anneal_rate'), bg='#f0f0f0',
                 font=self._f(14))
        w_lbl_rate.pack(side=tk.LEFT)
        self._reg_font(w_lbl_rate, 14)
        self._w_lbl_rate = w_lbl_rate

        self.anneal_rate = tk.StringVar(value="0.1")
        w_ent_rate = tk.Entry(rate_frame, textvariable=self.anneal_rate, width=6,
                 font=self._f(14))
        w_ent_rate.pack(side=tk.LEFT, padx=4)
        self._reg_font(w_ent_rate, 14)

        # 退火轮次
        w_lbl_times = tk.Label(rate_frame, text=_('anneal_times'), bg='#f0f0f0',
                 font=self._f(14))
        w_lbl_times.pack(side=tk.LEFT, padx=(10, 0))
        self._reg_font(w_lbl_times, 14)
        self._w_lbl_times = w_lbl_times

        self.anneal_times = tk.StringVar(value="1")
        w_ent_times = tk.Entry(rate_frame, textvariable=self.anneal_times, width=6,
                 font=self._f(14))
        w_ent_times.pack(side=tk.LEFT, padx=4)
        self._reg_font(w_ent_times, 14)

        # 边缘顶点参与退火
        edge_frame = tk.Frame(anneal_frame, bg='#f0f0f0')
        edge_frame.pack(fill=tk.X, padx=8, pady=2)
        w_lbl_edge = tk.Label(edge_frame, text=_('anneal_edge'), bg='#f0f0f0',
                 font=self._f(14))
        w_lbl_edge.pack(side=tk.LEFT)
        self._reg_font(w_lbl_edge, 14)
        self._w_lbl_edge = w_lbl_edge

        self.anneal_edge = tk.StringVar(value="1")
        w_rb_edge_yes = tk.Radiobutton(edge_frame, text=_('yes'), value="1",
                       variable=self.anneal_edge, bg='#f0f0f0',
                       font=self._f(14))
        w_rb_edge_yes.pack(side=tk.LEFT, padx=4)
        self._reg_font(w_rb_edge_yes, 14)
        self._w_rb_edge_yes = w_rb_edge_yes

        w_rb_edge_no = tk.Radiobutton(edge_frame, text=_('no'), value="0",
                       variable=self.anneal_edge, bg='#f0f0f0',
                       font=self._f(14))
        w_rb_edge_no.pack(side=tk.LEFT, padx=4)
        self._reg_font(w_rb_edge_no, 14)
        self._w_rb_edge_no = w_rb_edge_no

        # 内角平方和守卫
        self.anneal_inner_angle_guard = tk.IntVar(value=1)
        w_chk_angle = tk.Checkbutton(anneal_frame,
                       text=_('inner_vertices_hint'),
                       variable=self.anneal_inner_angle_guard,
                       bg='#f0f0f0', font=self._f(14),
                       wraplength=400)
        w_chk_angle.pack(fill=tk.X, padx=8, pady=4)
        self._reg_font(w_chk_angle, 14)
        self._w_chk_angle = w_chk_angle

        # 退火按钮
        self.anneal_btn = tk.Button(anneal_frame, text=_('execute_annealing'),
                                    command=self._run_anneal,
                                    font=self._f(14), bg='#FF9800',
                                    fg='white', padx=10, pady=4)
        self.anneal_btn.pack(pady=8)
        self._reg_font(self.anneal_btn, 14)

    def _create_action_buttons(self):
        """创建底部操作按钮"""
        btn_frame = tk.Frame(self.scrollable_frame, bg='#f0f0f0')
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        # 独立功能按钮（横向排列）
        row = tk.Frame(btn_frame, bg='#f0f0f0')
        row.pack(fill=tk.X)

        self.aux_btn = tk.Button(row, text=_('auxiliary_lines'),
                                 command=self._show_auxiliary_lines,
                                 font=self._f(14), bg='#9C27B0',
                                 fg='white', padx=8, pady=3)
        self.aux_btn.pack(side=tk.LEFT, padx=2)
        self._reg_font(self.aux_btn, 14)

        self.ellipse_btn = tk.Button(row, text=_('ellipse_fitting'),
                                     command=self._ellipse_fit,
                                     font=self._f(14), bg='#4CAF50',
                                     fg='white', padx=8, pady=3)
        self.ellipse_btn.pack(side=tk.LEFT, padx=2)
        self._reg_font(self.ellipse_btn, 14)

        self.export_btn = tk.Button(row, text=_('export_data'),
                                    command=self._export_data,
                                    font=self._f(14), bg='#607D8B',
                                    fg='white', padx=8, pady=3)
        self.export_btn.pack(side=tk.LEFT, padx=2)
        self._reg_font(self.export_btn, 14)

        self.undo_btn = tk.Button(row, text=_('undo'),
                                  command=self._undo,
                                  font=self._f(14), bg='#FF5722',
                                  fg='white', padx=8, pady=3)
        self.undo_btn.pack(side=tk.LEFT, padx=2)
        self._reg_font(self.undo_btn, 14)

    def _create_stats_panel(self):
        """创建右侧统计面板"""
        self.stats_title = tk.Label(self.right_stats_frame,
                                    text=_('statistics'),
                                    font=self._f(18, ('bold',)),
                                    bg='#f0f0f0', anchor='w')
        self.stats_title.pack(side=tk.TOP, fill=tk.X,
                              padx=10, pady=(10, 6), anchor='n')
        self._reg_font(self.stats_title, 18, ('bold',))

        def _make_group(title_text):
            lf = tk.LabelFrame(self.right_stats_frame, text=title_text,
                               bg='#f0f0f0', font=self._f(14))
            lf.pack(side=tk.TOP, fill=tk.X, padx=10, pady=(0, 10))
            self._reg_font(lf, 14)
            val = tk.Label(lf, text="--", bg='#f0f0f0',
                           font=self._f(14), justify=tk.LEFT, anchor='w')
            val.pack(side=tk.TOP, fill=tk.X, padx=10, pady=8)
            self._reg_font(val, 14)
            return lf, val

        self.stats_group_internal, self.stats_value_internal = _make_group(
            _('inner_vertices_stat'))
        self.stats_group_edge, self.stats_value_edge = _make_group(
            _('edge_vertices_stat'))
        self.stats_group_cells, self.stats_value_cells = _make_group(
            _('total_cells'))

        self._update_stats_panel()

    def _update_stats_panel(self, internal_vertices_total=None,
                            last_anneal_internal=None,
                            edge_vertices_total=None,
                            last_anneal_edge=None,
                            cell_total=None):
        """更新统计面板"""
        if not hasattr(self, 'stats_value_internal'):
            return

        def _safe(val):
            if val is None:
                return '--'
            return str(val)

        self.stats_value_internal.config(
            text=f"{_safe(internal_vertices_total)} / {_safe(last_anneal_internal)}")
        self.stats_value_edge.config(
            text=f"{_safe(edge_vertices_total)} / {_safe(last_anneal_edge)}")
        self.stats_value_cells.config(
            text=_safe(cell_total))

    def _vertex_internal_edge_totals(self):
        """计算内部/边缘顶点数"""
        global cellData
        if cellData is None or not getattr(cellData, 'cells', None):
            return None, None
        try:
            def _pt_key(p):
                try:
                    x = float(p[0])
                    y = float(p[1])
                except Exception:
                    x = float(getattr(p, 'x'))
                    y = float(getattr(p, 'y'))
                return (round(x, 8), round(y, 8))

            all_vertex_keys = set()
            for cell in cellData.cells:
                for pt in cell.points:
                    all_vertex_keys.add(_pt_key(pt))
            edge_vertices = anneal_util.get_all_edge_vertices(cellData.cells)
            edge_vertex_keys = {_pt_key(pt) for pt in edge_vertices}
            edge_total = len(edge_vertex_keys)
            internal_total = len(all_vertex_keys - edge_vertex_keys)
            return internal_total, edge_total
        except Exception:
            return None, None

    def _init_matplotlib(self):
        """初始化 matplotlib 画布"""
        self.fig = Figure(figsize=(12, 8))
        self.canvas = FigureCanvasTkAgg(self.fig, self.right_canvas_frame)
        self.canvas.draw()

        class ImageExportToolbar(NavigationToolbar2Tk):
            def save_figure(self, *args):
                desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
                initial_dir = desktop_path if os.path.exists(desktop_path) else os.path.expanduser("~")
                
                file_path = filedialog.asksaveasfilename(
                    title=_('save_image'),
                    initialdir=initial_dir,
                    defaultextension=".eps",
                    filetypes=[(_('eps_vector'), "*.eps"), (_('png_image'), "*.png")]
                )
                if not file_path:
                    return
                ext = os.path.splitext(file_path)[1].lower()
                if ext not in ('.eps', '.png'):
                    ext = '.eps'
                    file_path += ext
                save_format = ext.lstrip('.')
                try:
                    self.canvas.draw()
                    self.canvas.figure.savefig(file_path, format=save_format,
                                                dpi=300, bbox_inches='tight')
                    if (not os.path.exists(file_path)) or os.path.getsize(file_path) <= 0:
                        raise IOError(_('error_save_file').format(file_path=file_path))
                    messagebox.showinfo(_('success_save'), _('success_save_path').format(file_path=file_path), parent=self.parent.root)
                except PermissionError:
                    messagebox.showerror(_('error_save'), _('error_save_permission').format(file_path=file_path), parent=self.parent.root)
                except Exception as e:
                    messagebox.showerror(_('error_save'), _('error_export_image').format(str_e=str(e)), parent=self.parent.root)

        self.toolbar = ImageExportToolbar(self.canvas, self.right_canvas_frame)
        self.toolbar.parent = self
        self.toolbar.pack_forget()

        self.toolbar_frame = tk.Frame(self.right_canvas_frame, bg='#e8e8e8')
        self.toolbar_frame.pack(side=tk.TOP, fill=tk.X)

        btn_font = (self._default_font, 18)

        self.rect_zoom_btn = tk.Button(self.toolbar_frame, text=_('toolbar_rect_zoom'), font=btn_font,
                                        command=lambda: self.toolbar.zoom(),
                                        padx=4, pady=2, bg='white', relief=tk.RAISED)
        self.rect_zoom_btn.pack(side=tk.LEFT, padx=2)

        self.pan_btn = tk.Button(self.toolbar_frame, text=_('toolbar_pan'), font=btn_font,
                                  command=lambda: self.toolbar.pan(),
                                  padx=4, pady=2, bg='white', relief=tk.RAISED)
        self.pan_btn.pack(side=tk.LEFT, padx=2)

        self.reset_btn = tk.Button(self.toolbar_frame, text=_('toolbar_reset_view'), font=btn_font,
                                    command=lambda: self.toolbar.home(),
                                    padx=4, pady=2, bg='white', relief=tk.RAISED)
        self.reset_btn.pack(side=tk.LEFT, padx=2)

        self.save_btn = tk.Button(self.toolbar_frame, text=_('toolbar_save'), font=btn_font,
                                  command=lambda: self.toolbar.save_figure(),
                                  padx=4, pady=2, bg='white', relief=tk.RAISED)
        self.save_btn.pack(side=tk.LEFT, padx=2)

        self.coord_label = tk.Label(self.toolbar_frame, text="", font=(self._default_font, 18),
                                    bg='#e8e8e8', padx=10)
        self.coord_label.pack(side=tk.RIGHT)

        def on_mouse_move(event):
            try:
                x, y = event.xdata, event.ydata
                if x is not None and y is not None:
                    self.coord_label.config(text=f"X: {x:.2f}, Y: {y:.2f}")
            except Exception:
                pass

        self.canvas.mpl_connect('motion_notify_event', on_mouse_move)

        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    # ========================================================================
    # 核心功能方法
    # ========================================================================

    def _init_system(self):
        """初始化系统：生成维诺图 + 初始化退火器"""
        global cellData, annealer, cellSeed, param2

        try:
            subtype = self.current_mode
            
            self.w_ent_seed.update()
            self.w_ent_param.update()
            self.w_ent_rand_n.update()
            
            seed_val = self.w_ent_seed.get().strip()
            k_val = self.w_ent_param.get().strip()
            rand_seed_val = self.w_ent_rand_n.get().strip()
            
            print(f'[_init_system] subtype={subtype}, seed={seed_val}, k={k_val}, random_seed={rand_seed_val}')

            if subtype == 'grid':
                if not seed_val or not k_val:
                    messagebox.showerror(_('error_missing_params'), _('error_fill_voronoi'), parent=self.root)
                    return
                
                if not seed_val.isdigit() or int(seed_val) < 3:
                    messagebox.showerror(_('error'), _('error_seed_valid'), parent=self.root)
                    return
                
                try:
                    k_float = float(k_val)
                    if k_float < 0.0 or k_float > 1.0:
                        messagebox.showerror(_('error'), _('error_irregularity_range'), parent=self.root)
                        return
                except ValueError:
                    messagebox.showerror(_('error'), _('error_irregularity_number').format(k_val=k_val), parent=self.root)
                    return

                print(f'[_init_system] 准备生成随机扰动维诺图: n={seed_val}, k={k_float}')
            else:
                if not rand_seed_val:
                    messagebox.showerror(_('error_missing_params'), _('error_fill_seeds'), parent=self.root)
                    return

            if cellData and getattr(cellData, 'cells', None):
                ok = messagebox.askyesno(_('confirm'), _('confirm_overwrite'), parent=self.root)
                if not ok:
                    return

            if subtype == 'random':
                n = int(rand_seed_val)
                scale = None
                print(f'[_init_system] 准备生成均匀随机维诺图: n={n}')
                cells = Viro.getCellsBySource('random', n=n, scale=scale)
                for cell in cells:
                    for i in range(len(cell.points)):
                        cell.points[i] = cell.points[i].tolist() if hasattr(
                            cell.points[i], 'tolist') else list(cell.points[i])
                cellSeed = str(n)
                param2 = '0'
            else:
                cells = ViroinitData(seed_val, k_val, '0')
                cellSeed = seed_val
                param2 = '0'

            cellData = CellData(cells)
            cellData.flush(isGrow=True)

            # 2.5. 计算完整的层号（确保母细胞层和当前层使用相同的算法）
            layerMarker.layer_mark2(cellData.cells, cellSeed)

            # 3. 初始化退火器
            try:
                anneal_params = {
                    'annealingRate': float(self.anneal_rate.get()),
                    'edge_judge': int(self.anneal_edge.get()),
                    'inner_angle_sq_guard': int(self.anneal_inner_angle_guard.get())
                }
                annealer = Annealer(anneal_params)
            except Exception:
                annealer = Annealer()

            # 4. 保存初始层数
            for cell in cellData.cells:
                if not hasattr(cell, 'original_layer'):
                    cell.original_layer = cell.layer

            # 5. 显示
            self._display()

            # 6. 更新统计
            internal_total, edge_total = self._vertex_internal_edge_totals()
            self._update_stats_panel(
                internal_vertices_total=internal_total,
                last_anneal_internal=0,
                edge_vertices_total=edge_total,
                last_anneal_edge=0,
                cell_total=len(cellData.cells)
            )

            messagebox.showinfo(_('success'), _('success_init'), parent=self.root)

        except Exception as e:
            messagebox.showerror(_('error'), _('error_init').format(error=str(e)), parent=self.root)
            import traceback
            traceback.print_exc()

    def _run_anneal(self):
        """执行多次退火"""
        global cellData, annealer
        if cellData is None:
            messagebox.showwarning(_('warning'), _('warning_generate_first'), parent=self.root)
            return

        # 保存快照
        self._save_snapshot()

        # 校验参数
        rate_str = self.anneal_rate.get().strip()
        edge_str = self.anneal_edge.get().strip()
        if not rate_str or edge_str not in ('0', '1'):
            messagebox.showerror(_('error_missing_params'), _('error_fill_voronoi'), parent=self.root)
            return

        try:
            anneal_params = {
                'annealingRate': float(rate_str),
                'edge_judge': int(edge_str),
                'inner_angle_sq_guard': int(self.anneal_inner_angle_guard.get())
            }
            annealer = Annealer(anneal_params)
        except Exception as e:
            messagebox.showerror(_('error'), _('error_param').format(error=str(e)), parent=self.root)
            return

        times = 1
        try:
            times = max(1, int(self.anneal_times.get() or '1'))
        except Exception:
            times = 1

        for i in range(times):
            annealer.annealing(cellData.cells)
            cellData.flush(isGrow=True)

            internal_total, edge_total = self._vertex_internal_edge_totals()
            self._update_stats_panel(
                internal_vertices_total=internal_total,
                last_anneal_internal=int(getattr(annealer, 'internal_vertices', 0) or 0),
                edge_vertices_total=edge_total,
                last_anneal_edge=int(getattr(annealer, 'edge_vertices', 0) or 0),
                cell_total=len(cellData.cells)
            )
            self._display()

            if i < times - 1:
                self.root.update()
                time.sleep(0.5)

        if times == 1:
            messagebox.showinfo(_('complete'), _('complete_annealing'), parent=self.root)

    def _show_auxiliary_lines(self):
        """显示退火辅助线"""
        global cellData, annealer
        if cellData is None:
            messagebox.showwarning(_('warning'), _('warning_generate_first'), parent=self.root)
            return

        self._save_snapshot()

        try:
            # 补全辅助线数据
            for cell in cellData.cells:
                max_distance = anneal_util.get_distance_centerpoint_point(cell)
                if not hasattr(cell, 'actual_lines') or not getattr(cell, 'actual_lines', None):
                    cell.actual_lines = anneal_util.get_actual_lines(cell, max_distance)
                if not hasattr(cell, 'pre_best_lines') or not getattr(cell, 'pre_best_lines', None):
                    delta = anneal_util.get_best_rotate_delta_by_calculation(cell)
                    cell.pre_best_lines = anneal_util.get_pre_best_lines(cell, max_distance, delta)

            intersection_cell_blocks = []
            try:
                intersection_cell_blocks = anneal_util.get_intersection_cell_blocks(cellData.cells)
            except Exception:
                pass

            self._display(show_auxiliary_lines=True,
                          intersection_cell_blocks=intersection_cell_blocks)
        except Exception as e:
            messagebox.showerror(_('error'), _('error_display_rays').format(error=str(e)), parent=self.root)

    def _ellipse_fit(self):
        """椭圆拟合"""
        global cellData
        if cellData is None:
            messagebox.showwarning(_('warning'), _('warning_generate_first'), parent=self.root)
            return

        self._save_snapshot()

        try:
            for c in cellData.cells:
                c.like_ellipse(1)
            cellData.list_line_of_cell()
            self._display(show_ellipse=True)
        except Exception as e:
            messagebox.showerror(_('error'), _('error_ellipse').format(error=str(e)), parent=self.root)

    def _export_data(self):
        """输出数据到 Excel"""
        global cellData, annealer, param2
        if cellData is None:
            messagebox.showwarning(_('warning'), _('warning_generate_first'), parent=self.root)
            return

        try:
            cellData.list_line_of_cell()
            for c in cellData.cells:
                c.like_ellipse(1)
        except Exception as e:
            messagebox.showerror(_('error'), _('error_export_prepare').format(error=str(e)), parent=self.root)
            return

        file_path = filedialog.asksaveasfilename(
            title=_('save_data'),
            defaultextension=".xlsx",
            filetypes=[(_('excel_workbook'), "*.xlsx"), (_('all_files'), "*.*")]
        )
        if not file_path:
            return

        directory = os.path.dirname(file_path) or os.getcwd()
        base_name = os.path.splitext(os.path.basename(file_path))[0] or "export"
        timestamp = int(time.time())
        edge_judge = getattr(annealer, 'edge_judge', 1) if annealer else 1

        try:
            ignore = int(float(param2)) if param2 is not None else 0
        except Exception:
            ignore = 0
        N = getattr(cellData, 'length', len(cellData.cells))

        try:
            success = exportUtils.create(
                "export", cellData.cells, cellData.lineOfCell,
                edge_judge, N, ignore, currentTimes=timestamp
            )
            if not success:
                messagebox.showerror(_('error'), _('error_export'), parent=self.root)
                return

            src_ellipse = f"ellipse_{timestamp}.xlsx"
            src_edge = f"edgeAngle_{timestamp}.xlsx"
            src_me_ma = f"export_ME_MA_{timestamp}.xlsx"
            if not all(os.path.exists(f) for f in [src_ellipse, src_edge, src_me_ma]):
                messagebox.showerror(_('error'), _('error_export_not_found'), parent=self.root)
                return

            shutil.move(src_ellipse, os.path.join(directory, f"{base_name}_ellipse.xlsx"))
            shutil.move(src_edge, os.path.join(directory, f"{base_name}_edgeAngle.xlsx"))
            shutil.move(src_me_ma, os.path.join(directory, f"{base_name}_ME_MA.xlsx"))

            messagebox.showinfo(_('success'), _('success_export'), parent=self.root)
        except Exception as e:
            messagebox.showerror(_('error'), f"{_('error_export')}：{str(e)}", parent=self.root)

    def _undo(self):
        """回退到上次操作前的快照"""
        if self.cells_snapshot is None:
            messagebox.showinfo(_('warning'), _('error_no_snapshot'), parent=self.root)
            return

        ok = messagebox.askyesno(_('confirm'), _('confirm_undo'), parent=self.root)
        if ok:
            if self._restore_snapshot():
                messagebox.showinfo(_('success'), _('success_undo'), parent=self.root)
            else:
                messagebox.showerror(_('error'), _('error_undo'), parent=self.root)

    def _toggle_language(self):
        """切换语言"""
        current = i18n.get_current_language()
        new_lang = 'en' if current == 'zh' else 'zh'
        i18n.set_language(new_lang)
        self._update_all_text()

    def _update_all_text(self):
        """更新所有界面文本"""
        global _
        _ = i18n._

        if hasattr(self, '_lbl_title'):
            self._lbl_title.config(text=_('main_panel_title'))
        if hasattr(self, '_lbl_font'):
            self._lbl_font.config(text=_('font_label'))
        if hasattr(self, '_gen_frame'):
            s = self.font_scale.get()
            scaled = max(18, int(round(18 * s)))
            self._gen_frame.config(text=_('voronoi_init'), font=(self._default_font, scaled, 'bold'))
        if hasattr(self, '_w_lbl_type'):
            self._w_lbl_type.config(text=_('voronoi_type'))
        if hasattr(self, '_w_rb_grid'):
            self._w_rb_grid.config(text=_('voronoi_grid'))
        if hasattr(self, '_w_rb_random'):
            self._w_rb_random.config(text=_('voronoi_random'))
        if hasattr(self, '_w_lbl_k'):
            self._w_lbl_k.config(text=_('voronoi_param'))
        if hasattr(self, '_w_lbl_seed'):
            self._w_lbl_seed.config(text=_('voronoi_seed'))
        if hasattr(self, '_w_lbl_rand_n'):
            self._w_lbl_rand_n.config(text=_('random_seed'))
        if hasattr(self, 'init_btn'):
            self.init_btn.config(text=_('generate_voronoi'))
        if hasattr(self, '_anneal_frame'):
            s = self.font_scale.get()
            scaled = max(18, int(round(18 * s)))
            self._anneal_frame.config(text=_('cell_annealer'), font=(self._default_font, scaled, 'bold'))
        if hasattr(self, '_w_lbl_rate'):
            self._w_lbl_rate.config(text=_('anneal_rate'))
        if hasattr(self, '_w_lbl_times'):
            self._w_lbl_times.config(text=_('anneal_times'))
        if hasattr(self, '_w_lbl_edge'):
            self._w_lbl_edge.config(text=_('anneal_edge'))
        if hasattr(self, '_w_rb_edge_yes'):
            self._w_rb_edge_yes.config(text=_('yes'))
        if hasattr(self, '_w_rb_edge_no'):
            self._w_rb_edge_no.config(text=_('no'))
        if hasattr(self, '_w_chk_angle'):
            self._w_chk_angle.config(text=_('inner_vertices_hint'))
        if hasattr(self, 'anneal_btn'):
            self.anneal_btn.config(text=_('execute_annealing'))
        if hasattr(self, 'aux_btn'):
            self.aux_btn.config(text=_('auxiliary_lines'))
        if hasattr(self, 'ellipse_btn'):
            self.ellipse_btn.config(text=_('ellipse_fitting'))
        if hasattr(self, 'export_btn'):
            self.export_btn.config(text=_('export_data'))
        if hasattr(self, 'undo_btn'):
            self.undo_btn.config(text=_('undo'))
        if hasattr(self, 'stats_title'):
            self.stats_title.config(text=_('statistics'))
        if hasattr(self, 'stats_group_internal'):
            self.stats_group_internal.config(text=_('inner_vertices_stat'))
        if hasattr(self, 'stats_group_edge'):
            self.stats_group_edge.config(text=_('edge_vertices_stat'))
        if hasattr(self, 'stats_group_cells'):
            self.stats_group_cells.config(text=_('total_cells'))
        if hasattr(self, '_lang_label_zh') and hasattr(self, '_lang_label_en'):
            current_lang = i18n.get_current_language()
            s = self.font_scale.get()
            scaled = max(18, int(round(18 * s)))
            if current_lang == 'zh':
                self._lang_label_zh.config(font=(self._default_font, scaled, 'bold'))
                self._lang_label_en.config(font=(self._default_font, scaled))
            else:
                self._lang_label_zh.config(font=(self._default_font, scaled))
                self._lang_label_en.config(font=(self._default_font, scaled, 'bold'))
        if hasattr(self, 'root'):
            self.root.title(_('window_title'))
        
        if hasattr(self, 'rect_zoom_btn'):
            self.rect_zoom_btn.config(text=_('toolbar_rect_zoom'))
        if hasattr(self, 'pan_btn'):
            self.pan_btn.config(text=_('toolbar_pan'))
        if hasattr(self, 'reset_btn'):
            self.reset_btn.config(text=_('toolbar_reset_view'))
        if hasattr(self, 'save_btn'):
            self.save_btn.config(text=_('toolbar_save'))
        
        if hasattr(self, '_font_reset_btn'):
            self._font_reset_btn.config(text=_('font_reset'))

    def _save_snapshot(self):
        """保存当前细胞状态快照"""
        global cellData
        if cellData is None or not hasattr(cellData, 'cells'):
            self.cells_snapshot = None
            return
        try:
            snap = []
            for c in cellData.cells:
                pts = [[p[0], p[1]] if isinstance(p, (list, tuple))
                       else [p.x, p.y] for p in c.points]
                snap.append(pts)
            self.cells_snapshot = snap
        except Exception:
            self.cells_snapshot = None

    def _restore_snapshot(self):
        """恢复细胞状态快照"""
        global cellData
        if self.cells_snapshot is None or cellData is None:
            return False
        try:
            from utillib.mylib import Cell
            cells = [Cell(pts) for pts in self.cells_snapshot]
            from cell.CellData import CellData as _CD
            globals()['cellData'] = _CD(cells)
            cellData.flush(isGrow=True)
            self._display()
            internal_total, edge_total = self._vertex_internal_edge_totals()
            self._update_stats_panel(
                internal_vertices_total=internal_total,
                last_anneal_internal=0,
                edge_vertices_total=edge_total,
                last_anneal_edge=0,
                cell_total=len(cellData.cells)
            )
            return True
        except Exception:
            return False

    # ========================================================================
    # 显示方法
    # ========================================================================

    def _display(self, show_ellipse=False, show_auxiliary_lines=False,
                 intersection_cell_blocks=None):
        """显示细胞图"""
        global cellData, annealer, cellSeed

        if cellData is None:
            return

        cells = cellData.cells
        layerMarker.layer_mark2(cells, cellSeed)

        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.set_aspect(1)
        ax.tick_params(axis='both', labelsize=18)

        # 保存初始视图
        if not hasattr(self, '_initial_xlim'):
            all_x, all_y = [], []
            for cell in cells:
                for point in cell.points:
                    if isinstance(point, (list, tuple)):
                        all_x.append(point[0])
                        all_y.append(point[1])
                    else:
                        all_x.append(point.x)
                        all_y.append(point.y)
            if all_x and all_y:
                margin = 0.1
                x_range = max(all_x) - min(all_x)
                y_range = max(all_y) - min(all_y)
                self._initial_xlim = [min(all_x) - x_range * margin,
                                      max(all_x) + x_range * margin]
                self._initial_ylim = [min(all_y) - y_range * margin,
                                      max(all_y) + y_range * margin]

        colors = matplotlib.cm.tab20(np.linspace(0, 1, 20))
        color_list = ['#FF5722', '#009688', '#673AB7', '#FFC107', '#2196F3']
        color_index = 0

        try:
            ignore_layer = int(param2) if param2 is not None else 0
        except Exception:
            ignore_layer = 0

        for i, cell in enumerate(cells):
            cell.setArea()
            points_ = cell.points[:]
            points_.append(cell.points[0])
            points_ = np.array(points_)

            c_color = getattr(cell, 'color', '#eeeeee')
            ax.fill(points_[:, 0], points_[:, 1], facecolor=c_color,
                    edgecolor='black', linewidth=0.8, alpha=0.6)

            # 中心点
            if cell.ok or (annealer and not annealer.edge_judge):
                ax.scatter(cell.center_point.x, cell.center_point.y,
                          color='black', s=20)
            else:
                ax.scatter(cell.center_point.x, cell.center_point.y,
                          color='#dddddd', s=20)

            if cell.layer == 1:
                ax.scatter(cell.center_point.x, cell.center_point.y,
                          color='red', s=20)

            # 在形心旁边显示当前层数
            ax.text(cell.center_point.x + 0.08, cell.center_point.y + 0.08,
                    str(cell.layer), fontsize=16, color='black',
                    ha='left', va='bottom')

            # 边框
            color = colors[i % len(colors)]
            ax.plot(points_[:, 0], points_[:, 1], color=color, linewidth=0.8)

            # 椭圆
            if show_ellipse:
                try:
                    ellipse_data, add_points = cell.like_ellipse(1)
                    x, y = get_ellipse(
                        ellipse_data['cp'].x, ellipse_data['cp'].y,
                        ellipse_data['a'], ellipse_data['b'],
                        ellipse_data['angle']
                    )
                    ax.plot(x, y, 'b--', alpha=0.3, linewidth=0.5)
                except Exception:
                    pass

            # 辅助线
            if show_auxiliary_lines:
                try:
                    center_x = cell.center_point.x
                    center_y = cell.center_point.y
                    actual_lines = getattr(cell, 'actual_lines', None)
                    pre_best_lines = getattr(cell, 'pre_best_lines', None)

                    if actual_lines and pre_best_lines:
                        line_count = min(len(actual_lines), len(pre_best_lines))
                        for idx in range(line_count):
                            actual_line = actual_lines[idx]
                            pre_line = pre_best_lines[idx]

                            x_actual = center_x + actual_line.getX()
                            y_actual = center_y + actual_line.getY()
                            ax.plot([center_x, x_actual], [center_y, y_actual],
                                   color='grey', alpha=0.2, linewidth=0.5)

                            x_pre = center_x + pre_line.getX()
                            y_pre = center_y + pre_line.getY()
                            ax.plot([x_actual, x_pre, center_x],
                                   [y_actual, y_pre, center_y],
                                   color=color_list[color_index % len(color_list)],
                                   alpha=0.4, linewidth=0.8)
                        color_index += 1
                except Exception:
                    pass

        # 交汇三角形
        if show_auxiliary_lines and intersection_cell_blocks:
            try:
                edge_judge_display = not annealer.edge_judge if annealer else True
                for cb in intersection_cell_blocks:
                    if not (cb.cell1.ok or not edge_judge_display):
                        continue
                    try:
                        point_g = cb.getTriCentreOfGravity()
                        ax.scatter(point_g.x, point_g.y, color='blue',
                                  s=30, marker='o')
                    except Exception:
                        pass
                    try:
                        if hasattr(cb, 'triangle') and cb.triangle:
                            t_x, t_y = [], []
                            for p in cb.triangle:
                                if hasattr(p, 'x') and hasattr(p, 'y'):
                                    t_x.append(p.x)
                                    t_y.append(p.y)
                                elif isinstance(p, (list, tuple)) and len(p) >= 2:
                                    t_x.append(p[0])
                                    t_y.append(p[1])
                            if len(t_x) >= 3:
                                t_x.append(t_x[0])
                                t_y.append(t_y[0])
                                ax.plot(t_x, t_y, 'red', linewidth=1.5, alpha=0.8)
                    except Exception:
                        pass
            except Exception:
                pass

        self.canvas.draw()


# ============================================================================
# 程序入口
# ============================================================================

if __name__ == "__main__":
    print("====== Running only_annealing_main.py ======")
    root.deiconify()
    app = AnnealingGUI(root)
    root.mainloop()
