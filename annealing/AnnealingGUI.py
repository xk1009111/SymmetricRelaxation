import annealing.annealerUtil as util


class Annealer:
    """细胞退火器。负责生成每个细胞的实际线与预最优线、提取交汇细胞块并按策略移动顶点。annealingRate 为单步退火比例，edge_judge 控制是否处理边缘块，flag 用于轮次奇偶切换。"""
    annealingRate = 0.0
    edge_judge = False
    flag = True
    internal_vertices = 0
    edge_vertices = 0
    last_internal_vertices = 0
    last_edge_vertices = 0


    def __init__(self, params=None):
        """
        初始化退火器
        :param params: 参数字典，包含以下可选键：
            - annealingRate: 退火速率 (0~1)
            - edge_judge: 细胞块边缘是否参与退火 (True/False 或 1/0)
        """
        if params is None:
            params = {}
        self.init(params)

    def __str__(self):
        return ""

    # 细胞退火器参数初始化（参数化版本）
    def init(self, params=None):
        """
        参数化初始化方法
        :param params: 参数字典
        """
        if params is None:
            params = {}

        print("↓↓===细胞退火器参数设置===↓↓")
        self.annealingRate = params.get('annealingRate', 0.5)  # 默认0.5

        inner_angle_sq_guard = params.get('inner_angle_sq_guard', 1)
        if isinstance(inner_angle_sq_guard, bool):
            self.inner_angle_sq_guard = inner_angle_sq_guard
        elif isinstance(inner_angle_sq_guard, (int, str)):
            self.inner_angle_sq_guard = int(inner_angle_sq_guard) == 1
        else:
            self.inner_angle_sq_guard = True
        util.set_annealing_options(self.inner_angle_sq_guard)

        edge_judge = params.get('edge_judge', 0)  # 默认不参与
        if isinstance(edge_judge, bool):
            self.edge_judge = edge_judge
        elif isinstance(edge_judge, (int, str)):
            self.edge_judge = int(edge_judge) == 1
        else:
            self.edge_judge = False

        print("----------------------------")

    def annealing(self, cells):
        """一轮退火流程：为每个细胞构建实际/预最优连线→提取交汇细胞块→调用移动函数执行顶点移动，返回本轮实际移动的顶点数量"""
        for cell in cells:
            max_distence = util.get_distance_centerpoint_point(cell)
            cell.actual_lines = util.get_actual_lines(cell, max_distence)

            # 计算法计算旋转增量 Calculation of rotation increment by calculation method
            delta = util.get_best_rotate_delta_by_calculation(cell)

            cell.pre_best_lines = util.get_pre_best_lines(cell, max_distence, delta)

        intersection_cell_blocks = util.get_intersection_cell_blocks(cells)

        result = util.move_point(intersection_cell_blocks, self.annealingRate, self.edge_judge, self.flag, cells)
        self.last_internal_vertices = self.internal_vertices
        self.last_edge_vertices = self.edge_vertices

        # move_point 约定：(计数, {'internal_vertices': int, 'edge_vertices': int})
        annealing_count = 0
        if isinstance(result, (tuple, list)) and len(result) >= 2 and isinstance(result[1], dict):
            annealing_count = result[0]
            stats = result[1]
            try:
                self.internal_vertices = int(stats.get('internal_vertices', 0) or 0)
                self.edge_vertices = int(stats.get('edge_vertices', 0) or 0)
            except (TypeError, ValueError):
                self.internal_vertices = 0
                self.edge_vertices = 0
        else:
            try:
                annealing_count = int(result) if not isinstance(result, (tuple, list)) else int(result[0])
            except (TypeError, ValueError, IndexError):
                annealing_count = 0
            self.internal_vertices = 0
            self.edge_vertices = 0

        self.flag = not self.flag
        try:
            return int(annealing_count)
        except (TypeError, ValueError):
            return 0
