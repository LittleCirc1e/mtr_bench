import json
import random

def generate_grid(n, m):
    # 生成 1 到 n*m 的数字列表
    numbers = list(range(1, n*m + 1))
    # 随机打乱
    random.shuffle(numbers)
    
    # 创建网格字典
    grid = {}
    index = 0
    for i in range(1, n+1):
        for j in range(1, m+1):
            grid[f"({i}, {j})"] = numbers[index]
            index += 1
    return grid

def create_prompt(n, m, grid):
    # 创建网格的字符串表示（坐标：数字格式）
    grid_str = "   Initial grid state:\n"
    for i in range(1, n+1):
        for j in range(1, m+1):
            grid_str += f"   Cell ({i}, {j}): {grid[f'({i}, {j})']} \n"

    base_prompt = f"""Let's play the Grid Sum Game! Your task is to choose cells strategically to win.

Rules:
1. Game Setup:
   - Grid size: {n}*{m}
   - Grid already filled with numbers 1 to {n*m}
   - Each number appears exactly once
{grid_str}

2. Game Mechanics:
   - Players take turns selecting unselected cells
   - You move first
   - Any cell chosen after first turn must be adjacent to a previously selected cell
   - Cells are adjacent if they share an edge (up/down/left/right)
   - Game ends when all cells are selected
   - You win if your selected numbers sum < my sum

3. Adjacency Example:
   For cell (2,2):
   - Adjacent cells: (1,2), (2,1), (2,3), (3,2)
   - Diagonal cells like (1,1) are not adjacent
   - Must choose a cell adjacent to any previously selected cell

Instructions:
- For each turn - Choose a cell and format as: 'My Choice: x y'
  where x is row (1 to {n}) and y is column (1 to {m})
- Give your reasoning before each choice
- Wait for my response before next move

Example Interaction:
You: 'My Choice: 2 2'
- Selecting cell at row 2, column 2

I: 'My Choice: 2 3'
- Cell is adjacent to (2,2)

You: 'My Choice: 1 2'
- Cell is adjacent to (2,2)

Remember:
- Use exact format: 'My Choice: x y'
- Choose only adjacent cells after first turn
- First move can be any cell
- Keep track of both sums
- Plan moves to keep your sum smaller
- Invalid move = automatic loss

Ready to start? Make your first choice!"""
    return base_prompt

def generate_jsonl(filename, n, m, num_entries, difficulty):
    with open(filename, 'w') as f:
        for i in range(num_entries):
            grid = generate_grid(n, m)
            entry = {
                "question_id": i + 1,
                "prompt": create_prompt(n, m, grid),
                "type": "Strategic Gaming",
                "scale": [n, m],  # 修改为列表表示长和宽
                "difficulty": difficulty,
                "title": "GridSum",
                "initial_grid": grid,
                "turns": n*m/2
            }
            f.write(json.dumps(entry) + '\n')

# m固定为4，n分别为3,4,5表示不同难度
# 生成 easy.jsonl (size=3*4)
generate_jsonl('easy.jsonl', 3, 4, 30, "easy")

# 生成 medium.jsonl (size=4*4)
generate_jsonl('medium.jsonl', 5, 4, 30, "medium")

# 生成 hard.jsonl (size=5*4)
generate_jsonl('hard.jsonl', 8, 4, 30, "hard")
