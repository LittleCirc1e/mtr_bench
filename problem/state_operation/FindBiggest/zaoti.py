import json
import random
def create_prompt(grid_size):
    return f"""Let's play Finding the Biggest! Your task is to find and collect the highest value treasure through strategic movement on the grid.

Rules:
1. You are an explorer on a {grid_size}*{grid_size} grid
2. There are exactly 2 treasures hidden on the grid
3. Each treasure has a value between 1 and 100
4. You start at position (1,1)
5. Movement rules:
   - From position (x,y), you can move to any of its 8 adjacent cells:
   - (x-1,y-1), (x-1,y), (x-1,y+1)
   - (x,y-1),             (x,y+1)
   - (x+1,y-1), (x+1,y), (x+1,y+1)
   - Cannot move outside the grid boundaries
6. Direction System:
   - N:  treasure is somewhere in the region above your current position
   - NE: treasure is somewhere in the upper-right region
   - E:  treasure is somewhere in the region to your right
   - SE: treasure is somewhere in the lower-right region
   - S:  treasure is somewhere in the region below your current position
   - SW: treasure is somewhere in the lower-left region
   - W:  treasure is somewhere in the region to your left
   - NW: treasure is somewhere in the upper-left region
   The direction indicates a general area, not a specific cell
7. MAGNETIC INTERFERENCE:
   - When you get a direction, there's 50% chance it's completely wrong
   - However, wrong directions never appear in consecutive moves
   - If you get a wrong direction, the next move's direction is guaranteed correct

Move Types:
1. To move to a position:
   Format: 'My Choice: X Y'
   where X,Y are grid coordinates (1-based)
   Example: 'My Choice: 2 3' moves to row 2, column 3

2. To collect treasure:
   Format: 'My Choice: COLLECT'
   - Only use when you're sure you're on the highest value treasure
   - You only get one collection attempt

After each move:
- If you find a treasure: 'TREASURE v' (v is the treasure's value)
- If empty cell: 'EMPTY dir' (dir indicates which region contains nearest treasure)
- If invalid move: 'INVALID_MOVE'

Example interaction:
You: 'My Choice: 2 2'  
Me: 'EMPTY SW' (indicates treasure might be in lower-left region, but could be wrong)
You: 'My Choice: 1 2'
Me: 'EMPTY NE' (guaranteed correct: treasure is in upper-right region)
You: 'My Choice: 2 3'
Me: 'TREASURE 80'
You: 'My Choice: COLLECT'
Me: 'Win'

Key Points:
- Directions point to regions, not specific cells
- If a direction seems wrong, the next one will be correct
- Must find and be at highest value treasure to win
- Wrong COLLECT attempt = game over

Ready to start? Make your first move!"""

def generate_treasures(grid_size):
    # 生成两个不同的宝藏位置和不同的价值
    positions = []
    while len(positions) < 2:
        x = random.randint(1, grid_size)
        y = random.randint(1, grid_size)
        if (x, y) not in positions and (x, y) != (1, 1):  # 避开起点(1,1)
            positions.append((x, y))
    
    # 生成不同的价值
    values = random.sample(range(30, 100), 2)
    
    return [
        {"x": pos[0], "y": pos[1], "value": val}
        for pos, val in zip(positions, values)
    ]

def create_test_case(question_id, grid_size, difficulty):
    return {
        "question_id": question_id,
        "prompt": create_prompt(grid_size),
        "type": "State Operation",
        "scale": grid_size,
        "difficulty": difficulty,
        "title": "FindBiggest",
        "graph": {
            "grid_size": grid_size,
            "treasures": generate_treasures(grid_size)
        }
    }

def generate_file(difficulty, grid_size, filename):
    with open(filename, 'w') as f:
        for i in range(1, 31):
            test_case = create_test_case(i, grid_size, difficulty)
            f.write(json.dumps(test_case) + '\n')

# 生成三个难度的文件
generate_file("easy", 3, "easy.jsonl")
generate_file("medium", 4, "medium.jsonl")
generate_file("hard", 5, "hard.jsonl")

# 验证生成的文件
def verify_file(filename):
    seen_positions = set()
    with open(filename, 'r') as f:
        for i, line in enumerate(f, 1):
            data = json.loads(line)
            treasures = tuple((t["x"], t["y"], t["value"]) 
                            for t in data["graph"]["treasures"])
            # 检查是否有重复的宝藏配置
            if treasures in seen_positions:
                print(f"Warning: Duplicate treasure configuration in {filename} line {i}")
            seen_positions.add(treasures)
    print(f"Verified {filename}: {len(seen_positions)} unique configurations")

# 验证所有文件
verify_file("easy.jsonl")
verify_file("medium.jsonl")
verify_file("hard.jsonl")
