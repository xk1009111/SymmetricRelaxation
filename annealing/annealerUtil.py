import math
from utillib.mylib import Point, Line, Line_in_Polar_Coordinate_System, CellBlock
from cell.CellData import CellData
k_R = 0.1
k_D = 1.0
##正式的代码修改
# from cell.annealing_statistics import annealing_statistics

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






'''
    获取退火细胞块中的最大内角
    Obtain the maximum internal angle in the annealed cell block
    :param cb: 退火细胞块 Annealed cell block
    :return: 最大内角 Maximum internal angle
'''




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




'''
    自动计算边缘退火速率
    :param cb: 退火细胞块 Annealed cell block
    :return : 退火速率 Annealing rate
'''




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
    # 如果当前顶点已在三角形内部，则接近最优，不移动
    # If the current vertex is already inside the triangle, it is near optimal, do not move
    if is_point_in_triangle(cb.cell1.points[cb.index1], cb.triangle):
        return -1

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
    :param marginalcell1, marginalcell2: 退火细胞块两个边缘细胞
    :param move_point: 移动目标点
    :return : 判断标记
'''


#保证移动之后边缘细胞还是稳定的


'''
    获取线段与直线的交点
    :param x1: 所求细胞的中心X坐标
    :param y1: 所求细胞的中心Y坐标
    :param line: 直线方程
    :param p1: 线段端点坐标1
    :param p2: 线段端点坐标2
    :return : 返回交点坐标，如果没有交点，则返回None
'''




'''
    计算边缘退火移动目标点
    :param cb: 边缘退火细胞块
    :return move_point: 边缘退火移动目标点
'''


#{"variant":"standard","title":"is_vertex_angle_safe_01","id":"90211"}
#------------------------------------
#-------------------------
#~~~{"variant":"standard","title":"is_vertex_angle_safe_03（改进）","id":"70192"}


#-------------------------
#-------------------------

#修改边缘细胞的退火方法为：每个边缘顶点对应两个边缘角，将当前边缘顶点V沿较小边缘角的边缘边移动到目的地点P，使得两个边缘角相等,

def get_all_marginal_points(cells):
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

    all_marginal_points = []
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
                    all_marginal_points.append(p)
                    break

    return all_marginal_points

def find_marginal_key_points_new(point_v, cells):
    """
    按照新逻辑找关键点：V -> A, B -> marginal_cell1, marginal_cell2 -> O

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
            'marginal_cell1': marginal_cell1,
            'marginal_cell2': marginal_cell2,
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
    all_marginal_points = []
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
                    all_marginal_points.append(p)
                    break

    if len(all_marginal_points) < 3:  # 至少需要V、A、B三个边缘顶点
        print(f"[FindKeyPoints] 边缘顶点数量不足（{len(all_marginal_points)}），无法进行边缘退火")
        return None

    # 验证point_v是否是边缘顶点
    v_is_marginal_point = False
    for marginal_point in all_marginal_points:
        if points_equal(marginal_point, point_v):
            v_is_marginal_point = True
            break

    if not v_is_marginal_point:
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
    marginal_cell1 = None
    marginal_cell2 = None
    idx_va = None
    idx_vb = None

    marginal_points_as_neighbors = []
    for marginal_point in all_marginal_points:
        # 跳过V本身
        if points_equal(marginal_point, point_v):
            continue

        # 检查这个边缘顶点是否是V的邻点
        marginal_point_key = tuple(marginal_point) if isinstance(marginal_point, (list, tuple)) else marginal_point
        if marginal_point_key in v_neighbors:
            # 找到包含这条边（V-marginal_point）的细胞
            for cell in cells_with_v:
                v_idx = v_indices[cell]
                n = len(cell.points)
                prev_point = cell.points[(v_idx - 1) % n]
                next_point = cell.points[(v_idx + 1) % n]

                # 检查marginal_point是否是V的邻点
                if points_equal(prev_point, marginal_point) or points_equal(next_point, marginal_point):
                    # 确保这个细胞是边缘细胞（layer == 1）
                    if cell.layer == 1:
                        marginal_points_as_neighbors.append({
                            'point': marginal_point,
                            'cell': cell,
                            'v_idx': v_idx,
                            'neighbor_idx': (v_idx - 1) % n if points_equal(prev_point, marginal_point) else (v_idx + 1) % n
                        })
                        break

    # 找到两个不同的边缘顶点A和B（来自不同的边缘细胞）
    if len(marginal_points_as_neighbors) < 2:
        print(f"[FindKeyPoints] 找不到两个与V构成边缘边的边缘顶点（找到{len(marginal_points_as_neighbors)}个），V点坐标: ({point_v[0]:.6f}, {point_v[1]:.6f})")
        return None

    # 选择第一个作为A
    edge_info_a = marginal_points_as_neighbors[0]
    point_a = edge_info_a['point']
    marginal_cell1 = edge_info_a['cell']
    idx_va = edge_info_a['v_idx']

    # 找到来自不同细胞的第二个边缘顶点作为B
    edge_info_b = None
    for edge_info in marginal_points_as_neighbors[1:]:
        if edge_info['cell'] != marginal_cell1 and not points_equal(edge_info['point'], point_a):
            edge_info_b = edge_info
            break

    if edge_info_b is None:
        print(f"[FindKeyPoints] 找不到来自不同细胞的第二个边缘顶点B，V点坐标: ({point_v[0]:.6f}, {point_v[1]:.6f})")
        return None

    point_b = edge_info_b['point']
    marginal_cell2 = edge_info_b['cell']
    idx_vb = edge_info_b['v_idx']

    # Step 4: 由于AV和VB是边缘边，可以映射到两个边缘几何体（edge_cell1和edge_cell2）
    # 这一步已经在上面完成，edge_cell1包含AV边，edge_cell2包含VB边

    # Step 5: 检索V的邻点，找到除V以外被两个目标几何体（edge_cell1和edge_cell2）共有的点，那就是O
    point_o = None
    idx_oa = None
    idx_ob = None

    # 获取edge_cell1中V的所有邻点
    n1 = len(marginal_cell1.points)
    v_idx_in_cell1 = idx_va
    neighbors_in_cell1 = [
        marginal_cell1.points[(v_idx_in_cell1 - 1) % n1],  # 前一个邻点
        marginal_cell1.points[(v_idx_in_cell1 + 1) % n1]   # 后一个邻点
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
        for i, p in enumerate(marginal_cell2.points):
            if points_equal(p, neighbor):
                neighbor_in_cell2 = True
                neighbor_idx_in_cell2 = i
                break

        if neighbor_in_cell2:
            # 验证这个邻点在edge_cell2中是否与V相邻（确保V-O是edge_cell2的一条边）
            n2 = len(marginal_cell2.points)
            v_idx_in_cell2 = idx_vb
            prev_neighbor_in_cell2 = marginal_cell2.points[(neighbor_idx_in_cell2 - 1) % n2]
            next_neighbor_in_cell2 = marginal_cell2.points[(neighbor_idx_in_cell2 + 1) % n2]

            # 如果V是这个邻点的相邻点，则这是共边，邻点就是O
            if points_equal(prev_neighbor_in_cell2, point_v) or points_equal(next_neighbor_in_cell2, point_v):
                point_o = neighbor
                # 找到O在edge_cell1中的索引
                for i, p in enumerate(marginal_cell1.points):
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
        'marginal_cell1': marginal_cell1,
        'marginal_cell2': marginal_cell2,
        'idx_va': idx_va,
        'idx_vb': idx_vb,
        'idx_oa': idx_oa,
        'idx_ob': idx_ob
    }

#----------------------------------------------------------------------
def calculate_marginal_annealing_distance(point_v, cells):
    """
    计算边缘顶点的退火距离（不实际移动，只计算距离）
    距离 = V到目标点的欧氏距离（不乘退火速率），用于统一排序

    参数:
        point_v: 边缘顶点V [x, y]
        cells: 所有细胞列表

    返回:
        float: 退火距离，如果无法计算则返回0
    """
    import math

    # 使用新逻辑找关键点
    key_points = find_marginal_key_points_new(point_v, cells)
    if key_points is None:
        return 0.0

    point_a = key_points['point_a']
    point_b = key_points['point_b']
    point_o = key_points['point_o']
    marginal_cell1 = key_points['marginal_cell1']
    marginal_cell2 = key_points['marginal_cell2']

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
    is_triangle_geometry = (len(marginal_cell1.points) == 3 or len(marginal_cell2.points) == 3)

    # 根据几何体形状设置不同的退火阈值
    if is_triangle_geometry:
        angle_threshold = math.radians(60)  # 至少有一个三角形几何体，使用60度阈值
        print(f"[Shape] 检测到至少一个三角形几何体 (marginal_cell1: {len(marginal_cell1.points)}边, marginal_cell2: {len(marginal_cell2.points)}边)，使用60度阈值")
    else:
        angle_threshold = math.radians(20)  # 两个都不是三角形，使用20度阈值
        print(f"[Shape] 两个边缘几何体都不是三角形 (marginal_cell1: {len(marginal_cell1.points)}边, marginal_cell2: {len(marginal_cell2.points)}边)，使用20度阈值")

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

    # 计算退火距离（从V到目标点的距离，不乘退火速率，统一用于排序）
    distance = get_distance_point_point_by_list(point_v, target_point)

    return distance

def get_marginal_move_point(point_v, annealing_rate, cells):
    """
    边缘退火逻辑（直接从边缘顶点V开始）：
    1. 输入边缘顶点V（必须是边缘顶点，即只被2个细胞共享）
    2. 使用新逻辑找关键点：V -> A, B -> marginal_cell1, marginal_cell2 -> O
       - A、B必须是边缘顶点（只被2个细胞共享）
    3. 计算两边缘角 A-V-O 与 B-V-O，决定退火方向
    4. candidate_V 生成
    5. O 点安全检查（只检查 V-O 在 cell 中相邻的 cell）
       * 使用凸角规范化（防止 2π 误判 180°）
    6. 移动成功 → 更新两个边缘 cell 中的 V
    """
    import math


    #----------------------------------------
    # Step 1：使用新逻辑找关键点（V -> A, B -> marginal_cell1, marginal_cell2 -> O）
    #----------------------------------------
    key_points = find_marginal_key_points_new(point_v, cells)

    point_a = key_points['point_a']
    point_b = key_points['point_b']
    point_o = key_points['point_o']
    marginal_cell1 = key_points['marginal_cell1']
    marginal_cell2 = key_points['marginal_cell2']
    idx_va = key_points['idx_va']
    idx_vb = key_points['idx_vb']
    idx_oa = key_points['idx_oa']
    idx_ob = key_points['idx_ob']

    # point_a = cell_a.points[(idx_va - 1) % len(cell_a.points)]
    # point_b = cell_b.points[(idx_vb - 1) % len(cell_b.points)]

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
    is_triangle_geometry = (len(marginal_cell1.points) == 3 or len(marginal_cell2.points) == 3)

    # 根据几何体形状设置不同的退火阈值
    if is_triangle_geometry:
        angle_threshold = math.radians(60)  # 至少有一个三角形几何体，使用60度阈值
        print(f"[Shape] 检测到至少一个三角形几何体 (marginal_cell1: {len(marginal_cell1.points)}边, marginal_cell2: {len(marginal_cell2.points)}边)，使用60度阈值")
    else:
        angle_threshold = math.radians(20)  # 两个都不是三角形，使用20度阈值
        print(f"[Shape] 两个边缘几何体都不是三角形 (marginal_cell1: {len(marginal_cell1.points)}边, marginal_cell2: {len(marginal_cell2.points)}边)，使用20度阈值")

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
    # Step 6.5：退火后凸性检查（两个边缘细胞必须仍为凸多边形）
    #----------------------------------------
    if not is_cell_convex_after_move(marginal_cell1, idx_va, candidate_V):
        print("[ConvexCheck STOP] 退火后 marginal_cell1 非凸，跳过该顶点")
        print()  # 区分不同顶点的退火
        return 0
    if not is_cell_convex_after_move(marginal_cell2, idx_vb, candidate_V):
        print("[ConvexCheck STOP] 退火后 marginal_cell2 非凸，跳过该顶点")
        print()  # 区分不同顶点的退火
        return 0

    #----------------------------------------
    # Step 7：真正更新两个边缘 cell 的顶点 V
    #----------------------------------------
    marginal_cell1.points[idx_va] = candidate_V
    marginal_cell2.points[idx_vb] = candidate_V
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


#------------------------------------------------------------
















def move_point(intersection_cell_blocks, annealing_rate, marginal_point_judge, cells):
    """
    退火移动函数（统一队列版）：
    1. 统一收集 marginal points（边缘顶点）和 inner points（内部顶点）
    2. 按退火距离 D 降序排序（一次排序，本轮不变）
    3. 依序遍历：
       - marginal: 移动前重算 D_current，若 <=0 跳过；否则执行边缘退火
       - inner: 不加距离跳过，仅靠 judge_if_annealing 判断
    返回: (annealing_count, stats_dict)
    """
    count = 0  # 待退火细胞块总数 Total number of cell blocks to be annealed
    now_count = 0  # 当前待退火细胞块总数 Total number of cell blocks to be returned
    marginal_count = 0  # 边缘细胞块总数 Total number of marginal cell blocks
    best_count = 0  # 接近最优退火细胞块总数 The total number of cell blocks was close to the optimal annealing
    judge_180_count = 0  # 退火后不满足凸多边形的细胞块总数 Total number of cell blocks not meeting convex polygon after annealing
    judge_inner_angle_count = 0  # 退火后内角平方和会增大的细胞块总数 The total number of cell blocks increased after annealing
    marginal_annealing_points = 0
    inner_annealing_points = 0

    # 如果边缘退火开启，输出一次所有边缘顶点信息
    if marginal_point_judge:
        all_marginal_points = get_all_marginal_points(cells)
        print(f"[MarginalPoints] 全部边缘顶点个数: {len(all_marginal_points)}")
        print(f"[MarginalPoints] 边缘顶点坐标列表:")
        for i, vertex in enumerate(all_marginal_points):
            print(f"  [{i+1}] ({vertex[0]:.6f}, {vertex[1]:.6f})")

    # ============================================================
    # Step 1: 统一收集所有顶点（marginal + inner）到队列
    # ============================================================
    vertex_queue = []

    # 收集 marginal points（边缘顶点）
    if marginal_point_judge:
        all_marginal_points = get_all_marginal_points(cells)
        for point_v in all_marginal_points:
            D = calculate_marginal_annealing_distance(point_v, cells)
            vertex_queue.append({
                'type': 'marginal',
                'point': point_v,
                'distance': D
            })

    # 收集 inner points（内部顶点，来自 intersection_cell_blocks）
    for cb in intersection_cell_blocks:
        point_g = cb.getTriCentreOfGravity()  # Point 对象
        current_point = cb.cell1.points[cb.index1]  # 列表 [x, y]
        # point_g 是 Point 对象（有 .x .y），不能用 [] 索引
        D = math.sqrt((current_point[0] - point_g.x) ** 2 + (current_point[1] - point_g.y) ** 2)
        vertex_queue.append({
            'type': 'inner',
            'cb': cb,
            'distance': D
        })

    # ============================================================
    # Step 2: 按退火距离 D 降序排序（一次排序，本轮不变）
    # ============================================================
    vertex_queue.sort(key=lambda x: x['distance'], reverse=True)

    # ============================================================
    # Step 3: 依序遍历，执行退火
    # ============================================================
    for item in vertex_queue:
        if item['type'] == 'marginal':
            # marginal point：移动前重算退火距离（使用最新坐标）
            point_v = item['point']
            current_distance = calculate_marginal_annealing_distance(point_v, cells)
            # 如果距离为0，说明不需要退火，跳过
            if current_distance <= 0:
                continue
            # 执行边缘退火
            marginal_move_result = get_marginal_move_point(point_v, annealing_rate, cells)
            if marginal_move_result > 0:
                marginal_annealing_points += 1
        else:
            # inner point：不加距离跳过，仅靠 judge_if_annealing 判断
            cb = item['cb']
            count += 1  # 总数+1 Total + 1
            now_count += 1  # 当前总数+1 Current total + 1

            # 重新获取重心（使用最新坐标）
            point_g = cb.getTriCentreOfGravity()

            move_flag = False
            move_point_result = get_point_of_destination(cb.cell1.points[cb.index1], point_g, annealing_rate)
            flag_index = judge_if_annealing(cb, move_point_result)
            if flag_index == 0:  # 如果可以移动，则返回true
                move_flag = True
                inner_annealing_points += 1
            elif flag_index == -1:
                best_count += 1
            elif flag_index == -3:
                judge_180_count += 1
                print("judge_180_count:", judge_180_count)
            elif flag_index == -4:
                judge_inner_angle_count += 1

            if not move_flag:  # 经判断，该点无法退火
                continue
            # 移动 move
            cb.cell1.points[cb.index1] = [move_point_result.x, move_point_result.y]
            cb.cell2.points[cb.index2] = [move_point_result.x, move_point_result.y]
            cb.cell3.points[cb.index3] = [move_point_result.x, move_point_result.y]
            cb.cell1.setVertex()
            cb.cell2.setVertex()
            cb.cell3.setVertex()

    # 计算实际退火细胞块总数（正确的方法）
    actual_annealed_cell_blocks = marginal_annealing_points + inner_annealing_points
    # 输出相关信息 Output relevant information
    print("一次退火完成，本次退火相关信息如下：")
    print("应退火细胞块总数：{0}，实际退火细胞块总数：{1},实际退火的边缘顶点{2},实际退火的内部顶点{3}".format(
        now_count,
        actual_annealed_cell_blocks,
        marginal_annealing_points,
        inner_annealing_points
    ))

    # 与 AnnealingGUI.Annealer 约定：元组第二项为内外退火顶点数，供统计面板等使用
    annealing_count = now_count - marginal_count - best_count - judge_180_count - judge_inner_angle_count
    stats = {
        'marginal_points': marginal_annealing_points,
        'inner_points': inner_annealing_points,
    }
    return annealing_count, stats
