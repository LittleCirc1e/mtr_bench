import json
import random
from typing import Dict, List, Tuple, Set
from collections import deque

def create_prompt(grid_size):
    return f"""Let's play DarkMazeExplorer! Your task is to find your way through a dark maze using only directional movements.

Rules:
1. You are exploring a {grid_size}*{grid_size} maze
2. Each cell may have walls in any direction (North, East, South, West)
3. You start at position (1,1) and must reach ({grid_size},{grid_size})
4. You can only make one directional move at a time
5. You cannot move through walls or outside the maze boundaries

Move Types:
1. To make a move:
   Format: 'My Choice: X'
   where:
   - X is one of: N, E, S, W (representing directions)
   - N = North, E = East, S = South, W = West
   Example: 'My Choice: E'

After each move you will receive:
- MOVED: successfully moved into the next cell in your chosen direction
- BLOCKED: wall exists in that direction
- INVALID: tried to move outside maze boundaries
- WIN: reached the exit at ({grid_size},{grid_size})

Example Interaction:
Starting at (1,1) with North and West walls
You: 'My Choice: E'
Me: 'MOVED'
You: 'My Choice: N'
Me: 'BLOCKED'
You: 'My Choice: S'
Me: 'WIN'

Instructions:
1. Make moves based on feedback
2. Use exactly the format shown above
3. Explain your reasoning before each move
4. Plan your path carefully

Remember:
- Starting room (1,1) has North and West walls
- You can only see walls when you encounter them
- Need to mentally map the maze
- Cannot move through walls or outside boundaries
- Must reach ({grid_size},{grid_size}) to win

Ready to start? Make your first move!"""

def find_path(maze: Dict, start: Tuple[int, int], end: Tuple[int, int]) -> bool:
    """使用BFS查找从起点到终点的路径"""
    grid_size = maze["size"]
    visited = set()
    queue = deque([(start)])
    visited.add(start)
    
    while queue:
        x, y = queue.popleft()
        if (x, y) == end:
            return True
            
        current = maze["rooms"][f"{x},{y}"]["walls"]
        
        # 检查四个方向
        if 'N' not in current and x > 1 and (x-1,y) not in visited:
            queue.append((x-1,y))
            visited.add((x-1,y))
        if 'S' not in current and x < grid_size and (x+1,y) not in visited:
            queue.append((x+1,y))
            visited.add((x+1,y))
        if 'W' not in current and y > 1 and (x,y-1) not in visited:
            queue.append((x,y-1))
            visited.add((x,y-1))
        if 'E' not in current and y < grid_size and (x,y+1) not in visited:
            queue.append((x,y+1))
            visited.add((x,y+1))
            
    return False

def generate_maze(grid_size: int) -> Dict:
    """使用改进的Prim算法生成迷宫，确保存在可行路径"""
    while True:  # 不断尝试直到生成有效迷宫
        # 初始化迷宫
        maze = {
            "size": grid_size,
            "rooms": {},
            "paths": []
        }
        
        # 初始化所有房间
        for x in range(1, grid_size+1):
            for y in range(1, grid_size+1):
                maze["rooms"][f"{x},{y}"] = {
                    "walls": ["N", "E", "S", "W"],
                    "visited": False
                }
        
        def remove_wall_safely(room_key: str, wall: str):
            """安全地移除墙壁"""
            walls = maze["rooms"][room_key]["walls"]
            if wall in walls:
                walls.remove(wall)
        
        # 从(1,1)开始生成迷宫
        start_x, start_y = 1, 1
        frontier = []
        maze["rooms"]["1,1"]["visited"] = True
        maze["rooms"]["1,1"]["walls"] = ["N", "W"]  # 确保起始房间只有北墙和西墙
        
        # 将起始房间的邻居加入前沿列表
        if start_y < grid_size:  # 东
            frontier.append(('E', start_x, start_y, start_x, start_y+1))
        if start_x < grid_size:  # 南
            frontier.append(('S', start_x, start_y, start_x+1, start_y))
        
        # 主循环
        while frontier:
            # 随机选择前沿
            idx = random.randrange(len(frontier))
            direction, x1, y1, x2, y2 = frontier.pop(idx)
            
            if not maze["rooms"][f"{x2},{y2}"]["visited"]:
                # 移除墙
                opposite = {'N':'S', 'S':'N', 'E':'W', 'W':'E'}[direction]
                remove_wall_safely(f"{x1},{y1}", direction)
                remove_wall_safely(f"{x2},{y2}", opposite)
                
                maze["rooms"][f"{x2},{y2}"]["visited"] = True
                
                # 记录路径
                maze["paths"].append([[x1,y1], [x2,y2]])
                maze["paths"].append([[x2,y2], [x1,y1]])
                
                # 添加新的前沿
                for new_dir, dx, dy in [('N',-1,0), ('E',0,1), ('S',1,0), ('W',0,-1)]:
                    nx, ny = x2 + dx, y2 + dy
                    if (1 <= nx <= grid_size and 1 <= ny <= grid_size and 
                        not maze["rooms"][f"{nx},{ny}"]["visited"]):
                        frontier.append((new_dir, x2, y2, nx, ny))
        
        # 确保外墙
        for x in range(1, grid_size+1):
            if "W" not in maze["rooms"][f"{x},1"]["walls"]:
                maze["rooms"][f"{x},1"]["walls"].append("W")
            if "E" not in maze["rooms"][f"{x},{grid_size}"]["walls"]:
                maze["rooms"][f"{x},{grid_size}"]["walls"].append("E")
        for y in range(1, grid_size+1):
            if "N" not in maze["rooms"][f"1,{y}"]["walls"]:
                maze["rooms"][f"1,{y}"]["walls"].append("N")
            if "S" not in maze["rooms"][f"{grid_size},{y}"]["walls"]:
                maze["rooms"][f"{grid_size},{y}"]["walls"].append("S")
        
        # 确保(1,1)只有北墙和西墙
        maze["rooms"]["1,1"]["walls"] = ["N", "W"]
        
        # 清理访问标记
        for x in range(1, grid_size+1):
            for y in range(1, grid_size+1):
                del maze["rooms"][f"{x},{y}"]["visited"]
        
        # 验证是否存在可行路径
        if find_path(maze, (1,1), (grid_size,grid_size)):
            return maze

def create_test_case(question_id: int, grid_size: int, difficulty: str) -> Dict:
    maze = generate_maze(grid_size)
    return {
        "question_id": question_id,
        "prompt": create_prompt(grid_size),
        "type": "State Operation",
        "scale": grid_size,
        "difficulty": difficulty,
        "title": "DarkMazeExplorer",
        "maze": maze
    }

def generate_file(difficulty: str, grid_size: int, filename: str):
    with open(filename, 'w') as f:
        for i in range(1, 31):
            test_case = create_test_case(i, grid_size, difficulty)
            f.write(json.dumps(test_case) + '\n')

def verify_file(filename: str):
    with open(filename, 'r') as f:
        for i, line in enumerate(f, 1):
            data = json.loads(line)
            maze = data["maze"]
            grid_size = maze["size"]
            
            # 检查起始房间墙壁
            start_walls = set(maze["rooms"]["1,1"]["walls"])
            if start_walls != {'N', 'W'}:
                print(f"Warning: Starting room walls incorrect in {filename} line {i}")
            
            # 检查外墙
            for x in range(1, grid_size+1):
                if "W" not in maze["rooms"][f"{x},1"]["walls"]:
                    print(f"Warning: Missing west wall at ({x},1)")
                if "E" not in maze["rooms"][f"{x},{grid_size}"]["walls"]:
                    print(f"Warning: Missing east wall at ({x},{grid_size})")
            for y in range(1, grid_size+1):
                if "N" not in maze["rooms"][f"1,{y}"]["walls"]:
                    print(f"Warning: Missing north wall at (1,{y})")
                if "S" not in maze["rooms"][f"{grid_size},{y}"]["walls"]:
                    print(f"Warning: Missing south wall at ({grid_size},{y})")
            
            # 检查路径可达性
            if not find_path(maze, (1,1), (grid_size,grid_size)):
                print(f"Warning: No valid path to exit in {filename} line {i}")
    
    print(f"Verified {filename}")

# 生成三个难度的文件
generate_file("easy", 2, "easy.jsonl")
generate_file("medium", 3, "medium.jsonl")
generate_file("hard", 4, "hard.jsonl")

# 验证生成的文件
verify_file("easy.jsonl")
verify_file("medium.jsonl")
verify_file("hard.jsonl")
