import json
import random
from typing import Tuple, List, Dict, Optional
def generate_valid_maze(n: int, m: int) -> List[List[str]]:
    """生成一个有效的迷宫"""
    # 初始化为普通格子
    maze = [['.' for _ in range(m)] for _ in range(n)]
    
    # 设置起点
    maze[0][0] = '.'
    
    # 随机放置一些危险格子（*），但确保存在可行路径
    num_dangerous = random.randint(n-1, n*m//3)  # 控制危险格子数量
    
    # 随机选择终点位置（不是起点）
    while True:
        finish_x = random.randint(0, n-1)
        finish_y = random.randint(0, m-1)
        if not (finish_x == 0 and finish_y == 0):
            maze[finish_x][finish_y] = 'F'
            break
    
    # 放置危险格子，但保证起点和终点之间有路
    dangerous_positions = set()
    for _ in range(num_dangerous):
        while True:
            x = random.randint(0, n-1)
            y = random.randint(0, m-1)
            if maze[x][y] == '.' and (x, y) != (0, 0):
                maze[x][y] = '*'
                dangerous_positions.add((x, y))
                if has_valid_path(maze, n, m):  # 检查是否存在可行路径
                    break
                maze[x][y] = '.'  # 如果没有可行路径，撤销放置
                dangerous_positions.remove((x, y))
    
    return maze

def has_valid_path(maze: List[List[str]], n: int, m: int) -> bool:
    """检查是否存在从起点到终点的有效路径"""
    def dfs(x: int, y: int, visited: set[Tuple[int, int]]) -> bool:
        if x < 0 or x >= n or y < 0 or y >= m or maze[x][y] == '*' or (x, y) in visited:
            return False
        if maze[x][y] == 'F':
            return True
            
        visited.add((x, y))
        # 四个方向尝试
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            if dfs(x + dx, y + dy, visited):
                return True
        return False
    
    return dfs(0, 0, set())

def create_prompt(n: int, m: int, grid: List[List[str]]) -> str:
    # 将网格转换为字符串表示
    grid_str = '\n'.join([''.join(row) for row in grid])
    
    # 找到特殊点的坐标
    start_pos = "(1, 1)"
    finish_pos = None
    dangerous_pos = []
    
    for i in range(n):
        for j in range(m):
            if grid[i][j] == 'F':
                finish_pos = f"({i+1}, {j+1})"
            elif grid[i][j] == '*':
                dangerous_pos.append(f"({i+1}, {j+1})")
    
    dangerous_str = "\n     ".join(dangerous_pos)

    return f"""Let's play Vladik's Maze Game! Your task is to navigate through a maze with potentially swapped controls to reach the finish point.

Rules:
1. Game Field:
   - A {n} * {m} grid with three types of cells:
     * "." - normal cell you can visit
     * "F" - finish cell (exactly one)
     * "*" - dangerous cell (avoid these)
   - Coordinates are 1-based indexing: (row, column)
   - Current cell positions:
     * Start: {start_pos} (top-left corner)
     * Finish: {finish_pos}
     * Dangerous cells: 
     {dangerous_str}

2. Movement Controls:
   - Four direction buttons: U(up), D(down), L(left), R(right)
   - Button Functions may be swapped:
     * L and R might be swapped with each other
     * U and D might be swapped with each other
   - Swaps (if any) are set at game start and remain fixed
   - Effects of each button when NOT swapped:
     * U: moves to (current_row - 1, current_col)
     * D: moves to (current_row + 1, current_col)
     * L: moves to (current_row, current_col - 1)
     * R: moves to (current_row, current_col + 1)

3. Movement Rules:
   - Each move returns your new position (x, y)
   - If move is invalid (out of grid), position stays same
   - Grid boundaries: 1 ≤ row ≤ {n}, 1 ≤ column ≤ {m}
   - If you hit dangerous cell, returns (-1, -1) and game ends
   - When you reach finish cell ({finish_pos}), game ends successfully

Move Format:
1. To make a move:
   Format: 'My Move: X'
   where X is one of: U, D, L, R
   Example: 'My Move: R'

2. System Response:
   Format: 'x y'
   where:
   - (x, y) is your new position
   - (-1, -1) if you hit dangerous cell
   Example: After 'My Move: R' at (1, 1), response might be '1 2'

Instructions:
1. Make moves based on previous responses
2. Use exactly the format shown above
3. Explain your reasoning before each move

Remember:
- Start position is {start_pos}
- Controls might be swapped
- Avoid dangerous cells at: {dangerous_str}
- Target is to reach {finish_pos}
- Watch for grid boundaries: 1 ≤ row ≤ {n}, 1 ≤ column ≤ {m}

Current Grid Layout:
{grid_str}

Ready to start? Make your first query!"""

def generate_jsonl(difficulty: str, n: int, m: int, num_examples: int):
    filename = f"{difficulty}.jsonl"
    
    with open(filename, 'w') as f:
        for i in range(num_examples):
            grid = generate_valid_maze(n, m)
            
            data = {
                "question_id": i + 1,
                "prompt": create_prompt(n, m, grid),
                "type": "State Operation",
                "scale": n,
                "difficulty": difficulty,
                "title": "VladikMaze",
                "grids": grid
            }
            
            f.write(json.dumps(data) + '\n')

# 设置参数
settings = {
    "easy": 4,
    "medium": 5,
    "hard": 6
}

if __name__ == "__main__":
    random.seed(42)  # 设置随机种子以保证可重现性
    
    # 为每个难度生成文件
    for diff, n in settings.items():
        generate_jsonl(diff, n, 4, 30)
