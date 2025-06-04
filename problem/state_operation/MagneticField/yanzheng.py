import json
from typing import List, Tuple, Set
import sys

class MagneticFieldHandler:
    def __init__(self, size: int, grid: List[List[str]]):
        self.size = size
        self.grid = grid
        # 定义磁场方向映射
        self.magnetic_dir = {
            'N': (-1, 0),
            'S': (1, 0),
            'E': (0, 1),
            'W': (0, -1)
        }

    def is_valid_position(self, x: int, y: int) -> bool:
        """检查位置是否在网格内"""
        return 1 <= x <= self.size and 1 <= y <= self.size

    def get_next_position(self, x: int, y: int) -> Tuple[int, int]:
        """根据磁场方向获取下一个位置"""
        cell = self.grid[x-1][y-1]
        if cell not in self.magnetic_dir:
            return (x, y)  # 不是磁场，返回原位置
        dx, dy = self.magnetic_dir[cell]
        next_x, next_y = x + dx, y + dy
        if not self.is_valid_position(next_x, next_y):
            return (x, y)  # 超出边界，保持原位
        return (next_x, next_y)

    def has_cycle_from(self, start_x: int, start_y: int) -> bool:
        """检查从 (start_x, start_y) 是否存在循环"""
        visited: Set[Tuple[int, int]] = set()
        current_x, current_y = start_x, start_y

        while True:
            if (current_x, current_y) in visited:
                # 如果回到起点，则存在循环
                return (current_x, current_y) == (start_x, start_y)
            visited.add((current_x, current_y))
            next_x, next_y = self.get_next_position(current_x, current_y)
            if (next_x, next_y) == (current_x, current_y):
                # 磁场指向自身或遇到边界或非磁场，停止
                return False
            current_x, current_y = next_x, next_y

    def contains_cycle(self) -> bool:
        """检查整个网格是否存在任何循环"""
        for i in range(1, self.size + 1):
            for j in range(1, self.size + 1):
                if self.grid[i-1][j-1] in self.magnetic_dir:
                    if self.has_cycle_from(i, j):
                        return True
        return False

def find_cycles_in_jsonl(file_path: str) -> List[int]:
    """读取 JSONL 文件，返回存在循环的 question_id 列表"""
    cyclic_question_ids = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line)
                question_id = data.get("question_id")
                graph = data.get("graph", {})
                size = graph.get("size")
                grid = graph.get("grid", [])
                if not size or not grid:
                    continue  # 跳过无效数据
                handler = MagneticFieldHandler(size, grid)
                if handler.contains_cycle():
                    cyclic_question_ids.append(question_id)
            except json.JSONDecodeError:
                print(f"Skipping invalid JSON line: {line}", file=sys.stderr)
            except Exception as e:
                print(f"Error processing line: {e}", file=sys.stderr)
    return cyclic_question_ids

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="检测 JSONL 文件中存在循环的磁场布局")
    parser.add_argument("file_path", help="JSONL 文件的路径")
    args = parser.parse_args()

    cyclic_ids = find_cycles_in_jsonl(args.file_path)
    if cyclic_ids:
        print("存在循环的 question_id:")
        for qid in cyclic_ids:
            print(qid)
    else:
        print("所有条目均不包含循环。")
