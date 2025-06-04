import json
import random
from typing import Dict, List, Tuple
from collections import defaultdict

def create_prompt(grid_size):
    return f"""Let's play SafepathFinder! Your task is to find a safe path from start to the goal while avoiding hidden traps.

Rules:
1. You are an explorer on a {grid_size}*{grid_size} grid
2. Start: (1,1), Goal: ({grid_size},{grid_size})
3. Each cell can be either:
   - SAFE: can move through
   - TRAP: ends game if stepped on (hidden)
4. At each cell, you can:
   - See the number of traps in adjacent cells (DANGER_LEVEL)
   - Cannot see traps until stepped on them
5. Movement rules:
   - From position (x,y), you can move to any adjacent cell:
   - (x-1,y-1), (x-1,y), (x-1,y+1)
   - (x,y-1),             (x,y+1)
   - (x+1,y-1), (x+1,y), (x+1,y+1)
   - Cannot move outside grid
   - Example: from (2,2) you can move to any surrounding cell

Move Format:
'My Choice: X Y'
where X,Y are coordinates (1-based)
Example: 'My Choice: 2 3'

After each move you will see:
DANGER_LEVEL v 
- v is the number of traps in the 8 adjacent cells
- Higher number means more danger nearby
- 0 means no traps in adjacent cells

Example interaction:
You: 'My Choice: 2 1'
Me: 'DANGER_LEVEL 1'
You: 'My Choice: 3 2'
Me: 'DANGER_LEVEL 2'

Game Ends When:
- SUCCESS: Reach ({grid_size},{grid_size})
- FAILURE: Step on a trap
- INVALID: Try to move outside grid or not to adjacent cell

Strategy Tips:
- Higher DANGER_LEVEL means more risk
- Watch how DANGER_LEVEL changes as you move
- Use these changes to deduce trap locations
- Sometimes longer path might be safer
- Pay attention to diagonal movements too

Ready to start? Make your first move!"""
def has_safe_path(grid_size: int, traps: List[Tuple[int, int]]) -> bool:
    """使用BFS验证是否存在从起点到终点的安全路径"""
    from collections import deque
    
    # 转换陷阱为集合以便快速查找
    trap_set = set(traps)
    
    # BFS队列，存储位置坐标
    queue = deque([(1, 1)])
    # 记录已访问的位置
    visited = {(1, 1)}
    
    while queue:
        x, y = queue.popleft()
        
        # 如果到达终点，返回True
        if (x, y) == (grid_size, grid_size):
            return True
            
        # 检查所有可能的移动方向
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                    
                new_x, new_y = x + dx, y + dy
                
                # 检查新位置是否有效
                if (new_x < 1 or new_x > grid_size or 
                    new_y < 1 or new_y > grid_size):
                    continue
                    
                # 检查新位置是否安全且未访问
                new_pos = (new_x, new_y)
                if (new_pos not in trap_set and 
                    new_pos not in visited):
                    queue.append(new_pos)
                    visited.add(new_pos)
    
    # 如果遍历完所有可能路径都没到终点，返回False
    return False

def generate_traps(grid_size: int) -> List[Tuple[int, int]]:
    """生成陷阱位置，确保存在安全路径"""
    while True:
        num_traps = grid_size-1
        traps = []
        
        # 确保至少一个陷阱在对角线上
        diagonal = [(i, i) for i in range(2, grid_size)]
        if diagonal:
            trap_pos = random.choice(diagonal)
            traps.append(trap_pos)
        
        # 生成剩余陷阱
        available = [(x, y) for x in range(1, grid_size+1) 
                           for y in range(1, grid_size+1)
                           if (x, y) not in traps and (x, y) != (1, 1) 
                           and (x, y) != (grid_size, grid_size)]
        
        while len(traps) < num_traps and available:
            pos = random.choice(available)
            traps.append(pos)
            available.remove(pos)
        
        # 验证是否存在安全路径
        if has_safe_path(grid_size, traps):
            return traps
        # 如果不存在安全路径，重新生成

def verify_file(filename: str):
    seen_traps = set()
    with open(filename, 'r') as f:
        for i, line in enumerate(f, 1):
            data = json.loads(line)
            traps = tuple(tuple(t) for t in data["traps"])
            grid_size = data["scale"]
            
            # 检查是否有重复的陷阱配置
            if traps in seen_traps:
                print(f"Warning: Duplicate trap configuration in {filename} line {i}")
            seen_traps.add(traps)
            
            # 检查是否至少有一个陷阱在对角线上
            has_diagonal = any((x, x) in set(traps) for x in range(2, grid_size))
            if not has_diagonal:
                print(f"Warning: No diagonal trap in {filename} line {i}")
            
            # 验证是否存在安全路径
            if not has_safe_path(grid_size, traps):
                print(f"Warning: No safe path exists in {filename} line {i}")
                
    print(f"Verified {filename}: {len(seen_traps)} unique configurations")
def create_test_case(question_id: int, grid_size: int, difficulty: str) -> Dict:
    traps = generate_traps(grid_size)
    return {
        "question_id": question_id,
        "prompt": create_prompt(grid_size),
        "type": "State Operation",
        "scale": grid_size,
        "difficulty": difficulty,
        "title": "SafepathFinder",
        "traps": traps
    }

def generate_file(difficulty: str, grid_size: int, filename: str):
    with open(filename, 'w') as f:
        for i in range(1, 31):
            test_case = create_test_case(i, grid_size, difficulty)
            f.write(json.dumps(test_case) + '\n')

# 生成三个难度的文件
generate_file("easy", 5, "easy.jsonl")
generate_file("medium", 6, "medium.jsonl")
generate_file("hard", 7, "hard.jsonl")

verify_file("easy.jsonl")
verify_file("medium.jsonl")
verify_file("hard.jsonl")