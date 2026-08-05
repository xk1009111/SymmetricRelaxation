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


    # 椭圆拟合部分
    # value 为阈值
    def like_ellipse(self,
                     rotate_angle):  # 椭圆拟合 ，传入数据为插值法旋转角度 Ellipse fitting, the input data is interpolation rotation angle
        points = self.points[:]  # 获取细胞点集合 Get cell point collection
        nn = len(points)  # 细胞边数
        # Since the starting point and the ending point coincide in the cell class, the number of vertices existing
        # in the cell class should be the number of cell edges minus the length of the point set
        # fitting() (V13.0) 直接返回几何参数 [cx, cy, a, b, theta]
        geo = fittinglib.fitting(points, self.center_point, self.area)

        data = self.make_final_ellipse(geo)

        # print("拟合前后点集",self.points, points)
        add_points = []
        for p in points:
            if p not in self.points:
                add_points.append(p)
        self.data = data
        self.add_points = add_points
        return data, add_points

    def make_final_ellipse(self, geo):
        # geo 为 fitting() 返回的几何参数 [cx, cy, a, b, theta]；
        # fitting() 已完成代数→几何转换，这里直接映射即可
        # geo is the geometric params [cx, cy, a, b, theta] returned by fitting();
        # fitting() has already done the algebraic→geometric conversion, so just
        # map them directly.
        ellipse_data = {}  # 声明存放椭圆参数的变量 Declare the variable that holds the ellipse parameters

        cx = float(geo[0])
        cy = float(geo[1])
        ellipse_data['cp'] = Point(cx, cy)  # 设置椭圆中心点 Set ellipse center point
        ellipse_data['a'] = float(geo[2])  # 设置椭圆长半轴数据 Set ellipse long half axis data
        ellipse_data['b'] = float(geo[3])  # 设置椭圆短半轴数据 Set ellipse minor axis data
        ellipse_data['angle'] = float(geo[4])  # 设置椭圆与水平轴倾斜角数据 Set the data of inclination angle between ellipse and horizontal axis

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

