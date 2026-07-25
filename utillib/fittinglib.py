# -*- coding: utf-8 -*-
"""
Created on Wed Jul 15 21:09:22 2020

@author: Song
"""
import os
import sys
import tkinter.messagebox as msg

# =========================================================================
# 步骤 1：定义环境配置与弹窗提示函数
# =========================================================================
# def setup_portable_r():
#     """
#     配置 R 环境并弹窗提示用户当前使用的 R 版本（便携版 vs 系统版）
#     """
#     # 1. 确定程序运行的基准路径
#     if getattr(sys, 'frozen', False):
#         # exe 运行时
#         base_path = os.path.dirname(sys.executable)
#     else:
#         # 源码运行时
#         base_path = os.path.dirname(os.path.abspath(__file__))

#     # 2. 拼接便携版 R 的预期路径
#     # 假设 R_Dist 就在 exe 旁边 (或者在 dist/unifiedMain/R_Dist)
#     portable_r_home = os.path.join(base_path, 'R_Dist')
#     portable_r_bin = os.path.join(portable_r_home, 'bin', 'x64')

#     # 3. 开始检测逻辑
#     status_title = "R 语言环境检测报告"
#     use_portable = False

#     # 检查便携版文件夹是否存在
#     if os.path.exists(portable_r_home) and os.path.exists(portable_r_bin):
#         # --- 情况 A：检测到便携版 ---
#         use_portable = True

#         # 强制设置环境变量
#         os.environ['R_HOME'] = portable_r_home
#         os.environ['PATH'] = portable_r_bin + ";" + os.environ.get('PATH', '')

#         info_text = (
#             "✅ 成功挂载便携版 R 环境 (Portable Mode)\n\n"
#             f"路径: {portable_r_home}\n\n"
#             "说明：程序将优先使用此文件夹内的 R 及其算法库，"
#             "无需依赖用户电脑上的 R。"
#         )
#         icon_type = "info"

#     else:
#         # --- 情况 B：未检测到便携版 ---
#         # 尝试检查系统环境变量（仅作提示，具体能不能用还得看运气）
#         system_r_home = os.environ.get('R_HOME', '未检测到')

#         info_text = (
#             "⚠️ 未找到便携版 R_Dist 文件夹 (System Mode)\n\n"
#             "程序将尝试调用系统安装的 R。\n"
#             f"系统 R_HOME 变量: {system_r_home}\n\n"
#             "注意：如果您的电脑未安装 R 或未配置环境变量，"
#             "椭圆拟合的高级功能可能会失效（自动降级为普通拟合）。"
#         )
#         icon_type = "warning"

#     # 4. 弹出提示框 (阻塞式，用户点确定后继续)
#     # 注意：这会在主界面启动前弹出
#     if use_portable:
#         msg.showinfo(status_title, info_text)
#     else:
#         msg.showwarning(status_title, info_text)

def _check_system_r():
    """
    检测系统是否已安装 R
    返回: True (系统 R 可用), False (不可用)
    """
    # 检查 R_HOME 环境变量
    r_home = os.environ.get('R_HOME', '')
    if r_home and os.path.exists(r_home):
        return True

    # 检查 PATH 中是否有 R
    r_paths = os.environ.get('PATH', '').split(os.pathsep)
    for p in r_paths:
        r_exe = os.path.join(p, 'R.exe')
        if os.path.exists(r_exe):
            return True

    # 尝试通过 where 命令查找 (Windows)
    try:
        import subprocess
        result = subprocess.run(['where', 'R'], capture_output=True, text=True, timeout=3)
        if result.returncode == 0 and result.stdout.strip():
            return True
    except Exception:
        pass

    return False


def _use_portable_r(base_path):
    """配置并使用便携版 R_Dist"""
    portable_r_home = os.path.join(base_path, 'R_Dist')
    portable_r_bin_root = os.path.join(portable_r_home, 'bin')
    portable_r_bin = os.path.join(portable_r_bin_root, 'x64')

    os.environ['R_HOME'] = portable_r_home
    os.environ['R_USER'] = portable_r_home
    os.environ['PATH'] = portable_r_bin + os.pathsep + portable_r_bin_root + os.pathsep + os.environ.get('PATH', '')

    if hasattr(os, 'add_dll_directory'):
        try:
            os.add_dll_directory(portable_r_bin)
            os.add_dll_directory(portable_r_bin_root)
        except Exception:
            pass

    return portable_r_home


def setup_portable_r():
    """
    配置 R 环境，优先级：
    1. 用户系统已安装的 R（通过 R_HOME / PATH 检测）
    2. 便携版 R_Dist（位于本程序目录下）
    3. 都不可用 → 降级为纯 Python 拟合（使用 scipy/numpy）
    """
    if getattr(sys, 'frozen', False):
        # exe 运行时：R_Dist 在 exe 同目录
        base_path = os.path.dirname(sys.executable)
    else:
        # 源码运行时：R_Dist 在 fittinglib.py 的上上级目录
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    status_title = "R 语言环境检测"
    _is_portable = False

    # —— 优先级 1：检测系统 R ——
    if _check_system_r():
        r_home = os.environ.get('R_HOME', '系统 PATH 中')
        msg.showinfo(status_title,
            f"✅ 检测到系统中已安装 R (System R detected)\n\n"
            f"R_HOME: {r_home}\n\n"
            "将使用系统 R 进行椭圆拟合。(Will use system R for ellipse fitting.)")
        return

    # —— 优先级 2：检测便携版 R_Dist ——
    portable_r_home_candidate = os.path.join(base_path, 'R_Dist')
    if os.path.exists(portable_r_home_candidate):
        r_path = _use_portable_r(base_path)
        _is_portable = True
        msg.showinfo(status_title,
            f"✅ 使用便携版 R 环境 (Using portable R environment)\n\n"
            f"路径: {r_path}\n\n"
            "说明：未检测到系统 R，已自动挂载内置 R。(Note: System R not detected, built-in R auto-mounted.)")
        return

    # —— 均不可用 ——
    system_r_home = os.environ.get('R_HOME', '未检测到')
    msg.showwarning(status_title,
        f"⚠️ 未找到可用的 R 环境 (No available R environment found)\n\n"
        f"系统 R_HOME: {system_r_home}\n\n"
        "椭圆拟合将降级为纯 Python 方式（最小二乘 / scipy LMG），仍可正常使用，但精度可能略低于 R-LMG 算法。\n"
        "(Ellipse fitting will fall back to pure Python mode (Least Squares / scipy LMG). Still usable, but accuracy may be slightly lower than R-LMG algorithm.)\n\n"
        "如需恢复 R 拟合，请：(To restore R fitting, please:)\n"
        "• 安装 R 并配置 R_HOME 环境变量，或 (• Install R and configure R_HOME environment variable, or)\n"
        f"• 将 R_Dist 文件夹放在: {base_path} (• Place R_Dist folder at: {base_path})")

# =========================================================================
# 步骤 2：立即执行配置 (必须在 import rpy2 之前！)
# =========================================================================
setup_portable_r()

# =========================================================================
# 步骤 3：设置语言环境 (解决中文乱码)
# =========================================================================
os.environ["LC_ALL"] = "C"
# 必须在设置完环境变量后，再 import rpy2
import rpy2.robjects as robjects
import math
import numpy as np
from scipy.optimize import least_squares  # 新增引用，用于实现R语言中的LMG算法
from pyenvelope import get_minimum_bounding_rectangle # [新增] MBR支持
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
from rpy2.robjects import numpy2ri
# 激活 numpy 到 R 矩阵的自动转换
from rpy2.robjects import conversion


def re_ellipse_fitting(points, eps=1e-12):
    """
    使用 SVD 伪逆 手搓最小二乘（数值稳定）
    等价于 numpy.linalg.lstsq 的数学本质

    模型:  x^2 + Bxy + Cy^2 + Dx + Ey + F = 0
    即:    A @ can_shu ≈ b
    """

    # --- 1. 数据准备 ---
    pts = np.array(points, dtype=float)
    x = pts[:, 0]
    y = pts[:, 1]

    # --- 2. 构建设计矩阵 A (N, 5) ---
    # 每一行: [xy, y^2, x, y, 1]
    A = np.column_stack([
        x * y,          # B
        y ** 2,         # C
        x,              # D
        y,              # E
        np.ones_like(x) # F
    ])

    # --- 3. 构建目标向量 b (N, 1) ---
    b = -(x ** 2)
    b = b.reshape(-1, 1)

    # --- 4. SVD 分解 A = U Σ V^T ---
    # full_matrices=False → 经济型 SVD，更高效
    U, S, Vt = np.linalg.svd(A, full_matrices=False)

    # --- 5. 构造 Σ^+（奇异值的伪逆）---
    # 对非常小的奇异值进行截断，防止数值爆炸
    S_inv = np.zeros_like(S)
    for i in range(len(S)):
        if S[i] > eps:
            S_inv[i] = 1.0 / S[i]
        else:
            S_inv[i] = 0.0

    # 也可以一行写完（等价）：
    # S_inv = np.where(S > eps, 1.0 / S, 0.0)

    # --- 6. 计算 A^+ = V Σ^+ U^T ---
    A_pinv = Vt.T @ np.diag(S_inv) @ U.T   # (5, N)

    # --- 7. 最小二乘解 can_shu = A^+ b ---
    can_shu = A_pinv @ b                   # (5, 1)

    return can_shu

#---------------------------------------------------------
#正规方程求解: (A^T A)^-1 A^T b
def re_ellipse_fitting_1(points):
    data=np.array(points)
    x=data[:,0]
    y=data[:,1]
    A=np.column_stack([
        x*y,
        y**2,
        x,
        y,
        np.ones_like(x)
    ])
    b = -(x ** 2)
    b = b.reshape(-1, 1)
    can_shu=np.linalg.inv(A.T@A)@A.T@b
    return can_shu

def re_ellipse_fitting_4(points):
    """
    使用 numpy.linalg.lstsq 重构的椭圆拟合底层函数
    """
    # 1. 将输入的点集转换为 numpy 数组 (N, 2)
    pts = np.array(points)
    x = pts[:, 0]
    y = pts[:, 1]

    # 2. 构建观测矩阵 A (每一行: [xy, y^2, x, y, 1])
    # 使用 np.column_stack 可以直接按列合并，避免显式的 Python 循环
    A = np.column_stack([
        x * y,          # B 对应的项
        y ** 2,         # C 对应的项
        x,              # D 对应的项
        y,              # E 对应的项
        np.ones_like(x) # F 对应的常数项
    ])

    # 3. 构建目标向量 b (-x^2)
    b = -(x ** 2)

    # 4. 调用高效的最小二乘算法
    # rcond=None 使用默认的截断值处理奇异矩阵
    # lstsq 返回: (系数解, 残差平方和, 秩, 奇异值)
    can_shu, residuals, rank, s = np.linalg.lstsq(A, b, rcond=None)

    # 5. 为了保持与原代码 find_a/b 等函数的兼容性，将结果重塑为 (5, 1)
    return can_shu.reshape(-1, 1)
#-------------------------------------------------

#  代码从此处开始为通过数据计算椭圆参数算法 其中椭圆的一般方程式为
#  Ax² + Bxy + Cy² + Dx + Ey + F = 0 在下面代码中的参数中:
#  A = 1
#  B = a
#  C = b
#  D = c
#  E = d
#  F = e
def find_y_c(can_shu):  # 根据传入参数求拟合椭圆纵坐标 计算公式是百度的
    jz = np.asmatrix(can_shu)  # 将矩阵参数转化为数组格式 Convert matrix parameters to array format
    # 为 a,b,c,d,e赋值 Assign a value to a, b, c, d, e
    a = jz[0][0]
    b = jz[1][0]
    c = jz[2][0]
    d = jz[3][0]
    e = jz[4][0]
    # 按照公式计算 Calculate according to formula
    y_c_a = (2 * d) - (a * c)
    xy_c_b = (a * a) - (4 * b)
    y_c = y_c_a / xy_c_b
    return y_c  # 返回拟合椭圆纵坐标 Returns the ordinate of the fitted ellipse


def find_x_c(can_shu):  # 根据传入参数求拟合椭圆横坐标 计算公式是百度的
    jz = np.asmatrix(can_shu)  # 将矩阵参数转化为数组格式 Convert matrix parameters to array format
    # 为 a,b,c,d,e赋值 Assign a value to a, b, c, d, e
    a = jz[0][0]
    b = jz[1][0]
    c = jz[2][0]
    d = jz[3][0]
    e = jz[4][0]
    # 按照公式计算 Calculate according to formula
    x_c_a = (2 * b * c) - (a * d)
    xy_c_b = (a * a) - (4 * b)
    x_c = x_c_a / xy_c_b
    return x_c  # 返回拟合椭圆横坐标 Returns the abscissa of the fitted ellipse

#-----------------------辅助函数begin-test-----------------------------------------------

def get_cell_sides(points):  # 获取细胞点集长度 传入数据points为细胞顶点集合
    # Get the length of cell point set and input data points as cell vertex set
    cell_sides = len(points)
    return cell_sides  # 返回细胞点集长度 Return cell point set length

def n_rotate(rotate_angle, value_x, value_y, point_x, point_y):  # 点绕点旋转 -> 相当于直线绕点旋转，返回旋转之后的新点 注意这边传出的是Point类型的点
    value_x = np.array(value_x)
    value_y = np.array(value_y)
    n_rotate_x = (value_x - point_x) * math.cos(rotate_angle) - (value_y - point_y) * math.sin(rotate_angle) + point_x
    n_rotate_y = (value_x - point_x) * math.sin(rotate_angle) + (value_y - point_y) * math.cos(rotate_angle) + point_y
    rotate_new_point = [n_rotate_x, n_rotate_y]
    return rotate_new_point
#-----------------------辅助函数end-test-----------------------------------------------
def insert_points(points, center_point, rotate_angle):
    """
    在每个顶点的前后插入旋转后的点，保持顶点顺序（顺时针或逆时针）
    参数:
        points: 细胞顶点集合（按顺序排列）
        center_point: 旋转中心
        rotate_angle: 旋转角度（度）
    返回: 更新后的顶点集合（保持原有顺序）
    """
    result = []
    n = len(points)
    for i in range(n):
        p = points[i]
        r_point = [p[0], p[1]]
        
        new_rotate_point = n_rotate(math.radians(rotate_angle), r_point[0], r_point[1], center_point.x, center_point.y)
        new_rotate_point2 = n_rotate(math.radians(-rotate_angle), r_point[0], r_point[1], center_point.x, center_point.y)
        
        prev_idx = (i - 1) % n
        next_idx = (i + 1) % n
        
        result.append(new_rotate_point2)
        result.append(p)
        result.append(new_rotate_point)
    
    return result

def mirror_points_180(points, centroid):
    """
    围绕形心镜像旋转180度，生成2n个点
    参数:
        points: 原始顶点集合
        centroid: 形心坐标（包含x, y属性）
    返回: 镜像后的2n个点（原始点 + 镜像点）
    """
    mirrored = []
    for p in points:
        mx = 2 * centroid.x - p[0]
        my = 2 * centroid.y - p[1]
        mirrored.append([mx, my])
    
    return points + mirrored


def find_center_point(can_shu):  # 求拟合椭圆中心点坐标 Find the center point coordinates of fitting ellipse
    x = find_x_c(can_shu)
    y = find_y_c(can_shu)
    return [float(x), float(y)]  # 返回拟合椭圆中心点坐标 return the center point coordinates of fitting ellipse


def find_a(can_shu):  # 求长半轴 Find the long half axis
    jz = np.asmatrix(can_shu)  # 将矩阵参数转化为数组格式 Convert matrix parameters to array format
    # 为 a,b,c,d,e赋值 Assign a value to a, b, c, d, e
    a = jz[0][0]
    b = jz[1][0]
    c = jz[2][0]
    d = jz[3][0]
    e = jz[4][0]
    # 按照公式计算 Calculate according to formula
    fen_zi = 2 * (a * c * d - b * c * c - d * d + 4 * e * b - a * a * e)
    fen_mu = (a * a - 4 * b) * (b - math.sqrt(a * a + (1 - b) * (1 - b)) + 1)
    ab_e_a = math.sqrt(math.fabs(fen_zi / fen_mu))
    return ab_e_a  # 返回拟合椭圆长半轴数据 Return fitting ellipse long half axis data


def find_b(can_shu):  # 求短半轴 Find the short half axis
    jz = np.asmatrix(can_shu)  # 将矩阵参数转化为数组格式 Convert matrix parameters to array format
    # 为 a,b,c,d,e赋值 Assign a value to a, b, c, d, e
    a = jz[0][0]
    b = jz[1][0]
    c = jz[2][0]
    d = jz[3][0]
    e = jz[4][0]
    # 按照公式计算 Calculate according to formula
    fen_zi = 2 * (a * c * d - b * c * c - d * d + 4 * e * b - a * a * e)
    fen_mu = (a * a - 4 * b) * (b + math.sqrt(a * a + (1 - b) * (1 - b)) + 1)
    ab_e_b = math.sqrt(math.fabs(fen_zi / fen_mu))
    return ab_e_b  # 返回拟合椭圆短半轴数据 Return to fitting ellipse short axis data


#  此处代码原有bug 在调试之后 A = 1 B = b C = c
def find_angle(can_shu):  # 求偏转角 Find deflection angle
    jz = np.asmatrix(can_shu)  # 将矩阵参数转化为数组格式 Convert matrix parameters to array format
    # 为 a,b,c赋值 Assign a value to a, b, c
    b = jz[0][0]
    c = jz[1][0]
    # 按照公式计算 Calculate according to formula
    qie_ta = math.atan(b / (1 - c))
    qie_ta = qie_ta / 2
    if c < 1:
        qie_ta = qie_ta+math.pi/2
    return qie_ta  # 返回拟合椭圆同水平轴偏转角数据 Return the data of the same horizontal axis deflection angle of fitting ellipse


def judge_pp_distance(c_point, point_0):  # 判求点与点之间的距离，返回距离值  # 没用的函数
    f_x = c_point[0]
    f_y = c_point[1]
    s_x = point_0[0]
    s_y = point_0[1]
    distance = math.sqrt((f_x-s_x)*(f_x-s_x)+(f_y-s_y)*(f_y-s_y))
    return distance

def do_middle_insert_all(points, ori_points, index):
    first_point = ori_points[index]
    second_point = ori_points[index + 1]
    renew_point_x = (first_point[0] + second_point[0]) / 2
    renew_point_y = (first_point[1] + second_point[1]) / 2
    renew_point = [renew_point_x, renew_point_y]
    
    try:
        idx = points.index(first_point)
        points.insert(idx + 1, renew_point)
    except ValueError:
        points.append(renew_point)
    
    return points

def middle_insert_all(points, ori_points):
    # print("点集",points)
    n = len(ori_points)
    #print("n=",n)
    i = -1
    while True:
        # print("i=",i)
        points = do_middle_insert_all(points, ori_points, i)
        i+=1
        if i>=n-1:
            break
    return points

def check_validity(a, b, strict_aspect=True):
    """
    [辅助验证] 检查长短轴是否合法
    参数:
        strict_aspect: 是否严格检查扁平率。对于少边形（边数<5）应设为False
    返回: (是否合法, 错误原因字符串)
    """
    # 1. 检查是否为 NaN 或 Inf (数学计算错误)
    if math.isnan(a) or math.isnan(b) or math.isinf(a) or math.isinf(b):
        return False, "数值无效(NaN/Inf)"

    # 2. 检查是否为 0 (防止除零错误)
    if a < 1e-6 or b < 1e-6:
        return False, "轴长接近0"

    # 3. 检查扁平率 (Aspect Ratio)
    # 正常的细胞大多是圆润的。如果 长轴 / 短轴 > 5，说明拟合出了一个极其扁长的形状
    # 对于少边形（如三角形），放宽此检查，因为R拟合的结果本身是可靠的
    if strict_aspect:
        major = max(a, b)
        minor = min(a, b)
        ratio = major / minor

        if ratio > 5.0:
            return False, f"形状太扁(比例 {ratio:.1f})"

    return True, "正常"





# def judge_value(can_shu, points, area, iterator, center_point, ori_points):
#     a = find_a(can_shu)
#     b = find_b(can_shu)
#     ell_area = a*b*math.pi
#     value = ell_area / area
#     if value > 3:
#         points = ori_points[:] # points回退
#         if iterator == 1: # 第一次异常，进行5度旋转测试
#             print("第一次异常，进行5度旋转测试")
#             points = insert_points(points, center_point, 5)
#             can_shu = re_ellipse_fitting(points)
#             can_shu = judge_value(can_shu, points, area, iterator+1, center_point, ori_points)
#         elif iterator==2: # 第二次异常，进行8度旋转测试
#             print("第二次异常，进行8度旋转测试")
#             points = insert_points(points, center_point, 8)
#             can_shu = re_ellipse_fitting(points)
#             can_shu = judge_value(can_shu, points, area, iterator+1, center_point, ori_points)
#         elif iterator==3: # 第三次异常，进行10度旋转测试
#             print("第三次异常，进行10度旋转测试")
#             points = insert_points(points, center_point, 10)
#             can_shu = re_ellipse_fitting(points)
#             can_shu = judge_value(can_shu, points, area, iterator+1, center_point, ori_points)
#         elif iterator==4: # 第四次异常，中值测试
#             print("第四次异常，中值测试")
#             points = middle_insert_all(points, ori_points)
#             can_shu = re_ellipse_fitting(points)
#             can_shu = judge_value(can_shu, points, area, iterator+1, center_point, ori_points)
#         else: # 第五次异常，输出相关数据
#             export(ori_points)
#     return can_shu

# def fitting_2(points, center_point, area):
#     # print("开始新细胞拟合")
#     ori_points = points[:]
#     length = len(points)

#     # flag 用于标记是否进行了插值，影响后续 iterator 的计数，保持原逻辑
#     flag = False

#     # --- [核心修改 START] ---
#     # 针对点数过少的细胞 (如三角形)，不再使用旋转插值，而是使用中点插值
#     # 目的：增加边上的约束点，防止拟合出穿越边界的扁长椭圆
#     if length < 5:
#         # 复制一份，防止修改原列表引用
#         points_to_interp = points[:]

#         # 进行一次中点插值 (3点 -> 6点; 4点 -> 8点)
#         # 这会填充顶点之间的空隙，让形状更"实"
#         points = middle_insert_all(points_to_interp, points)

#         # 如果点还是很稀疏（比如原来只有3个点，插值后6个可能还不够稳），可以再插一次
#         # if len(points) < 6:
#         #     points = middle_insert_all(points[:], points[:])

#         flag = True
#     # --- [核心修改 END] ---

#     # 进行拟合操作，获取参数
#     try:
#         # 调用 R 语言 / MBR 混合拟合
#         parameters = fitting_call_R_conicfit(points)
#     except Exception as e:
#         # print("LMG拟合失败，回退到代数拟合:", e)
#         parameters = re_ellipse_fitting(points)

#     iterator = 1
#     if flag:
#         iterator = 2

#     # 进行参数判断 (你的原始逻辑)
#     parameters = judge_value(parameters, points, area, iterator, center_point, ori_points)

#     return parameters

def fitting_1(points, center_point, area):
    #print("开始新细胞拟合")

    # 1. 【非常重要】先备份原始数据，再做任何修改！
    # 否则 judge_value 里的回退逻辑会拿到脏数据
    ori_points = points[:]
    length = len(points)
    flag = False

    # 2. 针对点数过少（如三角形）的情况，进行预处理
    if length < 5:
        # 【修改点】: 优先使用中值插值 (Middle Insert)
        # 这会将 3 个点变成 6 个点，或 4 个点变成 8 个点
        # 比单纯的旋转插值更能固定形状，防止拟合出无限大的椭圆

        # 注意：这里传入 points[:] 作为参考列表，防止在遍历时修改列表导致死循环
        points = middle_insert_all(points, points[:])

        flag = True
        # print(f"检测到顶点数{length} < 5，已执行中值插值，当前点数: {len(points)}")

    # 3. 进行拟合操作
    try:
        # 优先尝试 R 语言的高精度拟合
        parameters = fitting_call_R_conicfit(points)
    except Exception as e:
        # 如果 R 逻辑计算失败 (例如矩阵奇异)，回退到普通的代数拟合
        print("LMG拟合失败，回退到代数拟合:", e)
        parameters = re_ellipse_fitting(points)

    # 4. 设置 iterator 起始值
    # 如果前面进行了插值，说明这不是原始数据，iterator 从 2 开始
    iterator = 1
    if flag:
        iterator = 2

    return parameters
def fitting_2(points, center_point, area):
    #print("开始新细胞拟合")
    ori_points = points[:]
    length = len(points)
    flag = False
    if length < 5:
        # 插值
        points = insert_points(points, center_point, 5)
        # points = insert_points(points, center_point, -5)
        flag = True
        #print("边数小于5，已进行插值")
    # 进行拟合操作，获取参数
    try:
        parameters = fitting_call_R_conicfit(points)
        # parameters =fitting_with_MBR_logic(points)
        # 尝试使用高精度的 R 逻辑拟合
        #parameters = fitting_with_R_logic(points)
    except Exception as e:
        # 如果 R 逻辑计算失败 (例如矩阵奇异)，回退到普通的代数拟合
        print("LMG拟合失败，回退到代数拟合:", e)
        parameters = re_ellipse_fitting(points)
    iterator = 1
    if flag:
        iterator = 2
    return parameters

def fitting_3(points, center_point, area):
    """
    修改后的拟合逻辑:
    1. 默认先进行代数拟合。
    2. 如果检测到过拟合(面积比>3) 或 原始形状为三角形，
       则调用 R 语言 LMG 算法进行二次拟合。
    3. 对比代数拟合和 R 拟合的结果，保留面积更小(更紧致)的椭圆。
    """
    ori_points = points[:]
    length = len(points)
    flag = False

    # --- 1. 预处理：少边形插值 ---
    # 如果点数过少(如三角形)，先插值增加约束点
    if length < 5:
        points = insert_points(points, center_point, 5)
        flag = True

    # --- 2. 第一轮：基准代数拟合 ---
    try:
        can_shu = re_ellipse_fitting(points)

        # 计算代数拟合的面积
        a = find_a(can_shu)
        b = find_b(can_shu)
        # 如果出现无效值(NaN/Inf)，设面积为无限大
        if math.isnan(a) or math.isnan(b) or math.isinf(a) or math.isinf(b):
            area_alg = float('inf')
        else:
            area_alg = math.pi * a * b

    except Exception:
        can_shu = None
        area_alg = float('inf')

    # 计算面积比值 (拟合面积 / 细胞真实面积)
    if area > 0:
        ratio = area_alg / area
    else:
        ratio = float('inf')

    # --- 3. 决策逻辑：是否触发 R 语言优化 ---
    # 触发条件：(1) 比值 > 3  OR  (2) 原始形状是三角形 (length == 3)
    is_triangle = (length == 3)

    if ratio > 3 or is_triangle:
        # print(f"触发优化逻辑: 三角形={is_triangle}, 面积比={ratio:.2f}")
        try:
            # 调用 R 语言拟合
            can_shu_R = fitting_call_R_conicfit(points)

            # 计算 R 拟合的面积
            a_R = find_a(can_shu_R)
            b_R = find_b(can_shu_R)

            if math.isnan(a_R) or math.isnan(b_R) or math.isinf(a_R) or math.isinf(b_R):
                area_R = float('inf')
            else:
                area_R = math.pi * a_R * b_R

            # --- 4. 择优保留 ---
            # 只有当 R 拟合结果有效，且面积确实比代数拟合更小时，才采用 R 的结果
            if area_R > area_alg:
                # print(f"R语言优化生效: 面积从 {area_alg:.1f} 优化为 {area_R:.1f}")
                can_shu = can_shu_R
            # else:
                # print("R语言结果未更优，保持原结果")

        except Exception as e:
            print(f"R语言调用失败或计算异常: {e}，保持代数拟合结果")
            if can_shu is None:
                # 如果代数拟合之前也失败了，这里做最后的保底尝试
                can_shu = re_ellipse_fitting(points)

    # --- 5. 后续常规校验 (judge_value) ---
    iterator = 1
    return can_shu

def export(list):
    print("经不同方式的两次插值后，该细胞仍不符合条件，其多边形坐标为：")
    for p in list:
        for xy in p:
            print(xy,",",end="")
    print("")
    print("---------------------------")


def calculate_ellipse_residuals(params, x, y):
    """
    计算点到椭圆方程的残差，用于 fit.ellipseLMG (R代码中的核心逻辑)
    params: [cx, cy, a, b, theta]
    """
    cx, cy, a, b, theta = params
    cos_t = math.cos(theta)
    sin_t = math.sin(theta)

    # 坐标平移和旋转，转换到标准椭圆坐标系
    dx = x - cx
    dy = y - cy

    xt = dx * cos_t + dy * sin_t
    yt = -dx * sin_t + dy * cos_t

    # 构造残差方程 (x'/a)^2 + (y'/b)^2 - 1
    # 这是一个代数近似的几何距离，常用于LMG算法的快速收敛
    return (xt / a) ** 2 + (yt / b) ** 2 - 1


def ellipse_fitting_geometric_LMG(points, initial_params=None):
    """
    对应 R 中的 fit.ellipseLMG
    使用 Levenberg-Marquardt 算法进行非线性最小二乘拟合
    """
    pts = np.array(points)
    x_data = pts[:, 0]
    y_data = pts[:, 1]

    # 如果没有提供初值，使用代数拟合 (re_ellipse_fitting) 生成初值
    if initial_params is None:
        can_shu_alg = re_ellipse_fitting(points)
        cx, cy = find_center_point(can_shu_alg)
        a_alg = find_a(can_shu_alg)
        b_alg = find_b(can_shu_alg)
        theta = find_angle(can_shu_alg)
        initial_params = [cx, cy, a_alg, b_alg, theta]

    # 确保长短轴为正
    initial_params[2] = abs(initial_params[2])
    initial_params[3] = abs(initial_params[3])

    # 调用 scipy.optimize.least_squares (实现 Levenberg-Marquardt)
    result = least_squares(
        calculate_ellipse_residuals,
        initial_params,
        args=(x_data, y_data),
        method='lm'
    )

    return result.x # 返回 [cx, cy, a, b, theta]



def ellipse_fitting_geometric_LMG_version2(points, initial_params=None):
    """
    对应 R 中的 fit.ellipseLMG
    使用 Levenberg-Marquardt 算法进行非线性最小二乘拟合
    """
    pts = np.array(points)
    x_data = pts[:, 0]
    y_data = pts[:, 1]

    # 如果没有提供初值，使用代数拟合 (re_ellipse_fitting) 生成初值
    if initial_params is None:
        can_shu_alg = re_ellipse_fitting(points)
        cx, cy = find_center_point(can_shu_alg)
        a_alg = find_a(can_shu_alg)
        b_alg = find_b(can_shu_alg)
        theta = find_angle(can_shu_alg)
        initial_params = [cx, cy, a_alg, b_alg, theta]

        # --- B. 关键修改：初值安全性检查 (Sanity Check) ---
        # 计算点集的物理范围（Bounding Box），判断代数拟合是否离谱
        min_x, max_x = np.min(x_data), np.max(x_data)
        min_y, max_y = np.min(y_data), np.max(y_data)
        width = max_x - min_x
        height = max_y - min_y
        max_span = max(width, height) # 细胞的最大跨度

        # 判定条件：如果算出的中心跑到了十万八千里外，或者长轴比细胞本身大太多(比如4倍)
        # 说明代数拟合已经"飞出去了"
        is_bad_center = (cx < min_x - 2*max_span) or (cx > max_x + 2*max_span) or \
                        (cy < min_y - 2*max_span) or (cy > max_y + 2*max_span)
        is_huge_axis = (a_alg > 4 * max_span) or (b_alg > 4 * max_span)

        if is_bad_center or is_huge_axis or math.isnan(a_alg) or math.isnan(b_alg):
            # print("代数拟合失效，启用安全初值 (Safe Mode)")
            # 强制使用一个位于点集几何中心的圆作为初值
            safe_cx = np.mean(x_data)
            safe_cy = np.mean(y_data)
            safe_r = max_span / 2.0  # 假设是一个直径等于跨度的圆
            initial_params = [safe_cx, safe_cy, safe_r, safe_r, 0]
        else:
            # 代数拟合正常，使用它
            initial_params = [cx, cy, a_alg, b_alg, theta]

    # 确保长短轴为正
    initial_params[2] = abs(initial_params[2])
    initial_params[3] = abs(initial_params[3])

    # 调用 scipy.optimize.least_squares (实现 Levenberg-Marquardt)
    try:
        result = least_squares(
            calculate_ellipse_residuals,
            initial_params,
            args=(x_data, y_data),
            method='lm'
        )
        return result.x # 返回 [cx, cy, a, b, theta]
    except Exception as e:
        # 如果 LMG 崩溃，直接返回初值
        return initial_params


def geometric_to_algebraic(geo_params):
    """
    将几何参数 [cx, cy, a, b, theta] 转换为代数参数 [B, C, D, E, F] (假设 A=1)
    以匹配原程序 can_shu 的格式
    原方程模型: x^2 + Bxy + Cy^2 + Dx + Ey + F = 0
    """
    cx, cy, a, b, theta = geo_params

    cos_t = math.cos(theta)
    sin_t = math.sin(theta)
    cos_t2 = cos_t ** 2
    sin_t2 = sin_t ** 2
    a2 = a ** 2
    b2 = b ** 2

    # 构造一般方程系数 Ax^2 + Bxy + Cy^2 + Dx + Ey + F = 0
    A = cos_t2 / a2 + sin_t2 / b2
    B = 2 * cos_t * sin_t * (1/a2 - 1/b2)
    C = sin_t2 / a2 + cos_t2 / b2
    D = -2 * A * cx - B * cy
    E = -B * cx - 2 * C * cy
    F = A * cx**2 + B * cx * cy + C * cy**2 - 1

    # 归一化，使得 x^2 的系数为 1 (匹配 re_ellipse_fitting 的输出假设)
    # 注意：如果 A 为 0 (极其罕见，除非垂直且a无限大)，则需要特殊处理，但此处忽略
    return np.array([B/A, C/A, D/A, E/A, F/A]).reshape(-1, 1)


def calculate_teacher_pargini(points):
    """
    [新增/修改]  ParGini 初始值计算逻辑
    参数顺序：
    1. 多边形重心 X (并非矩形中心)
    2. 多边形重心 Y
    3. 矩形长 * 0.5 (半长轴)
    4. 矩形宽 * 0.5 (半短轴)
    5. 矩形长轴与 X 轴夹角
    """
    pts_np = np.array(points)

    # --- A. 计算多边形重心 (所有顶点的均值) ---
    poly_centroid = np.mean(pts_np, axis=0)
    center_x = poly_centroid[0]
    center_y = poly_centroid[1]

    # --- B. 计算最小外接矩形 (MBR) ---
    # 获取 MBR 顶点
    mbr_points = get_minimum_bounding_rectangle(points)
    mbr = np.array(mbr_points)

    # 取前三个点计算边向量 (p0->p1, p1->p2)
    p0, p1, p2 = mbr[0], mbr[1], mbr[2]
    vec1 = p1 - p0
    vec2 = p2 - p1
    len1 = np.linalg.norm(vec1)
    len2 = np.linalg.norm(vec2)

    # --- C. 区分长宽与角度 ---
    if len1 >= len2:
        rect_len = len1
        rect_width = len2
        # 计算长边向量的角度 (atan2 返回弧度)
        angle = math.atan2(vec1[1], vec1[0])
    else:
        rect_len = len2
        rect_width = len1
        angle = math.atan2(vec2[1], vec2[0])

    # --- D. 组装参数 ---
    # LMG 算法需要的 a, b 为半轴长，所以乘 0.5
    init_a = rect_len * 0.5
    init_b = rect_width * 0.5

    # 返回列表 [Cx, Cy, a, b, theta]
    return [center_x, center_y, init_a, init_b, angle]

def check_ls_quality_0203(can_shu, points, poly_area):
    """
    [新增] 按照老师规则判断拟合质量
    返回: True (合格), False (异常)
    """
    if can_shu is None:
        return False

    try:
        # 1. 获取椭圆参数
        a = find_a(can_shu)
        b = find_b(can_shu)
        cx, cy = find_center_point(can_shu)
        theta = find_angle(can_shu) # 需要用到角度来进行坐标变换验证重心

        if math.isnan(a) or math.isnan(b) or a <= 0 or b <= 0:
            return False

        # --- 规则 1：面积比校验 ---
        ellipse_area = math.pi * a * b
        if poly_area > 0:
            ratio = ellipse_area / poly_area
            if ratio < 1.0 or ratio > 3.0:
                # print(f"异常判定：面积比 {ratio:.2f} 不在 1~3 范围内")
                return False

        return True

    except Exception as e:
        print(f"校验过程出错: {e}")
        return False

def check_ls_quality(can_shu, points, poly_area):
    """
    [修改] 按照新规则判断拟合质量
    返回: True (合格), False (异常)
    """
    if can_shu is None:
        return False

    try:
        # 1. 获取椭圆参数
        a = find_a(can_shu)
        b = find_b(can_shu)

        # 基础数值检查
        if math.isnan(a) or math.isnan(b) or a <= 0 or b <= 0:
            return False

        # --- 核心规则更改：面积比校验 ---
        # 老师要求：面积比不在 1~3 范围内时判断为异常
        ellipse_area = math.pi * a * b
        if poly_area > 0:
            ratio = ellipse_area / poly_area
            if ratio < 1.0 or ratio > 3.0:
                # print(f"异常判定：面积比 {ratio:.2f} 不在 1~3 范围内")
                return False

        return True

    except Exception as e:
        print(f"校验过程出错: {e}")
        return False

def check_ls_quality_v5(can_shu, points, poly_area):
    """
    V5版本的拟合质量检查，面积比合格范围为1.0~3.0
    返回: True (合格), False (异常)
    """
    return check_ls_quality(can_shu, points, poly_area)

def fitting_call_R_conicfit(points, mbr_points=None):
    """
    [修改后] 调用 R 语言 fit.ellipseLMG，使用老师指定的 ParGini 初值
    :param points: 用于拟合的点集（实际拟合用的点）
    :param mbr_points: 用于计算MBR初值的点集（默认等于points）
    """
    try:
        pts_np = np.array(points)

        if mbr_points is None:
            mbr_points = points

        # --- 关键修改：使用指定的点集计算 ParGini 初值 ---
        pargini_list = calculate_teacher_pargini(mbr_points)

        # 构造 R 对象
        pargini_vec = robjects.FloatVector(pargini_list)
        par_gini_r = robjects.r.matrix(pargini_vec, ncol=1)

        # 导入包
        conicfit = importr('conicfit')

        # 使用局部转换器调用 R
        with conversion.localconverter(robjects.default_converter + numpy2ri.converter):
            # 调用 LMG 算法，tol 设为 1e-5 保证精度
            res_r = conicfit.fit_ellipseLMG(pts_np, par_gini_r, 1e-5)

            # 解析结果
            geo_params_r = res_r[0]
            geo_params = np.array(geo_params_r).flatten()

        # 转换回代数参数 [A,B,C,D,E,F] 格式
        return geometric_to_algebraic(geo_params)

    except Exception as e:
        print(f"R语言接口调用失败: {e}。回退到普通拟合。")
        return re_ellipse_fitting(points)

def calculate_mbr_initial_guess(points):
    """
    [新增函数] 基于 pyenvelope 最小外接矩形 (MBR) 计算 LMG 的几何初值
    按照老师的要求：
    - 中心：矩形几何中心
    - 长轴 a：矩形长 * 0.5
    - 短轴 b：矩形宽 * 0.5
    - 角度：矩形长边与 X 轴的夹角
    """
    # 1. 获取最小外接矩形顶点 (pyenvelope 返回的是 list of tuples)
    mbr_points = get_minimum_bounding_rectangle(points)
    mbr = np.array(mbr_points) # 转为 numpy 方便计算

    # pyenvelope 返回的通常是逆时针顺序的4个点 (构成闭合多边形可能返回5个点，取前4个即可)
    p0, p1, p2 = mbr[0], mbr[1], mbr[2]

    # 2. 计算两条邻边的向量和长度
    vec1 = p1 - p0
    len1 = np.linalg.norm(vec1)

    vec2 = p2 - p1
    len2 = np.linalg.norm(vec2)

    # 3. 确定哪条是长边 (Length)，哪条是宽边 (Width)
    # 并计算对应的旋转角 (长边与x轴夹角)
    if len1 >= len2:
        rect_len = len1
        rect_width = len2
        # atan2(y, x) 计算长边向量的角度
        angle = math.atan2(vec1[1], vec1[0])
    else:
        rect_len = len2
        rect_width = len1
        angle = math.atan2(vec2[1], vec2[0])

    # 4. 计算矩形中心 (对角线中点)
    # 矩形对角顶点是 p0 和 p2 (假设顺序是 p0-p1-p2-p3)
    # 但为了保险，直接用所有顶点的均值作为中心更稳健
    center = np.mean(mbr[:4], axis=0)
    cx, cy = center[0], center[1]

    # 5. 应用老师要求的缩放系数
    # 注意：LMG 算法中 a 和 b 通常指半长轴和半短轴
    init_a = rect_len * 0.5
    init_b = rect_width * 0.5

    return [cx, cy, init_a, init_b, angle]


def fitting_with_MBR_logic(points):
    """
    [新增函数] 替代原有的 fitting_with_R_logic
    流程：
    1. 使用 MBR (最小外接矩形) 获得稳健初值
    2. 将初值传入 LMG (Levenberg-Marquardt) 进行单次高精度拟合
    """
    try:
        # 1. 计算基于矩形的几何初值 [cx, cy, a, b, theta]
        initial_guess = calculate_mbr_initial_guess(points)

        # 2. 使用该初值进行 LMG 拟合
        # 直接调用你现有的 ellipse_fitting_geometric_LMG_version2
        # 因为初值已经很靠谱了，不需要再做插值(8点)步骤，直接对原始点集拟合即可
        geo_params_final = ellipse_fitting_geometric_LMG_version2(points, initial_params=initial_guess)

        # 3. 转换回代数参数返回
        return geometric_to_algebraic(geo_params_final)

    except Exception as e:
        print(f"MBR拟合阶段出错: {e}, 回退到普通代数拟合")
        # 如果矩形计算出错（极少见），回退到旧方法
        return re_ellipse_fitting(points)

# def fitting_with_R_logic(points):
#     """
#     完全复刻 R 代码的逻辑流程：
#     1. 插值生成 8 个点 (vertices + midpoints)
#     2. 在 8 点上拟合 (fit.ellipseLMG with initial guess)
#     3. 将结果作为初值，在原始 4 点上再次拟合
#     """
#     # 1. 插值 (对应 R 代码中的 XY 矩阵构造: 4 vertices + 4 midpoints)
#     # 使用现有的 middle_insert_all 函数，它会返回 原始点 + 中值点
#     # 注意 middle_insert_all 会直接修改列表，所以先复制
#     points_for_interp = points[:]
#     points_8 = middle_insert_all(points_for_interp, points)

#     # 2. 第一次拟合：在 8 个点上进行
#     # R代码: G <- fit.ellipseLMG(XY_8, ParGini)
#     # 这里的 ParGini (初值) 我们通过代数拟合 re_ellipse_fitting 自动获取
#     geo_params_step1 = ellipse_fitting_geometric_LMG(points_8, initial_params=None)

#     # 3. 第二次拟合：在原始 4 个点上进行，使用上一步的结果作为初值
#     # R代码: G <- fit.ellipseLMG(XY_4, ParGini=G_from_step1)
#     geo_params_final = ellipse_fitting_geometric_LMG(points, initial_params=geo_params_step1)

#     # 4. 将最终的几何参数转化为原项目使用的代数参数格式 (can_shu)
#     can_shu_final = geometric_to_algebraic(geo_params_final)

#     return can_shu_final

def enforce_triangle_boundary(can_shu, points):
    """
    [新增] 针对三角形的边界修正逻辑
    检查椭圆是否包围了所有顶点。如果有顶点在椭圆外，
    则计算缩放系数，将椭圆放大至刚好经过最远的那个顶点。
    """
    try:
        # 1. 获取几何参数
        cx, cy = find_center_point(can_shu)
        a = find_a(can_shu)
        b = find_b(can_shu)
        theta = find_angle(can_shu)

        if math.isnan(a) or math.isnan(b) or a <= 0 or b <= 0:
            return can_shu

        # 2. 坐标变换准备
        cos_t = math.cos(-theta) # 逆向旋转，将点转到标准椭圆坐标系
        sin_t = math.sin(-theta)

        max_dist_sq = 0.0

        # 3. 遍历三角形的三个顶点，寻找"最远"的点
        # 椭圆方程判定值: val = (x'/a)^2 + (y'/b)^2
        # val < 1 (内部), val = 1 (边界), val > 1 (外部)
        for p in points:
            dx = p[0] - cx
            dy = p[1] - cy

            # 旋转变换 dx, dy -> tx, ty
            tx = dx * cos_t - dy * sin_t
            ty = dx * sin_t + dy * cos_t

            # 计算椭圆距离平方
            dist_sq = (tx / a) ** 2 + (ty / b) ** 2
            if dist_sq > max_dist_sq:
                max_dist_sq = dist_sq

        # 4. 判断是否需要放大
        # 如果 max_dist_sq > 1.0，说明有点在椭圆外面
        # 我们稍微留一点冗余量 (例如 1.001) 防止浮点误差
        if max_dist_sq > 1.001:
            # 计算放大倍数 k
            # 新方程: (tx / (k*a))^2 + ... = 1  =>  (1/k^2) * old_val = 1  => k = sqrt(old_val)
            scale_factor = math.sqrt(max_dist_sq)

            # print(f"三角形修正: 顶点在外部 (max_val={max_dist_sq:.3f})，放大系数 k={scale_factor:.3f}")

            # 放大长短轴
            new_a = a * scale_factor
            new_b = b * scale_factor

            # 5. 转回代数参数
            # 注意：需确保 geometric_to_algebraic 函数在上下文中可用
            new_geo = [cx, cy, new_a, new_b, theta]
            return geometric_to_algebraic(new_geo)

    except Exception as e:
        print(f"三角形边界修正出错: {e}")

    return can_shu

def safe_calculate_area(can_shu):
    """
    [新增] 安全计算椭圆面积，用于最终的择优比较
    """
    if can_shu is None:
        return float('inf')

    try:
        a = find_a(can_shu)
        b = find_b(can_shu)
        if math.isnan(a) or math.isnan(b) or math.isinf(a) or math.isinf(b):
            return float('inf')
        return math.pi * a * b
    except Exception:
        return float('inf')

def safe_get_area(can_shu):
    """
    [新增辅助函数] 安全计算椭圆面积，用于最终择优
    如果参数无效，返回无穷大，确保在比较时被淘汰
    """
    if can_shu is None:
        return float('inf')
    try:
        a = find_a(can_shu)
        b = find_b(can_shu)
        # 检查 NaN 或 Inf
        if math.isnan(a) or math.isnan(b) or math.isinf(a) or math.isinf(b):
            return float('inf')
        return math.pi * a * b
    except Exception:
        return float('inf')

# def fitting_0203(points, center_point, area):
#     """
#     [重写 V3.0] 老师要求的最终实现版本
#     逻辑流：
#     1. 3或4边形 -> 直接进 LMG。
#     2. 5边及以上 -> 先尝试 最小二乘法 (LS)。
#        -> 检查结果 (面积比 > 3 或 重心外逸)。
#        -> 如果合格: 直接返回。
#        -> 如果异常: 进 LMG。
#     3. LMG 结果检查：
#        -> 如果 LMG 也判定为异常 (且存在 LS 结果)，则对比 LS 和 LMG 的面积。
#        -> 取面积较小的那个结果。
#     """
#     # 0. 数据备份
#     ori_points = points[:]
#     n_sides = len(points)

#     # 定义临时变量
#     ls_can_shu = None   # 最小二乘结果
#     lmg_can_shu = None  # LMG结果
#     final_can_shu = None

#     # 辅助函数：获取面积 (处理异常用)
#     def get_area_safe(params):
#         if params is None: return float('inf')
#         try:
#             val = math.pi * find_a(params) * find_b(params)
#             if math.isnan(val): return float('inf')
#             return val
#         except:
#             return float('inf')

#     # ==========================================
#     # 分支 A: 3边形 或 4边形 (直接用 LMG)
#     # ==========================================
#     if n_sides < 5:
#         try:
#             # 这里的 LMG 调用已经包含了你文件中 calculate_teacher_pargini 的逻辑
#             final_can_shu = fitting_call_R_conicfit(points)
#         except Exception:
#             # 保底
#             final_can_shu = re_ellipse_fitting(points)

#     # ==========================================
#     # 分支 B: 5边及以上 (先 LS，后 LMG，最后 PK)
#     # ==========================================
#     else:
#         # --- 步骤 1: 尝试最小二乘法 (LS) ---
#         ls_can_shu = re_ellipse_fitting(points)

#         # 判断 LS 是否合格
#         is_ls_good = check_ls_quality(ls_can_shu, points, area)

#         if is_ls_good:
#             # 完美情况：LS 拟合正常，直接采纳
#             final_can_shu = ls_can_shu
#         else:
#             # --- 步骤 2: LS 异常，调用 LMG ---
#             # print(">>> 最小二乘异常，转调 LMG")
#             try:
#                 lmg_can_shu = fitting_call_R_conicfit(points)
#             except:
#                 lmg_can_shu = None

#             # 判断 LMG 是否合格
#             is_lmg_good = check_ls_quality(lmg_can_shu, points, area)

#             if is_lmg_good:
#                 # 情况：LS 不行，但 LMG 很完美
#                 final_can_shu = lmg_can_shu
#             else:
#                 # --- 步骤 3: 两个都不合格，进行面积 PK ---
#                 # print(">>> LMG 也异常，触发最终面积 PK")
#                 area_ls = get_area_safe(ls_can_shu)
#                 area_lmg = get_area_safe(lmg_can_shu)

#                 # 谁面积小用谁 (如果 LMG 没算出来，area_lmg 会是无穷大，自然选 LS)
#                 if area_lmg < area_ls:
#                     final_can_shu = lmg_can_shu
#                 else:
#                     final_can_shu = ls_can_shu

#     # ==========================================
#     # 统一出口与保底
#     # ==========================================
#     if final_can_shu is None:
#         final_can_shu = re_ellipse_fitting(points)

#     # 保留最后的格式化/微调 (Iterator设为5避免死循环)
#     final_can_shu = judge_value(final_can_shu, points, area, 5, center_point, ori_points)

#     return final_can_shu

def fitting(points, center_point, area):
    """
    [重写 V9.0] 新的三阶段拟合策略
    策略：
    1. n >= 5：
       - round1: 代数法，基于真实点（n个）
       - round2: 代数法，基于真实点+镜像点（2n个）
       - round3: R LMG，基于真实点+镜像点（2n个），用2n点的MBR做初值
    2. n < 5：
       - round1: R LMG，基于真实点（n个）
       - round2: 代数法，基于真实点+镜像点（2n个）
       - round3: R LMG，基于真实点+镜像点（2n个），用2n点的MBR做初值
    3. 面积比合格范围：1.0 ~ 3.0
    4. 不使用MBR保底，不使用插值法
    """
    ori_points = points[:]
    n_sides = len(points)
    final_can_shu = None

    mirrored_points = mirror_points_180(points[:], center_point)

    if n_sides >= 5:
        # --- n >= 5：代数法真实点 → 代数法2n点 → R LMG 2n点 ---
        
        # round1: 代数法，基于真实点（n个）
        can_shu_round1 = None
        try:
            can_shu_round1 = re_ellipse_fitting(points)
        except Exception as e:
            print(f"round1 代数拟合失败: {e}")
        
        if can_shu_round1 is not None:
            is_round1_ok = check_ls_quality_v5(can_shu_round1, points, area)
            if is_round1_ok:
                final_can_shu = can_shu_round1
            else:
                # round2: 代数法，基于真实点+镜像点（2n个）
                can_shu_round2 = None
                try:
                    can_shu_round2 = re_ellipse_fitting(mirrored_points)
                except Exception as e:
                    print(f"round2 代数拟合失败: {e}")
                
                if can_shu_round2 is not None:
                    is_round2_ok = check_ls_quality_v5(can_shu_round2, points, area)
                    if is_round2_ok:
                        final_can_shu = can_shu_round2
                    else:
                        # round3: R LMG，基于真实点+镜像点（2n个），用2n点的MBR做初值
                        can_shu_round3 = None
                        try:
                            can_shu_round3 = fitting_call_R_conicfit(mirrored_points, mbr_points=mirrored_points)
                        except Exception as e:
                            print(f"round3 R LMG拟合失败: {e}")
                        
                        if can_shu_round3 is not None:
                            is_round3_ok = check_ls_quality_v5(can_shu_round3, points, area)
                            if is_round3_ok:
                                final_can_shu = can_shu_round3
                            else:
                                final_can_shu = can_shu_round2
                        else:
                            final_can_shu = can_shu_round2
                else:
                    # round2失败，尝试round3
                    try:
                        can_shu_round3 = fitting_call_R_conicfit(mirrored_points, mbr_points=mirrored_points)
                        is_round3_ok = check_ls_quality_v5(can_shu_round3, points, area)
                        if is_round3_ok:
                            final_can_shu = can_shu_round3
                        else:
                            final_can_shu = can_shu_round1
                    except Exception:
                        final_can_shu = can_shu_round1
        else:
            # round1失败，尝试round2
            try:
                can_shu_round2 = re_ellipse_fitting(mirrored_points)
                is_round2_ok = check_ls_quality_v5(can_shu_round2, points, area)
                if is_round2_ok:
                    final_can_shu = can_shu_round2
                else:
                    try:
                        can_shu_round3 = fitting_call_R_conicfit(mirrored_points, mbr_points=mirrored_points)
                        is_round3_ok = check_ls_quality_v5(can_shu_round3, points, area)
                        if is_round3_ok:
                            final_can_shu = can_shu_round3
                        else:
                            final_can_shu = can_shu_round2
                    except Exception:
                        final_can_shu = can_shu_round2
            except Exception:
                try:
                    final_can_shu = fitting_call_R_conicfit(mirrored_points, mbr_points=mirrored_points)
                except Exception:
                    pass

    else:
        # --- n < 5：R LMG真实点 → 代数法2n点 → R LMG 2n点 ---
        
        # round1: R LMG，基于真实点（n个）
        can_shu_round1 = None
        try:
            can_shu_round1 = fitting_call_R_conicfit(points)
        except Exception as e:
            print(f"round1 R拟合失败: {e}")
            try:
                can_shu_round1 = re_ellipse_fitting(points)
            except Exception:
                pass
        
        if can_shu_round1 is not None:
            is_round1_ok = check_ls_quality_v5(can_shu_round1, points, area)
            if is_round1_ok:
                final_can_shu = can_shu_round1
            else:
                # round2: 代数法，基于真实点+镜像点（2n个）
                can_shu_round2 = None
                try:
                    can_shu_round2 = re_ellipse_fitting(mirrored_points)
                except Exception as e:
                    print(f"round2 代数拟合失败: {e}")
                
                if can_shu_round2 is not None:
                    is_round2_ok = check_ls_quality_v5(can_shu_round2, points, area)
                    if is_round2_ok:
                        final_can_shu = can_shu_round2
                    else:
                        # round3: R LMG，基于真实点+镜像点（2n个），用2n点的MBR做初值
                        can_shu_round3 = None
                        try:
                            can_shu_round3 = fitting_call_R_conicfit(mirrored_points, mbr_points=mirrored_points)
                        except Exception as e:
                            print(f"round3 R LMG拟合失败: {e}")
                        
                        if can_shu_round3 is not None:
                            is_round3_ok = check_ls_quality_v5(can_shu_round3, points, area)
                            if is_round3_ok:
                                final_can_shu = can_shu_round3
                            else:
                                final_can_shu = can_shu_round2
                        else:
                            final_can_shu = can_shu_round2
                else:
                    # round2失败，尝试round3
                    try:
                        can_shu_round3 = fitting_call_R_conicfit(mirrored_points, mbr_points=mirrored_points)
                        is_round3_ok = check_ls_quality_v5(can_shu_round3, points, area)
                        if is_round3_ok:
                            final_can_shu = can_shu_round3
                        else:
                            final_can_shu = can_shu_round1
                    except Exception:
                        final_can_shu = can_shu_round1
        else:
            # round1失败，尝试round2
            try:
                can_shu_round2 = re_ellipse_fitting(mirrored_points)
                is_round2_ok = check_ls_quality_v5(can_shu_round2, points, area)
                if is_round2_ok:
                    final_can_shu = can_shu_round2
                else:
                    try:
                        can_shu_round3 = fitting_call_R_conicfit(mirrored_points, mbr_points=mirrored_points)
                        is_round3_ok = check_ls_quality_v5(can_shu_round3, points, area)
                        if is_round3_ok:
                            final_can_shu = can_shu_round3
                        else:
                            final_can_shu = can_shu_round2
                    except Exception:
                        final_can_shu = can_shu_round2
            except Exception:
                try:
                    final_can_shu = fitting_call_R_conicfit(mirrored_points, mbr_points=mirrored_points)
                except Exception:
                    pass

    # 最终保底：只用代数法，不使用MBR
    if final_can_shu is None or safe_get_area(final_can_shu) == float('inf'):
        try:
            final_can_shu = re_ellipse_fitting(points)
        except Exception:
            final_can_shu = None

    return final_can_shu
