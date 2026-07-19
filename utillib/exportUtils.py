import openpyxl
from openpyxl.styles import Font, colors, Alignment
from openpyxl.utils import get_column_letter
import time
import math
import os
import cell
import utillib.i18n as i18n


'''
    椭圆拟合数据表
'''
def ellipse(excelName,cells,lineOfCell, edge_judge, currentTimes, ignore, printTime=''):

    workbook=openpyxl.Workbook()
    sheet =workbook.active

    # 添加表头
    # Add a header
    ellipse_headings = get_ellipse_headings()
    for i in range(len(ellipse_headings)):
        sheet.cell(row=1,column=i+1,value=ellipse_headings[i]).alignment=align
        if i<26:
            sheet.column_dimensions[chr(65+i)].width=18
        else:
            sheet.column_dimensions['A'+chr(65+i-26)].width=18

    i=0
    for c in cells:
        # if not c.ok:
        #     continue

        l=len(c.points)
        totalEdge=0
        perimeter=0
        # 判断是否存在相邻细胞
        # To see if there are adjacent cells
        for j in range(l):
            perimeter+=get_distance_point_point(c.points[j-1], c.points[j])
            string='{0}-{1}-{2}-{3}'.format(c.points[j][0],c.points[j][1],c.points[j-1][0],c.points[j-1][1])
            if string in lineOfCell:
                totalEdge+=len(lineOfCell[string].points)


        '''
        if (not c.ok) and edge_judge:
            continue
        '''
        sheet.cell(row=2+i,column=1,value=c.no).alignment=align

        ellipse_data = c.data
        add_points = c.add_points

        sheet.cell(row=2+i,column=2,value=str('('+str(ellipse_data['cp'].x)+','+str(ellipse_data['cp'].y)+')')).alignment=align
        sheet.cell(row=2+i,column=3,value=ellipse_data['a']).alignment=align
        sheet.cell(row=2+i,column=4,value=ellipse_data['b']).alignment=align
        sheet.cell(row=2+i,column=5,value=ellipse_data['angle']).alignment=align

        sheet.cell(row=2+i,column=6,value=totalEdge).alignment=align
        sheet.cell(row=2+i,column=7,value=l).alignment=align
        sheet.cell(row=2+i,column=8,value=perimeter).alignment=align
        sheet.cell(row=2+i,column=9,value=c.area).alignment=align

        # ================= [修改后的层数写入逻辑] =================
        # 1. 获取最初母细胞层数
        original_layer = getattr(c, 'original_layer', c.layer)

        # 2. 写入最初母细胞层数到第 10 列
        sheet.cell(row=2+i,column=10,value=original_layer).alignment=align

        # 3. 写入当前细胞层数到第 11 列
        sheet.cell(row=2+i,column=11,value=c.layer).alignment=align

        # 4. 整个循环体内【只保留这一个】i += 1，表示该细胞处理完毕，下一行准备写下一个细胞
        i += 1
        # =========================================================

    sheet.column_dimensions['B'].width = 45.0
    workbook.save('{0}_{1}.xlsx'.format(excelName, currentTimes))
    return True


def edgeangle(excelName,cells,lineOfCell, edge_judge, currentTimes, ignore, printTime=''):

    workbook=openpyxl.Workbook()
    sheet =workbook.active

    # 添加表头
    # Add a header
    edgeangle_headings = get_edgeangle_headings()
    for i in range(len(edgeangle_headings)):
        sheet.cell(row=1, column=i+1, value=edgeangle_headings[i]).alignment=align
        if i < 26:
            sheet.column_dimensions[chr(65+i)].width=18
        else:
            sheet.column_dimensions['A'+chr(65+i-26)].width=18

    i=0
    for c in cells:
        # if not c.ok:
        #     continue

        l=len(c.points)
        totalEdge=0
        # 判断是否存在相邻细胞
        # To see if there are adjacent cells
        for j in range(l):
            string='{0}-{1}-{2}-{3}'.format(c.points[j][0],c.points[j][1],c.points[j-1][0],c.points[j-1][1])
            if string in lineOfCell:
                totalEdge+=len(lineOfCell[string].points)

        for j in range(l):
            sheet.cell(row=2+i,column=1,value=c.no).alignment=align
            sheet.cell(row=2+i,column=2,value=len(c.points)).alignment=align
            sheet.cell(row=2+i,column=3,value=totalEdge).alignment=align

            p1 = c.points[j-1]
            p = c.points[j]
            p2 = c.points[(j+1)%l]

            angle = get_angle_by_three_point([p1,p,p2])
            d1 = get_distance_point_point(p1, p)
            d2 = get_distance_point_point(p, p2)

            sheet.cell(row=2+i,column=4,value=angle).alignment=align
            sheet.cell(row=2+i,column=5,value=d1).alignment=align
            sheet.cell(row=2+i,column=6,value=d2).alignment=align
            sheet.column_dimensions[get_column_letter(4)].width = 20.0
            sheet.column_dimensions[get_column_letter(5)].width = 20.0
            sheet.column_dimensions[get_column_letter(6)].width = 20.0

            # 1. 获取最初母细胞层数
            original_layer = getattr(c, 'original_layer', c.layer)

            # 2. 写入最初母细胞层数 (对应表头第7列)
            sheet.cell(row=2+i, column=7, value=original_layer).alignment = align

            # 3. 写入当前细胞层数 (对应表头第8列)
            sheet.cell(row=2+i, column=8, value=c.layer).alignment = align

            # 4. 游标 +1，准备写入该细胞的下一个角，或者下一个细胞
            i += 1

    sheet.column_dimensions[get_column_letter(7)].width = 15.0
    workbook.save('{0}_{1}.xlsx'.format(excelName, currentTimes))
    return True


# 将分裂情况填写到上一个文件
# Fill in the split in the previous file
def appendData(excelName,lastSplitData,currentTimes):
    if currentTimes < 1:
        print(0)
        return
    lastFile='{0}_{1}.xlsx'.format(excelName, currentTimes-1)
    print(lastFile)
    if os.path.isfile(lastFile):
        workbook=openpyxl.load_workbook(lastFile)
        sheet=workbook.active
    else:
        print(1)
        return

    sheet.cell(row=1, column=12, value="是否分裂").alignment=align
    sheet.cell(row=1, column=13, value="子细胞比例").alignment=align
    sheet.column_dimensions['L'].width = 15
    sheet.column_dimensions['M'].width = 15

    length = len(lastSplitData)
    for i in range(length):
        if lastSplitData[i][0]:
            c=sheet.cell(row=i+2,column=12,value='Divide')
            c.font=Font(color='ff0000')
            sheet.cell(row=i+2,column=13,value=lastSplitData[i][1]).alignment=align
        else :
            c=sheet.cell(row=i+2,column=12,value='non-divide')
        c.alignment=align
    workbook.save(lastFile)


def export_ME_MA_1(excelName, cells, edge_judge, currentTimes):
    """
    导出 ME (边缘边长) 和 MA (边缘角) 到单独的 Excel 表格
    """
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "ME_MA_Statistics"

    # 设置表头
    me_ma_headings_detail = i18n.languages[i18n.current_language].get('me_ma_headings_detail', 
        ["细胞序号", "参数类型", "数值", "单位", "位置索引(点/边)", "细胞层数"])
    headings = me_ma_headings_detail
    for i, h in enumerate(headings):
        sheet.cell(row=1, column=i+1, value=h).alignment = align
        sheet.column_dimensions[get_column_letter(i+1)].width = 15

    # 1. 统计所有边的出现次数，以识别边缘边 (ME)
    edge_counts = {}
    for c in cells:
        l = len(c.points)
        for j in range(l):
            p1 = tuple(c.points[j-1])
            p2 = tuple(c.points[j])
            # 排序以保证无向性
            edge_key = tuple(sorted((p1, p2)))
            edge_counts[edge_key] = edge_counts.get(edge_key, 0) + 1

    # 提取所有边缘边 (只出现一次的边)
    boundary_edges = {k for k, v in edge_counts.items() if v == 1}

    row_idx = 2
    for c in cells:
        # 只处理边缘层的细胞 (Layer 1)
        if c.layer != 1:
            continue

        l = len(c.points)
        for j in range(l):
            p_prev = c.points[j-1]
            p_curr = c.points[j]
            p_next = c.points[(j+1)%l]

            # 定义当前点连接的两条边
            edge_prev_key = tuple(sorted((tuple(p_prev), tuple(p_curr))))
            edge_next_key = tuple(sorted((tuple(p_curr), tuple(p_next))))

            # --- 输出 ME (边缘边长) ---
            if edge_next_key in boundary_edges:
                dist = get_distance_point_point(p_curr, p_next)

                sheet.cell(row=row_idx, column=1, value=c.no).alignment = align
                sheet.cell(row=row_idx, column=2, value="ME (边缘边长)").alignment = align
                sheet.cell(row=row_idx, column=3, value=dist).alignment = align
                sheet.cell(row=row_idx, column=4, value="Pixel").alignment = align
                sheet.cell(row=row_idx, column=5, value=f"Edge {j}-{(j+1)%l}").alignment = align
                sheet.cell(row=row_idx, column=6, value=c.layer).alignment = align
                row_idx += 1

            # --- 输出 MA (边缘角) ---
            if edge_prev_key in boundary_edges or edge_next_key in boundary_edges:
                angle = get_angle_by_three_point([p_prev, p_curr, p_next])
                angle_deg = math.degrees(angle)

                sheet.cell(row=row_idx, column=1, value=c.no).alignment = align
                sheet.cell(row=row_idx, column=2, value="MA (边缘角)").alignment = align
                sheet.cell(row=row_idx, column=3, value=angle_deg).alignment = align
                sheet.cell(row=row_idx, column=4, value="Degree").alignment = align
                sheet.cell(row=row_idx, column=5, value=f"Vertex {j}").alignment = align
                sheet.cell(row=row_idx, column=6, value=c.layer).alignment = align
                row_idx += 1

    filename = '{0}_ME_MA_{1}.xlsx'.format(excelName, currentTimes)
    workbook.save(filename)
    return True


def export_ME_MA(excelName, cells, edge_judge, currentTimes):
    """
    导出 ME (边缘边长) 和 MA (边缘角) 到单独的 Excel 表格
    按照老师要求：将一个边缘细胞的两个边缘角(MA)和一个边缘边(ME)以及层数放在一行
    """
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "ME_MA_Statistics"

    # 设置新的扁平化表头
    me_ma_headings = i18n.languages[i18n.current_language].get('me_ma_headings', 
        ["细胞序号", "边缘边长(ME)", "边缘角1(MA1)", "边缘角2(MA2)", "最初母细胞层数", "当前细胞层数"])
    headings = me_ma_headings
    for i, h in enumerate(headings):
        sheet.cell(row=1, column=i+1, value=h).alignment = align
        sheet.column_dimensions[get_column_letter(i+1)].width = 18

    # 1. 统计所有边的出现次数，以识别边缘边 (ME)
    edge_counts = {}
    for c in cells:
        l = len(c.points)
        for j in range(l):
            p1 = tuple(c.points[j-1])
            p2 = tuple(c.points[j])
            edge_key = tuple(sorted((p1, p2)))
            edge_counts[edge_key] = edge_counts.get(edge_key, 0) + 1

    # 提取所有边缘边 (只出现一次的边)
    boundary_edges = {k for k, v in edge_counts.items() if v == 1}

    row_idx = 2
    for c in cells:
        # 按照规定，边缘细胞为第一层，向内递增。这里只处理边缘细胞 (Layer 1)
        if c.layer != 1:
            continue

        mes = []
        mas = []

        l = len(c.points)
        for j in range(l):
            p_prev = c.points[j-1]
            p_curr = c.points[j]
            p_next = c.points[(j+1)%l]

            edge_prev_key = tuple(sorted((tuple(p_prev), tuple(p_curr))))
            edge_next_key = tuple(sorted((tuple(p_curr), tuple(p_next))))

            # 记录边缘边长
            if edge_next_key in boundary_edges:
                dist = get_distance_point_point(p_curr, p_next)
                mes.append(dist)

            # 记录边缘角 (如果顶点连接的任意一条边是边缘边)
            if edge_prev_key in boundary_edges or edge_next_key in boundary_edges:
                angle = get_angle_by_three_point([p_prev, p_curr, p_next])
                mas.append(math.degrees(angle))

        # 提取数据：标准的边缘细胞(不在死角)通常会有1条边缘边和2个边缘角
        me_val = mes[0] if len(mes) > 0 else "N/A"
        ma1_val = mas[0] if len(mas) > 0 else "N/A"
        ma2_val = mas[1] if len(mas) > 1 else "N/A"

        original_layer = getattr(c, 'original_layer', c.layer)

        sheet.cell(row=row_idx, column=1, value=c.no).alignment = align
        sheet.cell(row=row_idx, column=2, value=me_val).alignment = align
        sheet.cell(row=row_idx, column=3, value=ma1_val).alignment = align
        sheet.cell(row=row_idx, column=4, value=ma2_val).alignment = align
        sheet.cell(row=row_idx, column=5, value=original_layer).alignment = align
        sheet.cell(row=row_idx, column=6, value=c.layer).alignment = align
        row_idx += 1

    filename = '{0}_ME_MA_{1}.xlsx'.format(excelName, currentTimes)
    workbook.save(filename)
    return True


def create(excelName, cells, lineOfCell, edge_judge, N, ignore, currentTimes=0):
    # 依次调用三个导出函数：椭圆数据、边角数据、ME/MA数据
    res_me_ma = export_ME_MA(excelName, cells, edge_judge, currentTimes)

    # 调用原有的 ellipse 和 edgeangle 函数
    if ellipse("ellipse", cells, lineOfCell, edge_judge, currentTimes, ignore) \
        and edgeangle("edgeAngle", cells, lineOfCell, edge_judge, currentTimes, ignore) \
        and res_me_ma:
        return True
    else:
        return False


"""
    根据三个点获取角度，第二个点作为角中心点。（依据公式进行计算）
    The angle is obtained from three points, and the second point is used as the center point of the corner. (calculated according to the formula)
    :param p_list: 数组，包含三个点。 Array containing three points.
    :return: 角度 angle
"""
def get_angle_by_three_point(p_list):

    a = math.sqrt((p_list[1][0] - p_list[2][0]) * (p_list[1][0] - p_list[2][0]) + (p_list[1][1] - p_list[2][1]) * (p_list[1][1] - p_list[2][1]))
    b = math.sqrt((p_list[0][0] - p_list[2][0]) * (p_list[0][0] - p_list[2][0]) + (p_list[0][1] - p_list[2][1]) * (p_list[0][1] - p_list[2][1]))
    c = math.sqrt((p_list[1][0] - p_list[0][0]) * (p_list[1][0] - p_list[0][0]) + (p_list[1][1] - p_list[0][1]) * (p_list[1][1] - p_list[0][1]))

    if (a*a + c*c -b*b)/(2*a*c) >= -1 and (a*a + c*c -b*b)/(2*a*c) <=1:
        angle = math.acos((a*a + c*c -b*b)/(2*a*c))
    elif (a*a + c*c -b*b)/(2*a*c) < -1:
        angle = math.acos(-1)
    elif (a*a + c*c -b*b)/(2*a*c) > 1:
        angle = math.acos(1)

    return angle


"""
    计算两点之间的距离(根据公式进行计算)
    Calculate the distance between two points (according to the formula)
    :param p1: Point对象 Point object
    :param l2: Point对象 Point object
    :return: 距离 distance
"""
def get_distance_point_point(p1, p2):

    distance = math.sqrt((p1[0] - p2[0])*(p1[0] - p2[0]) +
                                 (p1[1] - p2[1])*(p1[1] - p2[1]))
    return distance


def get_before_headings():
    return i18n.languages[i18n.current_language].get('before_headings', ["拟合椭圆数据","细胞基本数据"])

def get_ellipse_headings():
    return i18n.languages[i18n.current_language].get('ellipse_headings', [
        "细胞序号",
        "椭圆中心点",
        "长半轴",
        "短半轴",
        "短半轴与x轴的夹角",
        "相邻细胞边数和",
        "细胞边数",
        "细胞周长",
        "细胞面积",
        "最初母细胞层数",
        "当前细胞层数"
    ])

def get_edgeangle_headings():
    return i18n.languages[i18n.current_language].get('edgeangle_headings', [
        "细胞序号",
        "边数",
        "相邻细胞边数和",
        "内角",
        "夹边1",
        "夹边2",
        "最初母细胞层数",
        "当前细胞层数"
    ])

def get_headings():
    return i18n.languages[i18n.current_language].get('headings', [
        "细胞序号",
        "椭圆中心点",
        "长半轴",
        "短半轴",
        "短半轴与x轴的夹角",
        "从属层",
        "边数",
        "面积",
        "相邻细胞边数和",
        "内角1",
        "角1夹边1",
        "角1夹边2",
        "内角2",
        "角2夹边1",
        "角2夹边2",
        "内角3",
        "角3夹边1",
        "角3夹边2",
        "内角4",
        "角4夹边1",
        "角4夹边2",
        "内角5",
        "角5夹边1",
        "角5夹边2",
        "内角6",
        "角6夹边1",
        "角6夹边2",
        "内角7",
        "角7夹边1",
        "角7夹边2",
        "内角8",
        "角8夹边1",
        "角8夹边2",
        "更多..."
    ])

align=Alignment(horizontal='center',vertical='center',wrap_text=True)
