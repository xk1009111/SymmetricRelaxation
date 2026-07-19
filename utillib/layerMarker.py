# -*- coding: utf-8 -*-
"""
Created on Wed Aug 12 23:11:12 2020

@author: Lenovo
"""
import math


'''
    周边探索法。
    Peripheral exploration method
    :param cells: 细胞集，Cell对象列表 Cell set, cell object list
    :param N: 细胞维诺图种子数  Seed number of cell Vinot map
'''
def layer_mark2(cells, N):
    """
    周边探索法（改进版：确保所有细胞都被标记，从第1层开始）。
    通过逐层向外扩散的方式标记所有细胞，避免出现"第0层"的未标记细胞。
    当一个细胞与多个不同层的细胞相邻时，取最小相邻层号+1。
    :param cells: 细胞集，Cell对象列表 Cell set, cell object list
    :param N: 细胞维诺图种子数（保留参数，不再用于限制循环次数） Seed number of cell Vinot map (reserved, no longer used for loop bound)
    """
    # 初始时，边缘细胞已由 setting_layer() 标记为第1层
    # 使用BFS逐层标记：第2层只标记与第1层相邻的，第3层只标记与第2层相邻的...
    
    # 获取第1层的细胞作为初始队列
    current_layer_cells = [c for c in cells if c.layer == 1]
    current_layer = 1
    
    while current_layer_cells:
        next_layer_cells = []
        next_layer = current_layer + 1
        
        for c in current_layer_cells:
            # 找到所有与当前层细胞相邻的未标记细胞
            for tc in cells:
                if tc.layer != 0:  # 已标记的跳过
                    continue
                
                # 判断是否相邻（共享至少一个点）
                is_neighbor = False
                for cp in c.points:
                    if cp in tc.points:
                        is_neighbor = True
                        break
                
                if is_neighbor:
                    tc.layer = next_layer
                    next_layer_cells.append(tc)
        
        current_layer_cells = next_layer_cells
        current_layer = next_layer


'''
    周边探索法II，作用于非整齐细胞矩阵的情况。
    Peripheral exploration method
    :param cells: 细胞集，Cell对象列表 Cell set, cell object list
    :param N: 细胞维诺图种子数  Seed number of cell Vinot map
'''


def layer_mark3(cells):
    index = 2
    while True:
        flag = True

        for c in cells:
            # print(c.layer)
            if not c.layer == 0:  # 如果该细胞已被标记，则进行下一次循环 If the cell has been labeled, the next cycle is performed
                continue
            else:
                flag = False
            for tc in cells:  # 判断周围细胞 Judging the surrounding cells
                if tc.layer == 0 or tc.layer == index:  # 如果待判断细胞为未标记细胞 或 该待测细胞为同层，则没有判断的必要 If the cells to be determined are unlabeled cells or the cells to be tested are in the same layer, there is no need to judge
                    continue
                for cp in c.points:  # 循环判断各个细胞点是否在待测细胞中  Cycle to determine whether each cell point is in the cell to be tested
                    if cp in tc.points:  # 如果在，则进行标记（此处不需要判断外围细胞是否已标记） If yes, mark it (there is no need to judge whether the peripheral cells have been labeled)
                        c.layer = index
        index += 1
        if flag:
            break


'''
    循环探索法。 本方法不适用维诺图模型，已弃用
    Cycle exploration method. This method is not suitable for veno map model and has been abandoned
    :param cells: 细胞集，Cell对象列表 Cell set, cell object list
    :param N: 细胞维诺图种子数  Seed number of cell Vinot map
'''
def layer_mark(cells, N):
    for index in range(2,int(int(N)/2+1)):
        # 正序遍历左侧和上侧
        row_control = False
        rowc_times = 0
        col_control = False
        colc_times = 0
        row = 1
        col = 1
        pre = -1
        for i in range(len(cells)):
            if not cells[i].layer==pre and pre==1:
                if row_control: # 发现行控制器打开
                    row_control=False # 关闭行控制器
                row+=1 # 换行
                col=2 # 列初始化
                col_control = False # 列控制器初始化，下同
                colc_times = 0


            if cells[i].layer==0 and not row_control and rowc_times==0: # 出现0、行控制器是关闭状态 且 行控制器从未打开过

                row_control=True # 打开行控制器，下次换行时关闭
                rowc_times+=1 # 行控制器打开次数+1 避免下次重复打开

            if cells[i].layer==0 and not col_control and  colc_times==0: # 出现0、列控制器是关闭状态 且 列控制器从未打开过（在本行内）
                col_control=True # 打开列控制器，使用结束后立刻关闭
                colc_times+=1 # 列控制器打开次数+1 避免下次重复打开

            if cells[i].layer==0 and not cells[i].layer==pre and (row_control or col_control):
                cells[i].layer = index
                if col_control: # 发现列控制器打开
                    col_control=False # 关闭列控制器
            #print(row,col)
            col+=1 # 列在使用完后进行+1
            pre = cells[i].layer # 前置数据更新

        # 逆序遍历右侧和下侧
        row_control = False
        rowc_times = 0
        col_control = False
        colc_times = 0
        row = 1
        col = 1
        pre = -1
        for i in range(len(cells)-1,-1,-1):
            if not cells[i].layer==pre and pre==1:
                if row_control: # 发现行控制器打开
                    row_control=False # 关闭行控制器
                row+=1 # 换行
                col=2 # 列初始化
                col_control = False # 列控制器初始化，下同
                colc_times = 0


            if cells[i].layer==0 and not row_control and rowc_times==0: # 出现0、行控制器是关闭状态 且 行控制器从未打开过

                row_control=True # 打开行控制器，下次换行时关闭
                rowc_times+=1 # 行控制器打开次数+1 避免下次重复打开

            if cells[i].layer==0 and not col_control and  colc_times==0: # 出现0、列控制器是关闭状态 且 列控制器从未打开过（在本行内）
                col_control=True # 打开列控制器，使用结束后立刻关闭
                colc_times+=1 # 列控制器打开次数+1 避免下次重复打开

            if cells[i].layer==0 and not cells[i].layer==pre and (row_control or col_control):
                cells[i].layer = index
                if col_control: # 发现列控制器打开
                    col_control=False # 关闭列控制器
            #print(row,col)
            col+=1 # 列在使用完后进行+1
            pre = cells[i].layer # 前置数据更新
