# -*- coding: utf-8 -*-
"""
Created on Sun May 24 17:49:22 2020

@author: Lenovo
"""
from decimal import Decimal
import math
from utillib import fittinglib


# 点类
# Point class
class Point:
    x = 0
    y = 0
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return str((self.x, self.y))

# 线段类（直角坐标系）
# Line segment class (rectangular coordinate system)
class Line:
    p1 = Point(0,0)
    p2 = Point(0,0)
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2

    def __str__(self):
        return str([self.p1, self.p2])

    def getA(self):
        a = self.p2[1] - self.p1[1]
        if math.fabs(a) < 1e-9:
            a = 0
        return a

    def getB(self):
        b = self.p1[0] - self.p2[0]
        if math.fabs(b) < 1e-9:
            b = 0
        return b

    def getC(self):
        c = self.p2[0] * self.p1[1] - self.p1[0] * self.p2[1]
        if math.fabs(c) < 1e-9:
            c = 0
        return c

# 线段类（极坐标系）
# Line segment class (polar coordinate system)
class Line_in_Polar_Coordinate_System:
    cita = 0
    r = 1
    def __init__(self, cita, r):
        self.cita = cita
        self.r = r

    def __str__(self):
        return str([self.cita, self.r])

    def getX(self):
        # print(math.cos(self.cita))
        return self.r * math.cos(self.cita)

    def getY(self):
        return self.r * math.sin(self.cita)



# 细胞类
# Cell class
class Cell:
    no = 0
    cell_no = 0
    ok = True # 是否最外两层 Is it the outermost two layers
    layer = 0 # 层数，默认为0 The number of layers is 0 by default
    cell_tier = 0# 细胞层级标记 Cell tier mark Mc=1,Nc-MC=2，第三层 Third_tier=3 Ic=4,未分类 Unclassified
    edge_line_index = ''
    edge_line_index = ''  # 边缘细胞壁两端点索引，如果该细胞为边缘细胞，则会存储边缘细胞壁的数据
    points = []
    center_point = Point(0, 0)
    vx = 0
    vy = 0
    area = 0
    actual_lines = []
    pre_best_lines = []

    # 拟合数据
    data = None
    # 拟合辅助点
    add_points = None

    def __init__(self,points):
        self.ok = True  # 是否不在边缘 Not on the edge
        self.points = points  # 逆时针存储点 Anticlockwise storage point
        self.cell_tier = 0  # 新增：初始化分层标记
        self.setNo()
        self.setVertex()
        self.setArea()
        self.layer = 0



    def __str__(self):
        return str(self.center_point)

    # 设置细胞编号
    # Set cell number
    def setNo(self):
        Cell.cell_no+=1
        self.no=Cell.cell_no

    # 计算中心点
    # Computing center
    def setVertex(self):
        points=self.points
        if len(points) <= 2:
            return list()

        area = Decimal(0.0)
        x, y = Decimal(0.0), Decimal(0.0)
        for i in range(len(points)):
            # print('points[i]', points[i])
            # print('points[i-1]', points[i-1])
            lng = Decimal(points[i][0])
            lat = Decimal(points[i][1])
            nextlng = Decimal(points[i-1][0])
            nextlat = Decimal(points[i-1][1])

            tmp_area = (nextlng*lat - nextlat*lng)/Decimal(2.0)
            area += tmp_area
            x += tmp_area*(lng+nextlng)/Decimal(3.0)
            y += tmp_area*(lat+nextlat)/Decimal(3.0)
        # print('x, area', x, area)
        # print('self.vx, self.vy', self.vx, self.vy)
        if math.fabs(x * area) < 1e-10:
            return
        x = x/area
        y = y/area
        self.vx=float(x)
        self.vy=float(y)
        self.center_point=Point(float(x), float(y))
    # 设置面积
    # Set the area
    def setArea(self):
        s=0
        i=0
        points=self.points
        length=len(points)
        while i<length :
            s+=points[i-1][0]*points[i][1]-points[i][0]*points[i-1][1]
            i+=1
        s/=2
        self.area= s


    #成长mul倍
    # grow mul times
    def grow(self,mul):
        points = self.points
        for i in range(len(points)):
            points[i][0] *= mul
            points[i][1] *= mul
        self.setVertex()
        self.setArea()


    # 椭圆拟合部分
    # value 为阈值
    def like_ellipse(self,
                     rotate_angle):  # 椭圆拟合 ，传入数据为插值法旋转角度 Ellipse fitting, the input data is interpolation rotation angle
        points = self.points[:]  # 获取细胞点集合 Get cell point collection
        nn = len(points)  # 细胞边数
        # Since the starting point and the ending point coincide in the cell class, the number of vertices existing
        # in the cell class should be the number of cell edges minus the length of the point set
        can_shu = fittinglib.fitting(points, self.center_point, self.area)

        data = self.make_final_ellipse(can_shu)

        # print("拟合前后点集",self.points, points)
        add_points = []
        for p in points:
            if p not in self.points:
                add_points.append(p)
        if len(add_points) != 0:
            self.perfect_fit_flag = False
        self.data = data
        self.add_points = add_points
        return data, add_points

    def make_final_ellipse(self, can_shu):
        ellipse_data = {}  # 声明存放椭圆参数的变量 Declare the variable that holds the ellipse parameters
        cp = fittinglib.find_center_point(can_shu)  # 获取拟合椭圆的中心点 Get the center point of fitting ellipse
        cp = Point(cp[0], cp[1])  # 同上 ditto
        ellipse_data['cp'] = cp  # 设置椭圆中心点 Set ellipse center point
        ellipse_data['a'] = fittinglib.find_a(can_shu)  # 设置椭圆长半轴数据 Set ellipse long half axis data
        ellipse_data['b'] = fittinglib.find_b(can_shu)  # 设置椭圆短半轴数据 Set ellipse minor axis data
        ellipse_data['angle'] = fittinglib.find_angle(
            can_shu)  # 设置椭圆与水平轴倾斜角数据 Set the data of inclination angle between ellipse and horizontal axis

        return ellipse_data  # 返回所有椭圆数据信息 Returns all ellipse data information


# 退火细胞块类
# Annealed cell block class
class CellBlock:
    cell1 = object
    index1 = 0
    cell2 = object
    index2 = 0
    cell3 = object
    index3 = 0
    point = Point(0,0)
    triangle = [] # 拟合三角形点集，包含逆时针排列的三个点 The set of fitted triangle points contains three points arranged anticlockwise

    def __init__(self):
        self.cell1 = object
        self.index1 = 0
        self.cell2 = object
        self.index2 = 0
        self.cell3 = object
        self.index3 = 0
        self.point = Point(0,0)

    def setCell1(self, c, i):
        self.cell1 = c
        self.index1 = i

    def setCell2(self, c, i):
        self.cell2 = c
        self.index2 = i

    def setCell3(self, c, i):
        self.cell3 = c
        self.index3 = i

    def setPoint(self, p):
        self.point = p

    #计算三角形重心 Calculate the center of gravity of the triangle
    def getTriCentreOfGravity(self):
        if self.triangle[2] is None:
            print(self.triangle[2])
        x1 = self.triangle[0].x
        y1 = self.triangle[0].y
        x2 = self.triangle[1].x
        y2 = self.triangle[1].y
        x3 = self.triangle[2].x
        y3 = self.triangle[2].y

        xg = (x1+x2+x3) / 3 ;
        yg = (y1+y2+y3) / 3 ;
        #print('in:',xg,yg)
        return Point(xg, yg)
    #新增一个函数def get_destination_by_now_Gravity(self),计算当前坐标和重心之间的距离
    def get_destination_by_now_Gravity(self):
        xg = self.getTriCentreOfGravity().x
        yg = self.getTriCentreOfGravity().y
        distance_now_end = math.sqrt((self.x - xg) * (self.x - xg) +
                         (self.y - yg) * (self.y - yg))
        return distance_now_end

class ETCellBlock:
    type = 0  # 类型： 0为非边缘型、1为边缘型
    # 注：非边缘型细胞块，有四个细胞；边缘型细胞块，有三个细胞

    center_cell = object
    neighbor_cells = []
    point1_indexes = []
    point2_indexes = []

    def __init__(self, type):
        self.center_cell = object
        self.neighbor_cells = []
        self.point1_indexes = []
        self.point2_indexes = []

        self.type = type

    def setCenterCell(self, center_point):
        self.center_cell = center_point

    def addCell(self, c, p):
        self.neighbor_cells.append(c)
        self.point1_indexes.append(p)

    def addPoint2(self, p):
        self.point2_indexes.append(p)

    def zoom_judge(self, p1, p2, to_p1, to_p2, cells):
        p1_flag = True
        p2_flag = True
        if self.type == 0:  # 非边缘型
            pass
        else:  # 边缘型
            c1 = self.neighbor_cells[0]  # 获取一个相邻细胞
            c2 = self.neighbor_cells[1]  # 获取一个相邻细胞
            judge_p1 = self.center_cell.points[self.center_cell.points.index(p1)-1]  # 获取判断点1，无需判断（未移动的点）
            if judge_p1 in c1.points:
                judge_p2 = c1.points[c1.points.index(judge_p1)-1]  # 获取判断点2，需判断
                #  判断上述判断点是否为真
                if judge_p2 in self.center_cell.points:  # 如果判断点2在中心细胞中，则应修改
                    judge_p2 = c1.points[(c1.points.index(judge_p1) + 1) % len(c1.points)]
            else:
                judge_p2 = c2.points[c2.points.index(judge_p1) - 1]  # 获取判断点2，需判断
                #  判断上述判断点是否为真
                if judge_p2 in self.center_cell.points:  # 如果判断点2在中心细胞中，则应修改
                    judge_p2 = c2.points[(c2.points.index(judge_p1) + 1) % len(c2.points)]

            # 对缩放前后两个点进行可行性判断
            judge_line = Line(judge_p1, judge_p2)
            flag1 = judge_line.getA() * p1[0] + judge_line.getB() * p1[1] + judge_line.getC()
            flag2 = judge_line.getA() * to_p1[0] + judge_line.getB() * to_p1[1] + judge_line.getC()
            if flag1 * flag2 < 0 or math.fabs(flag1 * flag2) < 1e-9:
                p1_flag = False
            flag1 = judge_line.getA() * p2[0] + judge_line.getB() * p2[1] + judge_line.getC()
            flag2 = judge_line.getA() * to_p2[0] + judge_line.getB() * to_p2[1] + judge_line.getC()
            if flag1 * flag2 < 0 or math.fabs(flag1 * flag2) < 1e-9:
                p2_flag =  False

            # 对中心点移动的情况进行追加判断
            if judge_p1 not in c1.points or judge_p1 not in c2.points:  # 如果未移动的点不同时在两个相邻细胞中，则中心点发生了移动
                center_move_p = p1
                center_to_move_p = to_p1
                if p2 in c1.points and p2 in c2.points:  # 如果第二个移动点同时在两个相邻细胞中，则第二个点是中心点
                    center_move_p = p2
                    center_to_move_p = to_p2
                print("center_move_p", center_move_p)
                print("center_to_move_p", center_to_move_p)
                judge_p3 = []
                for ncp1 in c1.points:
                    if ncp1 in c2.points and ncp1 not in self.center_cell.points:
                        judge_p3 = ncp1
                        break
                #judge_c = object
                judge_c = Point
                for c in cells:
                    if judge_p3 in c.points and c not in self.neighbor_cells:
                        judge_c = c
                        break
                judge_p4 = judge_c.points[judge_c.points.index(judge_p3) - 1]
                judge_p5 = judge_c.points[(judge_c.points.index(judge_p3) + 1) % len(judge_c.points)]
                # 对缩放前后两个中心点进行可行性判断
                judge_line = Line(judge_p3, judge_p4)
                flag1 = judge_line.getA() * center_move_p[0] + judge_line.getB() * center_move_p[1] + judge_line.getC()
                flag2 = judge_line.getA() * center_to_move_p[0] + judge_line.getB() * center_to_move_p[1] + judge_line.getC()
                if flag1 * flag2 < 0 or math.fabs(flag1 * flag2) < 1e-9:
                    if center_move_p == p1:
                        p1_flag = False
                    else:
                        p2_flag = False
                judge_line = Line(judge_p3, judge_p5)
                flag1 = judge_line.getA() * center_move_p[0] + judge_line.getB() * center_move_p[1] + judge_line.getC()
                flag2 = judge_line.getA() * center_to_move_p[0] + judge_line.getB() * center_to_move_p[1] + judge_line.getC()
                if flag1 * flag2 < 0 or math.fabs(flag1 * flag2) < 1e-9:
                    if center_move_p == p1:
                        p1_flag = False
                    else:
                        p2_flag = False

        return [p1_flag, p2_flag]

    def zoom(self, zoom_rate, line, cells):
        # print('边缘三边细胞边缩放')
        p1 = line[0]
        p2 = line[1]
        middle_p = [(p1[0]+p2[0])/2, (p1[1]+p2[1])/2]
        vector_mp1 = [p1[0]-middle_p[0], p1[1]-middle_p[1]]
        vector_mp2 = [p2[0]-middle_p[0], p2[1]-middle_p[1]]

        # 移动目标点
        to_p1 = [zoom_rate*vector_mp1[0]+middle_p[0], zoom_rate*vector_mp1[1]+middle_p[1]]
        to_p2 = [zoom_rate*vector_mp2[0]+middle_p[0], zoom_rate*vector_mp2[1]+middle_p[1]]

        # 对目标点进行可行性判断
        move_flag =  self.zoom_judge(p1, p2, to_p1, to_p2, cells)
        if not (move_flag[0] or move_flag[1]):  # 如果p1 和 p2 都不能移动
            return 0
        # 移动目标点
        for c in self.neighbor_cells:
            if p1 in c.points and move_flag[0]:
                index1 = c.points.index(p1)
                c.points[index1] = to_p1
            if p2 in c.points and move_flag[1]:
                index2 = c.points.index(p2)
                c.points[index2] = to_p2
        if move_flag[0]:
            index1 = self.center_cell.points.index(p1)
            self.center_cell.points[index1] = to_p1
        if move_flag[1]:
            index2 = self.center_cell.points.index(p2)
            self.center_cell.points[index2] = to_p2
        return 1

class ETCellBlockII:
    type = 0  # 类型： 0为非边缘型、1为边缘型
    # 注：非边缘型细胞块，有四个细胞；边缘型细胞块，有三个细胞

    line = list()  # 转移边,由两个点构成
    increase_cells = list()  # 增加型细胞
    to_be_moved_points = list()  # 增加型细胞，待移动点的索引
    reduce_cells = list()  # 减少型细胞
    to_be_moved_points_a = list()  # 减少型细胞，待移动点的索引
    to_be_moved_points_b = list()  # 减少型细胞，待删除点的索引

    target_point_a = list()
    target_point_b = list()

    zoom_point_a = list()
    zoom_point_b = list()

    def __init__(self, line):
        self.type = 0  # 类型： 0为非边缘型、1为边缘型
        # 注：非边缘型细胞块，有四个细胞；边缘型细胞块，有三个细胞
        self.line = list()  # 转移边,由两个点构成
        self.increase_cells = list()  # 增加型细胞
        self.to_be_moved_points = list()  # 增加型细胞，待移动点的索引
        self.reduce_cells = list()  # 减少型细胞
        self.to_be_moved_points_a = list()  # 减少型细胞，待移动点的索引
        self.to_be_moved_points_b = list()  # 减少型细胞，待删除点的索引

        self.target_point_a = list()
        self.target_point_b = list()

        self.zoom_point_a = list()
        self.zoom_point_b = list()

        self.line = line

    def get_distance_point_point_by_list(self, p1, p2):
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

    def get_distance_point_line(self, point, line):
        a = line[1][1] - line[0][1]
        b = line[0][0] - line[1][0]

        c = line[1][0] * line[0][1] - line[0][0] * line[1][1]
        dis = (math.fabs(a * point.x + b * point.y + c)) / (math.pow(a * a + b * b, 0.5))
        return dis


    def setType(self, type):
        self.type = type

    def addIncreaseCell(self, c, p):
        self.increase_cells.append(c)
        self.to_be_moved_points.append(c.points.index(p))

    def addReduceCell(self, c, p1, p2):
        self.reduce_cells.append(c)
        self.to_be_moved_points_a.append(c.points.index(p1))
        self.to_be_moved_points_b.append(c.points.index(p2))

    def judge_alpha(self, k_alpha):
        """
        判断是否满足 Alpha 类型 T1 变换条件：
        定义：细胞大小 A > k * B 且 A > k * C，其中 B, C 共有边（即 B, C 是 reduce_cells）。
        在这个模型中，reduce_cells 是共享短边的细胞（即将失去边的细胞）。
        increase_cells 是短边两端的细胞（即将获得边的细胞）。
        所以 Alpha Type 意味着：Increase Cell (A) 很大，Reduce Cells (B, C) 很小。
        条件：存在一个 increase_cell (A)，使得 A.area > k * B.area 且 A.area > k * C.area。
        """
        # 遍历每一个增加型细胞作为潜在的大细胞 A
        for inc_cell in self.increase_cells:
            is_larger_than_all_reduce = True
            for red_cell in self.reduce_cells:
                # 检查是否 A > k * B
                if not (inc_cell.area > k_alpha * red_cell.area):
                    is_larger_than_all_reduce = False
                    break

            # 如果该增加型细胞比所有减少型细胞都大（满足倍数关系），则满足条件
            if is_larger_than_all_reduce and len(self.reduce_cells) > 0:
                return True

        return False

    def judge_beta(self, k_beta):
        """
        判断是否满足 Beta 类型 T1 变换条件：
        定义：细胞大小 A > k * B 且 A > k * C，其中 B, C 被 A 的一条边隔开。
        在这个模型中，reduce_cells 是共享短边的细胞（即短边属于它们）。
        increase_cells 是短边两端的细胞（它们目前被隔开）。
        所以 Beta Type 意味着：Reduce Cell (A) 很大（它拥有这条短边），Increase Cells (B, C) 很小（被隔开）。
        条件：存在一个 reduce_cell (A)，使得 A.area > k * B.area 且 A.area > k * C.area。
        """
        # 遍历每一个减少型细胞作为潜在的大细胞 A
        for red_cell in self.reduce_cells:
            is_larger_than_all_increase = True
            for inc_cell in self.increase_cells:
                # 检查是否 A > k * B
                if not (red_cell.area > k_beta * inc_cell.area):
                    is_larger_than_all_increase = False
                    break

            # 如果该减少型细胞比所有增加型细胞都大（满足倍数关系），则满足条件
            if is_larger_than_all_increase and len(self.increase_cells) > 0:
                return True

        return False

    def judge(self, condition):
        if self.type == 1 or condition == 2:  # 边缘细胞或全部满足面积要求
            for c1 in self.increase_cells:
                for c2 in self.reduce_cells:
                    if c2.area > c1.area:  # 如果减小型细胞面积大于增加型细胞面积，则不进行边转移，返回False
                        return False
        elif condition == 1:  # 只需一侧满足面积要求即可
            c1 = self.increase_cells[0]
            for c2 in self.reduce_cells:
                if c2.area > c1.area:  # 如果减小型细胞面积大于增加型细胞面积，则不进行边转移，返回False
                    return False
        return True  # 未发现减小型细胞面积大于增加型细胞面积的情况，进行边转移，返回True

    def get_target_point(self):
        print(self.type)
        if self.type == 0:  # 非边缘型细胞
            # print("非边缘型细胞边转移")
            a = self.line[0][0]
            b = self.line[0][1]
            c = self.line[1][0]
            d = self.line[1][1]

            # self.target_point_a = [(a+b+c-d)/2, (b+c+d-a)/2]
            # self.target_point_b = [(a-b+c+d)/2, (a+b-c+d)/2]

            ax = (a+b+c-d)/2  # 此处计算的是，未经缩放的两点坐标
            ay = (b+c+d-a)/2
            bx = (a-b+c+d)/2
            by = (a+b-c+d)/2

            # result_flag = False
            # for rate in [1]:  # 循环缩小缩放比率，直到满足限制
            #     self.target_point_a = [(ax + bx) * (1 - rate) / 2 + rate * ax, (ay + by) * (1 - rate) / 2 + rate * ay]
            #     self.target_point_b = [(ax + bx) * (1 - rate) / 2 + rate * bx, (ay + by) * (1 - rate) / 2 + rate * by]
            #     if self.result_judge(self.target_point_a, self.target_point_b):  # 满足限制，跳出循环
            #         result_flag = True
            #         break
            #     print('进一步缩放')
            # if not result_flag:
            #     print('经过缩放仍不满足条件')
            #     return False

            rate = 1
            self.target_point_a = [(ax + bx) * (1 - rate) / 2 + rate * ax, (ay + by) * (1 - rate) / 2 + rate * ay]
            self.target_point_b = [(ax + bx) * (1 - rate) / 2 + rate * bx, (ay + by) * (1 - rate) / 2 + rate * by]
            if not self.result_judge(self.target_point_a, self.target_point_b, selfJudge=True):  # 不满足限制，退出
                print("self.target_point_a, self.target_point_b", self.target_point_a, self.target_point_b)
                return False

        else:  # 边缘型细胞
            # print("边缘型细胞边转移")
            # print("测试数据:self.line[0]=", self.line[0])
            p_a = self.line[0]
            p_b = self.line[1]
            i_cell = self.increase_cells[0]
            p_xy1 = p_a
            if p_a in i_cell.points:
                p_xy1 = p_b

            # result_flag = False
            # for rate in [1]:  # 循环缩小缩放比率，直到满足限制
            #     d = self.get_distance_point_point_by_list(p_a, p_b) * rate
            #     for cell in self.reduce_cells:
            #         p_xy2 = cell.points[cell.points.index(p_xy1) - 1]
            #         if p_xy2 in i_cell.points:
            #             p_xy2 = cell.points[(cell.points.index(p_xy1) + 1) % len(cell.points)]
            #         r = self.get_distance_point_point_by_list(p_xy1, p_xy2)
            #         x = (d / r) * (p_xy2[0] - p_xy1[0]) + p_xy1[0]
            #         y = (d / r) * (p_xy2[1] - p_xy1[1]) + p_xy1[1]
            #         if len(self.target_point_a) == 0:
            #             self.target_point_a = [x, y]
            #         else:
            #             self.target_point_b = [x, y]
            #     if self.result_judge(self.target_point_a, self.target_point_b):  # 满足限制，跳出循环
            #         result_flag = True
            #         break
            #     self.target_point_a = []
            #     self.target_point_b = []
            #     print('进一步缩放')
            # if not result_flag:
            #     print('经过缩放仍不满足条件')
            #     return False
            rate = 1
            d = self.get_distance_point_point_by_list(p_a, p_b) * rate
            for cell in self.reduce_cells:
                p_xy2 = cell.points[cell.points.index(p_xy1) - 1]
                if p_xy2 in i_cell.points:
                    p_xy2 = cell.points[(cell.points.index(p_xy1) + 1) % len(cell.points)]
                r = self.get_distance_point_point_by_list(p_xy1, p_xy2)
                x = (d / r) * (p_xy2[0] - p_xy1[0]) + p_xy1[0]
                y = (d / r) * (p_xy2[1] - p_xy1[1]) + p_xy1[1]
                if len(self.target_point_a) == 0:
                    self.target_point_a = [x, y]
                else:
                    self.target_point_b = [x, y]
            if not self.result_judge(self.target_point_a, self.target_point_b, selfJudge=True):  # 不满足限制，退出
                return False

        return True

    def get_zoom_point(self, zoom_rate):
        p1 = self.line[0]
        p2 = self.line[1]
        middle_p = [(p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2]
        vector_mp1 = [p1[0] - middle_p[0], p1[1] - middle_p[1]]
        vector_mp2 = [p2[0] - middle_p[0], p2[1] - middle_p[1]]
        self.zoom_point_a = [zoom_rate * vector_mp1[0] + middle_p[0], zoom_rate * vector_mp1[1] + middle_p[1]]
        self.zoom_point_b = [zoom_rate * vector_mp2[0] + middle_p[0], zoom_rate * vector_mp2[1] + middle_p[1]]
        if not self.result_judge(self.zoom_point_a, self.zoom_point_b):  # 不满足限制，退出
            # print('缩放判断未通过')
            return False
        else:
            return True

    def zoom(self):
        # print("进行边缩放操作==============")
        # print('reduce_cells', self.reduce_cells[0])

        for cell in self.reduce_cells:
            # print('减少型细胞中心点', cell)
            if self.line[0] in cell.points:
                index1 = cell.points.index(self.line[0])
                # print("cell.points[index1]", cell.points[index1])
                # print("self.zoom_point_a", self.zoom_point_a)
                cell.points[index1] = self.zoom_point_a
            if self.line[1] in cell.points:
                index2 = cell.points.index(self.line[1])
                # print("cell.points[index2]", cell.points[index2])
                # print("self.zoom_point_b", self.zoom_point_b)
                cell.points[index2] = self.zoom_point_b

        for cell in self.increase_cells:
            # print('增加型细胞中心点', cell)
            if self.line[0] in cell.points:
                index1 = cell.points.index(self.line[0])
                # print("cell.points[index1]", cell.points[index1])
                # print("self.zoom_point_a", self.zoom_point_a)
                cell.points[index1] = self.zoom_point_a
            if self.line[1] in cell.points:
                index2 = cell.points.index(self.line[1])
                # print("cell.points[index2]", cell.points[index2])
                # print("self.zoom_point_b", self.zoom_point_b)
                cell.points[index2] = self.zoom_point_b

    # 结果判断：判断移动后的细胞块是否满足维诺图定义。
    def result_judge(self, point_a, point_b, selfJudge = False):
        judge_flag = True
        for index in range(len(self.increase_cells)):
            middle_point_index = self.to_be_moved_points[index]
            line1_point1 = self.increase_cells[index].points[middle_point_index - 1]
            line1_point2 = self.increase_cells[index].points[middle_point_index - 2]
            line2_point1 = self.increase_cells[index].points[(middle_point_index + 1) % len(self.increase_cells[index].points)]
            line2_point2 = self.increase_cells[index].points[(middle_point_index + 2) % len(self.increase_cells[index].points)]
            crossover_point = self.get_crossover_point(
                line1_point1[0], line1_point1[1], line1_point2[0], line1_point2[1],
                line2_point1[0], line2_point1[1], line2_point2[0], line2_point2[1])

            if crossover_point == None:
                print('type', self.type)
                print('crossover_point', crossover_point)
                print('line1_point1', line1_point1)
                print('line1_point2', line1_point2)
                print('line2_point1', line2_point1)
                print('line2_point2', line2_point2)

                if line1_point1[0] < line2_point1[0]:
                    p_min = line1_point1[0]
                    p_max = line2_point1[0]
                else:
                    p_max = line1_point1[0]
                    p_min = line2_point1[0]

                if p_min < point_a[0] < p_max and p_min < point_b[0] < p_max:
                    continue
                else:
                    return False

            vector_a = [line1_point1[0]-crossover_point[0], line1_point1[1]-crossover_point[1]]
            vector_b = [line2_point1[0]-crossover_point[0], line2_point1[1]-crossover_point[1]]
            vector_r1 = [point_a[0]-crossover_point[0], point_a[1]-crossover_point[1]]
            vector_r2 = [point_b[0]-crossover_point[0], point_b[1]-crossover_point[1]]

            m1 = (vector_r1[1]*vector_a[0] - vector_a[1]*vector_r1[0])/(vector_b[1]*vector_a[0] - vector_a[1]*vector_b[0])
            n1 = (vector_b[1]*vector_r1[0] - vector_r1[1]*vector_b[0])/(vector_b[1]*vector_a[0] - vector_a[1]*vector_b[0])
            m2 = (vector_r2[1]*vector_a[0] - vector_a[1]*vector_r2[0])/(vector_b[1]*vector_a[0] - vector_a[1]*vector_b[0])
            n2 = (vector_b[1]*vector_r2[0] - vector_r2[1]*vector_b[0])/(vector_b[1]*vector_a[0] - vector_a[1]*vector_b[0])

            type_flag = self.get_distance_point_point_by_list(line1_point1, line2_point1) - self.get_distance_point_point_by_list(line1_point2, line2_point2)
            if m1 < 0 or n1 < 0 or m2 < 0 or n2 < 0:
                judge_flag = False
                break
            if type_flag < 0:  # 交点在外侧
                if m1+n1 >= 1 or m2+n2 >= 1:
                    judge_flag = False
                    break
            else:  # 交点在内侧
                if m1+n1 <= 1 or m2+n2 <= 1:
                    judge_flag = False
                    break
        if selfJudge:
            # 结构体中心判断
            for i in range(0, len(self.increase_cells)):
                pre_point = self.increase_cells[i].points[self.to_be_moved_points[i] - 1]  # 前一个点（判断用）
                aft_point = self.increase_cells[i].points[
                    (self.to_be_moved_points[i] + 1) % len(self.increase_cells[i].points)]  # 后一个点（判断用）
                daA = self.get_distance_point_point_by_list(pre_point, self.target_point_a)  # aA的距离
                dbB = self.get_distance_point_point_by_list(aft_point, self.target_point_b)  # bB的距离

                daB = self.get_distance_point_point_by_list(pre_point, self.target_point_b)  # aB的距离
                dbA = self.get_distance_point_point_by_list(aft_point, self.target_point_a)  # bA的距离

                # 如果满足下式，则证明左式为实际配对情况（对于相等的情况需要另做讨论，不过出现相等的概率不大）
                if daA * daA + dbB * dbB < daB * daB + dbA * dbA:  # 先将当前点修改为target_point_a, 然后插入target_point_b
                    dis_p_l_1 = self.get_distance_point_line(self.increase_cells[i].center_point, [pre_point,  self.target_point_b])
                    dis_p_p_1 = self.get_distance_point_point_by_list([self.increase_cells[i].center_point.x, self.increase_cells[i].center_point.y], self.target_point_a)
                    dis_p_l_2 = self.get_distance_point_line(self.increase_cells[i].center_point, [aft_point, self.target_point_a])
                    dis_p_p_2 = self.get_distance_point_point_by_list([self.increase_cells[i].center_point.x, self.increase_cells[i].center_point.y], self.target_point_b)
                    if dis_p_l_1 > dis_p_p_1 or dis_p_l_2 > dis_p_p_2:
                        judge_flag = False
                        break
                else:  # 否则，则先将当前点修改为target_point_b, 然后插入target_point_a
                    dis_p_l_1 = self.get_distance_point_line(self.increase_cells[i].center_point, [pre_point, self.target_point_a])
                    dis_p_p_1 = self.get_distance_point_point_by_list([self.increase_cells[i].center_point.x, self.increase_cells[i].center_point.y], self.target_point_b)
                    dis_p_l_2 = self.get_distance_point_line(self.increase_cells[i].center_point, [aft_point, self.target_point_b])
                    dis_p_p_2 = self.get_distance_point_point_by_list([self.increase_cells[i].center_point.x, self.increase_cells[i].center_point.y], self.target_point_a)
                    if dis_p_l_1 > dis_p_p_1 or dis_p_l_2 > dis_p_p_2:
                        judge_flag = False
                        break


        return judge_flag

    """
        斜率计算方法
        Slope calculation method
        :param x1,y1,x2,y2: 两点坐标 Two point coordinates
        :return: 斜率 Slope
    """

    def get_slope_by_xy(self, x1, y1, x2, y2):
        k = (y1 - y2) / (x1 - x2)
        return k

    """
        获取两条直线的交点坐标
        Get the intersection coordinates of two lines
        :param l1: 第一条直线，Line对象 First line, line object
        :param l2: 第二条直线，Line对象 Second line, line object
        :return: 交点坐标，Point对象 Intersection coordinates, point object
    """

    def get_crossover_point(self, x1, y1, x2, y2, x3, y3, x4, y4):
        # 分三种情况，计算交点坐标 In three cases, the coordinates of intersection point are calculated
        if not (math.isclose(x1, x2, rel_tol=1e-9) or math.isclose(x3, x4, rel_tol=1e-9)):  # 一般情况下  Normally
            k1 = self.get_slope_by_xy(x1, y1, x2, y2)
            k2 = self.get_slope_by_xy(x3, y3, x4, y4)
            if math.isclose(k1, k2, rel_tol=1e-12):
                return None
            x = -(((y1 - k1 * x1) - (y3 - k2 * x3)) / (k1 - k2))
            y = k1 * x + (y1 - k1 * x1)
        elif not math.isclose(x3, x4, rel_tol=1e-9):  # l2不垂直于x轴 L2 is not perpendicular to the X axis
            k2 = self.get_slope_by_xy(x3, y3, x4, y4)
            x = x1
            y = k2 * (x - x3) + y3
        elif not math.isclose(x1, x2, rel_tol=1e-9):  # l1不垂直于x轴 L1 is not perpendicular to the X axis
            k1 = self.get_slope_by_xy(x1, y1, x2, y2)
            x = x3
            y = k1 * (x - x1) + y1
        else:
            return None
        return [x, y]

    def move_point(self):
        # print("移动点")
        # print('目标点', self.target_point_a, self.target_point_b)
        # print("1-1")
        # if self.type == 1:
        #     return
        # print("1-2")
        # 减少型细胞的操作
        cell1 = self.reduce_cells[0]
        if len(self.reduce_cells) > 1:
            cell2 = self.reduce_cells[1]

        d1 = self.get_distance_point_point_by_list([cell1.vx, cell1.vy], self.target_point_a)
        d2 = self.get_distance_point_point_by_list([cell1.vx, cell1.vy], self.target_point_b)
        # print("1-3")
        if d1 < d2:  # 若d1<d2，则target_point_a属于cell1
            # print("1-3-1")
            cell1.points[self.to_be_moved_points_a[0]] = self.target_point_a
            # print("1-3-1-0")
            cell1.points.pop(self.to_be_moved_points_b[0])
            # print("1-3-1-1")
            if len(self.reduce_cells) > 1:
                cell2.points[self.to_be_moved_points_a[1]] = self.target_point_b
                # print("1-3-1-2")
                cell2.points.pop(self.to_be_moved_points_b[1])

        else:  # 否则，则target_point_a属于cell2
            # print("1-3-2")
            if len(self.reduce_cells) > 1:
                cell2.points[self.to_be_moved_points_a[1]] = self.target_point_a
                # print("1-3-2-0")
                cell2.points.pop(self.to_be_moved_points_b[1])
            # print("1-3-2-1")
            cell1.points[self.to_be_moved_points_a[0]] = self.target_point_b
            # print("1-3-2-2")
            cell1.points.pop(self.to_be_moved_points_b[0])

        # print("1-4")
        # 增加型细胞的操作
        for i in range(0, len(self.increase_cells)):
            pre_point = self.increase_cells[i].points[self.to_be_moved_points[i] - 1]  # 前一个点（判断用）
            aft_point = self.increase_cells[i].points[(self.to_be_moved_points[i] + 1) % len(self.increase_cells[i].points)]  # 后一个点（判断用）
            daA = self.get_distance_point_point_by_list(pre_point, self.target_point_a)  # aA的距离
            dbB = self.get_distance_point_point_by_list(aft_point, self.target_point_b)  # bB的距离

            daB = self.get_distance_point_point_by_list(pre_point, self.target_point_b)  # aB的距离
            dbA = self.get_distance_point_point_by_list(aft_point, self.target_point_a)  # bA的距离

            # 如果满足下式，则证明左式为实际配对情况（对于相等的情况需要另做讨论，不过出现相等的概率不大）
            if daA*daA + dbB*dbB < daB*daB + dbA*dbA:  # 先将当前点修改为target_point_a, 然后插入target_point_b
                self.increase_cells[i].points[self.to_be_moved_points[i]] = self.target_point_a
                self.increase_cells[i].points.insert(self.to_be_moved_points[i] + 1, self.target_point_b)
            else:  # 否则，则先将当前点修改为target_point_b, 然后插入target_point_a
                self.increase_cells[i].points[self.to_be_moved_points[i]] = self.target_point_b
                self.increase_cells[i].points.insert(self.to_be_moved_points[i] + 1, self.target_point_a)

        # print("1-5")


'''
    边转移细胞块——边缘三角形相邻情况
    由三个细胞组成
'''


class ETCellBlockIII:
    type = 2  # 类型 取值恒为2 （该取值只存在于ETCellBlockIII中， 用于区分）
    center_point = []  # 三个细胞的中心点
    center_cell = object  # 唯一不是三角形的细胞
    triangle_cells = []  # 两个三角形细胞

    def __init__(self):
        self.type = 2
        self.center_point = []
        self.center_cell = object
        self.triangle_cells = []

    def setCenterCell(self, center_cell):
        self.center_cell = center_cell

    def setCenterPoint(self, center_point):
        self.center_point = center_point

    def addTriangleCell(self, c):
        self.triangle_cells.append(c)

    def handle(self):
        center_index_in_center = self.center_cell.points.index(self.center_point)
        self.center_cell.points.pop((center_index_in_center + 1) % len(self.center_cell.points))
        self.center_cell.points.pop(center_index_in_center)
        self.center_cell.points.pop(center_index_in_center - 1)
