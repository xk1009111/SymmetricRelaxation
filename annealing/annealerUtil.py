import math
from utillib.mylib import Point, Line, Line_in_Polar_Coordinate_System, CellBlock
from cell.CellData import CellData
k_R = 0.1
k_D = 1.0
##正式的代码修改
# from cell.annealing_statistics import annealing_statistics
def n_rotate(angle, x, y, cx, cy):
    """
    将点 (x, y) 绕点 (cx, cy) 逆时针旋转 angle 弧度
    :param angle: 旋转角度（弧度）
    :param x: 原始点 x 坐标
    :param y: 原始点 y 坐标
    :param cx: 旋转中心 x 坐标
    :param cy: 旋转中心 y 坐标
    :return: 旋转后的 (x, y) 坐标
    """
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    dx = x - cx
    dy = y - cy
    new_x = dx * cos_a - dy * sin_a + cx
    new_y = dx * sin_a + dy * cos_a + cy
    return new_x, new_y

"""
    根据三个点获取角度，第二个点作为角中心点。（依据公式进行计算）
    The angle is obtained from three points, and the second point is used as the center point of the corner. (calculated according to the formula)
    :param p_list: 数组，包含三个点。 Array containing three points.
    :return: 角度 angle
"""
##test
##这里的abc是边长？根据勾股定理求abc的边长用来求角度？
def get_angle_by_three_point(p_list):
    """
    根据三个点计算内角，能够正确处理大于180度的凹角（优角）。
    假定顶点是按逆时针顺序排列的。
    """
    p1, p_vertex, p2 = p_list[0], p_list[1], p_list[2]

    # 从顶点p_vertex指向p1和p2的向量
    v1 = [p1[0] - p_vertex[0], p1[1] - p_vertex[1]]
    v2 = [p2[0] - p_vertex[0], p2[1] - p_vertex[1]]

    # 向量的点积
    dot_product = v1[0] * v2[0] + v1[1] * v2[1]

    # 向量的模长
    mag1 = math.sqrt(v1[0]**2 + v1[1]**2)
    mag2 = math.sqrt(v2[0]**2 + v2[1]**2)

    # 防止除零错误
    if mag1 * mag2 == 0:
        return 0

    # 计算余弦值并限制在[-1, 1]范围内，防止浮点误差
    cos_angle = max(-1.0, min(1.0, dot_product / (mag1 * mag2)))

    # 通过反余弦计算基础角 (0 to pi)
    angle = math.acos(cos_angle)

    # 使用二维向量的叉乘来判断角度方向
    # 叉乘 Z 分量: v1.x * v2.y - v1.y * v2.x
    cross_product_z = v1[0] * v2[1] - v1[1] * v2[0]

    # 假设多边形顶点是逆时针(CCW)顺序。
    # 在CCW多边形中，所有内角都应该是"左转"。
    # v1到v2的叉乘为正，表示左转，是凸角 (<180)。
    # 如果叉乘为负，表示右转，是凹角 (>180)，我们需要取其优角。
    if cross_product_z < 0:
        return 2 * math.pi - angle  # 返回大于180度的优角
    else:
        return angle  # 返回小于180度的锐角或钝角


"""
    计算两点之间的距离(根据公式进行计算)
    Calculate the distance between two points (according to the formula)
    :param p1: Point对象 Point object
    :param p2: Point对象 Point object
    :return: 距离 distance
"""


def get_distance_point_point_last(p1, p2):
    distance = math.sqrt((p1.x - p2.x) * (p1.x - p2.x) +
                         (p1.y - p2.y) * (p1.y - p2.y))
    return distance

def get_distance_point_point(p1, p2):
    """
    计算两点之间的距离，支持多种格式

    Args:
        p1: 点1，可以是 Point 对象、列表 [x,y] 或元组 (x,y)
        p2: 点2，格式同 p1

    Returns:
        float: 两点间的距离
    """
    # 处理 p1
    if hasattr(p1, 'x') and hasattr(p1, 'y'):
        # p1 是 Point 对象
        x1, y1 = p1.x, p1.y
    elif isinstance(p1, (list, tuple)) and len(p1) >= 2:
        # p1 是列表或元组 [x,y]
        x1, y1 = p1[0], p1[1]
    else:
        raise ValueError(f"不支持的坐标格式: {type(p1)}")

    # 处理 p2
    if hasattr(p2, 'x') and hasattr(p2, 'y'):
        # p2 是 Point 对象
        x2, y2 = p2.x, p2.y
    elif isinstance(p2, (list, tuple)) and len(p2) >= 2:
        # p2 是列表或元组 [x,y]
        x2, y2 = p2[0], p2[1]
    else:
        raise ValueError(f"不支持的坐标格式: {type(p2)}")

    # 计算距离
    distance = math.sqrt((x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2))
    return distance

"""
    计算两点之间的距离(根据公式进行计算)（点为列表类型）
    Calculate the distance between two points (according to the formula)
    :param p1: list []
    :param p2: list []
    :return: 距离 distance
"""

##勾股定理求距离，但p1，p2的作用是？
###为什么有两个求距离的函数？？
def get_distance_point_point_by_list(p1, p2):
    distance = math.sqrt((p1[0] - p2[0]) * (p1[0] - p2[0]) +
                         (p1[1] - p2[1]) * (p1[1] - p2[1]))
    return distance


"""
    计算点到线的距离
    Calculate the distance from the point to the line(calculated according to the formula)
    :param point: Point对象 Point object
    :param line: Line对象 Line object
    :return: 距离 distance
"""

def get_distance_point_line(point, line):
    a = line.p2.y - line.p1.y
    b = line.p1.x - line.p2.x
##c是两点叉乘
    c = line.p2.x * line.p1.y - line.p1.x * line.p2.y
    dis = (math.fabs(a * point.x + b * point.y + c)) / (math.pow(a * a + b * b, 0.5))
    return dis


"""
    获取中心点到细胞端点的最大距离
    Gets the maximum distance from the center point to the cell endpoint
    :param cell: Cell细胞对象 Cell object
    :return: 中心点到细胞端点的最大距离 Maximum distance from center point to cell end point
"""


def get_distance_centerpoint_point(cell):
    central_point = cell.center_point
    max_distance = 0
    for point in cell.points:  # 循环遍历所有端点到中心点的距离 Loop through the distances from all endpoints to the center
        # print(point)

        tmp_distance = get_distance_point_point(Point(point[0], point[1]), central_point)
        #print("central")
        if tmp_distance > max_distance:
            max_distance = tmp_distance
        # print(point,central_point,tmp_distance)
    return max_distance


"""
    获取从细胞中心点过细胞所有顶点的所有直线，以弧度制表示
    Obtain all lines from the center point of the cell through all the vertices of the cell, expressed in radians
    :param cell: 细胞信息，Cell对象 Cell object
    :param max_distence: 细胞中心点距离细胞顶点的最大距离 The maximum distance between the cell center and the cell apex
    :return: Line_in_Polar_Coordinate_System对象的列表 List of Line_ In_ Polar_ Coordinate_System objects
"""


def get_actual_lines(cell, max_distence):
    center_point = cell.center_point
    r = max_distence
    actual_lines = []
    for point in cell.points:  # 遍历细胞所有顶点 Traverse all the vertices of the cell
        ##求取中心点和顶点的相对xy差值
        p = Point(point[0] - center_point.x, point[1] - center_point.y)
        if p.x == 0:
            cita = math.pi/2
        else:
            cita = math.atan(p.y / p.x)
        if p.x < 0:  # 根据坐标，判断cita的实际取值 According to the coordinates, determine the actual value of CITA
            if p.y > 0:
                cita = math.pi + cita
            else:
                cita = cita - math.pi
        ##求取极坐标下的θ转回笛卡尔坐标用来绘制从细胞中心点过细胞所有顶点的所有直线
        line = Line_in_Polar_Coordinate_System(cita, r)
        actual_lines.append(line)
    return actual_lines


"""
    获取过细胞中心点，且靠近各个顶点的n条预最优直线，以弧度制表示
    The N pre optimal lines passing through the cell center and close to each vertex are expressed in radians
    :param cell: 细胞信息，Cell对象 Cell object
    :param max_distence: 细胞中心点距离细胞顶点的最大距离 The maximum distance between the cell center and the cell apex
    :param delta: 旋转增量，默认为0 Rotation increment, the default is 0
    :return: Line_in_Polar_Coordinate_System对象的列表 List of Line_ In_ Polar_ Coordinate_System objects
"""


def get_pre_best_lines(cell, max_distence, delta=0):
    center_point = cell.center_point
    r = max_distence
    unit_angle = 2 * math.pi / len(
        cell.points)  # 根据顶点个数计算的实际间隔 The actual interval calculated according to the number of vertices
    pre_best_lines = []
    cita = delta
    for point in cell.points:  # # 遍历细胞所有顶点 Traverse all the vertices of the cell
        if len(pre_best_lines) == 0:  # 如果是第一个顶点 If it's the first vertex
            p = Point(point[0] - center_point.x, point[1] - center_point.y)
            if p.x == 0:
                cita = cita + math.pi/2
            else:
                cita = cita + math.atan(p.y / p.x)
            if p.x < 0:  # 根据坐标，判断cita的实际取值 According to the coordinates, determine the actual value of CITA
                if p.y > 0:
                    cita = math.pi + cita
                else:
                    cita = cita - math.pi
            line = Line_in_Polar_Coordinate_System(cita, r)
            pre_best_lines.append(line)
        else:  # 如果不是第一次循环
            cita = cita + unit_angle  # 上次循环的角度加上实际间隔角度 The angle of the last cycle plus the actual interval angle
            line = Line_in_Polar_Coordinate_System(cita, r)
            pre_best_lines.append(line)
    return pre_best_lines


"""
    获取实际连线与预最优连线的角度平方和
    Get the square sum of the angles between the actual line and the pre optimal line
    :param actual_lines: 实际细胞连线 Actual cell line
    :param pre_best_lines: 预最优细胞连线 Pre optimal cell line
    :return: 实际连线与预最优连线的角度平方和 The sum of the squares of the angles between the actual line and the pre optimal line
"""

##求取当前角度和理论最优线的角度差
def get_sum_angle(actual_lines, pre_best_lines):
    sum = 0
    for i in range(0, len(actual_lines)):
        cita1 = pre_best_lines[i].cita
        cita2 = actual_lines[i].cita
        diffrence = cita1 - cita2
        if diffrence > math.pi:
            diffrence = 2 * math.pi - diffrence
        sum = sum + (diffrence * (diffrence))
    # print(sum)
    return sum


'''
    通过公式计算的方法，找到旋转增量的精确值（根据公式进行计算）
    The exact value of rotation increment is found by formula calculation.(calculated according to the formula)
    :param cell: 细胞对象 Cell object
    :return : 细胞连线达到最优时的旋转角度增量 delta The increment delta of rotation angle when the cell line is optimal
'''


def get_best_rotate_delta_by_calculation(cell):
    N = len(cell.points)
    n = 0  # 索引
    sum_Bn = 0

    # 寻找其中最小角度为A1 Find the minimum angle A1
    index = 0
    min_cita = 100
    for i in range(0, N):
        if min_cita > cell.actual_lines[i].cita:
            min_cita = cell.actual_lines[i].cita
            index = i

    A1 = cell.actual_lines[index].cita

    index_ = index
    for i in range(0, N):
        cell_constant = n * 2 * math.pi / N  # 此处计算公式本为（n-1）由于索引n本身从0开始，故直接使用即可。 The calculation formula here is (n-1). Since the index n itself starts from 0, it can be used directly.
        An = cell.actual_lines[index_].cita
        Bn = An - cell_constant
        sum_Bn = sum_Bn + Bn
        n += 1
        index_ = (index_ + 1) % N
    X1 = sum_Bn / N
    X1 = X1 - index * 2 * math.pi / N
    A1 = cell.actual_lines[0].cita

    delta = X1 - A1  # 将计算出的偏转角与实际角度相减，得到旋转增量。 The rotation increment is obtained by subtracting the calculated deflection angle with the actual angle.

    return delta


"""
    获取点在细胞内的索引
    Gets the index of the point in the cell
    :param cell: 细胞，Cell对象 Cell object
    :param point: 点，元组 Dot, tuple
    :return: 点在细胞内的索引 Index of point in cell
"""


def get_point_index_in_cell(cell, point):
    points = cell.points
    index = points.index(point)
    return index


"""
    获取三个细胞交汇的交汇细胞块列表，CellBlock对象
    Get the list of intersecting cell blocks where three cells meet, CELLBLOCK object
    :param cells: 细胞集，Cell对象列表 list of Cell object
    :return: 交汇细胞块列表，CellBlock对象 List of intersecting cell blocks, CellBlock object
"""


def get_intersection_cell_blocks(cells):
    if len(cells[0].pre_best_lines) == 0:  # 异常验证  Exception verification
        print("细胞尚未退火，请先退火！")
        return []

    intersection_cell_blocks = []  # 细胞块集合 Cell mass assembly

    pre_intersection_points = []  # 细胞点集 Cell point set
    pre_intersection_points_index = []  # 细胞点数量统计表 Statistical table of cell number

    pre_cell_index = []  # 点-细胞索引：第几个点，过哪几个细胞 Point cell index: the point, which cells

    cell_index = 0
    for cell in cells:
        point_index = 0
        for point in cell.points:
            # print(point)
            # print(pre_intersection_points)
            # print(point)
            # print(type(point))
            # print(type([0, 0]))
            if point in pre_intersection_points:
                # 这里需要保存新的 点-细胞索引。在原有点-细胞索引的位置上追加保存
                # The new point cell index needs to be saved here. Save the original point cell index in the position
                pre_cell_index[pre_intersection_points.index(point)].append(cell_index)
                # 统计该点出现次数，将其加 1 Count the occurrence times of this point and add 1
                pre_intersection_points_index[pre_intersection_points.index(point)] += 1

            else:
                # print(point)
                pre_intersection_points.append(point)  # 保存该点 Save the point
                # print(pre_intersection_points)
                pre_intersection_points_index.append(1)  # 统计该点出现次数，初始化为1次 Count the occurrence times of this point and initialize it as 1 time
                pre_cell_index.append([cell_index])  # 存放过该点的第一个细胞索引 The first cell index stored at this point

            point_index += 1
        cell_index += 1

    ##遍历将细胞点数量统计表中，出现次数超过三次的点进行提取，构造出一个细胞块，并绘制三条直线构成三角形
    for i in range(0, len(pre_intersection_points)):
        if pre_intersection_points_index[i] == 3:
            # 将细胞点数量统计表中，出现次数超过三次的点进行提取，构造出一个细胞块
            # In the statistical table of cell number, the points that appear more than three times are extracted to construct a cell block
            cell_block = CellBlock()
            cell_block.setCell1(cells[pre_cell_index[i][0]],
                                get_point_index_in_cell(cells[pre_cell_index[i][0]], pre_intersection_points[i]))
            cell_block.setCell2(cells[pre_cell_index[i][1]],
                                get_point_index_in_cell(cells[pre_cell_index[i][1]], pre_intersection_points[i]))
            cell_block.setCell3(cells[pre_cell_index[i][2]],
                                get_point_index_in_cell(cells[pre_cell_index[i][2]], pre_intersection_points[i]))
            cell_block.setPoint(pre_intersection_points[i])
            line1 = Line(Point(cell_block.cell1.vx, cell_block.cell1.vy),
                         Point(cell_block.cell1.vx + cell_block.cell1.pre_best_lines[cell_block.index1].getX(),
                               cell_block.cell1.vy + cell_block.cell1.pre_best_lines[cell_block.index1].getY()))

            line2 = Line(Point(cell_block.cell2.vx, cell_block.cell2.vy),
                         Point(cell_block.cell2.vx + cell_block.cell2.pre_best_lines[cell_block.index2].getX(),
                               cell_block.cell2.vy + cell_block.cell2.pre_best_lines[cell_block.index2].getY()))

            line3 = Line(Point(cell_block.cell3.vx, cell_block.cell3.vy),
                         Point(cell_block.cell3.vx + cell_block.cell3.pre_best_lines[cell_block.index3].getX(),
                               cell_block.cell3.vy + cell_block.cell3.pre_best_lines[cell_block.index3].getY()))

            cell_block.triangle = get_triangle_by_lines([line1, line2, line3])

            intersection_cell_blocks.append(cell_block)

    # return intersection_points
    return intersection_cell_blocks




#统计内部和边缘顶点个数，并保存，保存形式为两个列表，分别统计边缘和内部顶点的个数并返回这两个列表
# def get_cell_block_points_index(cells):
#     edge_points_index = []
#     internal_points_index = []
#     for cell in cells:
#         for point_idx, point in enumerate(cell.points):
#             # 根据Cell类的属性判断是否为边缘点
#             # 假设Cell类有layer属性，layer!=1表示边缘细胞
#             # 或者根据其他属性如ok属性判断
#             if hasattr(cell, 'layer') and cell.layer != 1:
#                 edge_points_index.append(point_idx)
#             else:
#                 internal_points_index.append(point_idx)
#     return edge_points_index, internal_points_index



'''
    根据退火速率计算退火目标点
    The annealing target point is calculated according to the annealing rate
    :param point_pre: 当前点 Current point
    :param point_pre: 退火点 Annealing point
    :param point_pre: 退火速率 Annealing rate
'''


def get_point_of_destination(point_pre, point_fin, step):
    point_pre = Point(point_pre[0], point_pre[1])

    ##new_point是从当前位置到目标位置的距离（Δx和Δy）
    new_point = Point(point_fin.x - point_pre.x, point_fin.y - point_pre.y)

    ##单次退火移动的距离
    move_point = Point(step * new_point.x + point_pre.x, step * new_point.y + point_pre.y)

    return move_point


"""
    斜率计算方法
    Slope calculation method
    :param x1,y1,x2,y2: 两点坐标 Two point coordinates
    :return: 斜率 Slope
"""


def get_slope_by_xy(x1, y1, x2, y2):
    k = (y1 - y2) / (x1 - x2)
    return k


"""
    获取两条直线的交点坐标
    Get the intersection coordinates of two lines
    :param l1: 第一条直线，Line对象 First line, line object
    :param l2: 第二条直线，Line对象 Second line, line object
    :return: 交点坐标，Point对象 Intersection coordinates, point object
"""


def get_crossover_point(l1, l2):
    x1 = l1.p1.x
    y1 = l1.p1.y
    x2 = l1.p2.x
    y2 = l1.p2.y

    x3 = l2.p1.x
    y3 = l2.p1.y
    x4 = l2.p2.x
    y4 = l2.p2.y

    # 分三种情况，计算交点坐标 In three cases, the coordinates of intersection point are calculated
    if not (math.isclose(x1, x2, rel_tol=1e-9) or math.isclose(x3, x4, rel_tol=1e-9)):  # 一般情况下  Normally
        k1 = get_slope_by_xy(x1, y1, x2, y2)
        k2 = get_slope_by_xy(x3, y3, x4, y4)
        if math.isclose(k1, k2, rel_tol=1e-12):
            return None
        x = -(((y1 - k1 * x1) - (y3 - k2 * x3)) / (k1 - k2))
        y = k1 * x + (y1 - k1 * x1)
    elif math.isclose(x1, x2, rel_tol=1e-9):  # l1垂直于x轴 L1 is perpendicular to the X axis
        k2 = get_slope_by_xy(x3, y3, x4, y4)
        x = x1
        y = k2 * (x - x3) + y3
    elif math.isclose(x3, x4, rel_tol=1e-9):  # l2垂直于x轴 L2 is perpendicular to the X axis
        k1 = get_slope_by_xy(x1, y1, x2, y2)
        x = x3
        y = k1 * (x - x1) + y1
    else:
        return None
    return Point(x, y)


"""
    根据三条线（3 × 2个点）,获取三角形（三个顶点）
    According to three lines (3 × 2 points), get the triangle (three vertices)
    :param lines: 三条线的集合，Line对象列表 Collection of three lines, list of line objects
    :return: 三角形三点坐标集 Three point coordinate set of triangle
"""


def get_triangle_by_lines(lines):
    point1 = get_crossover_point(lines[0], lines[1])
    point2 = get_crossover_point(lines[0], lines[2])
    point3 = get_crossover_point(lines[1], lines[2])
    point4 = point1  # 形成闭环，便于作图 Form a closed loop for drawing

    return [point1, point2, point3, point4]


'''
    排序算法，对退火细胞块，按照最大内角降序排列
    Sorting algorithm: annealing cells are arranged in descending order according to the maximum inner angle
    :param intersection_cell_blocks: 退火细胞块列表 Annealed cell block list
    :return: 排序后的退火细胞块列表 Sorted annealing cell block list
'''
def sort_intersection_cell_blocks(intersection_cell_blocks):
    dict_cbs = []
    for cb in intersection_cell_blocks:
        dict_cb = {}
        dict_cb['cb'] = cb
        dict_cb['max_angle'] = get_max_angle(cb)
        dict_cbs.append(dict_cb)
    dict_cbs = sorted(dict_cbs, key=lambda e: e.__getitem__('max_angle'), reverse=True)

    return dict_cbs
def get_cell_block_type(cells):
    """
    判断细胞块类型

    :param cell_block: 细胞块对象
    :return: 细胞块类型，"internal" 或 "edge"
    """
    if cells.layer == 1:  # 边缘细胞
        return "edge"
    else:  # 内部细胞
        return "internal"
'''新排序算法，对退火细胞块，按照距离退火目标点距离进行升序排列'''
# def sort_cells_by_displacement_test02(cells):
#     """
#     按照细胞到理想目标点的完整位移排序，同时处理内部和外部细胞
#     返回包含详细信息的排序列表

#     :param intersection_cell_blocks: 细胞块列表
#     :param cells: 所有细胞列表（用于边缘细胞判断）
#     :return: 排序后的细胞块信息列表，包含类型标记和距离信息
#     """
#     sorted_cell_info = []

#     for i, cb in enumerate(intersection_cell_blocks):
#         # 1. 判断细胞类型
#         cell_type = get_cell_block_type(cb)
#         is_edge = (cell_type != "internal")

#         # 2. 获取当前顶点位置
#         current_point = cb.cell1.points[cb.index1]

#         # 3. 根据类型计算目标点
#         if is_edge:
#             # 使用新的理想目标点计算函数
#             target_point = calculate_ideal_target_point(cb, cells)
#         else:
#             # 内部细胞使用三角形重心
#             target_point = cb.getTriCentreOfGravity()

#         # 4. 计算完整位移距离
#         displacement = get_distance_point_point(current_point, target_point)

#         # # 5. 添加类型权重（可选：边缘细胞优先级调整）
#         # weight = get_type_weight(cell_type)
#         # weighted_displacement = displacement * weight

#         # 6. 构建详细信息字典
#         # cell_info = {
#         #     'index': i,  # 原始索引
#         #     'cell_block': cb,
#         #     'displacement': displacement,
#         #     'cell_type': cell_type,
#         #     'is_edge': is_edge,
#         #     'current_point': current_point,
#         #     'target_point': target_point,
#         #     #'weighted_displacement': weighted_displacement,
#         #     #'weight': weight
#         # }

#         #sorted_cell_info.append(cell_info)

#     # 7. 按照加权位移降序排列
#     sorted_cell_info = sorted(sorted_cell_info, key=lambda x: x['weighted_displacement'],reverse=True)
#     return sorted_cell_info

# def sort_cells_by_displacement(cells):
#     sorted_cell_info = []
#     for cell in cells:
#         if cell.layer == 1:  # 边缘细胞
#             cell.displacement = get_distance_point_point(cell.points[0], cell.points[1])
#         else:  # 内部细胞
#             cell.displacement = get_distance_point_point(cell.points[0], cell.points[1])
#             cell.displacement += get_distance_point_point(cell.points[1], cell.points[2])
#     sorted_cell_info = sorted(sorted_cell_info, key=lambda x: x['weighted_displacement'],reverse=True)
#     return sorted_cell_info
##sort_cells_by_annealing_distance_des
##sort_cells_by_distance的辅助函数

def is_edge_cell_block(cb):
    """判断细胞块是否为边缘细胞块"""
    edge_count = 0
    if hasattr(cb.cell1, 'layer') and cb.cell1.layer != 1: edge_count += 1
    if hasattr(cb.cell2, 'layer') and cb.cell2.layer != 1: edge_count += 1
    if hasattr(cb.cell3, 'layer') and cb.cell3.layer != 1: edge_count += 1

    return edge_count > 0

def get_cell_block_type(cb):
    """获取细胞块的具体类型"""
    edge_count = 0
    if hasattr(cb.cell1, 'layer') and cb.cell1.layer != 1: edge_count += 1
    if hasattr(cb.cell2, 'layer') and cb.cell2.layer != 1: edge_count += 1
    if hasattr(cb.cell3, 'layer') and cb.cell3.layer != 1: edge_count += 1

    if edge_count == 0:
        return "internal"
    elif edge_count == 1:
        return "edge_single"
    elif edge_count == 2:
        return "edge_double"
    else:
        return "edge_triple"


def sort_cells_by_distance(intersection_cell_blocks, cells):
    """
    计算每个交汇块当前顶点到理想目标点的距离 D，并按 D 降序排序
    - 内部细胞目标点：三角形重心
    - 边缘细胞目标点：使两个边缘角相等的点
    返回包含距离、类型标记与当前/目标点的列表
    """
    cell_distance_info = []

    for idx, cb in enumerate(intersection_cell_blocks):
        # 1. 获取当前顶点位置
        current_point = cb.cell1.points[cb.index1]

        # 2. 根据细胞类型计算理想目标点
        if is_edge_cell_block(cb):
            target_point = calculate_ideal_target_point(cb, cells)  # 边缘细胞目标点
        else:
            target_point = cb.getTriCentreOfGravity()  # 内部细胞目标点（三角形重心）

        # 3. 计算退火距离（当前点到目标点的欧氏距离）

        annealing_distance = get_distance_point_point(current_point, target_point)
        #print("target")
        # 4. 记录细胞块信息和距离
        cell_info = {
            'original_index': idx,  # 原始索引
            'cell_block': cb,
            'annealing_distance': annealing_distance,
            'current_point': current_point,
            'target_point': target_point,
            'is_edge': is_edge_cell_block(cb)
        }

        cell_distance_info.append(cell_info)

    # 5. 按照退火距离降序排列（距离大的优先）
    sorted_cell_info = sorted(cell_distance_info, key=lambda x: x['annealing_distance'], reverse=True)
    return sorted_cell_info



'''
    获取退火细胞块中的最大内角
    Obtain the maximum internal angle in the annealed cell block
    :param cb: 退火细胞块 Annealed cell block
    :return: 最大内角 Maximum internal angle
'''


def get_max_angle(cb):
    a1 = get_angle_by_three_point([cb.cell1.points[cb.index1 - 1], cb.cell1.points[cb.index1],
                                   cb.cell1.points[(cb.index1 + 1) % len(cb.cell1.points)]])
    a2 = get_angle_by_three_point([cb.cell2.points[cb.index2 - 1], cb.cell2.points[cb.index2],
                                   cb.cell2.points[(cb.index2 + 1) % len(cb.cell2.points)]])
    a3 = get_angle_by_three_point([cb.cell3.points[cb.index3 - 1], cb.cell3.points[cb.index3],
                                   cb.cell3.points[(cb.index3 + 1) % len(cb.cell3.points)]])
    max_a = a1
    if a2 > max_a:
        max_a = a2
    if a3 > max_a:
        max_a = a3
    return max_a


'''
    判断一个退火细胞块内的三个细胞是否符合条件。
    Determine whether three cells in an annealed cell block meet the conditions.
    :param intersection_cell_blocks: 退火细胞块 Annealed cell block
    :param move_point: 移动后的点坐标 Point coordinates after moving
    :return: True or False，代表该退火细胞块是否符合条件 Represents whether the annealed cell block meets the conditions
'''


def judge_by_intersection_cell_blocks(intersection_cell_blocks, move_point):
    if judge_by_cell(intersection_cell_blocks.cell1, intersection_cell_blocks.index1, move_point):
        return True
    if judge_by_cell(intersection_cell_blocks.cell2, intersection_cell_blocks.index2, move_point):
        return True
    if judge_by_cell(intersection_cell_blocks.cell3, intersection_cell_blocks.index3, move_point):
        return True

    return False


'''
    判断一个细胞内的三个受影响角度是否符合条件。
    Determine whether the three affected angles in a cell meet the conditions.
    :param cell: 细胞 cell object
    :param index: 索引,代表该细胞中的哪个点将会移动。 Index that represents which point in the cell will move.
    :param move_point: 移动后的点坐标 Point coordinates after moving
    :return: True or False，代表该细胞是否符合条件 Represents whether the cell is eligible
'''


def judge_by_cell(cell, index, move_point):
    # 角度方法，在2.0及以上的版本中已弃用 Angle method, obsolete in versions 2.0 and above
    '''
    vp = (cell.vx, cell.vy)

    cell_points_len = len(cell.points)

    points = cell.points[:]
    #print(points[index])
    points[index] = (move_point.x,move_point.y)
    #print(points[index])
    for i in range(index-2, index+1):
        if judge_by_point([points[i], points[(i+1)%cell_points_len], points[(i+2)%cell_points_len]], vp):
            return True
    return False
    '''

    # 状态改变方法 State change method
    vp = [cell.vx, cell.vy]

    cell_points_len = len(cell.points)

    points = cell.points[:]

    ii = 0
    for i in range(index - 2, index + 1):
        if judge_by_change(Line(Point(points[i][0], points[i][1]),
                                Point(points[(i + 2) % cell_points_len][0], points[(i + 2) % cell_points_len][1])),
                           Point(vp[0], vp[1]),
                           Point(points[(i + 1) % cell_points_len][0], points[(i + 1) % cell_points_len][1]),
                           move_point, ii):
            return True
        ii += 1
    return False


'''
    同侧改变判断法：通过判断移动前后，同侧或异常的状态是否发生改变，来判断移动后的图形是否满足条件。
    Ipsilateral change judgment method: by judging whether the ipsilateral or abnormal state changes before and after moving, it can judge whether the moved figure meets the conditions.
    :param line: 线段l， Line对象 Line L, line object
    :param o: 细胞重心点，Point对象，下同  Cell center of gravity, point object, the same below
    :param p: 中间点  Intermediate point
    :param moved_p: 移动后的点 Point after moving
    :param i: 移动点的索引 Index of moving point
    :return: True or False，代表是否满足条件 Represents whether it is eligible
'''


def judge_by_change(line, o, p, move_p, i):
    # 计算线段l的一般式参数 Calculating the parameters of general formula of line segment L
    a = line.p2.y - line.p1.y
    b = line.p1.x - line.p2.x
    c = line.p2.x * line.p1.y - line.p1.x * line.p2.y

    flag = True  # 状态改变参数，默认为True，即已改变 State change parameter, the default is true, that is changed
    in_flag = False  # 是否在线段上的标志。默认初始状态不在线段上
    # 判断原始两点是否在l两侧部分 Judge whether the original two points are on both sides of L
    judge_param = (a * o.x + b * o.y + c) * (
                a * p.x + b * p.y + c)  # 判断参数: 通过将点带入直线一般式，计算两点一般式的乘积 来判断是否在直线两侧 Judgment parameter: by bringing the point into the general formula of the line and calculating the product of the general formula of two points to judge whether it is on both sides of the line
    # print(judge_param,'--------------------------------------')
    # if math.fabs(judge_param) < 1e-10:
    #     print(judge_param)
    #     print(p.x, p.y)
    if math.fabs(judge_param) < 1e-10:  # 一旦某个点在线上，则不可移动 Once a point is on the line, it cannot be moved
        # print("不可移动")
        in_flag = True  # 切换为初始在线上
    if judge_param > 0:  # 两点同侧 Two points on the same side
        flag = True  # 此处表示两点同侧，本参数会和移动后的结果求异或，从而正确表示状态是否改变 Here, two points are on the same side. This parameter will be different from or after moving, so as to correctly indicate whether the state has changed
    else:
        flag = False  # 此处表示两点异侧 Here are two opposite sides

    # 判断移动后的两点是否在l两侧部分 Judge whether the two points after moving are on both sides of L
    if i == 0:  # 移动点的上一个判断 Last judgment of moving point
        a = move_p.y - line.p1.y
        b = line.p1.x - move_p.x
        c = move_p.x * line.p1.y - line.p1.x * move_p.y
    elif i == 1:  # 移动点的判断 Judgment of moving point
        p = move_p
    else:  # 移动点的下一个判断 The next judgment of moving point
        a = line.p2.y - move_p.y
        b = move_p.x - line.p2.x
        c = line.p2.x * move_p.y - move_p.x * line.p2.y

    judge_param = (a * o.x + b * o.y + c) * (a * p.x + b * p.y + c)  # 判断参数 Judgment parameters

    if in_flag:  # 根据不同的初始状态，进行不同的操作  如果初始在线上
        if math.fabs(judge_param) < 1e-10:  # 一旦某个点在线上，则不可移动 Once a point is on the line, it cannot be moved
            return True
        elif judge_param < 0:
            return False
        else:
            return True
    else:  # 不在线上
        if math.fabs(judge_param) < 1e-10:  # 一旦某个点在线上，则不可移动 Once a point is on the line, it cannot be moved
            return True
        if judge_param > 0:  # 两点同侧 Two points on the same side
            return flag ^ True
        else:
            return flag ^ False


'''
    计算移动前后的内角平方和是否增加
    Calculate whether the sum of squares of interior angles increases before and after moving
    :param cb: 退火细胞块 Annealed cell block
    :param mp: 移动后的中心点坐标。Point对象 The center point coordinates after moving. Point object
    :return : True or False 表示是否增加 Represents whether to increase
'''


def judge_sum_inner_angle2(cb, mp):
    len_points1 = len(cb.cell1.points)
    len_points2 = len(cb.cell2.points)
    len_points3 = len(cb.cell3.points)

    angle1 = get_angle_by_three_point([cb.cell1.points[(cb.index1 - 1)], cb.cell1.points[(cb.index1)],
                                       cb.cell1.points[(cb.index1 + 1) % len_points1]])
    angle2 = get_angle_by_three_point([cb.cell2.points[(cb.index2 - 1)], cb.cell2.points[(cb.index2)],
                                       cb.cell2.points[(cb.index2 + 1) % len_points2]])
    angle3 = get_angle_by_three_point([cb.cell3.points[(cb.index3 - 1)], cb.cell3.points[(cb.index3)],
                                       cb.cell3.points[(cb.index3 + 1) % len_points3]])

    '''
    if not ((angle1 >= math.pi*8/9 and angle1<math.pi) or (angle2 >= math.pi*8/9 and angle2<math.pi) or (angle3 >= math.pi*8/9 and angle3<math.pi)):
        return False
    '''

    # 计算移动之前的内角平方和 Calculate the sum of squares of interior angles before moving
    be_sia = angle1 * angle1
    be_sia += angle2 * angle2
    be_sia += angle3 * angle3

    # 计算移动之后的内角平方和 Calculate the sum of squares of interior angles after moving
    af_angle1 = get_angle_by_three_point([cb.cell1.points[(cb.index1 - 1)], (mp.x, mp.y),
                                       cb.cell1.points[(cb.index1 + 1) % len_points1]])
    af_angle2 = get_angle_by_three_point([cb.cell2.points[(cb.index2 - 1)], (mp.x, mp.y),
                                        cb.cell2.points[(cb.index2 + 1) % len_points2]])
    af_angle3 = get_angle_by_three_point([cb.cell3.points[(cb.index3 - 1)], (mp.x, mp.y),
                                        cb.cell3.points[(cb.index3 + 1) % len_points3]])
    af_sia = af_angle1 * af_angle1 + af_angle2 * af_angle2 + af_angle3 * af_angle3

    if af_sia > be_sia:
        return True
    else:
        return False


'''
    判断点point是否在三角形内
    Judge whether the point is in the triangle
    :param point: 待判断的点 Points to be judged
    :param triangle: 三角形顶点点集 Vertex set of triangle
    :return: True or False，代表点point是否在三角形内 Is the representative point in the triangle
'''


def is_point_in_triangle(point, triangle):
    a = triangle[0]
    b = triangle[1]
    c = triangle[2]
    p = Point(point[0], point[1])

    ap = Point(p.x - a.x, p.y - a.y)
    ac = Point(c.x - a.x, c.y - a.y)
    ab = Point(b.x - a.x, b.y - a.y)

    u = (ab.x * ap.y - ap.x * ab.y) / (ab.x * ac.y - ac.x * ab.y)
    v = (ap.x * ac.y - ac.x * ap.y) / (ab.x * ac.y - ac.x * ab.y)

    if u > 0 and v > 0 and u + v < 1:  # 根据向量法进行判断  Judge according to vector method
        return True
    else:
        return False

# ----------------- 多边形凸性检查（用于边缘退火前验证） -----------------
def is_polygon_convex(points, eps=1e-9):
    """
    判断多边形是否凸，默认顶点顺序为多边形顺序。
    通过统一的方向（根据面积确定）检查所有相邻边的叉积符号。
    """
    if len(points) < 3:
        return False

    # 计算有向面积，确定多边形方向（正：CCW，负：CW）
    area = 0.0
    n = len(points)
    for i in range(n):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % n]
        area += x1 * y2 - x2 * y1
    orient = 1 if area >= 0 else -1

    # 检查每个顶点处的叉积符号是否与整体方向一致
    prev_sign = 0
    for i in range(n):
        p0 = points[i]
        p1 = points[(i + 1) % n]
        p2 = points[(i + 2) % n]
        v1 = (p1[0] - p0[0], p1[1] - p0[1])
        v2 = (p2[0] - p1[0], p2[1] - p1[1])
        cross = v1[0] * v2[1] - v1[1] * v2[0]
        if abs(cross) < eps:
            continue  # 共线视为可接受
        sign = 1 if cross > 0 else -1
        if prev_sign == 0:
            prev_sign = sign
        else:
            if sign != prev_sign:
                return False
    # 若全部共线（prev_sign==0），视为非凸
    if prev_sign == 0:
        return False
    # 方向需与整体一致
    if prev_sign != orient:
        return False
    return True


def is_cell_convex_after_move(cell, idx, candidate_point):
    """
    将 cell 的 idx 顶点替换为 candidate_point 后，判断是否仍为凸多边形。
    """
    temp_points = []
    for i, p in enumerate(cell.points):
        if i == idx:
            temp_points.append([candidate_point[0], candidate_point[1]])
        else:
            temp_points.append([p[0], p[1]])
    return is_polygon_convex(temp_points)


'''
    自动计算退火速率（已弃用
    :param cb: 退火细胞块 Annealed cell block
    :return : 退火速率 Annealing rate
'''


def get_annealing_rate(cb):
    len_points1 = len(cb.cell1.points)
    len_points2 = len(cb.cell2.points)
    len_points3 = len(cb.cell3.points)

    angle1 = get_angle_by_three_point([cb.cell1.points[(cb.index1 - 1)], cb.cell1.points[(cb.index1)],
                                       cb.cell1.points[(cb.index1 + 1) % len_points1]])
    angle2 = get_angle_by_three_point([cb.cell2.points[(cb.index2 - 1)], cb.cell2.points[(cb.index2)],
                                       cb.cell2.points[(cb.index2 + 1) % len_points2]])
    angle3 = get_angle_by_three_point([cb.cell3.points[(cb.index3 - 1)], cb.cell3.points[(cb.index3)],
                                       cb.cell3.points[(cb.index3 + 1) % len_points3]])

    max_angle = angle1
    if max_angle < angle2:
        max_angle = angle2
    if max_angle < angle3:
        max_angle = angle3

    annealing_rate = 0.1
    if max_angle > math.pi*17/18: #  大于170度
        annealing_rate = 0.1
    elif max_angle > math.pi*8/9: #  大于160度
        annealing_rate = 0.06
    elif max_angle > math.pi*15/18: #  大于150度
        annealing_rate = 0.03
    elif max_angle > math.pi * 14 / 18:  # 大于140度
        annealing_rate = 0.02
    # elif max_angle > math.pi * 13 / 18:  # 大于140度
    #     annealing_rate = 0.01
    else:  # 小于140度 大于120度
        annealing_rate = 0.01
    # print(annealing_rate)
    return annealing_rate


'''
    自动计算边缘退火速率
    :param cb: 退火细胞块 Annealed cell block
    :return : 退火速率 Annealing rate
'''


def get_edge_annealing_rate(p_a, p_b, p_v, p_o):
    # print("---5.1")
    # print([p_a, p_v, p_o])
    angle1 = get_angle_by_three_point([p_a, p_v, p_o])
    angle2 = get_angle_by_three_point([p_b, p_v, p_o])
    # print("---5.2")
    dif_angle = math.fabs(angle1 - angle2)
    # print("---5.3")
    annealing_rate = 0.2
    if dif_angle > math.pi*15/18:  #  大于150度
        annealing_rate = 0.2
    elif dif_angle > math.pi*12/18:  #  大于120度
        annealing_rate = 0.1
    elif dif_angle > math.pi*9/18:  #  大于90度
        annealing_rate = 0.06
    elif dif_angle > math.pi * 6 / 18:  # 大于60度
        annealing_rate = 0.03
    elif dif_angle > math.pi * 3 / 18:  # 大于30度
        annealing_rate = 0.02
    else:  # 小于140度 大于120度
        annealing_rate = 0.01
    # print("---5.6")
    return annealing_rate


'''
    根据移动目标点，判断是否应进行移动
    :param cb: 退火细胞块
    :param move_point: 移动目标点
    :return : 判断标记
'''

# 是否启用"移动后对应3个内角平方和增大则拒绝退火"的约束；默认开启，保持旧行为
USE_INNER_ANGLE_SQ_GUARD = True


def set_annealing_options(use_inner_angle_sq_guard=True):
    """设置退火阶段的可选约束开关。"""
    global USE_INNER_ANGLE_SQ_GUARD
    USE_INNER_ANGLE_SQ_GUARD = bool(use_inner_angle_sq_guard)


def judge_if_annealing(cb, move_point):
    # 如果移动点在三角形内部，则不移动 If the moving point is inside the triangle, it does not move
    if is_point_in_triangle(cb.cell1.points[cb.index1], cb.triangle):
        return -1

#如果移动点还在原地，则无需移动/如果移动后，会使细胞不满足凸多边形性质，则不移动 接收不到返回值
    # 如果移动点还在原地，则无需移动 If the moving point is still in place, there is no need to move
    if [move_point.x, move_point.y] in cb.cell1.points:
        return -2

    # 如果移动后，会使细胞不满足凸多边形性质，则不移动
    # If the cell does not satisfy the convex polygon property after moving, it will not move
    if judge_by_intersection_cell_blocks(cb, move_point):
        return -3

    # 可选约束：若退火后，该内部顶点对应的3个内角平方和变大，则不进行退火
    # 该条件现在由 GUI 参数控制，可在"退火设定"中选择是否启用。
    if USE_INNER_ANGLE_SQ_GUARD and judge_sum_inner_angle2(cb, move_point):
        return -4
    return 0


'''
    根据移动目标点，判断边缘是否应进行移动
    :param point_o: 退火细胞块中心点
    :param edgecell1, edgecell2: 退火细胞块两个边缘细胞
    :param move_point: 移动目标点
    :return : 判断标记
'''


#保证移动之后边缘细胞还是稳定的
def judge_edge_if_annealing(point_v, point_o, edgecell1, edgecell2, move_point):

    judge_line_list = []  # 线段列表

    # 判断两个边缘细胞的位置  判断后  1 为左  2为右
    if edgecell2.points.index(point_v)-edgecell2.points.index(point_o) == 1:
        tmpcell = edgecell1
        edgecell1 = edgecell2
        edgecell2 = tmpcell

    # 计算六条线段的方程，存入线段列表
    len_cell1 = len(edgecell1.points)
    len_cell2 = len(edgecell2.points)
    line1 = Line(point_o, edgecell1.points[edgecell1.points.index(point_o) - 1])
    judge_line_list.append(line1)
    line2 = Line(point_o, edgecell2.points[(edgecell2.points.index(point_o) + 1) % len_cell2])
    judge_line_list.append(line2)

    line3 = Line(point_o, edgecell1.points[(edgecell1.points.index(point_o) + 2) % len_cell1])
    judge_line_list.append(line3)
    line4 = Line(point_o, edgecell2.points[edgecell2.points.index(point_o) - 2])
    judge_line_list.append(line4)

    line5 = Line(edgecell1.points[(edgecell1.points.index(point_o) + 2) % len_cell1], edgecell1.points[(edgecell1.points.index(point_o) + 3) % len_cell1])
    judge_line_list.append(line5)
    line6 = Line(edgecell2.points[edgecell2.points.index(point_o) - 2], edgecell2.points[edgecell2.points.index(point_o) - 3])
    judge_line_list.append(line6)

    # 循环判断移动前后两点是否处在六条线段所围成的安全区内
    for l in judge_line_list:
        flag = (l.getA() * point_v[0] + l.getB() * point_v[1] + l.getC()) * (l.getA() * move_point[0] + l.getB() * move_point[1] + l.getC())
        if flag <= 0 or math.fabs(flag) < 1e-9:
            return -1

    return 1


'''
    获取线段与直线的交点
    :param x1: 所求细胞的中心X坐标
    :param y1: 所求细胞的中心Y坐标
    :param line: 直线方程
    :param p1: 线段端点坐标1
    :param p2: 线段端点坐标2
    :return : 返回交点坐标，如果没有交点，则返回None
'''


def get_point_from_line_and_2_point(x1, y1, line, p1, p2):
    x2 = line.getX() + x1
    y2 = line.getY() + y1
    line_A = y2 - y1
    line_B = x1 - x2
    line_C = x2 * y1 - x1 * y2
    if (line_A * p1[0] + line_B * p1[1] + line_C) * (line_A * p2[0] + line_B * p2[1] + line_C) > 0:  # 没有交点
        return None
    else:
        l1 = Line(Point(x1, y1), Point(x2, y2))
        l2 = Line(Point(p1[0], p1[1]), Point(p2[0], p2[1]))
        return get_crossover_point(l1, l2)


'''
    计算边缘退火移动目标点
    :param cb: 边缘退火细胞块
    :return move_point: 边缘退火移动目标点
'''


def get_edge_move_point_last(cb, annealing_rate, cells):
    ##判断是否三个细胞都是边缘细胞，需要寻找两边一内的细胞块组合
    # print(---0)
    # print(cb)
    # print("cb.cell1:", cb.cell1.points)
    # print("cb.cell2:", cb.cell2.points)
    # print("cb.cell3:", cb.cell3.points)
    # print("cb.index1:", cb.index1)
    # print("cb.index2:", cb.index2)
    # print("cb.index3:", cb.index3)
    # print(cb.cell1.points[cb.index1])
    point_o = cb.cell1.points[cb.index1]
    point_v = []
    point_a = []
    point_b = []
    point_move_v = []
    edge_cell1 = object
    edge_cell2 = object
    # print(2)
    if cb.cell1.layer != 1:
        edge_cell1 = cb.cell2
        edge_cell2 = cb.cell3
    elif cb.cell2.layer != 1:
        edge_cell1 = cb.cell1
        edge_cell2 = cb.cell3
    elif cb.cell3.layer != 1:
        edge_cell1 = cb.cell1
        edge_cell2 = cb.cell2
    else:  # 如果退火细胞块全是边缘细胞，则不进行退火操作
        # print(cb)
        # print(cb.cell1.layer)
        # print(cb.cell2.layer)
        # print(cb.cell3.layer)
        return 0
    # print(---1)
    # print("edge_cell1.points", edge_cell1.points)
    # print("edge_cell2.points", edge_cell2.points)

    ##寻找与边缘细胞相交但不与内部细胞相交的点
    for p in edge_cell1.points:
        if p in edge_cell2.points and p != point_o:
            # print(---1.5)
            # print(p)
            # print(point_o)
            # print(p != point_o)
            point_v = p
    if len(point_v) == 0:
        print("这里出现了错误：point_v为空")
    if len(point_o) == 0:
        print("这里出现了错误：point_o为空")


    # 验证该细胞块是否是边缘细胞块
    flag_count = 0
    for c in cells:
        for p in c.points:
            if p == point_v:
                flag_count = flag_count + 1
    if flag_count > 2:
        return -1
    # print(---2)
    # print(edge_cell1.points)
    # print("point_o:", point_o)
    #
    # print("point_v:", point_v)

    # print(edge_cell1.points.index(point_v))
    # print(edge_cell1.points.index(point_o))


    if edge_cell1.points.index(point_v)-edge_cell1.points.index(point_o) > 0 and edge_cell1.points.index(point_v)+1 < len(edge_cell1.points):
        # print(---2.1)
        if edge_cell1.points.index(point_v)+1 >= len(edge_cell1.points):
            # print(---2.2)
            point_a = edge_cell1.points[0]
        else:
            # print(---2.3)
            point_a = edge_cell1.points[edge_cell1.points.index(point_v)+1]
        point_b = edge_cell2.points[edge_cell2.points.index(point_v)-1]
    else:
        # print(---2.4)
        if edge_cell2.points.index(point_v)+1 >= len(edge_cell2.points):
            # print(---2.5)
            point_b = edge_cell2.points[0]
        else:
            # print(---2.6)
            point_b = edge_cell2.points[edge_cell2.points.index(point_v)+1]
        point_a = edge_cell1.points[edge_cell1.points.index(point_v)-1]
    # print(---3)
    # print("point_a:", point_a)
    # print("point_a==point_v:", point_a == point_v)
    # d_oa = get_distance_point_point_by_list(point_a, point_o)
    # d_ob = get_distance_point_point_by_list(point_a, point_o)
    # d_ov = get_distance_point_point_by_list(point_a, point_o)
    #
    # if d_ob > d_oa and d_ov > d_oa:  # 第一种情况
    #     angle_aov = (get_angle_by_three_point([point_a, point_o, point_b]) - math.acos(d_oa / d_ob)) / 2

    pre_best_lines_a = edge_cell1.pre_best_lines[edge_cell1.points.index(point_v)]
    pre_best_lines_b = edge_cell2.pre_best_lines[edge_cell2.points.index(point_v)]

    flag = 0
    p_av_o1v = get_point_from_line_and_2_point(edge_cell1.vx, edge_cell1.vy, pre_best_lines_a, point_a, point_v)
    if p_av_o1v is not None:
        flag += 1

    p_av_o2v = get_point_from_line_and_2_point(edge_cell2.vx, edge_cell2.vy, pre_best_lines_b, point_a, point_v)
    if p_av_o2v is not None:
        flag += 2

    p_bv_o1v = get_point_from_line_and_2_point(edge_cell1.vx, edge_cell1.vy, pre_best_lines_a, point_b, point_v)
    if p_bv_o1v is not None:
        flag -= 1

    p_bv_o2v = get_point_from_line_and_2_point(edge_cell2.vx, edge_cell2.vy, pre_best_lines_b, point_b, point_v)
    if p_bv_o2v is not None:
        flag -= 2
    # print(---4)
    x1 = pre_best_lines_a.getX() + edge_cell1.vx
    y1 = pre_best_lines_a.getY() + edge_cell1.vy

    x2 = pre_best_lines_b.getX() + edge_cell2.vx
    y2 = pre_best_lines_b.getY() + edge_cell2.vy
    # print(---4.3)
    l1 = Line(Point(x1, y1), Point(edge_cell1.vx, edge_cell1.vy))
    l2 = Line(Point(x2, y2), Point(edge_cell2.vx, edge_cell2.vy))

    # print(---4.4)
    p_o1v_o2v = get_crossover_point(l1, l2)
    if p_o1v_o2v is None:
        return 0

    # print(---4.5)
    # print("flag=", flag)

    # Calculate the two edge angles
    angle_avo = get_angle_by_three_point([point_a, point_v, point_o])
    angle_bvo = get_angle_by_three_point([point_b, point_v, point_o])

    # New logic: The target point is the midpoint of the edge that needs to be shortened.
    # This provides a stable restoring force without causing rotation.
    if angle_avo < angle_bvo:
        # v-a edge is part of the smaller angle, so it's the one to shorten.
        target_edge_point = point_a
    else:
        # v-b edge is part of the smaller angle, so it's the one to shorten.
        target_edge_point = point_b

    # The destination point is the midpoint of the edge to be shortened.
    xg = (point_v[0] + target_edge_point[0]) / 2
    yg = (point_v[1] + target_edge_point[1]) / 2



    # print(---4.9)
    point_move_v = [xg, yg]
    # print(---5)
    # print("point_move_v:", point_move_v)

    # rate = get_edge_annealing_rate(point_a, point_b, point_v, point_o)
    rate = annealing_rate

    # print("rate:", rate)
    point_move_v_fin = get_point_of_destination(edge_cell1.points[edge_cell1.points.index(point_v)],
                                                Point(point_move_v[0], point_move_v[1]), rate)
    point_move_v_fin = [point_move_v_fin.x, point_move_v_fin.y]

    # 角度安全判断，防止相关顶点内角超过180度
    idx_v1 = edge_cell1.points.index(point_v)
    idx_o1 = edge_cell1.points.index(point_o)
    idx_v2 = edge_cell2.points.index(point_v)
    idx_o2 = edge_cell2.points.index(point_o)
    if not (is_vertex_angle_safe(edge_cell1, idx_v1, point_move_v_fin) and
            is_vertex_angle_safe(edge_cell1, idx_o1, point_move_v_fin) and
            is_vertex_angle_safe(edge_cell2, idx_v2, point_move_v_fin) and
            is_vertex_angle_safe(edge_cell2, idx_o2, point_move_v_fin)):
        return 0

    # 180度判断及几何安全区判断
    if judge_edge_if_annealing(point_v, point_o, edge_cell1, edge_cell2, point_move_v_fin) > 0:
        edge_cell1.points[edge_cell1.points.index(point_v)] = point_move_v_fin
        edge_cell2.points[edge_cell2.points.index(point_v)] = point_move_v_fin
        return 1
    else:
        return 0
def is_vertex_angle_safe_01(cell, index, candidate):
    """
    检查一次虚拟的顶点移动是否会导致细胞内角大于180度。
    这会检查被移动顶点自身，以及其左右两个邻居顶点的角度。
    """
    # 创建一个临时点列表用于模拟移动
    # 注意：需要确保 cell.points 列表中的元素支持 .copy() 方法
    # 如果 cell.points 是 numpy 数组列表，这是可以的。
    try:
        temp_points = [p.copy() for p in cell.points]
    except AttributeError:
        # 如果点是元组或列表，则这样复制
        temp_points = [list(p) for p in cell.points]

    temp_points[index] = list(candidate)

    l = len(temp_points)

    # 循环检查三个关键角度：被移动的顶点(index)和它的左右邻居(index-1, index+1)
    for i in range(-1, 2):
        # 我们要检查的顶点的索引
        vertex_index_to_check = (index + i + l) % l

        # 组成这个角的三个点
        p_prev = temp_points[(vertex_index_to_check - 1 + l) % l]
        p_curr = temp_points[vertex_index_to_check]
        p_next = temp_points[(vertex_index_to_check + 1) % l]

        # 计算角度
        angle = get_angle_by_three_point([p_prev, p_curr, p_next])

        # 核心判断：如果任何一个角度大于或接近180度，则移动是不安全的
        if angle >= math.pi/2:
            return False

    # 如果所有三个角都小于180度，则是安全的
    return True
#{"variant":"standard","title":"is_vertex_angle_safe_01","id":"90211"}
#------------------------------------
def is_vertex_angle_safe_04(cell, index, candidate):
    """
    扩展版角度安全性检查：
    移动前检查该顶点是否导致：
      - 自身角
      - 左邻 / 右邻角（共3个直接角）
      - 两个间接影响的角
      - 一个次邻接角
    共6个角是否超过 180°。
    """

    # 复制顶点列表并替换移动后的点
    try:
        temp = [p.copy() for p in cell.points]
    except:
        temp = [list(p) for p in cell.points]

    temp[index] = list(candidate)
    n = len(temp)

    # 简化点访问
    def P(i):
        return temp[i % n]

    # 计算三点角
    def angle(i_prev, i_curr, i_next):
        return get_angle_by_three_point([P(i_prev), P(i_curr), P(i_next)])

    # -------------------------------
    # A. 直接相关 3 个角
    # -------------------------------
    angle_self = angle(index - 1, index, index + 1)
    angle_left = angle(index - 2, index - 1, index)
    angle_right = angle(index, index + 1, index + 2)

    # -------------------------------
    # B. 间接影响的 2 个角
    #    跨越一个点的角度
    # -------------------------------
    angle_cross1 = angle(index - 2, index - 1, index + 1)
    angle_cross2 = angle(index - 1, index + 1, index + 2)

    # -------------------------------
    # C. 额外的一个次邻接角（第6个角）
    #    使用 index-3 的方向
    # -------------------------------
    angle_second_neighbor = angle(index - 3, index - 2, index - 1)

    # 打包所有 6 个角
    angles = [
        angle_self,
        angle_left,
        angle_right,
        angle_cross1,
        angle_cross2,
        angle_second_neighbor
    ]

    # 检查是否有角 >=180 度
    for a in angles:
        if a >= math.pi - 1e-9:
            return False

    return True
#-------------------------
#~~~{"variant":"standard","title":"is_vertex_angle_safe_03（改进）","id":"70192"}
def is_vertex_angle_safe_03(cell, index, candidate):
    """
    改进版角度安全检查：
    - 对直接相关的3个角实行强约束（必须 < 180°）
    - 对跨越角和次邻角放宽约束（允许一定范围）
    """
    # 替换 candidate
    try:
        temp = [p.copy() for p in cell.points]
    except:
        temp = [list(p) for p in cell.points]

    temp[index] = list(candidate)
    n = len(temp)

    def P(i):
        return temp[i % n]

    def angle(i_prev, i_curr, i_next):
        return get_angle_by_three_point([P(i_prev), P(i_curr), P(i_next)])

    # ---------------------------------------
    # A. 三个关键角（必须严格凸）
    # ---------------------------------------
    angle_self = angle(index-1, index, index+1)
    angle_left = angle(index-2, index-1, index)
    angle_right = angle(index, index+1, index+2)

    critical_angles = [angle_self, angle_left, angle_right]

    for a in critical_angles:
        if a >= math.pi - 1e-9:    # 必须 < 180°
            print("角度检查失败:必须 < 180°")
            return False

    # ---------------------------------------
    # B. 两个跨越角（允许达到 200°）
    # ---------------------------------------
    angle_cross1 = angle(index-2, index-1, index+1)
    angle_cross2 = angle(index-1, index+1, index+2)

    cross_angles = [angle_cross1, angle_cross2]

    for a in cross_angles:
        if a > math.radians(200):   # 放宽
            print("角度检查失败:允许达到 200°")
            return False

    # ---------------------------------------
    # C. 次邻角（影响最弱，允许达到 210°）
    # ---------------------------------------
    angle_second_neighbor = angle(index-3, index-2, index-1)

    if angle_second_neighbor > math.radians(210):
        print("角度检查失败:次邻角（影响最弱，允许达到 210°）")
        return False

    return True


#-------------------------
def judge_by_intersection_cell_blocks_new(cb, move_point):
    """
    用于边缘退火的轻量级检查函数，复用原有 judge_by_intersection_cell_blocks 的逻辑，
    但参数更简单，可直接被 get_edge_move_point 调用。

    回传：
        True  = 可以移动
        False = 不应退火（并打印原因）
    """

    # 要移动的目标点
    new_x, new_y = move_point[0], move_point[1]

    # ------------------- 检查 1：180° 凸性检查 -------------------
    # 简化检验方式：对 cb 的三个细胞的对应角做一次"临时替换点"检查
    involved = [
        (cb.cell1, cb.index1),
        (cb.cell2, cb.index2),
        (cb.cell3, cb.index3),
    ]

    for cell, idx in involved:
        # 复制 points
        try:
            temp = [p.copy() for p in cell.points]
        except:
            temp = [list(p) for p in cell.points]

        temp[idx] = [new_x, new_y]
        n = len(temp)

        # 取三点用于计算角度
        def P(i):
            return temp[i % n]

        # angle(prev, current, next)
        ang = get_angle_by_three_point([P(idx - 1), P(idx), P(idx + 1)])

        if ang >= math.pi - 1e-9:
            print(f"[EdgeCheck-Stop] 失败原因：移动后会产生 >=180° 的角")
            #print(f"[EdgeCheck-Stop] 失败原因：移动后会产生 >=180° 的角（cell.id={cell.id}, index={idx}）")
            return False

    # ------------------- 检查 2：移动是否会破坏三细胞一致性 -------------------
    # 三个细胞必须共享并更新同一个点，因此检查 move_point 是否过大导致可能穿越
    # 简单判断：若移动距离过大，则认为潜在风险
    ori = cb.cell1.points[cb.index1]
    move_dist = math.hypot(new_x - ori[0], new_y - ori[1])
    if move_dist > 5.0:  # 阈值可调整
        print(f"[EdgeCheck-Stop] 失败原因：移动过大，可能破坏几何框架，dist={move_dist:.4f}")
        return False

    # ------------------- 检查 3：通过即可 -------------------
    return True
#-------------------------
def is_vertex_angle_safe_05(cell, index, candidate):
    #利用get_edge_move_point函数获取预退火移动点，判断预退火点与相邻几个点构成的角度是否满足要求<=180°的要求，优先只判断边缘顶点相邻的两个角度
    return True

#修改边缘细胞的退火方法为：每个边缘顶点对应两个边缘角，将当前边缘顶点V沿较小边缘角的边缘边移动到目的地点P，使得两个边缘角相等,
def is_neighbors_angles_safe(cell, index_changed, candidate):
    points = cell.points[:]
    points[index_changed] = [candidate[0], candidate[1]]
    l = len(points)
    left = (index_changed - 1) % l
    right = (index_changed + 1) % l
    # 左邻角
    p1 = points[(left - 1) % l]
    p = points[left]
    p2 = points[(left + 1) % l]
    angle_left = get_angle_by_three_point([p1, p, p2])
    # 右邻角
    p1 = points[(right - 1) % l]
    p = points[right]
    p2 = points[(right + 1) % l]
    angle_right = get_angle_by_three_point([p1, p, p2])
    return (angle_left < math.pi - 1e-9) and (angle_right < math.pi - 1e-9)

def get_edge_move_point_last01_1127(cb, annealing_rate, cells):
    """
    新的边缘退火逻辑：
    1. 设置三个列表存储原始顶点、移动后顶点、移动前角度
    2. 遍历细胞块获取边缘顶点和角度
    3. 比较角度差，决定是否进行退火移动
    """
    # 第一步：初始化三个列表
    original_vertices = []      # 原始边缘顶点列表
    moved_vertices = []         # 移动后的边缘顶点列表
    pre_angles = []             # 移动前的角度列表（存储元组：(angle1, angle2)）

    # 第二步：遍历细胞块获取边缘顶点和角度
    edge_vertices = get_edge_vertices_from_cellblock(cb, cells)
    #print("第一次：edge_vertices:", edge_vertices)

    edge_vertices =get_edge_vertices_directly(cells)
    #print("第二次：edge_vertices:", edge_vertices)

    edge_vertices =enhanced_get_edge_vertices(cells, min_shared_count=2)
    # print("第三次：edge_vertices:", edge_vertices)
    for vertex_info in edge_vertices:
        point_v = vertex_info['point_v']  # 边缘顶点
        point_o = vertex_info['point_o']  # 共享顶点
        point_a = vertex_info['point_a']  # 相邻顶点A
        point_b = vertex_info['point_b']  # 相邻顶点B
        edge_cell1 = vertex_info['edge_cell1']  # 边缘细胞1
        edge_cell2 = vertex_info['edge_cell2']  # 边缘细胞2

        # 计算两个边缘角
        angle_AVO = get_angle_by_three_point([point_a, point_v, point_o])
        angle_BVO = get_angle_by_three_point([point_b, point_v, point_o])

        # 添加到列表
        original_vertices.append(point_v)
        pre_angles.append((angle_AVO, angle_BVO))

    # 第三步：比较角度差并决定是否退火
    moved_count = 0
    for i, vertex_info in enumerate(edge_vertices):
        point_v = vertex_info['point_v']
        point_o = vertex_info['point_o']
        point_a = vertex_info['point_a']
        point_b = vertex_info['point_b']
        edge_cell1 = vertex_info['edge_cell1']
        edge_cell2 = vertex_info['edge_cell2']

        angle_AVO, angle_BVO = pre_angles[i]

        # 计算角度差
        angle_diff = abs(angle_AVO - angle_BVO)
        angle_threshold = 0.01  # 角度差阈值（约0.57度），可调整

        # 如果角度差超过阈值，则进行退火移动
        if angle_diff > angle_threshold:
            # 计算目标点：使两个角度近似相等
            target_point = calculate_equal_angle_target(point_v, point_o, point_a, point_b, angle_AVO, angle_BVO)

            # 应用退火速率
            move_point_fin = get_point_of_destination(
                point_v,
                Point(target_point[0], target_point[1]),
                annealing_rate
            )
            move_point_fin = [move_point_fin.x, move_point_fin.y]

            # 安全检查
            if is_move_safe(edge_cell1, edge_cell2, point_v, point_o, move_point_fin):
                # 执行移动
                edge_cell1.points[edge_cell1.points.index(point_v)] = move_point_fin
                edge_cell2.points[edge_cell2.points.index(point_v)] = move_point_fin

                # 添加到移动后顶点列表
                moved_vertices.append(move_point_fin)
                moved_count += 1
                print(f"边缘顶点移动成功: {point_v} -> {move_point_fin}")
            else:
                # 移动不安全，保持原顶点
                moved_vertices.append(point_v)
                print(f"边缘顶点移动被拒绝（安全约束）: {point_v}")
        else:
            # 角度差太小，不移动
            moved_vertices.append(point_v)
            print(f"角度差太小({angle_diff:.4f} < {angle_threshold:.4f})，不移动顶点: {point_v}")

    # 可选：打印统计信息
    # print(f"边缘退火统计: 总顶点数={len(edge_vertices)}, 移动顶点数={moved_count}")

    return moved_count
#------------------------------------------------------------
#存在缺陷：
def get_edge_move_point_last02_1127(cb, annealing_rate, cells):
    """
    修改后的边缘退火函数，使用新的边缘顶点获取方法
    """
    # 第一步：初始化三个列表
    original_vertices = []      # 原始边缘顶点列表
    moved_vertices = []         # 移动后的边缘顶点列表
    pre_angles = []             # 移动前的角度列表（存储元组：(angle1, angle2)）

    # 第二步：遍历细胞块获取边缘顶点和角度
    #edge_vertices = get_edge_vertices_from_cellblock(cb, cells)



    edge_vertices =get_edge_vertices_directly(cells)
    # print("第二次：edge_vertices:", edge_vertices)

    #edge_vertices =get_edge_vertices(cells, min_shared_count=2)
    #print("第三次：edge_vertices:", edge_vertices)

    for vertex_info in edge_vertices:
        point_v = vertex_info['point_v']  # 边缘顶点
        point_o = vertex_info['point_o']  # 共享顶点
        point_a = vertex_info['point_a']  # 相邻顶点A
        point_b = vertex_info['point_b']  # 相邻顶点B
        edge_cell1 = vertex_info['edge_cell1']  # 边缘细胞1
        edge_cell2 = vertex_info['edge_cell2']  # 边缘细胞2

        # 计算两个边缘角
        angle_AVO = get_angle_by_three_point([point_a, point_v, point_o])
        angle_BVO = get_angle_by_three_point([point_b, point_v, point_o])

        # 添加到列表
        original_vertices.append(point_v)
        pre_angles.append((angle_AVO, angle_BVO))

    # # 第三步：处理每个边缘顶点，存储原始信息
    # for vertex_info in edge_vertices:
    #     vertex = vertex_info['vertex']
    #     sharing_cells = vertex_info['cells']
    #     neighbors_info = vertex_info['neighbors']

    #     # 存储原始信息
    #     original_vertices.append(vertex)
    #     pre_angles.append(vertex_info['angles'])  # 存储所有相关角度

    # # 第四步：边缘退火逻辑 - 使边缘相邻两角相等
    # moved_count = 0
    # angle_threshold = math.radians(1.0)  # 1度阈值

    # for i, vertex_info in enumerate(edge_vertices):
    #     vertex = vertex_info['vertex']
    #     angles = vertex_info['angles']
    #     sharing_cells = vertex_info['cells']
    #     neighbors_info = vertex_info['neighbors']

    #     # 只处理有两个共享细胞的边缘顶点
    #     if len(sharing_cells) != 2:
    #         continue

    #     # 获取两个相邻角
    #     if len(angles) >= 2:
    #         angle1, angle2 = angles[0], angles[1]
    #         angle_diff = abs(angle1 - angle2)
    #         print(f"成功获取顶点：顶点 {vertex} 角度差: {math.degrees(angle_diff):.2f}°")
    #         # 如果角度差超过阈值，进行退火调整
    #         if angle_diff > angle_threshold:
    #             print(f"顶点 {vertex} 角度差: {math.degrees(angle_diff):.2f}°, 进行退火调整")

    #             # 计算目标角度：使两个角相等
    #             target_angle = (angle1 + angle2) / 2

    #             # 获取与顶点相关的边信息
    #             edge1 = neighbors_info[0]['edge']
    #             edge2 = neighbors_info[1]['edge']

    #             # 计算移动方向：使两个角趋于相等
    #             # 方法：将顶点沿着角平分线方向移动
    #             move_vector = calculate_bisector_move(vertex, edge1, edge2, angle1, angle2, target_angle)

    #             # 应用退火移动
    #             new_vertex = (
    #                 vertex[0] + move_vector[0] * annealing_rate,
    #                 vertex[1] + move_vector[1] * annealing_rate
    #             )

    #             # 更新顶点位置
    #             update_vertex_position(vertex, new_vertex, sharing_cells)

    #             # 记录移动后的顶点和角度
    #             moved_vertices.append(new_vertex)
    #             moved_count += 1

    #             print(f"顶点移动: {vertex} -> {new_vertex}")
    #             print(f"角度调整: {math.degrees(angle1):.2f}°, {math.degrees(angle2):.2f}° -> 目标: {math.degrees(target_angle):.2f}°")
    #         else:
    #             print(f"顶点 {vertex} 角度差: {math.degrees(angle_diff):.2f}°, 无需调整")
    #     else:
    #         print(f"顶点 {vertex} 的共享细胞数不足，无法计算角度差")

    # return moved_count


def get_edge_move_point_last01_1129(cb, annealing_rate, cells):
    """
    全新边缘退火逻辑（按照用户要求）:
    1. 建立三个列表：原始顶点 / 移动后顶点 / 移动前角度
    2. 获取当前细胞块 cb 的边缘顶点 V，并计算两个边缘角
    3. 若两角差超过阈值，则沿较小角所在边方向退火移动，使两个角趋于相等
    """
    # ---------------------- 新增（1）边缘顶点识别打印 ------------------------
    # 识别边缘顶点：即 cb 的三个点中哪个属于 layer == 1 的 cell
    edge_indices = []
    if cb.cell1.layer == 1:
        edge_indices.append(("cell1", cb.index1))
    if cb.cell2.layer == 1:
        edge_indices.append(("cell2", cb.index2))
    if cb.cell3.layer == 1:
        edge_indices.append(("cell3", cb.index3))

    # print(f"[EdgeCheck] 识别到 cb 的边缘顶点数量: {len(edge_indices)}")
    # for name, idx in edge_indices:
    #     print(f"[EdgeCheck] 边缘点: {name} 的 index = {idx}, 坐标 = {cb.__getattribute__(name).points[idx]}")

    # 如果没有边缘点，直接返回 0，避免继续执行
    if len(edge_indices) == 0:
        print("[EdgeCheck] !!! 未找到边缘顶点，本 cb 不执行边缘退火")
        return 0
    # ------------------------------------------------------------------------

    # 第一步：建立三个列表
    original_vertices = []
    moved_vertices = []
    pre_angles = []
    sum_angle=[]


    # 第二步：从 cb 中获取边缘顶点 V 及其相关数据

    # 找到三个细胞中 layer==1 的两个边缘细胞
    edge_cells = []
    for c in [cb.cell1, cb.cell2, cb.cell3]:
        if c.layer == 1:
            edge_cells.append(c)
    if len(edge_cells) != 2:
        return 0  # 不是边缘细胞块

    cell_a, cell_b = edge_cells

    # 共享点 O
    point_o = cb.cell1.points[cb.index1]


    # 找共享边缘顶点 V（不是 O）
    shared_vertices = [p for p in cell_a.points if p in cell_b.points]
    point_v = None
    for p in shared_vertices:
        if p != point_o:
            point_v = p
            break
    if point_v is None:
        return 0

    # 获取 point_v 在两个细胞中的相邻点 A 和 B
    idx_va = cell_a.points.index(point_v)
    idx_vb = cell_b.points.index(point_v)

    # 在每个边缘 cell 中，V 点有两个邻居：一个是内部共享点 O，另一个是外侧边界点。
    # 我们希望 A、B 都取"外侧邻居"，否则如果把 O 当成邻居，会出现 A=O 或 B=O，
    # 导致 ∠AVO 或 ∠BVO 变成 0°。
    def get_outer_neighbor(cell, idx_v, shared_O_point):
        n = len(cell.points)
        prev_p = cell.points[(idx_v - 1) % n]
        next_p = cell.points[(idx_v + 1) % n]

        # 如果前一个点是 O，则外侧点是后一个；反之亦然
        if prev_p == shared_O_point and next_p != shared_O_point:
            return next_p
        if next_p == shared_O_point and prev_p != shared_O_point:
            return prev_p

        # 正常几何结构下，V 的两个邻居中应该恰好有一个是 O；
        # 若不是，说明拓扑或点序有问题，这里做一个保守兜底：仍然取原来的"前一个点"，并打印提示。
        print("[EdgeCheck] 警告：在 cell 中 V 的两个邻居都不是（或都是） O，使用默认前一顶点作为外侧点")
        return prev_p

    point_a = get_outer_neighbor(cell_a, idx_va, shared_O)
    point_b = get_outer_neighbor(cell_b, idx_vb, shared_O)


    # 计算两个边缘角

    angle_AVO = get_angle_by_three_point([point_a, point_v, point_o])
    sum_angle.append(angle_AVO)
    angle_BVO = get_angle_by_three_point([point_b, point_v, point_o])
    sum_angle.append(angle_BVO)

    # 加入列表
    original_vertices.append(point_v)
    pre_angles.append((angle_AVO, angle_BVO))


    # 第三步：比较角度差，决定是否移动

    #----------------------------------------
    # 形状审查 - 判断是否为三角形几何体
    #----------------------------------------
    is_triangle_geometry = (len(cell_a.points) == 3 or len(cell_b.points) == 3)

    # 根据几何体形状设置不同的退火阈值
    if is_triangle_geometry:
        angle_threshold = math.radians(60)  # 至少有一个三角形几何体，使用60度阈值
        cell_a_is_triangle = len(cell_a.points) == 3
        cell_b_is_triangle = len(cell_b.points) == 3
        print(f"[Shape] 检测到至少一个三角形几何体 (cell_a: {len(cell_a.points)}边, cell_b: {len(cell_b.points)}边)，使用60度阈值")
    else:
        angle_threshold = math.radians(20)  # 两个都不是三角形，使用20度阈值
        print(f"[Shape] 两个边缘几何体都不是三角形 (cell_a: {len(cell_a.points)}边, cell_b: {len(cell_b.points)}边)，使用20度阈值")

    angle_diff = abs(angle_AVO - angle_BVO)

    if angle_diff < angle_threshold:
        # 不移动
        moved_vertices.append(point_v)
        return 0


    # 计算目标点 P：使两个角相等
    # 规则：沿较小角所在的边方向向外移动

    if angle_AVO < angle_BVO:
        # AVO 太小 → 沿 AV 方向移动
        direction = [point_a[0] - point_v[0], point_a[1] - point_v[1]]
    else:
        # BVO 太小 → 沿 BV 方向移动
        direction = [point_b[0] - point_v[0], point_b[1] - point_v[1]]

    # 单位化方向
    length = math.sqrt(direction[0]**2 + direction[1]**2)
    if length == 0:
        return 0
    direction = [direction[0] / length, direction[1] / length]


    # 移动目标点（线性退火）
    target_point = [
        point_v[0] + direction[0] * annealing_rate,
        point_v[1] + direction[1] * annealing_rate
    ]
    # candidate_point = [x, y]

    # O 的安全检查
    # ① 找到三细胞共有的内部点 O
    shared_O = None
    for p in cb.cell1.points:
        if p in cb.cell2.points and p in cb.cell3.points:
            shared_O = p
            break

    if shared_O is None:
        print("[O-Check] 找不到共享 O，跳过")
        return 0

    idxO1 = cb.cell1.points.index(shared_O)
    idxO2 = cb.cell2.points.index(shared_O)
    idxO3 = cb.cell3.points.index(shared_O)

    if not is_O_vertex_safe(cb.cell1, idxO1, target_point): return 0
    if not is_O_vertex_safe(cb.cell2, idxO2, target_point): return 0
    if not is_O_vertex_safe(cb.cell3, idxO3, target_point): return 0


#--------安全检查---------------



    # 安全性检查
    # if not is_vertex_angle_safe_04(cell_a, idx_va, target_point):
    #     return 0
    # if not is_vertex_angle_safe_03(cell_b, idx_vb, target_point):
    #     return 0
    # candidate = [px, py]  # 你的目标点
    # if not judge_by_intersection_cell_blocks_new(cb, target_point):
    #     print("[EdgeCheck] candidate 未通过 judge_by_intersection_cell_blocks_new 检查")
    #     return 0


    # 执行更新

    cell_a.points[idx_va] = target_point
    cell_b.points[idx_vb] = target_point

    moved_vertices.append(target_point)
    return 1
#------------------------------------------------------------
def get_edge_move_point_last02_1129(cb, annealing_rate, cells):
    """
    全新边缘退火逻辑（满足用户要求）:
    1. 识别边缘顶点并打印。
    2. 找到边缘顶点 V 和内部顶点 O。
    3. 比较两个边缘角（A-V-O 和 B-V-O），沿较小角方向移动 V。
    4. 对 candidate V 做 O 点安全检查（只检查 V-O 相邻的 cell）。
    """
    # ---------------------- step 0：识别边缘顶点（打印） ----------------------
    edge_indices = []
    if cb.cell1.layer == 1:
        edge_indices.append((cb.cell1, cb.index1))
    if cb.cell2.layer == 1:
        edge_indices.append((cb.cell2, cb.index2))
    if cb.cell3.layer == 1:
        edge_indices.append((cb.cell3, cb.index3))

    print(f"\n[EdgeCheck] 识别到边缘顶点数量: {len(edge_indices)}")

    if len(edge_indices) == 0:
        print("[EdgeCheck] 无边缘顶点，退出")
        return 0

    # for c, idx in edge_indices:
    #     print(f"[EdgeCheck] cell.id={getattr(c, 'id', '?')}  index={idx}  coord={c.points[idx]}")

    # ---------------------- step 1：找到两个边缘 cell ----------------------
    edge_cells = [c for c in [cb.cell1, cb.cell2, cb.cell3] if c.layer == 1]
    if len(edge_cells) != 2:
        return 0  # 非边缘块

    cell_a, cell_b = edge_cells

    # ---------------------- step 2：找到共享内部点 O ----------------------
    shared_O = None
    for p in cb.cell1.points:
        if p in cb.cell2.points and p in cb.cell3.points:
            shared_O = p
            break

    if shared_O is None:
        print("[O-Check] 找不到共享 O，退出")
        return 0

    # O 在三个 cell 中的索引
    idxO1 = cb.cell1.points.index(shared_O)
    idxO2 = cb.cell2.points.index(shared_O)
    idxO3 = cb.cell3.points.index(shared_O)

    # ---------------------- step 3：找到共享边缘点 V ----------------------
    shared_vertices = [p for p in cell_a.points if p in cell_b.points]
    point_v = None
    for p in shared_vertices:
        if p != shared_O:
            point_v = p
            break
    if point_v is None:
        return 0

    # V 在两个 cell 中的索引
    idx_va = cell_a.points.index(point_v)
    idx_vb = cell_b.points.index(point_v)

    # 获取 A 和 B
    point_a = cell_a.points[(idx_va - 1) % len(cell_a.points)]
    point_b = cell_b.points[(idx_vb - 1) % len(cell_b.points)]

    # ---------------------- step 4：计算两边缘角 ----------------------
    # 关键修复：直接计算向量夹角，不使用 get_angle_by_three_point。
    # get_angle_by_three_point 设计用于计算多边形内角，在此处使用会因其凹角判断逻辑而返回错误的大于180度的角度，从而导致系统性旋转。
    # 正确的方法是计算两个向量间的直接夹角（0-180度）。
    def calculate_simple_angle(p1, vertex, p2):
        v1 = (p1[0] - vertex[0], p1[1] - vertex[1])
        v2 = (p2[0] - vertex[0], p2[1] - vertex[1])
        dot_product = v1[0] * v2[0] + v1[1] * v2[1]
        mag1 = math.hypot(*v1)
        mag2 = math.hypot(*v2)
        if math.isclose(mag1 * mag2, 0):
            return 0
        cos_val = max(-1.0, min(1.0, dot_product / (mag1 * mag2)))
        return math.acos(cos_val)

    angle_AVO = calculate_simple_angle(point_a, point_v, shared_O)
    angle_BVO = calculate_simple_angle(point_b, point_v, shared_O)

    #----------------------------------------
    # 形状审查 - 判断是否为三角形几何体
    #----------------------------------------
    is_triangle_geometry = (len(cell_a.points) == 3 or len(cell_b.points) == 3)

    # 根据几何体形状设置不同的退火阈值
    if is_triangle_geometry:
        angle_threshold = math.radians(60)  # 至少有一个三角形几何体，使用60度阈值
        cell_a_is_triangle = len(cell_a.points) == 3
        cell_b_is_triangle = len(cell_b.points) == 3
        print(f"[Shape] 检测到至少一个三角形几何体 (cell_a: {len(cell_a.points)}边, cell_b: {len(cell_b.points)}边)，使用60度阈值")
    else:
        angle_threshold = math.radians(20)  # 两个都不是三角形，使用20度阈值
        print(f"[Shape] 两个边缘几何体都不是三角形 (cell_a: {len(cell_a.points)}边, cell_b: {len(cell_b.points)}边)，使用20度阈值")

    print(f"[Angle] A-V-O={angle_AVO:.6f}, B-V-O={angle_BVO:.6f}")

    if abs(angle_AVO - angle_BVO) < angle_threshold:
        print(f"[Angle] 角度差太小（阈值{math.degrees(angle_threshold):.0f}°），无需退火")
        return 0

    # ---------------------- step 5：生成 candidate_point ----------------------
    if angle_AVO < angle_BVO:
        move_dir = (point_a[0] - point_v[0], point_a[1] - point_v[1])
    else:
        move_dir = (point_b[0] - point_v[0], point_b[1] - point_v[1])

    L = math.hypot(move_dir[0], move_dir[1])
    if L < 1e-12:
        print("[Move] move_dir 太小，退出")
        return 0

    dx, dy = move_dir[0] / L, move_dir[1] / L
    candidate_V = [point_v[0] + dx * annealing_rate,
                   point_v[1] + dy * annealing_rate]

    #print(f"[Move] candidate_V={candidate_V}")

    # ---------------------- step 6：改进版 O 点安全检查 ----------------------
    # 找到真正需要检查的 cell（只有 V 与 O 在该 cell 中相邻时才检查）
    cells_to_check = []

    def push_if_adjacent(cell, idxO):
        if point_v in cell.points:
            idxV = cell.points.index(point_v)
            n = len(cell.points)
            if (idxV == idxO - 1) or (idxV == (idxO + 1) % n):
                cells_to_check.append((cell, idxO, idxV))

    push_if_adjacent(cb.cell1, idxO1)
    push_if_adjacent(cb.cell2, idxO2)
    push_if_adjacent(cb.cell3, idxO3)

    if len(cells_to_check) == 0:
        print("[O-Check] V 与 O 在所有 cell 中均不相邻，可安全移动")
    else:
        for cell_check, idxO, idxV in cells_to_check:
            n_cp = len(cell_check.points)
            def P(i): return cell_check.points[i % n_cp]

            A = P(idxO - 1)
            Ocoord = P(idxO)
            B = P(idxO + 1)
            V_before = P(idxV)
            V_after = (candidate_V[0], candidate_V[1])

            # 原角
            Ang_AOV_before = get_angle_by_three_point([A, Ocoord, V_before])
            Ang_VOB_before = get_angle_by_three_point([V_before, Ocoord, B])
            Ang_AOB_before = get_angle_by_three_point([A, Ocoord, B])

            # 新角
            Ang_AOV_after = get_angle_by_three_point([A, Ocoord, V_after])
            Ang_VOB_after = get_angle_by_three_point([V_after, Ocoord, B])
            Ang_AOB_after = get_angle_by_three_point([A, Ocoord, B])

            print(f"[O-Check] cell.id={getattr(cell_check,'id','?')} idxO={idxO} idxV={idxV}")
            print(f"    before: AOV={Ang_AOV_before:.6f}, VOB={Ang_VOB_before:.6f}, AOB={Ang_AOB_before:.6f}")
            print(f"     after: AOV={Ang_AOV_after:.6f}, VOB={Ang_VOB_after:.6f}, AOB={Ang_AOB_after:.6f}")

            eps = 1e-8
            delta = 1e-4  # 需要显著增大才算非法

            if (Ang_AOV_after >= math.pi - eps) and ((Ang_AOV_after - Ang_AOV_before) > delta):
                print("[O-Check STOP] A-O-V >=180° 且显著增大")
                return 0

            if (Ang_VOB_after >= math.pi - eps) and ((Ang_VOB_after - Ang_VOB_before) > delta):
                print("[O-Check STOP] V-O-B >=180° 且显著增大")
                return 0

            if (Ang_AOB_after >= math.pi - eps) and ((Ang_AOB_after - Ang_AOB_before) > delta):
                print("[O-Check STOP] A-O-B >=180° 且显著增大")
                return 0

    # ---------------------- step 7：更新两个 cell 中的 V ----------------------
    cell_a.points[idx_va] = candidate_V
    cell_b.points[idx_vb] = candidate_V

    print("[Update] 边缘顶点 V 已退火")
    return 1
#----------------------------------------------------------------------

def get_all_edge_vertices(cells):
    """
    获取所有边缘顶点（只被两个细胞共享的顶点）

    参数:
        cells: 所有细胞列表

    返回:
        list: 所有边缘顶点的列表 [[x, y], ...]
    """
    # 辅助函数：判断两个点是否相等（考虑浮点误差）
    def points_equal(p1, p2, tolerance=1e-9):
        if isinstance(p1, (list, tuple)) and isinstance(p2, (list, tuple)):
            return abs(p1[0] - p2[0]) < tolerance and abs(p1[1] - p2[1]) < tolerance
        return False

    all_edge_vertices = []
    vertex_to_cells = {}  # 记录每个顶点被哪些细胞共享

    # 统计每个顶点被多少个细胞共享
    for cell in cells:
        for p in cell.points:
            p_key = tuple(p) if isinstance(p, (list, tuple)) else p
            if p_key not in vertex_to_cells:
                vertex_to_cells[p_key] = []
            # 检查是否已经添加过这个细胞（避免重复）
            if cell not in vertex_to_cells[p_key]:
                vertex_to_cells[p_key].append(cell)

    # 筛选出边缘顶点（只被2个细胞共享的顶点）
    for p_key, sharing_cells in vertex_to_cells.items():
        if len(sharing_cells) == 2:  # 只被2个细胞共享
            # 获取点的实际坐标（从第一个细胞中获取）
            p_key_list = list(p_key) if isinstance(p_key, tuple) else p_key
            for p in sharing_cells[0].points:
                if points_equal(p, p_key_list):
                    all_edge_vertices.append(p)
                    break

    return all_edge_vertices

def find_edge_key_points_new(point_v, cells):
    """
    按照新逻辑找关键点：V -> A, B -> edge_cell1, edge_cell2 -> O

    新逻辑：
    1. 首先定位所有的边缘顶点，只被两个细胞共享的点为边缘顶点，保存全部的边缘顶点信息
    2. 逐个处理边缘顶点，记当前处理的边缘顶点为V
    3. 检索全部的边缘顶点，寻找存在与V构成一边的顶点，应当可以找到这样的两个边缘顶点，分别记为A,B
    4. 由于是AV，VB是边缘边，所以两边可以映射到两个边缘几何体为两个目标几何体
    5. 随后再检索V的邻点，是否存在除V以外的一点被两个目标几何体的共有，若存在，则该点为O

    参数:
        point_v: 边缘顶点V [x, y]
        cells: 所有细胞列表

    返回:
        dict: {
            'point_v': point_v,
            'point_a': point_a,
            'point_b': point_b,
            'point_o': point_o,
            'edge_cell1': edge_cell1,
            'edge_cell2': edge_cell2,
            'idx_va': idx_va,  # V在edge_cell1中的索引
            'idx_vb': idx_vb,  # V在edge_cell2中的索引
            'idx_oa': idx_oa,  # O在edge_cell1中的索引
            'idx_ob': idx_ob   # O在edge_cell2中的索引
        }
        如果找不到关键点，返回None
    """
    # 辅助函数：判断两个点是否相等（考虑浮点误差）
    def points_equal(p1, p2, tolerance=1e-9):
        if isinstance(p1, (list, tuple)) and isinstance(p2, (list, tuple)):
            return abs(p1[0] - p2[0]) < tolerance and abs(p1[1] - p2[1]) < tolerance
        return False

    # Step 1: 首先定位所有的边缘顶点，只被两个细胞共享的点为边缘顶点
    all_edge_vertices = []
    vertex_to_cells = {}  # 记录每个顶点被哪些细胞共享

    # 统计每个顶点被多少个细胞共享
    for cell in cells:
        for p in cell.points:
            p_key = tuple(p) if isinstance(p, (list, tuple)) else p
            if p_key not in vertex_to_cells:
                vertex_to_cells[p_key] = []
            # 检查是否已经添加过这个细胞（避免重复）
            if cell not in vertex_to_cells[p_key]:
                vertex_to_cells[p_key].append(cell)

    # 筛选出边缘顶点（只被2个细胞共享的顶点）
    for p_key, sharing_cells in vertex_to_cells.items():
        if len(sharing_cells) == 2:  # 只被2个细胞共享
            # 获取点的实际坐标（从第一个细胞中获取）
            p_key_list = list(p_key) if isinstance(p_key, tuple) else p_key
            for p in sharing_cells[0].points:
                if points_equal(p, p_key_list):
                    all_edge_vertices.append(p)
                    break

    if len(all_edge_vertices) < 3:  # 至少需要V、A、B三个边缘顶点
        print(f"[FindKeyPoints] 边缘顶点数量不足（{len(all_edge_vertices)}），无法进行边缘退火")
        return None

    # 验证point_v是否是边缘顶点
    v_is_edge_vertex = False
    for edge_vertex in all_edge_vertices:
        if points_equal(edge_vertex, point_v):
            v_is_edge_vertex = True
            break

    if not v_is_edge_vertex:
        print(f"[FindKeyPoints] 输入的point_v不是边缘顶点（不是只被2个细胞共享），V点坐标: ({point_v[0]:.6f}, {point_v[1]:.6f})")
        return None

    # Step 2 & 3: 检索全部的边缘顶点，寻找与V构成一边的顶点，找到两个边缘顶点A和B
    # 找到所有包含V的细胞（用于确定V的邻点）
    cells_with_v = []
    v_indices = {}  # 记录V在每个细胞中的索引
    for cell in cells:
        for i, p in enumerate(cell.points):
            if points_equal(p, point_v):
                cells_with_v.append(cell)
                v_indices[cell] = i
                break

    if len(cells_with_v) < 2:
        print(f"[FindKeyPoints] 边缘顶点V被少于2个细胞共享，无法进行边缘退火，V点坐标: ({point_v[0]:.6f}, {point_v[1]:.6f})")
        return None

    # 找到V的所有邻点（在包含V的细胞中）
    v_neighbors = set()  # 使用set避免重复
    for cell in cells_with_v:
        v_idx = v_indices[cell]
        n = len(cell.points)
        prev_point = cell.points[(v_idx - 1) % n]
        next_point = cell.points[(v_idx + 1) % n]
        # 将邻点转换为tuple以便比较
        v_neighbors.add(tuple(prev_point) if isinstance(prev_point, (list, tuple)) else prev_point)
        v_neighbors.add(tuple(next_point) if isinstance(next_point, (list, tuple)) else next_point)

    # 在所有边缘顶点中，找到与V构成边的两个边缘顶点A和B
    # 即：A和B必须是边缘顶点，且是V的邻点
    point_a = None
    point_b = None
    edge_cell1 = None
    edge_cell2 = None
    idx_va = None
    idx_vb = None

    edge_vertices_as_neighbors = []
    for edge_vertex in all_edge_vertices:
        # 跳过V本身
        if points_equal(edge_vertex, point_v):
            continue

        # 检查这个边缘顶点是否是V的邻点
        edge_vertex_key = tuple(edge_vertex) if isinstance(edge_vertex, (list, tuple)) else edge_vertex
        if edge_vertex_key in v_neighbors:
            # 找到包含这条边（V-edge_vertex）的细胞
            for cell in cells_with_v:
                v_idx = v_indices[cell]
                n = len(cell.points)
                prev_point = cell.points[(v_idx - 1) % n]
                next_point = cell.points[(v_idx + 1) % n]

                # 检查edge_vertex是否是V的邻点
                if points_equal(prev_point, edge_vertex) or points_equal(next_point, edge_vertex):
                    # 确保这个细胞是边缘细胞（layer == 1）
                    if cell.layer == 1:
                        edge_vertices_as_neighbors.append({
                            'point': edge_vertex,
                            'cell': cell,
                            'v_idx': v_idx,
                            'neighbor_idx': (v_idx - 1) % n if points_equal(prev_point, edge_vertex) else (v_idx + 1) % n
                        })
                        break

    # 找到两个不同的边缘顶点A和B（来自不同的边缘细胞）
    if len(edge_vertices_as_neighbors) < 2:
        print(f"[FindKeyPoints] 找不到两个与V构成边缘边的边缘顶点（找到{len(edge_vertices_as_neighbors)}个），V点坐标: ({point_v[0]:.6f}, {point_v[1]:.6f})")
        return None

    # 选择第一个作为A
    edge_info_a = edge_vertices_as_neighbors[0]
    point_a = edge_info_a['point']
    edge_cell1 = edge_info_a['cell']
    idx_va = edge_info_a['v_idx']

    # 找到来自不同细胞的第二个边缘顶点作为B
    edge_info_b = None
    for edge_info in edge_vertices_as_neighbors[1:]:
        if edge_info['cell'] != edge_cell1 and not points_equal(edge_info['point'], point_a):
            edge_info_b = edge_info
            break

    if edge_info_b is None:
        print(f"[FindKeyPoints] 找不到来自不同细胞的第二个边缘顶点B，V点坐标: ({point_v[0]:.6f}, {point_v[1]:.6f})")
        return None

    point_b = edge_info_b['point']
    edge_cell2 = edge_info_b['cell']
    idx_vb = edge_info_b['v_idx']

    # Step 4: 由于AV和VB是边缘边，可以映射到两个边缘几何体（edge_cell1和edge_cell2）
    # 这一步已经在上面完成，edge_cell1包含AV边，edge_cell2包含VB边

    # Step 5: 检索V的邻点，找到除V以外被两个目标几何体（edge_cell1和edge_cell2）共有的点，那就是O
    point_o = None
    idx_oa = None
    idx_ob = None

    # 获取edge_cell1中V的所有邻点
    n1 = len(edge_cell1.points)
    v_idx_in_cell1 = idx_va
    neighbors_in_cell1 = [
        edge_cell1.points[(v_idx_in_cell1 - 1) % n1],  # 前一个邻点
        edge_cell1.points[(v_idx_in_cell1 + 1) % n1]   # 后一个邻点
    ]

    # 检查edge_cell1中V的每个邻点，看是否也在edge_cell2中
    for neighbor in neighbors_in_cell1:
        # 跳过V本身（虽然理论上不应该出现）
        if points_equal(neighbor, point_v):
            continue

        # 跳过A和B（因为它们已经是边缘顶点，不是我们要找的O）
        if points_equal(neighbor, point_a) or points_equal(neighbor, point_b):
            continue

        # 检查这个邻点是否在edge_cell2中
        neighbor_in_cell2 = False
        neighbor_idx_in_cell2 = None
        for i, p in enumerate(edge_cell2.points):
            if points_equal(p, neighbor):
                neighbor_in_cell2 = True
                neighbor_idx_in_cell2 = i
                break

        if neighbor_in_cell2:
            # 验证这个邻点在edge_cell2中是否与V相邻（确保V-O是edge_cell2的一条边）
            n2 = len(edge_cell2.points)
            v_idx_in_cell2 = idx_vb
            prev_neighbor_in_cell2 = edge_cell2.points[(neighbor_idx_in_cell2 - 1) % n2]
            next_neighbor_in_cell2 = edge_cell2.points[(neighbor_idx_in_cell2 + 1) % n2]

            # 如果V是这个邻点的相邻点，则这是共边，邻点就是O
            if points_equal(prev_neighbor_in_cell2, point_v) or points_equal(next_neighbor_in_cell2, point_v):
                point_o = neighbor
                # 找到O在edge_cell1中的索引
                for i, p in enumerate(edge_cell1.points):
                    if points_equal(p, point_o):
                        idx_oa = i
                        break
                idx_ob = neighbor_idx_in_cell2
                break

    if point_o is None:
        print(f"[FindKeyPoints] 找不到V的邻点中同时被edge_cell1和edge_cell2共有的点O，V点坐标: ({point_v[0]:.6f}, {point_v[1]:.6f})")
        return None

    # 返回所有关键点信息
    return {
        'point_v': point_v,
        'point_a': point_a,
        'point_b': point_b,
        'point_o': point_o,
        'edge_cell1': edge_cell1,
        'edge_cell2': edge_cell2,
        'idx_va': idx_va,
        'idx_vb': idx_vb,
        'idx_oa': idx_oa,
        'idx_ob': idx_ob
    }

#----------------------------------------------------------------------
def calculate_edge_annealing_distance(point_v, annealing_rate, cells):
    """
    计算边缘顶点的退火距离（不实际移动，只计算距离）

    参数:
        point_v: 边缘顶点V [x, y]
        annealing_rate: 退火速率
        cells: 所有细胞列表

    返回:
        float: 退火距离，如果无法计算则返回0
    """
    import math

    # 使用新逻辑找关键点
    key_points = find_edge_key_points_new(point_v, cells)
    if key_points is None:
        return 0.0

    point_a = key_points['point_a']
    point_b = key_points['point_b']
    point_o = key_points['point_o']
    edge_cell1 = key_points['edge_cell1']
    edge_cell2 = key_points['edge_cell2']

    # 计算两边缘角
    def calculate_simple_angle(p1, vertex, p2):
        v1 = (p1[0] - vertex[0], p1[1] - vertex[1])
        v2 = (p2[0] - vertex[0], p2[1] - vertex[1])
        dot_product = v1[0] * v2[0] + v1[1] * v2[1]
        mag1 = math.hypot(*v1)
        mag2 = math.hypot(*v2)
        if math.isclose(mag1 * mag2, 0):
            return 0
        cos_val = max(-1.0, min(1.0, dot_product / (mag1 * mag2)))
        return math.acos(cos_val)

    angle_AVO = calculate_simple_angle(point_a, point_v, point_o)
    angle_BVO = calculate_simple_angle(point_b, point_v, point_o)

    #----------------------------------------
    # 形状审查 - 判断是否为三角形几何体
    #----------------------------------------
    is_triangle_geometry = (len(edge_cell1.points) == 3 or len(edge_cell2.points) == 3)

    # 根据几何体形状设置不同的退火阈值
    if is_triangle_geometry:
        angle_threshold = math.radians(60)  # 至少有一个三角形几何体，使用60度阈值
        print(f"[Shape] 检测到至少一个三角形几何体 (edge_cell1: {len(edge_cell1.points)}边, edge_cell2: {len(edge_cell2.points)}边)，使用60度阈值")
    else:
        angle_threshold = math.radians(20)  # 两个都不是三角形，使用20度阈值
        print(f"[Shape] 两个边缘几何体都不是三角形 (edge_cell1: {len(edge_cell1.points)}边, edge_cell2: {len(edge_cell2.points)}边)，使用20度阈值")

    # 如果角度差小于阈值，返回0（不需要退火）
    if abs(angle_AVO - angle_BVO) < angle_threshold:
        return 0.0

    # 确定目标点（向较小角方向移动）
    # 目标点修改为当前点V和邻点（A或B）的中点
    if angle_AVO < angle_BVO:
        # 使用V和A的中点A'作为目标点
        target_point = [(point_v[0] + point_a[0]) / 2, (point_v[1] + point_a[1]) / 2]
    else:
        # 使用V和B的中点B'作为目标点
        target_point = [(point_v[0] + point_b[0]) / 2, (point_v[1] + point_b[1]) / 2]

    # 计算移动后的位置
    candidate_V = [point_v[0] + (target_point[0] - point_v[0]) * annealing_rate,
                   point_v[1] + (target_point[1] - point_v[1]) * annealing_rate]

    # 计算退火距离（从V到candidate_V的距离）
    distance = get_distance_point_point_by_list(point_v, candidate_V)

    return distance

def get_edge_move_point(point_v, annealing_rate, cells):
    """
    边缘退火逻辑（直接从边缘顶点V开始）：
    1. 输入边缘顶点V（必须是边缘顶点，即只被2个细胞共享）
    2. 使用新逻辑找关键点：V -> A, B -> edge_cell1, edge_cell2 -> O
       - A、B必须是边缘顶点（只被2个细胞共享）
    3. 计算两边缘角 A-V-O 与 B-V-O，决定退火方向
    4. candidate_V 生成
    5. O 点安全检查（只检查 V-O 在 cell 中相邻的 cell）
       * 使用凸角规范化（防止 2π 误判 180°）
    6. 移动成功 → 更新两个边缘 cell 中的 V
    """
    import math

    #----------------------------------------
    # 辅助：角度规范化为凸角（0~π）
    #----------------------------------------
    def convex_angle(theta):
        """把角度压缩到 0~π，用于凸角判定"""
        if theta > math.pi:
            return 2 * math.pi - theta
        return theta

    #----------------------------------------
    # Step 1：使用新逻辑找关键点（V -> A, B -> edge_cell1, edge_cell2 -> O）
    #----------------------------------------
    key_points = find_edge_key_points_new(point_v, cells)
    if key_points is None:
        print(f"[EdgeCheck] 使用新逻辑找不到关键点，退出，V点坐标: ({point_v[0]:.6f}, {point_v[1]:.6f})")
        return 0

    point_a = key_points['point_a']
    point_b = key_points['point_b']
    point_o = key_points['point_o']
    edge_cell1 = key_points['edge_cell1']
    edge_cell2 = key_points['edge_cell2']
    idx_va = key_points['idx_va']
    idx_vb = key_points['idx_vb']
    idx_oa = key_points['idx_oa']
    idx_ob = key_points['idx_ob']

    # 验证找到的V确实是输入的point_v
    def points_equal(p1, p2, tolerance=1e-9):
        if isinstance(p1, (list, tuple)) and isinstance(p2, (list, tuple)):
            return abs(p1[0] - p2[0]) < tolerance and abs(p1[1] - p2[1]) < tolerance
        return False

    if not points_equal(key_points['point_v'], point_v):
        found_v = key_points['point_v']
        print(f"[EdgeCheck] 警告：找到的V与输入的V不一致，输入的V: ({point_v[0]:.6f}, {point_v[1]:.6f})，找到的V: ({found_v[0]:.6f}, {found_v[1]:.6f})")
        return 0

    # point_a = cell_a.points[(idx_va - 1) % len(cell_a.points)]
    # point_b = cell_b.points[(idx_vb - 1) % len(cell_b.points)]
     # 在每个边缘 cell 中，V 点有两个邻居：一个是内部共享点 O，另一个是外侧边界点。
    # 我们希望 A、B 都取"外侧邻居"，否则如果把 O 当成邻居，会出现 A=O 或 B=O，
    # 导致 ∠AVO 或 ∠BVO 变成 0°。
    def get_outer_neighbor(cell, idx_v, shared_O_point):
        n = len(cell.points)
        prev_p = cell.points[(idx_v - 1) % n]
        next_p = cell.points[(idx_v + 1) % n]

        # 如果前一个点是 O，则外侧点是后一个；反之亦然
        if prev_p == shared_O_point and next_p != shared_O_point:
            return next_p
        if next_p == shared_O_point and prev_p != shared_O_point:
            return prev_p

        # 正常几何结构下，V 的两个邻居中应该恰好有一个是 O；
        # 若不是，说明拓扑或点序有问题，这里做一个保守兜底：仍然取原来的"前一个点"，并打印提示。
        print("[EdgeCheck] 警告：在 cell 中 V 的两个邻居都不是（或都是） O，使用默认前一顶点作为外侧点")
        return prev_p

    # 注意：A和B已经通过新逻辑找到了，它们是边缘边的另一个端点
    # 不需要再通过get_outer_neighbor查找

    # 输出调试信息：先输出V点坐标，再换行输出A,B,O的坐标信息
    print(f"V点坐标: ({point_v[0]:.6f}, {point_v[1]:.6f})")
    print(f"A点坐标: ({point_a[0]:.6f}, {point_a[1]:.6f}), B点坐标: ({point_b[0]:.6f}, {point_b[1]:.6f}), O点坐标: ({point_o[0]:.6f}, {point_o[1]:.6f})")

    # # 检查重复点
    # if A == V or V == O or A == O:
    #     #print("[Debug] 重复点检测到：", "A==V" if A==V else "", "V==O" if V==O else "", "A==O" if A==O else "")
    #     # 处理：直接认为不可退火（防止除0），返回 0 或跳过该顶点
    #     return 0

    # # 计算向量并检查长度
    # vAV = safe_vec(A, V)   # A - V
    # vOV = safe_vec(O, V)   # O - V
    # lenAV = math.hypot(vAV[0], vAV[1])
    # lenOV = math.hypot(vOV[0], vOV[1])

    # if lenAV < eps_len or lenOV < eps_len:
    #     #print(f"[Debug] 向量长度太小：lenAV={lenAV:.3e}, lenOV={lenOV:.3e}，可能存在重合点或非常靠近的点，跳过退火")
    #     return 0

    # # 计算 cosθ 并数值稳健化
    # dot = vAV[0]*vOV[0] + vAV[1]*vOV[1]
    # cos_theta = dot / (lenAV * lenOV)
    # # 修正可能的数值误差
    # if cos_theta > 1.0: cos_theta = 1.0
    # if cos_theta < -1.0: cos_theta = -1.0
    # theta = math.acos(cos_theta)

    # # # 若角度非常接近 0（例如 < 1e-6），说明共线且同向
    # # if theta < 1e-8:
    # #     print(f"[Debug] 角度接近 0（theta={theta:.3e}），A-V-O 共线且同向。")
    # #     # 处理策略（可选）：
    # #     # 1) 认为不适合沿该边移动，尝试用另一方向或跳过
    # #     # 2) 这里我们选择跳过退火以安全为先
    # #     return 0

    # # # 若角度接近 π（共线反向），theta ≈ π → 仍可以继续（不是 0）
    # # if abs(theta - math.pi) < 1e-8:
    # #     print(f"[Debug] 角度接近 π（theta≈{theta:.3e}），A-V-O 共线且反向（允许或按需处理）")
    # # ======= end 插入点 =======

    #----------------------------------------
    # Step 4：计算两边缘角
    #----------------------------------------
    # print("[DEBUG] A =", point_a)
    # print("[DEBUG] V =", point_v)
    # print("[DEBUG] O =", point_o)
    # print("[DEBUG] B =", point_b)
    # 使用简单的向量夹角计算，避免凹角误判
    def calculate_simple_angle(p1, vertex, p2):
        v1 = (p1[0] - vertex[0], p1[1] - vertex[1])
        v2 = (p2[0] - vertex[0], p2[1] - vertex[1])
        dot_product = v1[0] * v2[0] + v1[1] * v2[1]
        mag1 = math.hypot(*v1)
        mag2 = math.hypot(*v2)
        if math.isclose(mag1 * mag2, 0):
            return 0
        cos_val = max(-1.0, min(1.0, dot_product / (mag1 * mag2)))
        return math.acos(cos_val)

    # 辅助函数：将弧度转换为角度（度），如果大于180度则输出360-原角度值
    def rad_to_deg_display(angle_rad):
        """将弧度转换为角度（度），如果大于180度则输出360-原角度值"""
        angle_deg = math.degrees(angle_rad)
        if angle_deg > 180:
            return 360 - angle_deg
        return angle_deg

    angle_AVO = calculate_simple_angle(point_a, point_v, point_o)
    angle_BVO = calculate_simple_angle(point_b, point_v, point_o)

    #----------------------------------------
    # Step 4.5：形状审查 - 判断是否为三角形几何体
    #----------------------------------------
    is_triangle_geometry = (len(edge_cell1.points) == 3 or len(edge_cell2.points) == 3)

    # 根据几何体形状设置不同的退火阈值
    if is_triangle_geometry:
        angle_threshold = math.radians(60)  # 至少有一个三角形几何体，使用60度阈值
        print(f"[Shape] 检测到至少一个三角形几何体 (edge_cell1: {len(edge_cell1.points)}边, edge_cell2: {len(edge_cell2.points)}边)，使用60度阈值")
    else:
        angle_threshold = math.radians(20)  # 两个都不是三角形，使用20度阈值
        print(f"[Shape] 两个边缘几何体都不是三角形 (edge_cell1: {len(edge_cell1.points)}边, edge_cell2: {len(edge_cell2.points)}边)，使用20度阈值")

    # 转换为角度值并格式化输出
    aov_deg = rad_to_deg_display(angle_AVO)
    vob_deg = rad_to_deg_display(angle_BVO)
    print(f"before: AOV_before={aov_deg:.6f}°, VOB_before={vob_deg:.6f}°")
    if abs(angle_AVO - angle_BVO) < angle_threshold:
        print(f"[Angle] 两角几乎相等（阈值{math.degrees(angle_threshold):.0f}°），不需要退火")
        print()  # 每个点的边缘退火都换行空一行
        return 0

    #----------------------------------------
    # Step 5：生成 candidate_V
    #----------------------------------------
    # 朝较小角方向移动，目标是缩短对应的边
    # 目标点修改为当前点V和邻点（A或B）的中点
    if angle_AVO < angle_BVO:
        # 使用V和A的中点A'作为目标点
        target_point = [(point_v[0] + point_a[0]) / 2, (point_v[1] + point_a[1]) / 2]
    else:
        # 使用V和B的中点B'作为目标点
        target_point = [(point_v[0] + point_b[0]) / 2, (point_v[1] + point_b[1]) / 2]

    # 计算移动向量：(Target - V) * rate
    # 这样长边移动快，短边移动慢，且自然收敛
    candidate_V = [point_v[0] + (target_point[0] - point_v[0]) * annealing_rate,
                   point_v[1] + (target_point[1] - point_v[1]) * annealing_rate]

    #print(f"[Move] candidate_V = {candidate_V}")

    #----------------------------------------
    # Step 6：O 点安全检查（只检查 O-V 相邻的 cell）
    #----------------------------------------
    cells_to_check = []

    def push_if_adjacent(cell, idxO):
        if point_v in cell.points:
            idxV = cell.points.index(point_v)
            n = len(cell.points)
            if (idxV == (idxO - 1) % n) or (idxV == (idxO + 1) % n):
                cells_to_check.append((cell, idxO, idxV))

    # 检查edge_cell1和edge_cell2中O-V是否相邻
    push_if_adjacent(edge_cell1, idx_oa)
    push_if_adjacent(edge_cell2, idx_ob)

    # 还需要检查包含O点的其他细胞（如果有第三个细胞也包含O点）
    for cell in cells:
        if cell != edge_cell1 and cell != edge_cell2:
            if point_o in cell.points:
                idxO_other = cell.points.index(point_o)
                push_if_adjacent(cell, idxO_other)

    #print(f"[O-Check] 需要检查的 cell 数量: {len(cells_to_check)}")

    for cell_check, idxO, idxV in cells_to_check:
        ncp = len(cell_check.points)
        def P(i): return cell_check.points[i % ncp]

        A = P(idxO - 1)
        Ocoord = P(idxO)
        B = P(idxO + 1)
        V_before = P(idxV)
        V_after = (candidate_V[0], candidate_V[1])

        # 原角
        AOV_b = convex_angle(get_angle_by_three_point([A, Ocoord, V_before]))
        VOB_b = convex_angle(get_angle_by_three_point([V_before, Ocoord, B]))
        AOB_b = convex_angle(get_angle_by_three_point([A, Ocoord, B]))

        # 新角
        AOV_a = convex_angle(get_angle_by_three_point([A, Ocoord, V_after]))
        VOB_a = convex_angle(get_angle_by_three_point([V_after, Ocoord, B]))
        AOB_a = convex_angle(get_angle_by_three_point([A, Ocoord, B]))

        # print(f"[O-Check] cell.id={getattr(cell_check,'id','?')} idxO={idxO} idxV={idxV}")
        # print(f"    convex_before: AOV={AOV_b:.6f}, VOB={VOB_b:.6f}, AOB={AOB_b:.6f}")
        # print(f"    convex_after : AOV={AOV_a:.6f}, VOB={VOB_a:.6f}, AOB={AOB_a:.6f}")
        # print(f"    convex_before: AOV={AOV_b:.6f}, VOB={VOB_b:.6f}")
        # print(f"    convex_after : AOV={AOV_a:.6f}, VOB={VOB_a:.6f}")

        eps = 1e-8
        delta = 1e-4

        if AOV_a >= math.pi - eps and (AOV_a - AOV_b) > delta:
            print("[O-Check STOP] A-O-V >=180° 且显著增大")
            return 0

        if VOB_a >= math.pi - eps and (VOB_a - VOB_b) > delta:
            print("[O-Check STOP] V-O-B >=180° 且显著增大")
            return 0

        if AOB_a >= math.pi - eps and (AOB_a - AOB_b) > delta:
            print("[O-Check STOP] A-O-B >=180° 且显著增大")
            return 0

    #----------------------------------------
    # Step 6.5：退火后凸性检查（两个边缘细胞必须仍为凸多边形）
    #----------------------------------------
    if not is_cell_convex_after_move(edge_cell1, idx_va, candidate_V):
        print("[ConvexCheck STOP] 退火后 edge_cell1 非凸，跳过该顶点")
        print()  # 区分不同顶点的退火
        return 0
    if not is_cell_convex_after_move(edge_cell2, idx_vb, candidate_V):
        print("[ConvexCheck STOP] 退火后 edge_cell2 非凸，跳过该顶点")
        print()  # 区分不同顶点的退火
        return 0

    #----------------------------------------
    # Step 7：真正更新两个边缘 cell 的顶点 V
    #----------------------------------------
    edge_cell1.points[idx_va] = candidate_V
    edge_cell2.points[idx_vb] = candidate_V
    angle_AVO = get_angle_by_three_point([point_a, candidate_V, point_o])
    angle_BVO = get_angle_by_three_point([point_b, candidate_V, point_o])

    # 转换为角度值并格式化输出
    aov_deg_after = rad_to_deg_display(angle_AVO)
    vob_deg_after = rad_to_deg_display(angle_BVO)
    print(f"after: AOV_after={aov_deg_after:.6f}°, VOB_after={vob_deg_after:.6f}°")
    #打印空行
    print()
    #print("[Update] 边缘顶点 V 已退火成功")
    return 1

#-------------------------------------------------
def get_edge_move_point_gradient(cb, annealing_rate, cells,
                                 max_iter=40, grad_eps=1e-6, init_lr=0.5, tol=1e-5):
    """
    基于数值梯度下降求使两个边缘角相等的目标点（更精确、平滑收敛）。
    最终按 annealing_rate 从当前 V 向目标点前进一步（与框架兼容）。
    返回 1: 移动成功并写回 edge_cell1/edge_cell2
           0: 未移动（不安全或未收敛）
    说明：本函数仅处理单个 cell-block cb（边缘块），与原 move_point 的调用一致。
    """

    # 识别两个边缘细胞和共享点 O（与现有实现一致）
    if cb.cell1.layer != 1:
        edge_cell1 = cb.cell2
        edge_cell2 = cb.cell3
    elif cb.cell2.layer != 1:
        edge_cell1 = cb.cell1
        edge_cell2 = cb.cell3
    elif cb.cell3.layer != 1:
        edge_cell1 = cb.cell1
        edge_cell2 = cb.cell2
    else:
        return 0

    point_o = cb.cell1.points[cb.index1]

    # 找 V（两个边缘细胞共同但不是 O 的顶点）
    point_v = None
    for p in edge_cell1.points:
        if p in edge_cell2.points and p != point_o:
            point_v = p
            break
    if point_v is None:
        return 0

    # 验证为边缘顶点（只被至多两个细胞共享）
    cnt = 0
    for c in cells:
        for p in c.points:
            if p == point_v:
                cnt += 1
    if cnt > 2:
        return 0

    # 获取相邻点 A、B（对应两个边缘角 A-V-O, B-V-O）
    idx_v1 = edge_cell1.points.index(point_v)
    idx_o1 = edge_cell1.points.index(point_o)
    idx_v2 = edge_cell2.points.index(point_v)
    idx_o2 = edge_cell2.points.index(point_o)

    # 计算点 A（edge_cell1 的与 V 相邻的那个在边缘方向上）
    if (idx_v1 - idx_o1) > 0:
        # V 在 O 之后
        point_a = edge_cell1.points[(idx_v1 + 1) % len(edge_cell1.points)]
        point_b = edge_cell2.points[(idx_v2 - 1) % len(edge_cell2.points)]
    else:
        point_a = edge_cell1.points[(idx_v1 - 1) % len(edge_cell1.points)]
        point_b = edge_cell2.points[(idx_v2 + 1) % len(edge_cell2.points)]

    # 辅助：给定 V 值，返回两个角（AVO, BVO）
    def two_angles(v_xy):
        a = get_angle_by_three_point([point_a, v_xy, point_o])
        b = get_angle_by_three_point([point_b, v_xy, point_o])
        return a, b

    # 目标函数：角差平方（可微的数值优化目标）
    def loss(v_xy):
        a, b = two_angles(v_xy)
        d = a - b
        return d * d

    # 数值梯度（中心差分）
    def numeric_grad(v_xy, eps=grad_eps):
        x, y = v_xy[0], v_xy[1]
        f0 = loss([x, y])
        fx = loss([x + eps, y])
        fy = loss([x, y + eps])
        # 中心差分更稳定，但这里用前差分或中心差分都可；为简洁使用前差分
        gx = (fx - f0) / eps
        gy = (fy - f0) / eps
        return [gx, gy]

    # 初始点（float copy）
    curr = [float(point_v[0]), float(point_v[1])]

    # 如果角度差已经在容忍范围，直接不动
    a0, b0 = two_angles(curr)
    if abs(a0 - b0) < 1e-4:
        return 0

    lr = init_lr
    best = curr[:]
    best_loss = loss(curr)

    # 梯度下降主循环（带 backtracking：若 candidate 不安全或 loss 不降则缩 lr）
    for it in range(max_iter):
        g = numeric_grad(curr)
        gnorm = math.hypot(g[0], g[1])
        if gnorm == 0:
            break

        # 归一化梯度以获得稳定步长，再乘以 lr
        step = [-(g[0] / gnorm) * lr, -(g[1] / gnorm) * lr]

        # 尝试若干回退步骤（如果违反安全或 loss 不降则 shrink）
        success_step = False
        local_lr = lr
        for back in range(8):
            cand = [curr[0] + step[0], curr[1] + step[1]]
            cand_loss = loss(cand)

            # 临时 final point：在 cand 上不会立刻写回；我们只检查安全性。
            # 使用 is_vertex_angle_safe_01 对两个边缘细胞的 idx_v 与 idx_o 进行安全检查
            safe1 = is_vertex_angle_safe_01(edge_cell1, idx_v1, cand)
            safe1 = safe1 and is_vertex_angle_safe_01(edge_cell1, idx_o1, cand)
            safe2 = is_vertex_angle_safe_01(edge_cell2, idx_v2, cand)
            safe2 = safe2 and is_vertex_angle_safe_01(edge_cell2, idx_o2, cand)

            # 若安全且 loss 降低，则接受
            if safe1 and safe2 and cand_loss < best_loss + 1e-12:
                curr = cand
                best_loss = cand_loss
                best = cand[:]
                success_step = True
                break
            else:
                # 回退：缩小步长并重算 step
                local_lr *= 0.5
                step = [-(g[0] / gnorm) * local_lr, -(g[1] / gnorm) * local_lr]

        if not success_step:
            # 如果本次无法找到安全且降低 loss 的步长，停止迭代（防止破坏拓扑）
            break

        # 判断收敛（loss 降得很小）
        if best_loss < tol:
            break

        # 可自适应缩小 lr（使收敛更平滑）
        lr = min(lr, local_lr)

    # 最终目标点 best（可能等于初始 curr）
    target_xy = best

    # 再次检查角度差，若仍然很大但安全无法进一步下降，则放弃
    final_a, final_b = two_angles(target_xy)
    if abs(final_a - final_b) > 1e-2:  # 若仍大于 ~0.57度，则认为未成功收敛到平衡
        # 但是可以尝试按 annealing_rate 做一次小步（仍需安全检查）
        pass

    # 按 annealing_rate 从原始 point_v 向 target 前进一步（与框架其余部分一致）
    # 若存在 get_point_of_destination 和 Point，可用它；否则做线性插值
    try:
        # 尝试使用已有函数（保持兼容性）
        tgt_point = Point(target_xy[0], target_xy[1])
        move_pt = get_point_of_destination(point_v, tgt_point, annealing_rate)
        move_point_fin = [move_pt.x, move_pt.y]
    except Exception:
        # 退化到线性插值
        move_point_fin = [
            point_v[0] + (target_xy[0] - point_v[0]) * annealing_rate,
            point_v[1] + (target_xy[1] - point_v[1]) * annealing_rate
        ]

    # 最终安全检查（6角）和边缘几何约束
    idx_v1 = edge_cell1.points.index(point_v)
    idx_o1 = edge_cell1.points.index(point_o)
    idx_v2 = edge_cell2.points.index(point_v)
    idx_o2 = edge_cell2.points.index(point_o)

    safe_final = (
        is_vertex_angle_safe_01(edge_cell1, idx_v1, move_point_fin) and
        is_vertex_angle_safe_01(edge_cell1, idx_o1, move_point_fin) and
        is_vertex_angle_safe_01(edge_cell2, idx_v2, move_point_fin) and
        is_vertex_angle_safe_01(edge_cell2, idx_o2, move_point_fin)
    )
    if not safe_final:
        return 0

    # 额外几何判断（保持原有 judge_edge_if_annealing 约束）
    if judge_edge_if_annealing(point_v, point_o, edge_cell1, edge_cell2, move_point_fin) <= 0:
        return 0

    # 写回并更新顶点（与现有实现一致）
    edge_cell1.points[idx_v1] = move_point_fin
    edge_cell2.points[idx_v2] = move_point_fin

    # 如果你有需要，可以在这里调用 setVertex() 更新几何信息：
    try:
        edge_cell1.setVertex()
        edge_cell2.setVertex()
    except Exception:
        pass

    return 1

#-------------------------------------------------
def calculate_bisector_move(vertex, edge1, edge2, angle1, angle2, target_angle):
    """
    计算使两个相邻角相等的移动向量
    方法：沿着角平分线方向移动顶点
    """
    # 获取两条边的向量
    vec1 = (edge1[1][0] - edge1[0][0], edge1[1][1] - edge1[0][1])
    vec2 = (edge2[1][0] - edge2[0][0], edge2[1][1] - edge2[0][1])

    # 计算单位向量
    length1 = math.sqrt(vec1[0]**2 + vec1[1]**2)
    length2 = math.sqrt(vec2[0]**2 + vec2[1]**2)

    if length1 > 0:
        unit_vec1 = (vec1[0]/length1, vec1[1]/length1)
    else:
        unit_vec1 = (0, 0)

    if length2 > 0:
        unit_vec2 = (vec2[0]/length2, vec2[1]/length2)
    else:
        unit_vec2 = (0, 0)

    # 计算角平分线方向（两个单位向量的和）
    bisector = (unit_vec1[0] + unit_vec2[0], unit_vec1[1] + unit_vec2[1])

    # 归一化角平分线向量
    bisector_length = math.sqrt(bisector[0]**2 + bisector[1]**2)
    if bisector_length > 0:
        unit_bisector = (bisector[0]/bisector_length, bisector[1]/bisector_length)
    else:
        unit_bisector = (0, 0)

    # 根据角度差确定移动方向和大小
    angle_diff = angle1 - angle2
    move_strength = abs(angle_diff) / math.pi  # 移动强度与角度差成正比

    # 确定移动方向：使较小的角增大，较大的角减小
    if angle_diff > 0:
        # angle1 > angle2，需要减小angle1，增大angle2
        move_direction = unit_bisector
    else:
        # angle1 < angle2，需要增大angle1，减小angle2
        move_direction = (-unit_bisector[0], -unit_bisector[1])

    # 计算最终移动向量
    move_vector = (move_direction[0] * move_strength, move_direction[1] * move_strength)

    return move_vector

def update_vertex_position(old_vertex, new_vertex, sharing_cells):
    """
    更新顶点在所有共享细胞中的位置
    """
    for cell in sharing_cells:
        for i in range(len(cell.points)):
            if (abs(cell.points[i][0] - old_vertex[0]) < 1e-6 and
                abs(cell.points[i][1] - old_vertex[1]) < 1e-6):
                cell.points[i] = [new_vertex[0], new_vertex[1]]
                break

#------------------------------------------------------------
def get_edge_vertices_from_cellblock_last(cb, cells):
    """
    从细胞块中提取边缘顶点信息
    返回包含顶点信息的字典列表
    """
    edge_vertices_info = []

    # 识别边缘细胞
    if cb.cell1.layer != 1:
        edge_cell1 = cb.cell2
        edge_cell2 = cb.cell3
    elif cb.cell2.layer != 1:
        edge_cell1 = cb.cell1
        edge_cell2 = cb.cell3
    elif cb.cell3.layer != 1:
        edge_cell1 = cb.cell1
        edge_cell2 = cb.cell2
    else:
        return edge_vertices_info  # 没有边缘细胞

    # 获取共享顶点O（三个细胞的交汇点）
    point_o = cb.cell1.points[cb.index1]

    # 寻找边缘细胞共享的顶点V（不是交汇点O）
    point_v = None
    for p in edge_cell1.points:
        if p in edge_cell2.points and p != point_o:
            point_v = p
            break

    if point_v is None:
        return edge_vertices_info

    # 确定相邻顶点A和B
    if edge_cell1.points.index(point_v) - edge_cell1.points.index(point_o) > 0:
        point_a = edge_cell1.points[(edge_cell1.points.index(point_v) + 1) % len(edge_cell1.points)]
        point_b = edge_cell2.points[edge_cell2.points.index(point_v) - 1]
    else:
        point_a = edge_cell1.points[edge_cell1.points.index(point_v) - 1]
        point_b = edge_cell2.points[(edge_cell2.points.index(point_v) + 1) % len(edge_cell2.points)]

    # 构建顶点信息字典
    vertex_info = {
        'point_v': point_v,
        'point_o': point_o,
        'point_a': point_a,
        'point_b': point_b,
        'edge_cell1': edge_cell1,
        'edge_cell2': edge_cell2
    }

    edge_vertices_info.append(vertex_info)
    return edge_vertices_info

def get_edge_vertices_from_cellblock(cb, cells):
    """
    重写版本：放弃细胞块概念，直接基于细胞收集边缘顶点信息
    步骤：
    1. 设置列表保存边缘顶点信息
    2. 遍历细胞，找到边缘细胞
    3. 找到边缘细胞的边缘顶点
    4. 将边缘顶点信息存放在列表中
    """
    edge_vertices_info = []

    # 第一步：设置列表保存边缘顶点信息
    # 这个列表将包含字典，每个字典表示一个边缘顶点的信息
    # 格式：{'vertex': 顶点坐标, 'cell1': 细胞1, 'cell2': 细胞2, 'neighbors': 相邻顶点列表}

    # 第二步：遍历所有细胞，找到边缘细胞
    edge_cells = []
    for cell in cells:
        if cell.layer == 1:  # 边缘细胞的layer等于1
            edge_cells.append(cell)

    print(f"找到 {len(edge_cells)} 个边缘细胞")

    # 第三步：找到边缘细胞的边缘顶点
    # 边缘顶点定义：被两个边缘细胞共享的顶点
    vertex_to_cells = {}  # 顶点到细胞的映射

    # 建立顶点到细胞的映射
    for cell in edge_cells:
        for vertex in cell.points:
            vertex_tuple = tuple(vertex)  # 将列表转换为元组，以便作为字典键
            if vertex_tuple not in vertex_to_cells:
                vertex_to_cells[vertex_tuple] = []
            vertex_to_cells[vertex_tuple].append(cell)

    # 第四步：将边缘顶点信息存放在列表中
    for vertex, sharing_cells in vertex_to_cells.items():
        # 只处理被两个或更多边缘细胞共享的顶点
        if len(sharing_cells) >= 2:
            # 获取相邻顶点信息
            neighbor_info = get_vertex_neighbors(vertex, sharing_cells)

            # 构建顶点信息字典
            vertex_info = {
                'vertex': list(vertex),  # 转回列表格式
                'cells': sharing_cells,  # 共享该顶点的细胞
                'neighbors': neighbor_info,  # 相邻顶点信息
                'type': 'edge_vertex'  # 标记为边缘顶点
            }

            edge_vertices_info.append(vertex_info)
            print(f"找到边缘顶点: {vertex}")

    print(f"总共找到 {len(edge_vertices_info)} 个边缘顶点")
    return edge_vertices_info


def get_vertex_neighbors(vertex, sharing_cells):
    """
    获取顶点在共享细胞中的相邻顶点信息
    """
    neighbor_info = []
    vertex_list = list(vertex)  # 将元组转回列表

    for cell in sharing_cells:
        # 找到顶点在细胞中的索引
        if vertex_list in cell.points:
            vertex_index = cell.points.index(vertex_list)
            num_points = len(cell.points)

            # 获取前一个和后一个顶点（考虑循环）
            prev_vertex = cell.points[(vertex_index - 1) % num_points]
            next_vertex = cell.points[(vertex_index + 1) % num_points]

            # 计算与相邻顶点形成的角度
            angle_prev = get_angle_by_three_point([prev_vertex, vertex_list, next_vertex])

            # 存储相邻顶点信息
            cell_neighbor_info = {
                'cell': cell,
                'prev_vertex': prev_vertex,
                'next_vertex': next_vertex,
                'angle': angle_prev
            }

            neighbor_info.append(cell_neighbor_info)

    return neighbor_info


def get_edge_vertices_directly(cells):
    """
    直接获取所有边缘顶点的替代函数
    这个函数不依赖于细胞块，直接从细胞中提取边缘顶点
    """
    edge_vertices = []

    # 第一步：收集所有边缘细胞
    edge_cells = [cell for cell in cells if cell.layer != 1]

    # 第二步：建立顶点到细胞的映射
    vertex_map = {}
    for cell in edge_cells:
        for i, vertex in enumerate(cell.points):
            vertex_key = tuple(vertex)  # 使用元组作为键
            if vertex_key not in vertex_map:
                vertex_map[vertex_key] = {
                    'vertex': vertex,
                    'cells': [],
                    'indices': []
                }
            vertex_map[vertex_key]['cells'].append(cell)
            vertex_map[vertex_key]['indices'].append(i)

    # 第三步：筛选出被多个边缘细胞共享的顶点
    for vertex_key, info in vertex_map.items():
        if len(info['cells']) >= 2:  # 被两个或更多边缘细胞共享
            # 获取相邻细胞信息
            neighbor_cells = []
            for i, cell in enumerate(info['cells']):
                vertex_index = info['indices'][i]
                num_points = len(cell.points)

                # 获取相邻顶点
                prev_index = (vertex_index - 1) % num_points
                next_index = (vertex_index + 1) % num_points

                prev_vertex = cell.points[prev_index]
                next_vertex = cell.points[next_index]

                # 计算角度
                angle = get_angle_by_three_point([prev_vertex, info['vertex'], next_vertex])

                neighbor_info = {
                    'cell': cell,
                    'prev_vertex': prev_vertex,
                    'next_vertex': next_vertex,
                    'angle': angle,
                    'index': vertex_index
                }

                neighbor_cells.append(neighbor_info)

            # 构建完整的顶点信息
            vertex_info = {
                'vertex': info['vertex'],
                'cells': info['cells'],
                'neighbors': neighbor_cells,
                'type': 'edge_vertex',
                'shared_count': len(info['cells'])
            }

            edge_vertices.append(vertex_info)

    return edge_vertices


def enhanced_get_edge_vertices(cells, min_shared_count=2):
    """
    增强版的边缘顶点获取函数
    可以指定最小共享细胞数
    """
    print("=== 开始收集边缘顶点信息 ===")

    # 收集所有边缘细胞
    edge_cells = [cell for cell in cells if hasattr(cell, 'layer') and cell.layer == 1]
    print(f"找到 {len(edge_cells)} 个边缘细胞")

    if not edge_cells:
        print("未找到边缘细胞")
        return []

    # 使用字典记录每个顶点被哪些细胞共享
    vertex_cell_map = {}

    for cell in edge_cells:
        cell_id = id(cell)  # 使用细胞ID作为标识

        for i, vertex in enumerate(cell.points):
            vertex_key = tuple(vertex)

            if vertex_key not in vertex_cell_map:
                vertex_cell_map[vertex_key] = {
                    'vertex': vertex,
                    'cells': [],
                    'indices': [],
                    'cell_ids': set()  # 用于快速查找
                }

            # 避免重复添加同一细胞
            if cell_id not in vertex_cell_map[vertex_key]['cell_ids']:
                vertex_cell_map[vertex_key]['cells'].append(cell)
                vertex_cell_map[vertex_key]['indices'].append(i)
                vertex_cell_map[vertex_key]['cell_ids'].add(cell_id)

    # 筛选出满足共享条件的顶点
    edge_vertices = []
    for vertex_key, info in vertex_cell_map.items():
        shared_count = len(info['cells'])

        if shared_count >= min_shared_count:
            #print(f"顶点 {vertex_key} 被 {shared_count} 个边缘细胞共享")

            # 获取详细的相邻信息
            detailed_info = get_detailed_vertex_info(info['vertex'], info['cells'], info['indices'])
            detailed_info['shared_count'] = shared_count

            edge_vertices.append(detailed_info)

    print(f"总共找到 {len(edge_vertices)} 个符合条件的边缘顶点")
    return edge_vertices

def get_edge_vertices(cells, min_shared_count=2):
    """
    增强版的边缘顶点获取函数
    可以指定最小共享细胞数

    参数:
    cells: 细胞列表
    min_shared_count: 最小共享细胞数，默认为2（被两个细胞共享且不被第三个共享）

    返回:
    list: 边缘顶点列表
    """
    print("=== 开始收集边缘顶点信息 ===")

    # 收集所有边缘细胞
    edge_cells = [cell for cell in cells if hasattr(cell, 'layer') and cell.layer == 1]
    print(f"找到 {len(edge_cells)} 个边缘细胞")

    if not edge_cells:
        print("未找到边缘细胞")
        return []

    # 统计每个顶点被多少个边缘细胞共享
    vertex_shared_count = {}

    # 遍历所有边缘细胞，统计顶点共享情况
    for i, cell in enumerate(edge_cells):
        if hasattr(cell, 'vertices'):
            for vertex in cell.vertices:
                if vertex not in vertex_shared_count:
                    vertex_shared_count[vertex] = set()
                vertex_shared_count[vertex].add(i)  # 记录共享此顶点的细胞索引

    print(f"统计了 {len(vertex_shared_count)} 个唯一顶点的共享信息")

    # 找出满足条件的边缘顶点：被恰好min_shared_count个细胞共享
    edge_vertices = []

    for vertex, sharing_cells in vertex_shared_count.items():
        share_count = len(sharing_cells)

        # 如果顶点被恰好min_shared_count个边缘细胞共享，则认为是边缘顶点
        if share_count == min_shared_count:
            edge_vertices.append(vertex)

    print(f"找到 {len(edge_vertices)} 个边缘顶点（被恰好 {min_shared_count} 个边缘细胞共享）")

    # 可选：打印详细信息用于调试
    if edge_vertices and len(edge_vertices) <= 20:  # 避免输出过多信息
        print("边缘顶点详情：")
        for i, vertex in enumerate(edge_vertices[:10]):  # 只显示前10个
            sharing_cells = vertex_shared_count[vertex]
            print(f"  顶点 {i+1}: 被边缘细胞 {sharing_cells} 共享")
        if len(edge_vertices) > 10:
            print(f"  ... 以及 {len(edge_vertices) - 10} 个更多顶点")

    return edge_vertices

def get_detailed_vertex_info(vertex, sharing_cells, indices):
    """
    获取顶点的详细信息，包括相邻顶点和角度
    """
    detailed_info = {
        'vertex': vertex,
        'cells': sharing_cells,
        'neighbors': [],
        'angles': []
    }

    for i, cell in enumerate(sharing_cells):
        vertex_index = indices[i]
        num_points = len(cell.points)

        # 获取前后相邻顶点
        prev_index = (vertex_index - 1) % num_points
        next_index = (vertex_index + 1) % num_points

        prev_vertex = cell.points[prev_index]
        next_vertex = cell.points[next_index]

        # 计算角度
        angle = get_angle_by_three_point([prev_vertex, vertex, next_vertex])

        # 存储信息
        cell_info = {
            'cell': cell,
            'prev_vertex': prev_vertex,
            'next_vertex': next_vertex,
            'angle': angle,
            'index_in_cell': vertex_index
        }

        detailed_info['neighbors'].append(cell_info)
        detailed_info['angles'].append(angle)

    return detailed_info

def calculate_equal_angle_target(point_v, point_o, point_a, point_b, angle_AVO, angle_BVO):
    """
    修改后的边缘退火目标点计算函数
    实现三步逻辑：
    1. 计算角度和angle_sum及最终角度angle_final
    2. 计算当前顶点到理想位置的距离distance
    3. 计算本次移动的目标点
    """
    # 第一步：计算角度和及最终角度
    angle_sum = angle_AVO + angle_BVO
    angle_final = angle_sum / 2.0  # 最终两个角度应该相等，各占一半

    print(f"角度计算: ∠AVO={math.degrees(angle_AVO):.2f}°, ∠BVO={math.degrees(angle_BVO):.2f}°")
    print(f"角度和: {math.degrees(angle_sum):.2f}°, 最终角度: {math.degrees(angle_final):.2f}°")

    # 第二步：计算当前顶点到理想位置的距离
    # 这里需要计算使两个角度相等的理想位置
    ideal_point = calculate_ideal_point_for_equal_angles(point_v, point_o, point_a, point_b, angle_final)

    # 计算当前顶点到理想位置的距离
    distance = get_distance_point_point(point_v, ideal_point)
    print(f"当前顶点到理想位置的距离: {distance:.4f}")

    # 第三步：计算本次移动的目标点（移动annealing_rate*distance的距离）
    # 计算移动方向向量
    direction_vector = [
        ideal_point[0] - point_v[0],
        ideal_point[1] - point_v[1]
    ]

    # 归一化方向向量
    vector_length = math.sqrt(direction_vector[0]**2 + direction_vector[1]**2)
    if vector_length > 0:
        unit_vector = [
            direction_vector[0] / vector_length,
            direction_vector[1] / vector_length
        ]
    else:
        # 如果向量长度为0，则不需要移动
        unit_vector = [0, 0]

    # 计算本次移动的距离
    move_distance = distance

    # 计算目标点
    target_x = point_v[0] + unit_vector[0] * move_distance
    target_y = point_v[1] + unit_vector[1] * move_distance

    target_point = [target_x, target_y]

    print(f"本次移动距离: {move_distance:.4f} )")
    print(f"目标点: {target_point}")

    return target_point


def calculate_ideal_point_for_equal_angles(point_v, point_o, point_a, point_b, target_angle):
    """
    计算使两个角度相等的理想顶点位置
    使用几何方法计算理想位置
    """
    # 方法1: 使用角平分线和距离比例计算理想位置

    # 计算向量VO
    vo_vector = [point_o[0] - point_v[0], point_o[1] - point_v[1]]
    vo_length = math.sqrt(vo_vector[0]**2 + vo_vector[1]**2)

    if vo_length == 0:
        return point_v  # 如果VO长度为0，则无法计算

    # 计算单位向量VO
    vo_unit = [vo_vector[0]/vo_length, vo_vector[1]/vo_length]

    # 计算向量VA和VB
    va_vector = [point_a[0] - point_v[0], point_a[1] - point_v[1]]
    vb_vector = [point_b[0] - point_v[0], point_b[1] - point_v[1]]

    # 计算VA和VB在VO方向上的投影长度
    va_proj = va_vector[0]*vo_unit[0] + va_vector[1]*vo_unit[1]
    vb_proj = vb_vector[0]*vo_unit[0] + vb_vector[1]*vo_unit[1]

    # 计算理想位置：在VO方向上移动，使得两个角度相等
    # 使用简单的线性插值方法
    ideal_proj = (va_proj + vb_proj) / 2.0

    # 计算理想位置
    ideal_x = point_v[0] + vo_unit[0] * ideal_proj
    ideal_y = point_v[1] + vo_unit[1] * ideal_proj

    return [ideal_x, ideal_y]

def calculate_equal_angle_target_last(point_v, point_o, point_a, point_b, angle_AVO, angle_BVO):
    """
    计算使两个角度相等的目标点
    """
    # 方法1: 角平分线法
    if angle_AVO < angle_BVO:
        # 向A方向移动，增大∠AVO
        direction_vector = [
            (point_a[0] - point_v[0]) + (point_o[0] - point_v[0]),
            (point_a[1] - point_v[1]) + (point_o[1] - point_v[1])
        ]
    else:
        # 向B方向移动，增大∠BVO
        direction_vector = [
            (point_b[0] - point_v[0]) + (point_o[0] - point_v[0]),
            (point_b[1] - point_v[1]) + (point_o[1] - point_v[1])
        ]

    # 归一化方向向量
    length = math.sqrt(direction_vector[0]**2 + direction_vector[1]**2)
    if length > 0:
        direction_vector = [direction_vector[0]/length, direction_vector[1]/length]

    # 基于角度差计算移动距离
    angle_diff = abs(angle_AVO - angle_BVO)
    move_distance = angle_diff * 0.5  # 可调整系数

    # 计算目标点
    target_x = point_v[0] + direction_vector[0] * move_distance
    target_y = point_v[1] + direction_vector[1] * move_distance

    return [target_x, target_y]


def is_move_safe(edge_cell1, edge_cell2, point_v, point_o, move_point):
    # """
    # 检查移动是否安全
    # """
    # # 检查顶点角度安全性
    # idx_v1 = edge_cell1.points.index(point_v)
    # idx_o1 = edge_cell1.points.index(point_o)
    # idx_v2 = edge_cell2.points.index(point_v)
    # idx_o2 = edge_cell2.points.index(point_o)

    # if not (is_vertex_angle_safe(edge_cell1, idx_v1, move_point) and
    #         is_vertex_angle_safe(edge_cell1, idx_o1, move_point) and
    #         is_vertex_angle_safe(edge_cell2, idx_v2, move_point) and
    #         is_vertex_angle_safe(edge_cell2, idx_o2, move_point)):
    #     return False

    # # 检查边缘退火几何约束
    # if judge_edge_if_annealing(point_v, point_o, edge_cell1, edge_cell2, move_point) <= 0:
    #     return False

    return True


def get_edge_move_point_test_default(cb, annealing_rate, cells):
    """
    基于角度判断的边缘退火移动函数
    将边缘顶点V沿较小边缘角的边缘边移动，使得两个边缘角相等
    """
    # 获取三个细胞共享的交汇点O
    point_o = cb.cell1.points[cb.index1]

    # 识别两个边缘细胞
    if cb.cell1.layer != 1:
        edge_cell1 = cb.cell2
        edge_cell2 = cb.cell3
    elif cb.cell2.layer != 1:
        edge_cell1 = cb.cell1
        edge_cell2 = cb.cell3
    elif cb.cell3.layer != 1:
        edge_cell1 = cb.cell1
        edge_cell2 = cb.cell2
    else:
        return 0  # 如果退火细胞块全是边缘细胞，则不进行退火操作

    # 寻找两个边缘细胞共享的顶点V
    point_v = None
    for p in edge_cell1.points:
        if p in edge_cell2.points and p != point_o:
            point_v = p
            break

    if point_v is None:
        return 0

    # 验证该顶点确实是边缘顶点（被不超过2个细胞共享）
    flag_count = 0
    for c in cells:
        for p in c.points:
            if p == point_v:
                flag_count += 1
    if flag_count > 2:
        return -1  # 内部顶点，不进行边缘退火

    # 确定相邻顶点A和B
    if edge_cell1.points.index(point_v) - edge_cell1.points.index(point_o) > 0 and \
       edge_cell1.points.index(point_v) + 1 < len(edge_cell1.points):
        if edge_cell1.points.index(point_v) + 1 >= len(edge_cell1.points):
            point_a = edge_cell1.points[0]  # 循环到起点
        else:
            point_a = edge_cell1.points[edge_cell1.points.index(point_v) + 1]
        point_b = edge_cell2.points[edge_cell2.points.index(point_v) - 1]
    else:
        if edge_cell2.points.index(point_v) + 1 >= len(edge_cell2.points):
            point_b = edge_cell2.points[0]
        else:
            point_b = edge_cell2.points[edge_cell2.points.index(point_v) + 1]
        point_a = edge_cell1.points[edge_cell1.points.index(point_v) - 1]

    # 计算当前两个边缘角
    angle_AVO = get_angle_by_three_point([point_a, point_v, point_o])
    angle_BVO = get_angle_by_three_point([point_b, point_v, point_o])
    #print("当前两个边缘角：", angle_AVO, angle_BVO)
    # 检查角度是否已经接近相等（设置容差）
    angle_tolerance = 0.01  # 弧度，约0.57度
    if abs(angle_AVO - angle_BVO) < angle_tolerance:
        return 0  # 角度已经基本相等，不需要移动

    # 计算角度差
    angle_diff = abs(angle_AVO - angle_BVO)

    # 确定移动方向：向较小角度的方向移动
    if angle_AVO < angle_BVO:
        # 向A移动，增大∠AVO，减小∠BVO
        #print("向A移动")
        target_point = point_a
    else:
        # 向B移动，减小∠AVO，增大∠BVO
        target_point = point_b
        #print("向B移动")
    # 计算移动向量
    move_vector = [target_point[0] - point_v[0], target_point[1] - point_v[1]]
    #print("移动向量：", move_vector)
    # 归一化移动向量（转换为单位向量）
    vector_length = math.sqrt(move_vector[0]**2 + move_vector[1]**2)
    if vector_length > 0:
        unit_vector = [move_vector[0]/vector_length, move_vector[1]/vector_length]
    else:
        return 0  # 点重合，无法移动
    #print   ("单位向量：", unit_vector)
    # 根据角度差和退火速率调整移动距离
    move_distance = angle_diff * annealing_rate

    # 计算新位置
    xg = point_v[0] + unit_vector[0] * move_distance
    yg = point_v[1] + unit_vector[1] * move_distance
    point_move_v = [xg, yg]

    # 应用退火速率，计算最终移动点
    point_move_v_fin = get_point_of_destination(
        edge_cell1.points[edge_cell1.points.index(point_v)],
        Point(point_move_v[0], point_move_v[1]),
        annealing_rate
    )
    point_move_v_fin = [point_move_v_fin.x, point_move_v_fin.y]
    #print("point_move_v_fin", point_move_v_fin)
    # 检查移动是否满足几何约束
    # 检查四个顶点角的安全性
    idx_v1 = edge_cell1.points.index(point_v)
    idx_o1 = edge_cell1.points.index(point_o)
    idx_v2 = edge_cell2.points.index(point_v)
    idx_o2 = edge_cell2.points.index(point_o)
    #print("边缘退火条件检查")
    # if not (is_vertex_angle_safe(edge_cell1, idx_v1, point_move_v_fin) and
    #         is_vertex_angle_safe(edge_cell1, idx_o1, point_move_v_fin) and
    #         is_vertex_angle_safe(edge_cell2, idx_v2, point_move_v_fin) and
    #         is_vertex_angle_safe(edge_cell2, idx_o2, point_move_v_fin)):
    #     return 0  # 顶点角安全检查失败
    #print("边缘退火条件检查成功")
    # 检查边缘退火条件
    if judge_edge_if_annealing(point_v, point_o, edge_cell1, edge_cell2, point_move_v_fin) > 0:
        # 移动点
        edge_cell1.points[edge_cell1.points.index(point_v)] = point_move_v_fin
        edge_cell2.points[edge_cell2.points.index(point_v)] = point_move_v_fin
        print("边缘退火移动完成，新位置:", point_move_v_fin)
        return 1
    else:
        print("边缘退火移动被拒绝，不满足几何约束")
        return 0


def get_edge_move_point_last(cb, annealing_rate, cells):
    """
    基于角度判断的边缘退火移动函数
    将边缘顶点V沿较小边缘角的边缘边移动，使得两个边缘角相等
    """
    # 获取三个细胞共享的交汇点O
    point_o = cb.cell1.points[cb.index1]

    # 识别两个边缘细胞
    if cb.cell1.layer != 1:
        edge_cell1 = cb.cell2
        edge_cell2 = cb.cell3
    elif cb.cell2.layer != 1:
        edge_cell1 = cb.cell1
        edge_cell2 = cb.cell3
    elif cb.cell3.layer != 1:
        edge_cell1 = cb.cell1
        edge_cell2 = cb.cell2
    else:
        return 0

    # 寻找两个边缘细胞共享的顶点V
    point_v = None
    for p in edge_cell1.points:
        if p in edge_cell2.points and p != point_o:
            point_v = p
            break

    if point_v is None:
        return 0

    # 验证该顶点确实是边缘顶点
    flag_count = 0
    for c in cells:
        for p in c.points:
            if p == point_v:
                flag_count += 1
    if flag_count > 2:
        return -1

    # 确定相邻顶点A和B
    if edge_cell1.points.index(point_v) - edge_cell1.points.index(point_o) > 0 and \
       edge_cell1.points.index(point_v) + 1 < len(edge_cell1.points):
        if edge_cell1.points.index(point_v) + 1 >= len(edge_cell1.points):
            point_a = edge_cell1.points[0]
        else:
            point_a = edge_cell1.points[edge_cell1.points.index(point_v) + 1]
        point_b = edge_cell2.points[edge_cell2.points.index(point_v) - 1]
    else:
        if edge_cell2.points.index(point_v) + 1 >= len(edge_cell2.points):
            point_b = edge_cell2.points[0]
        else:
            point_b = edge_cell2.points[edge_cell2.points.index(point_v) + 1]
        point_a = edge_cell1.points[edge_cell1.points.index(point_v) - 1]

    # 计算当前两个边缘角
    angle_AVO = get_angle_by_three_point([point_a, point_v, point_o])
    angle_BVO = get_angle_by_three_point([point_b, point_v, point_o])

    # 检查角度是否已经接近相等
    angle_tolerance = 0.01
    if abs(angle_AVO - angle_BVO) < angle_tolerance:
        return 0

    # 计算角度差
    angle_diff = abs(angle_AVO - angle_BVO)

    # 确定移动方向：向较小角度的方向移动
    if angle_AVO < angle_BVO:
        target_point = point_a
    else:
        target_point = point_b

    # 计算移动向量
    move_vector = [target_point[0] - point_v[0], target_point[1] - point_v[1]]

    # 归一化移动向量
    vector_length = math.sqrt(move_vector[0]**2 + move_vector[1]**2)
    if vector_length > 0:
        unit_vector = [move_vector[0]/vector_length, move_vector[1]/vector_length]
    else:
        return 0

    # 根据角度差和退火速率调整移动距离
    move_distance = angle_diff * annealing_rate

    # 计算新位置
    xg = point_v[0] + unit_vector[0] * move_distance
    yg = point_v[1] + unit_vector[1] * move_distance
    point_move_v = [xg, yg]

    # 应用退火速率，计算最终移动点
    point_move_v_fin = get_point_of_destination(
        edge_cell1.points[edge_cell1.points.index(point_v)],
        Point(point_move_v[0], point_move_v[1]),
        annealing_rate
    )
    point_move_v_fin = [point_move_v_fin.x, point_move_v_fin.y]

    # 检查移动是否满足几何约束
    if judge_edge_if_annealing(point_v, point_o, edge_cell1, edge_cell2, point_move_v_fin) > 0:
        # 移动点
        edge_cell1.points[edge_cell1.points.index(point_v)] = point_move_v_fin
        edge_cell2.points[edge_cell2.points.index(point_v)] = point_move_v_fin
        return 1
    else:
        return 0

def calculate_ideal_target_point(point_v, point_o, point_a, point_b, angle_AVO, angle_BVO):
    """
    计算理想目标点（使两个边缘角相等的点）
    这是一个独立的辅助函数
    """
    # 方法2: 数值优化（更精确）
    def angle_difference_func(new_v):
        new_angle_AVO = get_angle_by_three_point([point_a, new_v, point_o])
        new_angle_BVO = get_angle_by_three_point([point_b, new_v, point_o])
        return abs(new_angle_AVO - new_angle_BVO)

    # 使用优化算法找到使角度差最小的点
    from scipy.optimize import minimize
    result = minimize(angle_difference_func, point_v, method='BFGS')
    ideal_point = result.x

    distance = get_distance_point_point(point_v, ideal_point)
    return distance
def is_O_vertex_safe(cell_O, index_O, candidate_V):
    """
    以 O 为中心点，检查 O 与它的3个相邻点组成的三个角是否 >= 180°。

    cell_O : 包含 O 的 cell 对象
    index_O: O 在 cell 内的索引
    candidate_V : 移动后的 V 的坐标 [x, y]
    """

    # 复制一次 cell_O 的顶点
    try:
        pts = [p.copy() for p in cell_O.points]
    except:
        pts = [list(p) for p in cell_O.points]

    # O 的坐标
    Ox, Oy = pts[index_O]

    # 3 个相邻点：左、右、移动后的 V（与 cell edge 拥有公共边）
    n = len(pts)
    def P(i):
        return pts[i % n]

    leftP  = P(index_O - 1)
    rightP = P(index_O + 1)
    Vp     = candidate_V  # 替换为移动后的 V

    # 计算三个角
    angle_AOV = get_angle_by_three_point([leftP,  (Ox, Oy), Vp])
    angle_VOB = get_angle_by_three_point([Vp,     (Ox, Oy), rightP])
    angle_AOB = get_angle_by_three_point([leftP,  (Ox, Oy), rightP])

    # 检查是否 >= 180°
    if angle_AOV >= math.pi - 1e-9:
        print("[O-Check-STOP] 角 A-O-V >=180°，取消退火")
        return False

    if angle_VOB >= math.pi - 1e-9:
        print("[O-Check-STOP] 角 V-O-B >=180°，取消退火")
        return False

    if angle_AOB >= math.pi - 1e-9:
        print("[O-Check-STOP] 角 A-O-B >=180°，取消退火")
        return False

    return True

# def is_vertex_angle_safe(angle_AVO,angle_BVO,point_a):
#     # 检查角度是否已经接近相等（设置容差）
#     angle_tolerance = 0.01  # 弧度，约0.57度
#     if abs(angle_AVO - angle_BVO) < angle_tolerance:
#         return 0  # 角度已经基本相等，不需要移动

#     # 计算角度差
#     angle_diff = abs(angle_AVO - angle_BVO)

#     # 确定移动方向：向较小角度的方向移动
#     if angle_AVO < angle_BVO:
#         #move_direction = "A"  # 向A移动，增大∠AVO，减小∠BVO
#         target_point = point_a
#     else:
#         #move_direction = "B"  # 向B移动，减小∠AVO，增大∠BVO
#         target_point = point_b

#     # 计算移动向量
#     move_vector = [target_point[0] - point_v[0], target_point[1] - point_v[1]]

#     # 归一化移动向量（转换为单位向量）
#     vector_length = math.sqrt(move_vector[0]**2 + move_vector[1]**2)
#     if vector_length > 0:
#         unit_vector = [move_vector[0]/vector_length, move_vector[1]/vector_length]
#     else:
#         return 0  # 点重合，无法移动

#     # 根据角度差和退火速率调整移动距离
#     move_distance = angle_diff * annealing_rate
#     #move_distance = angle_diff * annealing_rate * 0.5  # 乘以0.5避免过度移动

#     # 计算新位置
#     xg = point_v[0] + unit_vector[0] * move_distance
#     yg = point_v[1] + unit_vector[1] * move_distance
#     point_move_v = [xg, yg]

#     # 应用退火速率，计算最终移动点
#     point_move_v_fin = get_point_of_destination(
#         edge_cell1.points[edge_cell1.points.index(point_v)],
#         Point(point_move_v[0], point_move_v[1]),
#         annealing_rate
#     )
#     point_move_v_fin = [point_move_v_fin.x, point_move_v_fin.y]

#     # 检查移动是否满足几何约束
#     idx_v1 = edge_cell1.points.index(point_v)
#     idx_o1 = edge_cell1.points.index(point_o)
#     idx_v2 = edge_cell2.points.index(point_v)
#     idx_o2 = edge_cell2.points.index(point_o)
#     if not (is_vertex_angle_safe(edge_cell1, idx_v1, point_move_v_fin) and
#             is_vertex_angle_safe(edge_cell1, idx_o1, point_move_v_fin) and
#             is_vertex_angle_safe(edge_cell2, idx_v2, point_move_v_fin) and
#             is_vertex_angle_safe(edge_cell2, idx_o2, point_move_v_fin)):
#         return 0
#     if judge_edge_if_annealing(point_v, point_o, edge_cell1, edge_cell2, point_move_v_fin) > 0:
#         # 移动点
#         edge_cell1.points[edge_cell1.points.index(point_v)] = point_move_v_fin
#         edge_cell2.points[edge_cell2.points.index(point_v)] = point_move_v_fin
#         print("边缘退火移动完成，新位置:", point_move_v_fin)
#         return 1
#     else:
#         print("边缘退火移动被拒绝，不满足几何约束")
#         return 0

def get_innear_point(cb, annealing_rate, cells):
        # 1. 计算重心点 - 内部退火的目标点
    point_g = cb.getTriCentreOfGravity()

    # 2. 计算移动目标点 - 基于当前点和重心点
    move_point = get_point_of_destination(cb.cell1.points[cb.index1], point_g, annealing_rate)

    # 3. 退火可行性判断
    flag_index = judge_if_annealing(cb, move_point)

    # 4. 根据判断结果处理
    if flag_index == 0:  # 可以退火
        move_flag = True
    elif flag_index == -1:
        best_count += 1      # 已接近最优，无需退火
    elif flag_index == -2:
        need_not_count += 1  # 不需要退火
    elif flag_index == -3:
        judge_180_count += 1 # 不满足凸多边形约束
    elif flag_index == -4:
        judge_inner_angle_count += 1 # 内角平方和会增大

    # 5. 如果判断可以退火，执行顶点更新
    if move_flag:
        # 更新三个共享顶点的细胞坐标
        cb.cell1.points[cb.index1] = [move_point.x, move_point.y]
        cb.cell2.points[cb.index2] = [move_point.x, move_point.y]
        cb.cell3.points[cb.index3] = [move_point.x, move_point.y]

        # 更新细胞的几何属性
        cb.cell1.setVertex()
        cb.cell2.setVertex()
        cb.cell3.setVertex()

'''
    退火移动方法（核心方法之一）
    Annealing moving method (one of core methods)
    :param intersection_cell_blocks: 退火细胞块列表 Annealed cell block list
    :param flag: 奇偶转换器  Parity converter
    :return annealing_count: 实际退火的细胞块总数 Total number of cell blocks actually annealed
'''
def calculate_ideal_target_point(cb, cells):
    """
    计算边缘细胞的理想目标点（使两个边缘角相等的点）
    基于新的边缘退火算法逻辑
    """
    # 获取三个细胞共享的交汇点O
    point_o = cb.cell1.points[cb.index1]

    # 识别两个边缘细胞
    if cb.cell1.layer != 1:
        edge_cell1 = cb.cell2
        edge_cell2 = cb.cell3
    elif cb.cell2.layer != 1:
        edge_cell1 = cb.cell1
        edge_cell2 = cb.cell3
    elif cb.cell3.layer != 1:
        edge_cell1 = cb.cell1
        edge_cell2 = cb.cell2
    else:
        # 如果退火细胞块全是边缘细胞，返回当前点（不移动）
        return Point(point_o[0], point_o[1])

    # 寻找两个边缘细胞共享的顶点V（不是交汇点O）
    point_v = None
    for p in edge_cell1.points:
        if p in edge_cell2.points and p != point_o:
            point_v = p
            break

    if point_v is None:
        print("错误：找不到共享顶点V")
        return Point(point_o[0], point_o[1])

    # 确定相邻顶点A和B
    if edge_cell1.points.index(point_v) - edge_cell1.points.index(point_o) > 0 and \
       edge_cell1.points.index(point_v) + 1 < len(edge_cell1.points):
        if edge_cell1.points.index(point_v) + 1 >= len(edge_cell1.points):
            point_a = edge_cell1.points[0]
        else:
            point_a = edge_cell1.points[edge_cell1.points.index(point_v) + 1]
        point_b = edge_cell2.points[edge_cell2.points.index(point_v) - 1]
    else:
        if edge_cell2.points.index(point_v) + 1 >= len(edge_cell2.points):
            point_b = edge_cell2.points[0]
        else:
            point_b = edge_cell2.points[edge_cell2.points.index(point_v) + 1]
        point_a = edge_cell1.points[edge_cell1.points.index(point_v) - 1]

    # 计算当前两个边缘角
    angle_AVO = get_angle_by_three_point([point_a, point_v, point_o])
    angle_BVO = get_angle_by_three_point([point_b, point_v, point_o])

    # 检查角度是否已经接近相等
    angle_tolerance = 0.01  # 弧度，约0.57度
    if abs(angle_AVO - angle_BVO) < angle_tolerance:
        return Point(point_v[0], point_v[1])  # 角度已经基本相等，返回当前点

    # 使用角平分线法计算理想目标点（比数值优化更快，适合排序）
    return calculate_target_by_angle_bisector(point_v, point_o, point_a, point_b, angle_AVO, angle_BVO)

def calculate_target_by_angle_bisector(point_v, point_o, point_a, point_b, angle_AVO, angle_BVO):
    """
    使用角平分线法计算使两个边缘角相等的目标点
    """
    # 计算向量VO, VA, VB
    vo_vector = [point_o[0] - point_v[0], point_o[1] - point_v[1]]
    va_vector = [point_a[0] - point_v[0], point_a[1] - point_v[1]]
    vb_vector = [point_b[0] - point_v[0], point_b[1] - point_v[1]]

    # 计算单位向量
    def normalize(vector):
        length = math.sqrt(vector[0]**2 + vector[1]**2)
        if length > 0:
            return [vector[0]/length, vector[1]/length]
        return vector

    vo_unit = normalize(vo_vector)
    va_unit = normalize(va_vector)
    vb_unit = normalize(vb_vector)

    # 计算角平分线方向（向量加法）
    if angle_AVO < angle_BVO:
        # 向A方向移动，使∠AVO增大
        bisector_direction = [
            va_unit[0] + vo_unit[0],
            va_unit[1] + vo_unit[1]
        ]
    else:
        # 向B方向移动，使∠BVO增大
        bisector_direction = [
            vb_unit[0] + vo_unit[0],
            vb_unit[1] + vo_unit[1]
        ]

    # 归一化角平分线方向
    bisector_unit = normalize(bisector_direction)

    # 计算移动距离（基于角度差）
    angle_diff = abs(angle_AVO - angle_BVO)
    move_distance = angle_diff * 0.5  # 经验系数

    # 计算目标点
    target_x = point_v[0] + bisector_unit[0] * move_distance
    target_y = point_v[1] + bisector_unit[1] * move_distance

    return Point(target_x, target_y)

def is_vertex_angle_safe_02(cell, index, candidate):
    """
    检查一次虚拟的顶点移动是否会导致细胞内角大于180度。
    这会检查被移动顶点自身，以及其左右两个邻居顶点的角度。
    """
    temp_points = [p.copy() for p in cell.points]
    temp_points[index] = candidate

    l = len(temp_points)

    # 检查点索引-1, 索引, 索引+1的三个角度
    for i in range(-1, 2):
        vertex_index_to_check = (index + i + l) % l

        p_prev = temp_points[(vertex_index_to_check - 1 + l) % l]
        p_curr = temp_points[vertex_index_to_check]
        p_next = temp_points[(vertex_index_to_check + 1) % l]

        angle = get_angle_by_three_point([p_prev, p_curr, p_next])

        # 如果任何一个角度大于或等于180度，则认为是不安全的移动
        if angle >= math.pi - 1e-9:
            return False

    return True

def move_point_last01(intersection_cell_blocks, annealing_rate, edge_judge, flag, cells):
    """
    修改版 move_point：对边缘退火增加退化/重试策略，优先使用现有 get_edge_move_point，
    失败时尝试缩小步长重试，再尝试数值梯度求解（若实现了 get_edge_move_point_gradient）。
    """
    count = 0
    now_count = 0
    edge_count = 0
    need_not_count = 0
    best_count = 0
    judge_180_count = 0
    judge_inner_angle_count = 0
    edge_annealing_points = 0
    inner_annealing_points = 0

    # 排序（保持原行为）
    sort_cells_by_distance(intersection_cell_blocks, cells)

    for cb in intersection_cell_blocks:
        count += 1
        now_count += 1

        # 判断是否为"边缘块"（三个 cell 中至少有两个 layer==1）
        is_edge_block = (
            (cb.cell1.layer == 1 and cb.cell2.layer == 1) or
            (cb.cell1.layer == 1 and cb.cell3.layer == 1) or
            (cb.cell2.layer == 1 and cb.cell3.layer == 1)
        )

        if is_edge_block and edge_judge:
            # --------------- 边缘退火处理 ---------------
            # 首先用现有的函数尝试一次（不改变 annealing_rate）
            edge_move_point = get_edge_move_point(cb, annealing_rate, cells)

            if edge_move_point and edge_move_point > 0:
                edge_annealing_points += 1
                edge_count += 1
                # 跳过内部退火（保持原逻辑）
                continue

            # 如果首次失败，尝试退化策略：逐步缩小 annealing_rate 重试
            # 例如尝试原始、/2、/4、/8（最多重试3次）
            tried = False
            rates_to_try = [annealing_rate * (0.5 ** k) for k in range(1, 4)]
            for r in rates_to_try:
                edge_move_point = None
                try:
                    edge_move_point = get_edge_move_point(cb, r, cells)
                except Exception:
                    edge_move_point = None

                if edge_move_point and edge_move_point > 0:
                    edge_annealing_points += 1
                    edge_count += 1
                    tried = True
                    break

            if tried:
                # 成功后继续下一个 cb（保持原有 continue 行为）
                continue

            # 如果仍失败且存在更强的数值方法（梯度/优化），调用它做最后尝试
            # 该函数名 get_edge_move_point_gradient 在之前讨论中已提供（若未实现则跳过）
            try:
                if 'get_edge_move_point_gradient' in globals():
                    grad_res = get_edge_move_point_gradient(cb, annealing_rate, cells)
                    if grad_res and grad_res > 0:
                        edge_annealing_points += 1
                        edge_count += 1
                        continue
            except Exception:
                # 若梯度方法报错，则忽略（保持稳健）
                pass

            # 所有尝试都失败：记录并继续（不阻塞）
            # 不使用 continue here? 保持原逻辑：边缘块处理完后跳过内部退火
            # 但为了兼容旧返回值，这里直接 continue
            continue

        else:
            # --------------- 内部退火处理 ---------------
            point_g = cb.getTriCentreOfGravity()
            move_flag = False
            move_point = get_point_of_destination(cb.cell1.points[cb.index1], point_g, annealing_rate)
            flag_index = judge_if_annealing(cb, move_point)

            if flag_index == 0:
                move_flag = True
                inner_annealing_points += 1
            elif flag_index == -1:
                best_count += 1
            elif flag_index == -2:
                need_not_count += 1
            elif flag_index == -3:
                judge_180_count += 1
            elif flag_index == -4:
                judge_inner_angle_count += 1

            if not move_flag:
                continue

            # 执行内部移动（保持现有写回方式）
            cb.cell1.points[cb.index1] = [move_point.x, move_point.y]
            cb.cell2.points[cb.index2] = [move_point.x, move_point.y]
            cb.cell3.points[cb.index3] = [move_point.x, move_point.y]
            try:
                cb.cell1.setVertex()
                cb.cell2.setVertex()
                cb.cell3.setVertex()
            except Exception:
                pass

    # 输出统计信息（与原代码格式兼容）
    actual_annealed_cell_blocks = edge_annealing_points + inner_annealing_points
    print("一次退火完成，本次退火相关信息如下：")
    print("应退火细胞块总数：{0}，实际退火细胞块总数：{1},实际退火的边缘顶点{2},实际退火的内部顶点{3}".format(
        now_count,
        actual_annealed_cell_blocks,
        edge_annealing_points,
        inner_annealing_points
    ))

    # 为兼容老调用返回值（原来返回 now_count - edge_count - need_not_count ...）
    try:
        return actual_annealed_cell_blocks, {'edge_vertices': edge_annealing_points, 'internal_vertices': inner_annealing_points}
    except Exception:
        # Fallback：返回整数
        return actual_annealed_cell_blocks

def move_point(intersection_cell_blocks, annealing_rate, edge_judge, flag, cells):
    # """修改后的退火移动函数，增加统计功能"""

    # # 初始化统计管理器
    # if stats_manager is None:
    #     #stats_manager = AnnealingStatistics()
    #     stats_manager = annealing_statistics()

    count = 0  # 待退火细胞块总数 Total number of cell blocks to be annealed
    now_count = 0  # 当前待退火细胞块总数 Total number of cell blocks to be returned
    edge_count = 0  # 边缘细胞块总数 Total number of marginal cell blocks
    need_not_count = 0  # 不需要退火细胞块总数 Total number of cell blocks not required to be annealed
    best_count = 0  # 接近最优退火细胞块总数 The total number of cell blocks was close to the optimal annealing
    judge_180_count = 0  # 退火后不满足凸多边形的细胞块总数 Total number of cell blocks not meeting convex polygon after annealing
    judge_inner_angle_count = 0  # 退火后内角平方和会增大的细胞块总数 The total number of cell blocks increased after annealing
    edge_annealing_points = 0
    inner_annealing_points = 0

    # 如果边缘退火开启，输出一次所有边缘顶点信息
    if edge_judge:
        all_edge_vertices = get_all_edge_vertices(cells)
        print(f"[EdgeVertices] 全部边缘顶点个数: {len(all_edge_vertices)}")
        print(f"[EdgeVertices] 边缘顶点坐标列表:")
        for i, vertex in enumerate(all_edge_vertices):
            print(f"  [{i+1}] ({vertex[0]:.6f}, {vertex[1]:.6f})")

    # 在这里对intersection_cell_blocks进行一个排序 Here, the cross section_ cell_ Blocks to sort
    #sort_intersection_cell_blocks(intersection_cell_blocks)

    # 在这里对cells进行按照距离进行排序
    sort_cells_by_distance(intersection_cell_blocks,cells)

    # 如果边缘退火开启，先处理所有边缘顶点
    if edge_judge:
        all_edge_vertices = get_all_edge_vertices(cells)

        # Step 1: 计算所有边缘顶点的初始退火距离并排序
        edge_vertex_info = []
        for point_v in all_edge_vertices:
            # 计算初始退火距离（用于排序）
            initial_distance = calculate_edge_annealing_distance(point_v, annealing_rate, cells)
            edge_vertex_info.append({
                'point_v': point_v,
                'initial_distance': initial_distance
            })

        # 按照初始退火距离由大到小排序
        edge_vertex_info.sort(key=lambda x: x['initial_distance'], reverse=True)

        # Step 2: 按排序后的顺序处理边缘顶点
        # 每次处理前重新计算当前顶点的退火距离（使用最新坐标）
        for vertex_info in edge_vertex_info:
            point_v = vertex_info['point_v']

            # 重新计算当前顶点的退火距离（使用最新的细胞结构）
            current_distance = calculate_edge_annealing_distance(point_v, annealing_rate, cells)

            # 如果距离为0，说明不需要退火，跳过
            if current_distance <= 0:
                continue

            # 执行边缘退火
            edge_move_result = get_edge_move_point(point_v, annealing_rate, cells)
            if edge_move_result > 0:
                edge_annealing_points += 1

    # 移动交汇点 move intersection（内部退火）
    for cb in intersection_cell_blocks:
        # annealing_rate = get_annealing_rate(cb) # 根据角度计算速率 （已弃用）
        count += 1  # 总数+1 Total + 1

        # 取消奇偶序号细胞块判断
        # if flag:
        #     if count % 2 == 0:
        #         continue
        # else:
        #     if not count % 2 == 0:
        #         continue

        now_count += 1  # 当前总数+1 Current total + 1

        # 跳过边缘细胞块（已在上面处理）
        # if (cb.cell1.layer == 1 and cb.cell2.layer == 1) \
        #         or (cb.cell1.layer == 1 and cb.cell3.layer == 1) \
        #         or (cb.cell2.layer == 1 and cb.cell3.layer == 1):
        #     continue
        # else:
        point_g = cb.getTriCentreOfGravity()


        '''
        根据角度判断标准，循环设置退火速率（已弃用）
        '''
        # annealing_rate_list = [0.1, 0.06, 0.03, 0.02, 0.01]
        # move_flag = False
        # while True:
        #     move_point = get_point_of_destination(cb.cell1.points[cb.index1], point_g, annealing_rate)
        #     flag_index = judge_if_annealing(cb, move_point)
        #     if flag_index == 0:  # 如果可以移动，则直接退出循环
        #         move_flag = True
        #         break
        #     if annealing_rate == 0.01:  # 如果循环到最后也不可移动，则返回False
        #         if flag_index == -1:
        #             best_count += 1
        #         elif flag_index == -2:
        #             need_not_count += 1
        #         elif flag_index == -3:
        #             judge_180_count += 1
        #         elif flag_index == -4:
        #             judge_inner_angle_count += 1
        #         move_flag = False
        #         break
        #
        #     annealing_rate = annealing_rate_list[annealing_rate_list.index(annealing_rate)+1]  # 改变退火速率，重新判断

        '''
        根据用户输入设置退火速率
        '''
        move_flag = False
        move_point = get_point_of_destination(cb.cell1.points[cb.index1], point_g, annealing_rate)
        flag_index = judge_if_annealing(cb, move_point)
        if flag_index == 0:  # 如果可以移动，则返回true
            move_flag = True
            inner_annealing_points+=1
        elif flag_index == -1:
            best_count += 1
            #print("best_count:", best_count)
        elif flag_index == -2:
            need_not_count += 1
            #这两个细胞块数值接收不到
            print("need_not_count:", need_not_count)
        elif flag_index == -3:
            judge_180_count += 1
            ##这两个细胞块数值接收不到
            print("judge_180_count:", judge_180_count)
        elif flag_index == -4:
            judge_inner_angle_count += 1
            #print("judge_inner_angle_count:", judge_inner_angle_count)



        if not move_flag:  # 经判断，该点无法退火
            continue
        # print(annealing_rate)
        # 移动 move
        cb.cell1.points[cb.index1] = [move_point.x, move_point.y]
        cb.cell2.points[cb.index2] = [move_point.x, move_point.y]
        cb.cell3.points[cb.index3] = [move_point.x, move_point.y]
        cb.cell1.setVertex()
        cb.cell2.setVertex()
        cb.cell3.setVertex()


    # 计算实际退火细胞块总数（正确的方法）
    actual_annealed_cell_blocks = edge_annealing_points + inner_annealing_points
    # 输出相关信息 Output relevant information
    print("一次退火完成，本次退火相关信息如下：")
    print("应退火细胞块总数：{0}，实际退火细胞块总数：{1},实际退火的边缘顶点{2},实际退火的内部顶点{3}".format(
        now_count,
        #now_count - edge_count - need_not_count - best_count - judge_180_count - judge_inner_angle_count
        actual_annealed_cell_blocks
        , edge_annealing_points,
        inner_annealing_points
    ))

    # 与 AnnealingGUI.Annealer 约定：元组第二项为内外退火顶点数，供统计面板等使用
    annealing_count = now_count - edge_count - need_not_count - best_count - judge_180_count - judge_inner_angle_count
    stats = {
        'edge_vertices': edge_annealing_points,
        'internal_vertices': inner_annealing_points,
    }
    return annealing_count, stats

def move_point_after(intersection_cell_blocks, annealing_rate, edge_judge, flag, cells):
    # """修改后的退火移动函数，增加统计功能"""

    # # 初始化统计管理器
    # if stats_manager is None:
    #     #stats_manager = AnnealingStatistics()
    #     stats_manager = annealing_statistics()

    count = 0
    now_count = 0
    edge_count = 0
    need_not_count = 0
    best_count = 0
    judge_180_count = 0
    judge_inner_angle_count = 0
    edge_vertices_moved = 0
    internal_vertices_moved = 0

    # 使用退火距离排序
    pending = sort_cells_by_distance(intersection_cell_blocks, cells)

    # 移动交汇点（实时更新剩余块的退火距离并重排）
    while pending:
        info = pending.pop(0)
        cb = info['cell_block']
        # annealing_rate = get_annealing_rate(cb) # 根据角度计算速率 （已弃用）
        count += 1  # 总数+1 Total + 1

        # 取消奇偶序号细胞块判断
        # if flag:
        #     if count % 2 == 0:
        #         continue
        # else:
        #     if not count % 2 == 0:
        #         continue


        now_count += 1  # 当前总数+1 Current total + 1

        # if edge_judge:
        #     # 边缘细胞是否需要参与退火 Do marginal cells need to participate in annealing
        #     if not cb.cell1.ok or not cb.cell2.ok or not cb.cell3.ok:
        #         edge_count += 1
        #         continue
        if edge_judge:
            #print("记录到边缘进行移动01")
            if (cb.cell1.layer == 1 and cb.cell2.layer == 1) \
                    or (cb.cell1.layer == 1 and cb.cell3.layer == 1) \
                    or (cb.cell2.layer == 1 and cb.cell3.layer == 1):

                # now_count -= 1
                edge_move_point = get_edge_move_point(cb, annealing_rate, cells)
                if edge_move_point > 0:
                    edge_vertices_moved += 1
                    print("统计到边缘退火顶点")
                    edge_count += 1
                    pending = sort_cells_by_distance([i['cell_block'] for i in pending], cells)
                    continue
                # print(edge_move_point)
                # print("ppp", ppp)
                # if ppp in cb.cell1.points:
                #     print("true")
                # else:
                #     print("false")
                # continue  # todo::需要再修改


        # print(10)
        point_g = cb.getTriCentreOfGravity()


        # 退火速率按用户输入与 k_R 组合，不再使用旧的循环策略

        '''
        根据用户输入设置退火速率
        '''
        move_flag = False
        move_point = get_point_of_destination(cb.cell1.points[cb.index1], point_g, annealing_rate)
        flag_index = judge_if_annealing(cb, move_point)
        if flag_index == 0:  # 如果可以移动，则返回true
            move_flag = True
        elif flag_index == -1:
            best_count += 1
        elif flag_index == -2:
            need_not_count += 1
        elif flag_index == -3:
            judge_180_count += 1
        elif flag_index == -4:
            judge_inner_angle_count += 1

        # '''
        # 根据用户输入设置退火速率
        # '''
        # move_flag = False
        # move_point = get_point_of_destination(cb.cell1.points[cb.index1], point_g, annealing_rate * k_R)
        # flag_index = judge_if_annealing(cb, move_point)
        # if flag_index == 0:
        #     candidate = [move_point.x, move_point.y]
        #     safe = (
        #         is_vertex_angle_safe(cb.cell1, cb.index1, candidate) and
        #         is_neighbors_angles_safe(cb.cell1, cb.index1, candidate) and

        #         is_vertex_angle_safe(cb.cell2, cb.index2, candidate) and
        #         is_neighbors_angles_safe(cb.cell2, cb.index2, candidate) and

        #         is_vertex_angle_safe(cb.cell3, cb.index3, candidate) and
        #         is_neighbors_angles_safe(cb.cell3, cb.index3, candidate)
        #     )
        #     if safe:
        #         move_flag = True
        #     else:
        #         judge_180_count += 1
        # elif flag_index == -1:
        #     best_count += 1
        # elif flag_index == -2:
        #     need_not_count += 1
        # elif flag_index == -3:
        #     judge_180_count += 1
        # elif flag_index == -4:
        #     judge_inner_angle_count += 1

        #print("进行退火判断测试01")

        if not move_flag:  # 经判断，该点无法退火
            #print("进行退火判断测试02")
            continue

        # if move_flag:  # 经判断，该点无法退火
        #     continue
        # print(annealing_rate)
        # 移动 move
        #print("进行退火判断测试03")
        cb.cell1.points[cb.index1] = [move_point.x, move_point.y]
        cb.cell2.points[cb.index2] = [move_point.x, move_point.y]
        cb.cell3.points[cb.index3] = [move_point.x, move_point.y]
        cb.cell1.setVertex()
        cb.cell2.setVertex()
        cb.cell3.setVertex()
        #internal_vertices_moved += 1
        pending = sort_cells_by_distance([i['cell_block'] for i in pending], cells)
        #print("进行退火判断测试04")

    # 输出相关信息 Output relevant information
    print("一次退火完成，本次退火相关信息如下：")
    print("应退火细胞块总数：{0}，实际退火细胞块总数：{1},实际退火的边缘顶点{2},实际退火的内部顶点{3}".format(
        now_count,
        now_count - edge_count - need_not_count - best_count - judge_180_count - judge_inner_angle_count
        , edge_vertices_moved,
        internal_vertices_moved
    ))
    # return (
    #     now_count - edge_count - need_not_count - best_count - judge_180_count - judge_inner_angle_count,
    #     {'edge_vertices': edge_vertices_moved, 'internal_vertices': internal_vertices_moved}
    # )


def move_point_temp(intersection_cell_blocks, annealing_rate, edge_judge, flag, cells, stats_manager=None, round_number=0):
    """修改后的退火移动函数，增加统计功能"""

    # # 初始化统计管理器
    # if stats_manager is None:
    #     stats_manager = AnnealingStatistics()

    # 统计顶点类型
    # stats_manager.count_vertex_types(cells, intersection_cell_blocks)

    count = 0
    now_count = 0
    edge_count = 0
    need_not_count = 0
    best_count = 0
    judge_180_count = 0
    judge_inner_angle_count = 0

    # 记录本轮被退火的顶点
    annealed_vertices_this_round = set()

    # 在这里对intersection_cell_blocks进行排序
    # sort_intersection_cell_blocks(intersection_cell_blocks)

    # 移动交汇点
    for cb in intersection_cell_blocks:
        count += 1
        now_count += 1

        # 记录当前顶点
        current_vertex = tuple(cb.cell1.points[cb.index1])
        vertex_type = stats_manager.vertex_type_dict.get(current_vertex, "unknown")

        if edge_judge:
            if (cb.cell1.layer == 1 and cb.cell2.layer == 1) or \
               (cb.cell1.layer == 1 and cb.cell3.layer == 1) or \
               (cb.cell2.layer == 1 and cb.cell3.layer == 1):

                edge_move_point = get_edge_move_point(cb, annealing_rate, cells)
                if edge_move_point > 0:
                    edge_count += 1
                    annealed_vertices_this_round.add(current_vertex)
                    continue

        point_g = cb.getTriCentreOfGravity()
        move_point = get_point_of_destination(cb.cell1.points[cb.index1], point_g, annealing_rate)
        flag_index = judge_if_annealing(cb, move_point)

        if flag_index == 0:
            # 移动顶点
            cb.cell1.points[cb.index1] = [move_point.x, move_point.y]
            cb.cell2.points[cb.index2] = [move_point.x, move_point.y]
            cb.cell3.points[cb.index3] = [move_point.x, move_point.y]
            cb.cell1.setVertex()
            cb.cell2.setVertex()
            cb.cell3.setVertex()

            # 记录被退火的顶点
            annealed_vertices_this_round.add(current_vertex)
        else:
            if flag_index == -1:
                best_count += 1
            elif flag_index == -2:
                need_not_count += 1
            elif flag_index == -3:
                judge_180_count += 1
            elif flag_index == -4:
                judge_inner_angle_count += 1

    # 更新统计信息
    actual_annealed_count = len(annealed_vertices_this_round)
    stats_manager.update_annealing_count(actual_annealed_count)

    # 打印详细统计信息
    print(f"\n=== 第{round_number}轮退火详细统计 ===")
    print(f"应退火细胞块总数: {now_count}")
    print(f"实际退火细胞块总数: {actual_annealed_count}")
    print(f"边缘退火细胞块数: {edge_count}")
    print(f"已达最优细胞块数: {best_count}")
    print(f"无需退火细胞块数: {need_not_count}")
    print(f"几何约束拒绝数: {judge_180_count}")
    print(f"内角优化拒绝数: {judge_inner_angle_count}")

    # 打印顶点类型统计
    stats_manager.print_statistics(round_number)

    return actual_annealed_count, stats_manager

def move_point_last02(intersection_cell_blocks, annealing_rate, edge_judge, flag, cells):
    count = 0  # 待退火细胞块总数 Total number of cell blocks to be annealed
    now_count = 0  # 当前待退火细胞块总数 Total number of cell blocks to be returned
    edge_count = 0  # 边缘细胞块总数 Total number of marginal cell blocks
    need_not_count = 0  # 不需要退火细胞块总数 Total number of cell blocks not required to be annealed
    best_count = 0  # 接近最优退火细胞块总数 The total number of cell blocks was close to the optimal annealing
    judge_180_count = 0  # 退火后不满足凸多边形的细胞块总数 Total number of cell blocks not meeting convex polygon after annealing
    judge_inner_angle_count = 0  # 退火后内角平方和会增大的细胞块总数 The total number of cell blocks increased after annealing

    # 在这里对intersection_cell_blocks进行一个排序 Here, the cross section_ cell_ Blocks to sort
    sort_intersection_cell_blocks(intersection_cell_blocks)

    # 移动交汇点 move intersection
    for cb in intersection_cell_blocks:
        # annealing_rate = get_annealing_rate(cb) # 根据角度计算速率 （已弃用）
        count += 1  # 总数+1 Total + 1

        # 取消奇偶序号细胞块判断
        # if flag:
        #     if count % 2 == 0:
        #         continue
        # else:
        #     if not count % 2 == 0:
        #         continue


        now_count += 1  # 当前总数+1 Current total + 1

        # if edge_judge:
        #     # 边缘细胞是否需要参与退火 Do marginal cells need to participate in annealing
        #     if not cb.cell1.ok or not cb.cell2.ok or not cb.cell3.ok:
        #         edge_count += 1
        #         continue
        if edge_judge:
            # 细胞块边缘是否需要参与退火
            # if not cb.cell1.layer == 1 or not cb.cell2.layer == 1 or not cb.cell3.layer == 1:
            # if cb.cell1.layer + cb.cell2.layer + cb.cell3.layer == 2:
            if (cb.cell1.layer == 1 and cb.cell2.layer == 1) \
                    or (cb.cell1.layer == 1 and cb.cell3.layer == 1) \
                    or (cb.cell2.layer == 1 and cb.cell3.layer == 1):

                # now_count -= 1
                edge_move_point = get_edge_move_point(cb, annealing_rate, cells)
                if edge_move_point > 0:
                    # print(edge_move_point)
                    edge_count += 1  # TODO::暂时不考虑这个变量
                    continue
                # print(edge_move_point)
                # print("ppp", ppp)
                # if ppp in cb.cell1.points:
                #     print("true")
                # else:
                #     print("false")
                # continue  # todo::需要再修改

        # print(10)
        point_g = cb.getTriCentreOfGravity()


        '''
        根据角度判断标准，循环设置退火速率（已弃用）
        '''
        # annealing_rate_list = [0.1, 0.06, 0.03, 0.02, 0.01]
        # move_flag = False
        # while True:
        #     move_point = get_point_of_destination(cb.cell1.points[cb.index1], point_g, annealing_rate)
        #     flag_index = judge_if_annealing(cb, move_point)
        #     if flag_index == 0:  # 如果可以移动，则直接退出循环
        #         move_flag = True
        #         break
        #     if annealing_rate == 0.01:  # 如果循环到最后也不可移动，则返回False
        #         if flag_index == -1:
        #             best_count += 1
        #         elif flag_index == -2:
        #             need_not_count += 1
        #         elif flag_index == -3:
        #             judge_180_count += 1
        #         elif flag_index == -4:
        #             judge_inner_angle_count += 1
        #         move_flag = False
        #         break
        #
        #     annealing_rate = annealing_rate_list[annealing_rate_list.index(annealing_rate)+1]  # 改变退火速率，重新判断

        '''
        根据用户输入设置退火速率
        '''
        move_flag = False
        move_point = get_point_of_destination(cb.cell1.points[cb.index1], point_g, annealing_rate)
        flag_index = judge_if_annealing(cb, move_point)
        if flag_index == 0:  # 如果可以移动，则返回true
            move_flag = True
        elif flag_index == -1:
            best_count += 1
        elif flag_index == -2:
            need_not_count += 1
        elif flag_index == -3:
            judge_180_count += 1
        elif flag_index == -4:
            judge_inner_angle_count += 1



        if not move_flag:  # 经判断，该点无法退火
            continue
        # print(annealing_rate)
        # 移动 move
        cb.cell1.points[cb.index1] = [move_point.x, move_point.y]
        cb.cell2.points[cb.index2] = [move_point.x, move_point.y]
        cb.cell3.points[cb.index3] = [move_point.x, move_point.y]
        cb.cell1.setVertex()
        cb.cell2.setVertex()
        cb.cell3.setVertex()

    # 输出相关信息 Output relevant information
    print("一次退火完成，本次退火相关信息如下：")
    print("应退火细胞块总数：{0}，实际退火细胞块总数：{1}".format(now_count,
                                            now_count - edge_count - need_not_count - best_count - judge_180_count - judge_inner_angle_count))

    # 返回实际退火的细胞块总数 Returns the total number of cell blocks actually annealed
    return now_count - edge_count - need_not_count - best_count - judge_180_count - judge_inner_angle_count