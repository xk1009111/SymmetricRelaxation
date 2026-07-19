class AnnealingStatistics:
    """退火统计管理类"""
    def __init__(self):
        self.internal_vertices = 0      # 内部顶点总数
        self.edge_vertices = 0         # 边缘顶点总数
        self.last_annealed_vertices = 0 # 上一轮退火顶点数
        self.current_annealed_vertices = 0  # 当前轮退火顶点数
        self.vertex_type_dict = {}      # 顶点类型字典：{顶点坐标: "internal"/"edge"}

    def count_vertex_types(self, cells, intersection_cell_blocks):
        """统计内部和边缘顶点个数"""
        self.internal_vertices = 0
        self.edge_vertices = 0
        self.vertex_type_dict.clear()

        # 统计交汇点（三个细胞共享的顶点）
        intersection_points = set()
        for cb in intersection_cell_blocks:
            point = cb.cell1.points[cb.index1]
            intersection_points.add(tuple(point))

        # 遍历所有细胞的所有顶点
        all_vertices = set()
        for cell in cells:
            for point in cell.points:
                vertex_tuple = tuple(point)
                if vertex_tuple not in all_vertices:
                    all_vertices.add(vertex_tuple)

                    # 判断顶点类型
                    if self._is_edge_vertex(vertex_tuple, cell, cells, intersection_points):
                        self.edge_vertices += 1
                        self.vertex_type_dict[vertex_tuple] = "edge"
                    else:
                        self.internal_vertices += 1
                        self.vertex_type_dict[vertex_tuple] = "internal"

    def _is_edge_vertex(self, vertex, current_cell, all_cells, intersection_points):
        """判断顶点是否为边缘顶点"""
        # 如果是三个细胞的交汇点，肯定是内部顶点
        if vertex in intersection_points:
            return False

        # 统计共享该顶点的细胞数量
        sharing_cells_count = 0
        for cell in all_cells:
            for point in cell.points:
                if tuple(point) == vertex:
                    sharing_cells_count += 1
                    break

        # 如果被少于3个细胞共享，则是边缘顶点
        return sharing_cells_count < 3

    def update_annealing_count(self, annealed_vertices_count):
        """更新退火统计"""
        self.last_annealed_vertices = self.current_annealed_vertices
        self.current_annealed_vertices = annealed_vertices_count

    def get_statistics(self):
        """获取统计信息"""
        return {
            "internal_vertices": self.internal_vertices,
            "edge_vertices": self.edge_vertices,
            "last_annealed_vertices": self.last_annealed_vertices,
            "current_annealed_vertices": self.current_annealed_vertices,
            "total_vertices": self.internal_vertices + self.edge_vertices
        }

    def print_statistics(self, round_number=0):
        """打印统计信息"""
        stats = self.get_statistics()
        print(f"\n=== 第{round_number}轮退火统计 ===")
        print(f"内部顶点个数: {stats['internal_vertices']}")
        print(f"边缘顶点个数: {stats['edge_vertices']}")
        print(f"顶点总数: {stats['total_vertices']}")
        print(f"当前轮退火顶点数: {stats['current_annealed_vertices']}")
        print(f"上一轮退火顶点数: {stats['last_annealed_vertices']}")
        print("=" * 30)
