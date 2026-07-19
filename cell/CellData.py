import numpy as np
import time
import math
class CellData:
    cells = []
    sumArea = 0  # 当前总面积 Current total area
    averageArea = 0
    length = 0
    lineOfCell = {}

    def __init__(self, cells):
        self.init(cells)
#-----------------------------

    # def is_marginally_cell(self, cell):
    #     mc_cells = []
    #     for c in self.cells:
    #         is_mc = False
    #         for i in range(len(c.points)):
    #             p1 = c.points[i-1]
    #             p2 = c.points[i]
    #             a = min(p1, p2)
    #             b = max(p1, p2)
    #             key = f"{a[0]}-{a[1]}-{b[0]}-{b[1]}"
    #             owners = self.lineOfCell.get(key, [])
    #             if len(owners) == 1 and owners[0] is c:
    #                 is_mc = True
    #                 break
    #         if is_mc:
    #             c.cell_tier = 1
    #             mc_cells.append(c)
    #     return mc_cells

    # def is_marginally_neighbor_cells_last(self,cell):
    #     """
    #     判断细胞是否位于NC-MC层,返回列表
    #     """
    #     nc_mc_cells=[]
    #     for cell_list in self.lineOfCell.values():
    #         #如果键值对的键==2，并且键值对中该键的值对应的细胞有一个为边缘细胞
    #         if len(cell_list) == 2 and  cell_list.cell.tier == 1 :
    #             print("识别出NC-MC细胞")
    #             cell.cell_tier = 2
    #             nc_mc_cells.append(cell)
    #     return nc_mc_cells

    # def is_marginally_neighbor_cells_last(self, cell):
    #     """
    #     判断细胞是否位于NC-MC层,返回列表
    #     """
    #     nc_mc_cells = []
    #     for cell_list in self.lineOfCell.values():
    #         # 检查条件：如果边被2个细胞共享，并且其中至少有一个细胞的tier为1（MC细胞）
    #         if len(cell_list) == 2:
    #             # 检查这两个细胞中是否有一个是MC细胞（tier=1）
    #             has_mc_cell = any(c.cell_tier == 1 for c in cell_list)

    #             if has_mc_cell:
    #                 # 找出不是MC细胞的另一个细胞
    #                 for c in cell_list:
    #                     if c.cell_tier != 1:  # 这个细胞不是MC细胞
    #                         print("识别出NC-MC细胞")
    #                         c.cell_tier = 2
    #                         if c not in nc_mc_cells:  # 避免重复添加
    #                             nc_mc_cells.append(c)

    #     return nc_mc_cells

    # def is_marginally_neighbor_cells(self, cell):
    #     #print("第一次识别代码：识别出NC-MC细胞")
    #     nc_mc_cells = []
    #     mc_set = {c for c in self.cells if getattr(c, 'cell_tier', 0) == 1}
    #     for c in self.cells:
    #         if getattr(c, 'cell_tier', 0) != 0:
    #             continue
    #         is_nc_mc = False
    #         for i in range(len(c.points)):
    #             p1 = c.points[i-1]
    #             p2 = c.points[i]
    #             a = min(p1, p2)
    #             b = max(p1, p2)
    #             key = f"{a[0]}-{a[1]}-{b[0]}-{b[1]}"
    #             owners = self.lineOfCell.get(key, [])
    #             if len(owners) >= 2 and any(o in mc_set for o in owners):
    #                 #print("第一次识别代码：正确识别出NC-MC细胞")
    #                 is_nc_mc = True
    #                 # c.cell_tier = 2
    #                 # nc_mc_cells.append(c)
    #                 break
    #         if is_nc_mc:
    #             c.cell_tier = 2
    #             nc_mc_cells.append(c)
    #     return nc_mc_cells

    # def calculate_slope(self, p1, p2):
    #     """
    #     计算两点之间线段的斜率

    #     Args:
    #         p1, p2: 两个点的坐标 [x, y]

    #     Returns:
    #         float: 线段的斜率，如果是垂直线返回无穷大(float('inf'))
    #     """
    #     dx = p2[0] - p1[0]
    #     dy = p2[1] - p1[1]

    #     if abs(dx) < 1e-9:  # 垂直线
    #         return float('inf')

    #     return dy / dx

    # def is_slope_similar(self, slope1, slope2, tolerance=0.1):
    #     """
    #     检查两个斜率是否相似

    #     Args:
    #         slope1, slope2: 要比较的两个斜率
    #         tolerance: 容差范围

    #     Returns:
    #         bool: 如果斜率相似返回True，否则返回False
    #     """
    #     # 处理垂直线的情况
    #     if slope1 == float('inf') and slope2 == float('inf'):
    #         return True
    #     elif slope1 == float('inf') or slope2 == float('inf'):
    #         return False

    #     # 计算斜率差的绝对值
    #     slope_diff = abs(slope1 - slope2)

    #     # 考虑斜率可能很大或很小的情况，使用相对误差
    #     if max(abs(slope1), abs(slope2)) > 1:
    #         relative_diff = slope_diff / max(abs(slope1), abs(slope2))
    #         return relative_diff < tolerance
    #     else:
    #         return slope_diff < tolerance

    # def is_point_similar(self, p1, p2, tolerance=1.0):
    #     """
    #     检查两个点是否相似（坐标相近）

    #     Args:
    #         p1, p2: 要比较的两个点 [x, y]
    #         tolerance: 坐标容差

    #     Returns:
    #         bool: 如果点相似返回True，否则返回False
    #     """
    #     dx = abs(p1[0] - p2[0])
    #     dy = abs(p1[1] - p2[1])
    #     return dx < tolerance and dy < tolerance
    # def is_third_tier_cells(self, cell):
    #     """
    #     判断细胞是否位于第三层,返回列表
    #     """
    #     third_tier_cells = []
    #     for cell_list in self.lineOfCell.values():
    #         # 检查条件：如果边被2个细胞共享，并且其中至少有一个细胞的tier为1（MC细胞）
    #         if len(cell_list) == 2:
    #             # 检查这两个细胞中是否有一个是NC-MC细胞（tier=2）
    #             has_mc_cell = any(c.cell_tier == 2 for c in cell_list)

    #             if has_mc_cell:
    #                 # 找出不是MC细胞的另一个细胞
    #                 for c in cell_list:
    #                     if c.cell_tier != 2:  # 这个细胞不是MC细胞
    #                         print("识别出第三层细胞")
    #                         c.cell_tier = 3
    #                         if c not in third_tier_cells:  # 避免重复添加
    #                             third_tier_cells.append(c)

    #     return third_tier_cells


    # def identify_marginal_cells(self):
    #     """识别边缘细胞(MC)"""
    #     mc_cells = []
    #     for cell in self.cells:
    #         is_marginal = False
    #         for i in range(len(cell.points)):
    #             p1 = cell.points[i-1]
    #             p2 = cell.points[i]
    #             # 创建规范化的边键
    #             if (p1[0], p1[1]) < (p2[0], p2[1]):
    #                 sorted_p1, sorted_p2 = p1, p2
    #             else:
    #                 sorted_p1, sorted_p2 = p2, p1
    #             canonical_key = f'{sorted_p1[0]}-{sorted_p1[1]}-{sorted_p2[0]}-{sorted_p2[1]}'

    #             # 如果这条边不在lineOfCell中，说明是边界边
    #             if canonical_key not in self.lineOfCell:
    #                 is_marginal = True
    #                 break

    #         if is_marginal:
    #             mc_cells.append(cell)
    #             cell.cell_tier = 1  # 设置Cell类的tier属性
    #     return mc_cells

    # def identify_marginal_cells(self):
    #     """
    #     识别并标记位于最外层的边缘细胞 (Marginal Cells, MC)
    #     MC: 至少有一条边位于网络边界（该边不与其他多边形共用）
    #     """
    #     mc_cells = []
    #     for cell in self.cells:
    #         is_marginal = False
    #         # 检查每条边是否在lineOfCell中（即是否与其他细胞共享）
    #         for i in range(len(cell.points)):
    #             p1 = cell.points[i-1]
    #             p2 = cell.points[i]
    #             # 创建规范化的边键,使得点/线排序顺序唯一
    #             if (p1[0], p1[1]) < (p2[0], p2[1]):
    #                 sorted_p1, sorted_p2 = p1, p2
    #             else:
    #                 sorted_p1, sorted_p2 = p2, p1
    #             canonical_key = f'{sorted_p1[0]}-{sorted_p1[1]}-{sorted_p2[0]}-{sorted_p2[1]}'

    #             # 如果这条边不在lineOfCell中，说明是边界边
    #             if canonical_key not in self.lineOfCell:
    #                 is_marginal = True
    #                 break

    #         if is_marginal:
    #             mc_cells.append(cell)
    #             cell.cell_tier = 1  # 标记为MC层
    #     return mc_cells

    # def identify_neighbor_cells_last(self, mc_cells):
    #     """
    #     识别并标记与MC细胞相邻的细胞 (Neighbor Cells, NC-MC)
    #     """
    #     nc_mc_cells = []
    #     mc_cell_set = set(mc_cells)

    #     for mc_cell in mc_cell_set:
    #         # 查找与MC细胞共享边的邻居细胞
    #         for i in range(len(mc_cell.points)):
    #             p1 = mc_cell.points[i-1]
    #             p2 = mc_cell.points[i]
    #             # 创建规范化的边键
    #             if (p1[0], p1[1]) < (p2[0], p2[1]):
    #                 sorted_p1, sorted_p2 = p1, p2
    #             else:
    #                 sorted_p1, sorted_p2 = p2, p1
    #             canonical_key = f'{sorted_p1[0]}-{sorted_p1[1]}-{sorted_p2[0]}-{sorted_p2[1]}'

    #             # 如果这条边在lineOfCell中，说明有共享细胞
    #             if canonical_key in self.lineOfCell:
    #                 neighbor_cells = self.lineOfCell[canonical_key]
    #                 for neighbor in neighbor_cells:
    #                     if neighbor != mc_cell and neighbor not in mc_cell_set and getattr(neighbor, 'cell_tier', 0) == 0:
    #                         neighbor.cell_tier = 2  # 标记为NC-MC层
    #                         nc_mc_cells.append(neighbor)

    #     return nc_mc_cells
    # def identify_neighbor_cells(self, mc_cells):
    #     """
    #     识别并标记与MC细胞相邻的细胞 (Neighbor Cells, NC-MC)
    #     新的标记逻辑：如果细胞有一条边与MC细胞共享，且有一条边与未标记细胞共享，则标记为NC-MC
    #     """
    #     nc_mc_cells = []
    #     mc_cell_set = set(mc_cells)

    #     print(f"[DEBUG] 开始识别NC-MC，MC细胞数量: {len(mc_cells)}")

    #     # 收集所有与MC细胞相邻的细胞
    #     all_neighbors = set()
    #     mc_neighbors = {}  # 记录每个细胞与哪些MC细胞相邻

    #     for mc_cell in mc_cell_set:
    #         for i in range(len(mc_cell.points)):
    #             p1 = mc_cell.points[i-1]
    #             p2 = mc_cell.points[i]
    #             # 创建规范化的边键
    #             if (p1[0], p1[1]) < (p2[0], p2[1]):
    #                 sorted_p1, sorted_p2 = p1, p2
    #             else:
    #                 sorted_p1, sorted_p2 = p2, p1
    #             canonical_key = f'{sorted_p1[0]}-{sorted_p1[1]}-{sorted_p2[0]}-{sorted_p2[1]}'

    #             # 如果这条边在lineOfCell中，说明有共享细胞
    #             if canonical_key in self.lineOfCell:
    #                 neighbor_cells = self.lineOfCell[canonical_key]
    #                 for neighbor in neighbor_cells:
    #                     if neighbor != mc_cell and neighbor not in mc_cell_set:
    #                         all_neighbors.add(neighbor)
    #                         if neighbor not in mc_neighbors:
    #                             mc_neighbors[neighbor] = set()
    #                         mc_neighbors[neighbor].add(mc_cell)

    #     print(f"[DEBUG] 找到与MC相邻的细胞数量: {len(all_neighbors)}")

    #     # 检查每个候选细胞是否也有一条边与未标记细胞共享
    #     for candidate in all_neighbors:
    #         # 如果细胞已经被标记，跳过
    #         if getattr(candidate, 'cell_tier', 0) != 0:
    #             continue

    #         has_unmarked_neighbor = False

    #         # 检查这个细胞的所有边
    #         for i in range(len(candidate.points)):
    #             p1 = candidate.points[i-1]
    #             p2 = candidate.points[i]
    #             # 创建规范化的边键
    #             if (p1[0], p1[1]) < (p2[0], p2[1]):
    #                 sorted_p1, sorted_p2 = p1, p2
    #             else:
    #                 sorted_p1, sorted_p2 = p2, p1
    #             canonical_key = f'{sorted_p1[0]}-{sorted_p1[1]}-{sorted_p2[0]}-{sorted_p2[1]}'

    #             # 如果这条边在lineOfCell中
    #             if canonical_key in self.lineOfCell:
    #                 neighbor_cells = self.lineOfCell[canonical_key]
    #                 for neighbor in neighbor_cells:
    #                     if (neighbor != candidate and
    #                         getattr(neighbor, 'cell_tier', 0) == 0 and
    #                         neighbor not in mc_cell_set):
    #                         # 找到与未标记细胞共享的边
    #                         has_unmarked_neighbor = True
    #                         break

    #                 if has_unmarked_neighbor:
    #                     break

    #         # 如果细胞满足条件：与MC相邻且与未标记细胞相邻
    #         if candidate in mc_neighbors and has_unmarked_neighbor:
    #             candidate.cell_tier = 2  # 标记为NC-MC层
    #             nc_mc_cells.append(candidate)
    #             print(f"[DEBUG] 细胞 {candidate.no} 被标记为NC-MC")

    #     print(f"[DEBUG] 最终标记的NC-MC数量: {len(nc_mc_cells)}")

    #     return nc_mc_cells


    # def identify_third_layer_cells(self, mc_cells, nc_mc_cells):
    #     """
    #     识别第三层细胞：与NC-MC有共用边，但既不是MC也不是NC-MC
    #     """
    #     third_layer_cells = []
    #     mc_cell_set = set(mc_cells)
    #     nc_mc_cell_set = set(nc_mc_cells)

    #     for nc_mc_cell in nc_mc_cell_set:
    #         # 查找与NC-MC细胞共享边的邻居细胞
    #         for i in range(len(nc_mc_cell.points)):
    #             p1 = nc_mc_cell.points[i-1]
    #             p2 = nc_mc_cell.points[i]
    #             # 创建规范化的边键
    #             if (p1[0], p1[1]) < (p2[0], p2[1]):
    #                 sorted_p1, sorted_p2 = p1, p2
    #             else:
    #                 sorted_p1, sorted_p2 = p2, p1
    #             canonical_key = f'{sorted_p1[0]}-{sorted_p1[1]}-{sorted_p2[0]}-{sorted_p2[1]}'

    #             if canonical_key in self.lineOfCell:
    #                 neighbor_cells = self.lineOfCell[canonical_key]
    #                 for neighbor in neighbor_cells:
    #                     if (neighbor != nc_mc_cell and
    #                         neighbor not in mc_cell_set and
    #                         neighbor not in nc_mc_cell_set and
    #                         getattr(neighbor, 'cell_tier', 0) == 0):
    #                         neighbor.cell_tier = 3  # 标记为第三层
    #                         third_layer_cells.append(neighbor)

    #     return third_layer_cells

    # def identify_inner_cells(self):
    #     """
    #     识别内部细胞IC：剩下的未标记细胞
    #     """
    #     ic_cells = []
    #     for cell in self.cells:
    #         if getattr(cell, 'cell_tier', 0) == 0:  # 未被标记的细胞
    #             cell.cell_tier = 4  # 标记为IC层
    #             ic_cells.append(cell)
    #     return ic_cells

    # def tier_cells(self, cell):
    #     # 确保所有细胞都有 cell_tier 属性
    #     for c in self.cells:
    #         if not hasattr(c, 'cell_tier'):
    #             c.cell_tier = 0
    #     # 更新线段归属字典
    #     self.list_line_of_cell()
    #     # 计算并标记 MC 和 NC-MC
    #     mc_cells = self.is_marginally_cell(cell)
    #     nc_mc_cells = self.is_marginally_neighbor_cells(cell)
    #     # print(f"[DEBUG] 找到的MC数量: {len(mc_cells)}")
    #     #print(f"[DEBUG] 找到的NC-MC数量: {len(nc_mc_cells)}")
    #     # 将剩余未标记的细胞标记为 IC
    #     ic_cells = []
    #     for c in self.cells:
    #         if getattr(c, 'cell_tier', 0) == 0:
    #             c.cell_tier = 4
    #             ic_cells.append(c)
    #     return {
    #         'tier1_mc': mc_cells,
    #         'tier2_nc_mc': nc_mc_cells,
    #         'tier4_ic': ic_cells
    #     }

    # def get_tier_name(self, tier_value):
    #     """
    #     根据分层值返回对应的分层名称
    #     """
    #     tier_mapping = {
    #         1: "MC",
    #         2: "NC-MC",
    #         # 3: "第三层",
    #         # 4: "IC",
    #         0: "未分类"
    #     }
    #     return tier_mapping.get(tier_value, "未知")
#-----------------------------
    def __str__(self):
        return ""

    # 细胞集参数初始化
    def init(self, cells):
        # 需求 5.4a: 记录上一轮移动的顶点数
        self.previous_internal_moved = 0
        self.previous_edge_moved = 0

        self.cells = cells
        self.length = len(cells)
        # 确保所有细胞都有cell_tier属性
        for cell in self.cells:
            if not hasattr(cell, 'cell_tier'):
                cell.cell_tier = 0

        for i in cells:
            self.sumArea += i.area
            i.setArea()

        self.averageArea = float('%.2f' % (self.sumArea / self.length))  # 平均面积 average area
        self.list_line_of_cell()
        # 初始化时进行分层
        #self.layer_cells()
        #self.tier_cells(cell)

    # 生长
    def grow(self):
        """按比例缩放网络以维持平均面积不变（每轮刷新时使用）"""
        # 维持平均面积不变，计算出成长比例b
        sArea = self.averageArea * self.length
        b = sArea / self.sumArea
        for c in self.cells:
            c.grow(np.sqrt(b))
        # 更新当前细胞图的总面积
        self.sumArea = sArea

    def topo_grow(self):
        for c in self.cells:
            c.setVertex()
            c.setArea()

    def list_line_of_cell_find_tier(self):
        """
        记录初始图中每条边的归属细胞

        Returns:
            dict: 以标准化边字符串为键，所属细胞对象列表为值的字典
        """
        lineOfCell = {}

        for j in range(len(self.cells)):
            cell = self.cells[j]
            for i in range(len(cell.points)):
                # 获取边的两个端点
                point1 = cell.points[i - 1]
                point2 = cell.points[i]

                # 标准化边方向：按坐标排序确保唯一性
                p1 = (min(point1, point2))  # 按坐标排序
                p2 = (max(point1, point2))

                # 生成标准化边标识
                edge_key = f"{p1[0]}-{p1[1]}-{p2[0]}-{p2[1]}"

                # 如果边不存在于字典中，初始化空列表
                if edge_key not in lineOfCell:
                    lineOfCell[edge_key] = []

                # 将当前细胞添加到该边的所属细胞列表
                # 避免重复添加同一个细胞
                if cell not in lineOfCell[edge_key]:
                    lineOfCell[edge_key].append(cell)

        self.lineOfCell = lineOfCell
        return lineOfCell

    def list_line_of_cell_new(self):
        # 将初始图的每条边的归属细胞记录
        # Record the attribution cell of each edge of the initial diagram
        lineOfCell = {}
        for j in range(len(self.cells)):
            cell = self.cells[j]
            for i in range(len(cell.points)):
                string = '{0}-{1}-{2}-{3}'.format(cell.points[i - 1][0], cell.points[i - 1][1], cell.points[i][0],
                                                  cell.points[i][1])
                lineOfCell[string] = cell
        # print(lineOfCell)
        self.lineOfCell = lineOfCell
        return lineOfCell

    def list_line_of_cell_last02(self):
        """
        生成细胞边归属字典，记录每条边被哪些细胞共享
        """
        lineOfCell = {}
        for cell in self.cells:
            for i in range(len(cell.points)):
                p1 = cell.points[i-1]
                p2 = cell.points[i]
                # 创建规范化的边键
                if (p1[0], p1[1]) < (p2[0], p2[1]):
                    sorted_p1, sorted_p2 = p1, p2
                else:
                    sorted_p1, sorted_p2 = p2, p1
                canonical_key = f'{sorted_p1[0]}-{sorted_p1[1]}-{sorted_p2[0]}-{sorted_p2[1]}'

                if canonical_key not in lineOfCell:
                    lineOfCell[canonical_key] = []
                # 确保不重复添加同一个细胞
                if cell not in lineOfCell[canonical_key]:
                    lineOfCell[canonical_key].append(cell)

        self.lineOfCell = lineOfCell



    def flush_last(self, isGrow=True, isListLineOfCell=True):
        self.length = len(self.cells)
        if isGrow:
            self.grow()
        else:
            self.topo_grow()

        if isListLineOfCell:
            self.list_line_of_cell()

        self.length = len(self.cells)

    def flush(self, isGrow=True, isListLineOfCell=True):
        self.length = len(self.cells)
        if isGrow:
            self.grow()
        else:
            self.topo_grow()

        if isListLineOfCell:
            self.list_line_of_cell()
            #print("键值对匹配成功")

        # 每次刷新时重新分层
        #self.tier_cells(self.cells)
        #刷新边缘细胞
        self.setting_layer()
        #self.layer_cells(self.cell)
        self.length = len(self.cells)



    ##进行细胞分层
    # def identify_marginal_cells(self):
    #     """
    #     识别并标记位于最外层的边缘细胞 (Marginal Cells, MC)
    #     """
    #     print(f"[DEBUG] lineOfCell 字典中的条目数量: {len(self.lineOfCell)}")
    #     # 打印前几条边及其对应的细胞ID，验证字典内容
    #     for i, (edge_str, cell) in enumerate(list(self.lineOfCell.items())[:3]):
    #         print(f"[DEBUG] 边示例 {i}: {edge_str} -> 细胞ID: {id(cell)}")
    #     mc_cells = []
    #     for cell in self.cells:
    #         is_marginal = False
    #         for i in range(len(cell.points)):
    #             p1 = cell.points[i-1]
    #             p2 = cell.points[i]
    #             # --- 修改点：使用与list_line_of_cell相同的规范化方法生成键 ---
    #             if (p1[0], p1[1]) < (p2[0], p2[1]):
    #                 sorted_p1, sorted_p2 = p1, p2
    #             else:
    #                 sorted_p1, sorted_p2 = p2, p1
    #             canonical_key = f'{sorted_p1[0]}-{sorted_p1[1]}-{sorted_p2[0]}-{sorted_p2[1]}'
    #             # --- 修改结束 ---

    #             # 如果这条规范化的键不在lineOfCell字典中，说明此边为边界边
    #             # if canonical_key not in self.lineOfCell:
    #             #     is_marginal = True
    #             #     break  # 只要找到一条边界边，就标记为边缘细胞
    #             if cell.ok!=True:
    #                 is_marginal = True

    #         if is_marginal:
    #             mc_cells.append(cell)
    #             cell.cell_tier = 1  # 标记为第一层
    #     return mc_cells

    # # def identify_marginal_cells(self):
    # #     """
    # #     识别并标记位于最外层的边缘细胞 (Marginal Cells, MC)
    # #     """
    # #     mc_cells = []
    # #     for cell in self.cells:
    # #         is_marginal = False
    # #         if cell.layer == 1:
    # #             is_marginal=True
    # #             mc_cells.append(cell)
    # #             cell.cell_tier = 1  # 标记为第一层
    # #     return mc_cells

    # def identify_neighbor_cells(self, mc_cells):
    #     """
    #     识别并标记与边缘细胞(MC)相邻的细胞 (Neighbor Cells, NC-MC) 作为第二层
    #     """
    #     nc_mc_cells = []
    #     # 首先，将所有MC细胞标记为第一层，并放入一个集合以便快速查找
    #     mc_cell_set = set(mc_cells)

    #     for mc_cell in mc_cell_set:
    #         for i in range(len(mc_cell.points)):
    #             point1 = mc_cell.points[i-1]
    #             point2 = mc_cell.points[i]
    #             edge_string = f'{point1[0]}-{point1[1]}-{point2[0]}-{point2[1]}'
    #             reverse_edge_string = f'{point2[0]}-{point2[1]}-{point1[0]}-{point1[1]}'

    #             # 查找共享此边的邻居细胞（注意排除自身）
    #             neighbor = self.lineOfCell.get(edge_string) or self.lineOfCell.get(reverse_edge_string)
    #             if neighbor is not None and neighbor != mc_cell and neighbor not in mc_cell_set:
    #                 if neighbor not in nc_mc_cells:
    #                     nc_mc_cells.append(neighbor)
    #                     neighbor.cell_tier = 2  # 标记为第二层
    #     return nc_mc_cells

    # def identify_inner_and_third_layer(self, mc_cells, nc_mc_cells):
    #     """
    #     识别内部细胞(IC)和第三层细胞。
    #     IC: 与任何NC-MC细胞都没有共享边的细胞。
    #     第三层细胞: 既不是MC、NC-MC，也不是IC的细胞（即介于NC-MC和IC之间）。
    #     """
    #     # 创建集合以便快速查找
    #     mc_cell_set = set(mc_cells)
    #     nc_mc_cell_set = set(nc_mc_cells)
    #     # 初始时，所有细胞中除去MC和NC-MC，都是潜在的内层或第三层
    #     remaining_cells = [cell for cell in self.cells if cell not in mc_cell_set and cell not in nc_mc_cell_set]

    #     ic_cells = []  # 内部细胞
    #     third_layer_cells = []  # 第三层细胞

    #     # 首先，找出所有与NC-MC有连接的细胞（这些细胞将包括NC-MC自身和第三层细胞）
    #     cells_connected_to_nc_mc = set()
    #     for nc_mc_cell in nc_mc_cell_set:
    #         # 获取一个NC-MC细胞的所有邻居（包括MC和其他）
    #         for i in range(len(nc_mc_cell.points)):
    #             point1 = nc_mc_cell.points[i-1]
    #             point2 = nc_mc_cell.points[i]
    #             edge_string = f'{point1[0]}-{point1[1]}-{point2[0]}-{point2[1]}'
    #             reverse_edge_string = f'{point2[0]}-{point2[1]}-{point1[0]}-{point1[1]}'
    #             neighbor = self.lineOfCell.get(edge_string) or self.lineOfCell.get(reverse_edge_string)
    #             if neighbor is not None and neighbor != nc_mc_cell:
    #                 cells_connected_to_nc_mc.add(neighbor)

    #     # IC细胞：是剩余细胞(remaining_cells)，但不与任何NC-MC相连（即不在cells_connected_to_nc_mc中）
    #     # 第三层细胞：是剩余细胞(remaining_cells)，但与NC-MC相连（即在cells_connected_to_nc_mc中），同时也不是MC或NC-MC
    #     for cell in remaining_cells:
    #         if cell not in cells_connected_to_nc_mc:
    #             ic_cells.append(cell)
    #             cell.cell_tier = 4  # 将IC标记为第4层
    #         else:
    #             third_layer_cells.append(cell)
    #             cell.cell_tier = 3  # 标记为第三层

    #     return ic_cells, third_layer_cells

    # def layer_cells(self):
    #     """
    #     主方法：执行细胞分层。
    #     """
    #     # 确保线段归属字典是最新的
    #     self.list_line_of_cell()

    #     # 执行分层步骤
    #     mc_cells = self.identify_marginal_cells()
    #     nc_mc_cells = self.identify_neighbor_cells(mc_cells)
    #     ic_cells, third_layer_cells = self.identify_inner_and_third_layer(mc_cells, nc_mc_cells)

    #     # 打印分层结果以供验证
    #     print(f"分层完成: MC={len(mc_cells)}, NC-MC={len(nc_mc_cells)}, 第三层={len(third_layer_cells)}, IC={len(ic_cells)}")

    #     # 返回结果，如果需要的话
    #     return {
    #         'tier1_mc': mc_cells,
    #         'tier2_nc_mc': nc_mc_cells,
    #         'tier3': third_layer_cells,
    #         'tier_ic': ic_cells
    #     }
    """
        生成细胞边归属字典，用于记录每条线段归属于哪个细胞
        A cell edge attribution dictionary is generated to record which cell each line segment belongs to
        :param cells: 细胞集，Cell对象列表 Cell set, cell object list
        :return lineOfCell: 细胞边归属字典，记录每条线段归属于哪个细胞 Cell edge attribution dictionary, recording which cell each line segment belongs to
    """
    def list_line_of_cell(self):
        # 将初始图的每条边的归属细胞记录
        # Record the attribution cell of each edge of the initial diagram
        # 注意：这里存储的是单个细胞，不是列表
        # 对于共享边，后遍历的细胞会覆盖前面的
        # 但这不影响 setting_layer() 的判断，因为它只检查边是否存在
        lineOfCell = {}
        for j in range(len(self.cells)):
            cell = self.cells[j]
            for i in range(len(cell.points)):
                # 使用固定的顺序：(i-1, i)，确保与 setting_layer() 一致
                string = '{0}-{1}-{2}-{3}'.format(cell.points[i - 1][0], cell.points[i - 1][1], cell.points[i][0],
                                                  cell.points[i][1])
                # 存储边和对应的细胞（后遍历的会覆盖前面的，但不影响判断）
                lineOfCell[string] = cell
        # print(lineOfCell)
        self.lineOfCell = lineOfCell

    """
        边缘细胞排除
        exclude marginal cells
        :param cells: 细胞集，Cell对象列表 Cell set, cell object list
        :param lineOfCell: 细胞边归属字典，记录每条线段归属于哪个细胞 Cell edge attribution dictionary, recording which cell each line segment belongs to
        :return: none
    """

    #去除从属层的代码，弃用
    def remove_border(self):
        # 初始化为正六边形分裂则不排除
        # Regular hexagon splitting is not ruled out
        for cell in self.cells:
            flag = False
            # 若边没有相邻细胞，则此细胞在边缘
            # If there are no adjacent cells on the edge, the cell is on the edge
            for i in range(len(cell.points)):
                string = '{0}-{1}-{2}-{3}'.format(cell.points[i][0], cell.points[i][1], cell.points[i - 1][0],
                                                  cell.points[i - 1][1])
                if string not in self.lineOfCell:
                    cell.edge_line_index = '{0}|{1}'.format(i-1, i)  # 存储边缘细胞壁两端点的索引
                    flag = True
                    break
            # 如果是边缘细胞，将周围细胞全部排除
            # If it is a marginal cell, exclude all surrounding cells
            if flag:
                cell.ok = False
                cell.layer = 1
    def setting_layer(self):
        # 初始化为正六边形分裂则不排除
        # Regular hexagon splitting is not ruled out
        # 重新构建边计数，统计每条边被多少个细胞共享
        # 边缘边只被一个细胞拥有，内部边被两个细胞共享
        # 关键：需要规范化边的表示，确保同一条边（无论方向）都使用相同的字符串

        def normalize_point(p):
            """将点转换为元组，确保类型一致"""
            if isinstance(p, (list, tuple)):
                return (float(p[0]), float(p[1]))
            elif hasattr(p, '__getitem__'):
                return (float(p[0]), float(p[1]))
            else:
                return (float(p.x), float(p.y))

        def normalize_edge(p1, p2):
            """规范化边：总是使用较小的点作为起点"""
            p1_tuple = normalize_point(p1)
            p2_tuple = normalize_point(p2)
            if p1_tuple < p2_tuple:
                return '{0}-{1}-{2}-{3}'.format(p1_tuple[0], p1_tuple[1], p2_tuple[0], p2_tuple[1])
            else:
                return '{0}-{1}-{2}-{3}'.format(p2_tuple[0], p2_tuple[1], p1_tuple[0], p1_tuple[1])

        edge_count = {}  # 统计每条边被多少个细胞拥有（使用规范化的边表示）
        for cell in self.cells:
            for i in range(len(cell.points)):
                p1 = cell.points[i - 1]
                p2 = cell.points[i]
                string = normalize_edge(p1, p2)
                edge_count[string] = edge_count.get(string, 0) + 1

        # 判断边缘细胞：如果细胞的某条边只被一个细胞拥有（计数为1），则该细胞是边缘细胞
        for cell in self.cells:
            flag = False
            # 若边没有相邻细胞，则此细胞在边缘
            # If there are no adjacent cells on the edge, the cell is on the edge
            for i in range(len(cell.points)):
                p1 = cell.points[i - 1]
                p2 = cell.points[i]
                string = normalize_edge(p1, p2)

                # 如果边只被一个细胞拥有（计数为1），说明是边缘边
                # 内部边被2个细胞共享，所以计数为2
                if edge_count.get(string, 0) == 1:
                    cell.edge_line_index = '{0}|{1}'.format(i-1, i)  # 存储边缘细胞壁两端点的索引
                    flag = True
                    break
            # 如果是边缘细胞，将周围细胞全部排除
            # If it is a marginal cell, exclude all surrounding cells
            if flag:
                cell.ok = False
                cell.layer = 1
