import math
from utillib.mylib import Point, Line, Line_in_Polar_Coordinate_System, CellBlock, get_distance_point_point, angle_by_three_points

"""
    计算两点之间的距离(根据公式进行计算)
    Calculate the distance between two points (according to the formula)
    :param p1: Point对象 Point object
    :param p2: Point对象 Point object
    :return: 距离 distance
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

    return intersection_cell_blocks


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

    return [point1, point2, point3]


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
    if math.fabs(judge_param) < 1e-10:  # 一旦某个点在线上，则不可移动 Once a point is on the line, it cannot be moved
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

    angle1 = angle_by_three_points(cb.cell1.points[(cb.index1 - 1)], cb.cell1.points[(cb.index1)],
                                   cb.cell1.points[(cb.index1 + 1) % len_points1])
    angle2 = angle_by_three_points(cb.cell2.points[(cb.index2 - 1)], cb.cell2.points[(cb.index2)],
                                   cb.cell2.points[(cb.index2 + 1) % len_points2])
    angle3 = angle_by_three_points(cb.cell3.points[(cb.index3 - 1)], cb.cell3.points[(cb.index3)],
                                   cb.cell3.points[(cb.index3 + 1) % len_points3])

    # 计算移动之前的内角平方和 Calculate the sum of squares of interior angles before moving
    be_sia = angle1 * angle1
    be_sia += angle2 * angle2
    be_sia += angle3 * angle3

    # 计算移动之后的内角平方和 Calculate the sum of squares of interior angles after moving
    af_angle1 = angle_by_three_points(cb.cell1.points[(cb.index1 - 1)], (mp.x, mp.y),
                                      cb.cell1.points[(cb.index1 + 1) % len_points1])
    af_angle2 = angle_by_three_points(cb.cell2.points[(cb.index2 - 1)], (mp.x, mp.y),
                                      cb.cell2.points[(cb.index2 + 1) % len_points2])
    af_angle3 = angle_by_three_points(cb.cell3.points[(cb.index3 - 1)], (mp.x, mp.y),
                                      cb.cell3.points[(cb.index3 + 1) % len_points3])
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


# ---------------------------------------------------------------------------
# 模块级辅助函数（供多处复用，避免在嵌套函数中重复定义）
# ---------------------------------------------------------------------------

def points_equal(p1, p2, tolerance=1e-9):
    """判断两个点是否相等（考虑浮点误差），支持 list/tuple 格式的点坐标"""
    if isinstance(p1, (list, tuple)) and isinstance(p2, (list, tuple)):
        return abs(p1[0] - p2[0]) < tolerance and abs(p1[1] - p2[1]) < tolerance
    return False


#修改边缘细胞的退火方法为：每个边缘顶点对应两个边缘角，将当前边缘顶点V沿较小边缘角的边缘边移动到目的地点P，使得两个边缘角相等,

def get_all_marginal_points(cells):
    """
    获取所有边缘顶点（只被两个细胞共享的顶点）

    参数:
        cells: 所有细胞列表

    返回:
        list: 所有边缘顶点的列表 [[x, y], ...]
    """
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
        float: 退火距离
    """

    # 使用新逻辑找关键点
    key_points = find_marginal_key_points_new(point_v, cells)

    point_a = key_points['point_a']
    point_b = key_points['point_b']
    point_o = key_points['point_o']

    # 计算两边缘角
    angle_AVO = angle_by_three_points(point_a, point_v, point_o)
    angle_BVO = angle_by_three_points(point_b, point_v, point_o)

    # 确定目标点（向较小角方向移动）
    # 目标点修改为当前点V和邻点（A或B）的中点
    if angle_AVO < angle_BVO:
        # 使用V和A的中点A'作为目标点
        target_point = [(point_v[0] + point_a[0]) / 2, (point_v[1] + point_a[1]) / 2]
    else:
        # 使用V和B的中点B'作为目标点
        target_point = [(point_v[0] + point_b[0]) / 2, (point_v[1] + point_b[1]) / 2]

    # 计算退火距离（从V到目标点的距离，不乘退火速率，统一用于排序）
    distance = get_distance_point_point(point_v, target_point)

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

    # 输出调试信息：先输出V点坐标，再换行输出A,B,O的坐标信息
    print(f"V点坐标: ({point_v[0]:.6f}, {point_v[1]:.6f})")
    print(f"A点坐标: ({point_a[0]:.6f}, {point_a[1]:.6f}), B点坐标: ({point_b[0]:.6f}, {point_b[1]:.6f}), O点坐标: ({point_o[0]:.6f}, {point_o[1]:.6f})")

    #----------------------------------------
    # Step 4：计算两边缘角
    #----------------------------------------
    # 使用简单的向量夹角计算，避免凹角误判

    # 辅助函数：将弧度转换为角度（度）
    def rad_to_deg_display(angle_rad):
        """将弧度转换为角度（度）。angle_by_three_points 恒返回 ≤180°，无需归一化。"""
        return math.degrees(angle_rad)

    angle_AVO = angle_by_three_points(point_a, point_v, point_o)
    angle_BVO = angle_by_three_points(point_b, point_v, point_o)

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
    angle_AVO = angle_by_three_points(point_a, candidate_V, point_o)
    angle_BVO = angle_by_three_points(point_b, candidate_V, point_o)

    # 转换为角度值并格式化输出
    aov_deg_after = rad_to_deg_display(angle_AVO)
    vob_deg_after = rad_to_deg_display(angle_BVO)
    print(f"after: AOV_after={aov_deg_after:.6f}°, VOB_after={vob_deg_after:.6f}°")
    #打印空行
    print()
    return 1

#-------------------------------------------------


#------------------------------------------------------------
















def move_point(intersection_cell_blocks, annealing_rate, marginal_point_judge, cells):
    """
    退火移动函数（统一队列版）：
    1. 统一收集 marginal points（边缘顶点）和 inner points（内部顶点）
    2. 按退火距离 D 降序排序（一次排序，本轮不变）
    3. 依序遍历：
       - marginal: 执行边缘退火（角度阈值与凸性由 get_marginal_move_point 把关）
       - inner: 仅靠 judge_if_annealing 判断
    返回: (annealing_count, stats_dict)
    """
    now_count = 0  # 当前待退火细胞块总数 Total number of cell blocks to be returned
    judge_180_count = 0  # 退火后不满足凸多边形的细胞块总数 Total number of cell blocks not meeting convex polygon after annealing
    marginal_annealing_points = 0
    inner_annealing_points = 0

    # 如果边缘退火开启，收集并输出所有边缘顶点信息（结果在下方收集阶段复用）
    all_marginal_points = None
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
            # marginal point：执行边缘退火（角度阈值与凸性由 get_marginal_move_point 把关）
            point_v = item['point']
            marginal_move_result = get_marginal_move_point(point_v, annealing_rate, cells)
            if marginal_move_result > 0:
                marginal_annealing_points += 1
        else:
            # inner point：不加距离跳过，仅靠 judge_if_annealing 判断
            cb = item['cb']
            now_count += 1  # 当前总数+1 Current total + 1

            # 重新获取重心（使用最新坐标）
            point_g = cb.getTriCentreOfGravity()

            move_flag = False
            move_point_result = get_point_of_destination(cb.cell1.points[cb.index1], point_g, annealing_rate)
            flag_index = judge_if_annealing(cb, move_point_result)
            if flag_index == 0:  # 如果可以移动，则返回true
                move_flag = True
                inner_annealing_points += 1
            elif flag_index == -3:
                judge_180_count += 1
                print("judge_180_count:", judge_180_count)

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
    stats = {
        'marginal_points': marginal_annealing_points,
        'inner_points': inner_annealing_points,
    }
    return actual_annealed_cell_blocks, stats
