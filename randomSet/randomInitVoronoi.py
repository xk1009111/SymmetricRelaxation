# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 18:28:12 2021

@author: shi
"""
import numpy as np
from scipy.spatial import Voronoi
import random
from utillib.mylib import Cell
import tkinter
import tkinter.messagebox  # 弹窗库


def handle_i(cellSeedNum, scale):  # 构造随机维诺图数据 Construct random venogram data
    arr_list = list()
    for i in range(cellSeedNum):
        r = random.uniform(0, 1)
        cita = random.uniform(0, 2 * np.pi)
        point_x = 1000 + 1000 * np.cos(cita)*(r**scale)
        point_y = 1000 + 1000 * np.sin(cita)*(r**scale)
        arr_list.append([point_x, point_y])
    return arr_list


def handle_ii(cellSeed, k, scale, region):
    arr_list = list()

    for x in range(cellSeed):
        for y in range(cellSeed + 1):
            tmp_k = k
            point_x = x
            point_y = y
            if y % 2 == 0:
                point_x += 0.5
            point_y = 0.5 * point_y * np.sqrt(3)
            while True:
                a = random.uniform(0, 2 * np.pi)
                b = random.uniform(0, np.sqrt(3) / 3)
                tmp_x = tmp_k * np.cos(a) * (b**scale)
                tmp_y = tmp_k * np.sin(a) * (b**scale)

                abs_x = np.abs(tmp_x)
                abs_y = np.abs(tmp_y)
                if region == 1:  # 小区域
                    if abs_x < 0.5 * tmp_k and abs_y + (abs_x - tmp_k) * np.sqrt(3) / 3 < 0:
                        break
                elif region == 2:  # 大区域
                    if abs_y < np.sqrt(3) * tmp_k / 2 and abs_y + (abs_x - tmp_k) * np.sqrt(3) < 0:
                        break
            point_x = point_x + tmp_x
            point_y = point_y + tmp_y
            p = (point_x, point_y)
            arr_list.append(p)

    return arr_list


def handle_iii(cellSeedNum, scale, cellSeedNum_, scale_):
    arr_list = list()
    for i in range(cellSeedNum):
        r = random.uniform(0, 1)
        cita = random.uniform(0, 2 * np.pi)
        point_x = 1000 + 1000 * np.cos(cita) * (r ** scale)
        point_y = 1000 + 1000 * np.sin(cita) * (r ** scale)
        arr_list.append([point_x, point_y])
    for i in range(cellSeedNum_):
        r = random.uniform(0, 1)
        cita = random.uniform(0, 2 * np.pi)
        point_x = 1000 + 1000 * np.cos(cita) * (r ** scale_)
        point_y = 1000 + 1000 * np.sin(cita) * (r ** scale_)
        arr_list.append([point_x, point_y])
    return arr_list


def handle_iv(cellSeedNum, cellSeedFrom, type):
    data = []
    try:
        with open('pi_data_512k.txt', 'r') as f:
            f.seek(cellSeedFrom - 1, 0)
            for i in range(cellSeedNum * 2):
                num = float(f.read(5))/1000.0
                data.append(num)
    except FileNotFoundError as ex:
        print(ex)
        print('文件未找到，请将文件“pi_data_512k”置于本程序同一目录下')
        tkinter.messagebox.showerror('错误', '文件未找到，请将文件“pi_data_512k”置于本程序同一目录下')
        exit(0)

    arr_list = list()
    for i in range(cellSeedNum):
        if type == 1:
            arr_list.append([data[i], data[i+cellSeedNum-1]])
        else:
            arr_list.append([data[i*2], data[i*2 + 1]])
    return arr_list


def just(vor, n):
    regions = vor.regions  # 所有细胞的点位置 The point position of all the cells
    vertices = vor.vertices  # 细胞点坐标 Cell point coordinates
    cells = list()
    for region in regions:
        flag = 0
        points = []
        for po in region:
            if po == -1:
                flag = 1
                break
            elif vertices[po][0] < -1 or vertices[po][0] > n+1 or vertices[po][1] < -1 or vertices[po][1] > n+1 :
                flag = 1
                break
            point = vertices[po].tolist()
            if len(point) == 0:
                break
            points.append(point)
        if len(points) < 3:
            continue
        if flag == 0 and points!=[]:
            c1=Cell(points)
            if c1.area<0:
                Cell.cell_no-=1
                points = points[::-1]
                c1=Cell(points)
            cells.append(c1)
    return cells


'''
    细胞集预处理，含有：
    1、去除边缘独立细胞
    2、细胞块边缘整齐化
'''
def pretreatment(cells):
    points_times = {}
    for c in cells:
        for p in c.points:
            p_key = '{:.10f}-{:.10f}'.format(p[0], p[1])
            if p_key in points_times.keys():
                points_times[p_key] += 1
            else:
                points_times[p_key] = 1

    # 去除边缘独立细胞
    i = -1
    while True:
        i += 1
        if i >= len(cells):
            break
        flag_count = 0
        for p in cells[i].points:
            p_key = '{:.10f}-{:.10f}'.format(p[0], p[1])
            if points_times[p_key] > 1:
                flag_count += 1
        if flag_count < 3:
            c = cells.pop(i)
            i -= 1
            # print(11111)
            for p in c.points:
                p_key = '{:.10f}-{:.10f}'.format(p[0], p[1])
                points_times[p_key] -= 1

    # 细胞块边缘整齐化
    for c in cells:
        p_i = -1
        while True:
            p_i += 1
            if p_i >= len(c.points):
                break
            p = [c.points[p_i][0], c.points[p_i][1]]
            p_key = '{:.10f}-{:.10f}'.format(p[0], p[1])
            if points_times[p_key] == 1:
                c.points.pop(p_i)
                p_i -= 1
    return cells


def getCells(handle, cellSeedNum=0, scale=0, cellSeed=2000, k=0, cellSeedNum_=0, scale_=0, region=1, cellSeedFrom=0, type=0):

    if handle == '1':
        arr = handle_i(cellSeedNum, scale)
    elif handle == '2':
        arr = handle_ii(cellSeed, k, scale, region)
    elif handle == '3':
        arr = handle_iii(cellSeedNum, scale, cellSeedNum_, scale_)
    else:
        arr = handle_iv(cellSeedNum, cellSeedFrom, type)
        cellSeed = 100
    vor = Voronoi(arr)  # 生成维诺图 Generate a vinot diagram
    cells = just(vor, cellSeed)
    # cells = pretreatment(cells)

    return [cells, arr]
