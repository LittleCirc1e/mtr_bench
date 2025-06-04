import json
import random

def create_prompt(size, initial_state):
    # 将初始状态转换为字符串格式
    initial_grid = '\n'.join(' '.join(row) for row in initial_state)
    
    base_prompt = """Let's play Color Magic Grid! Your task is to make all cells the same color through magical color transformations.

Rules:
1. You have a {}x{} grid where each cell contains one of three colors: Red(R), Blue(B), Yellow(Y)
2. There are three magic operations with unknown number assignments (1, 2, or 3):
   - Magic Alpha: Selected cell rotates R->B->Y->R, adjacent cells rotate R->Y->B->R
   - Magic Beta: Selected cell rotates B->Y->R->B, adjacent cells rotate B->R->Y->B 
   - Magic Gamma: Selected cell stays same, adjacent cells swap colors (R<->B, B<->Y, Y<->R)
3. Your goal is to make all cells the same color

Move Types:
1. To make a move:
   Format: 'My Move: OPERATION POSITION'
   where:
   - OPERATION is one of: 1, 2, 3 (each corresponds to a magic type)
   - POSITION is cell number (1-{}, numbered left to right, top to bottom)
   Example: 'My Move: 2 5'

Instructions:
1. Make moves based on observed color changes
2. Use exactly the format shown above
3. Explain your reasoning before each move
4. Try to discover which number corresponds to which magic

Example Interaction:
Current Grid:
R B Y
B R B
Y R Y
You: 'My Move: 1 5'
Me:
R R Y
R R R
Y B Y
- Note: This is just an example; in reality, 1 may not correspond to this operation.


Initial Grid:
{}

Remember:
- Each number (1,2,3) maps to one magic type (Alpha/Beta/Gamma)
- You must figure out the mapping through experimentation
- Grid positions are numbered from 1 to {} from left to right, top to bottom
- Adjacent means sharing an edge (not diagonal)
- Need to make all cells the same color to win

Ready to start? Make your first move!""".format(size, size, size*size, initial_grid, size*size)
    return base_prompt


def generate_initial_state(size, id):
    # 根据id生成不同的初始状态
    colors = ['R', 'B', 'Y']
    state = []
    for i in range(size):
        row = []
        for j in range(size):
            color_idx = (i + j + id) % 3
            row.append(colors[color_idx])
        state.append(row)
    return state

def get_target_state(size):
    # 随机选择目标颜色
    target_color = random.choice(['R', 'B', 'Y'])
    return [[target_color]*size for _ in range(size)]

def apply_operation(state, operation, position, size):
    # 返回一个操作后的新状态
    def get_adjacent_positions(pos, size):
        row, col = (pos-1) // size, (pos-1) % size
        adjacent = []
        for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < size and 0 <= new_col < size:
                adjacent.append((new_row, new_col))
        return adjacent
    
    new_state = [row[:] for row in state]
    row, col = (position-1) // size, (position-1) % size
    
    # 定义颜色变换规则
    color_maps = {
        'alpha': {'center': {'R':'B', 'B':'Y', 'Y':'R'},
                 'adjacent': {'R':'Y', 'B':'R', 'Y':'B'}},
        'beta': {'center': {'B':'Y', 'Y':'R', 'R':'B'},
                'adjacent': {'B':'R', 'Y':'B', 'R':'Y'}},
        'gamma': {'center': {'R':'R', 'B':'B', 'Y':'Y'},
                'adjacent': {'R':'B', 'B':'Y', 'Y':'R'}}
    }
    
    rules = color_maps[operation]
    # 改变中心格子
    new_state[row][col] = rules['center'][state[row][col]]
    
    # 改变相邻格子
    for adj_row, adj_col in get_adjacent_positions(position, size):
        new_state[adj_row][adj_col] = rules['adjacent'][state[adj_row][adj_col]]
    
    return new_state

def generate_initial_state(size, required_steps):
    # 从目标状态反向生成初始状态
    target = get_target_state(size)
    current = [row[:] for row in target]
    operations = ['alpha', 'beta', 'gamma']
    steps = []
    
    # 反向应用操作来生成初始状态
    for _ in range(required_steps):
        operation = random.choice(operations)
        position = random.randint(1, size*size)
        steps.append((operation, position))
        
        # 应用反向操作
        reverse_ops = {
            'alpha': 'beta',
            'beta': 'alpha',
            'gamma': 'gamma'
        }
        current = apply_operation(current, reverse_ops[operation], position, size)
    
    return current, steps

def create_graph(size, id, required_steps):
    initial_state, solution = generate_initial_state(size, required_steps)
    target_state = get_target_state(size)
    
    return {
        "size": size,
        "initial_state": initial_state,
        "target_state": target_state,
        "operations": {
            "alpha": {"center": "RBY", "adjacent": "RYB"},
            "beta": {"center": "BYR", "adjacent": "BRY"},
            "gamma": {"center": "same", "adjacent": "swap"}
        },
        "solution": solution  # 可选：记录解决方案，用于验证
    }

def create_jsonl_file(difficulty, size, steps, filename):
    with open(filename, 'w') as f:
        for i in range(1, 31):
            graph = create_graph(size, i, steps)
            data = {
                "question_id": i,
                "prompt": create_prompt(size, graph["initial_state"]),  # 传入初始状态
                "type": "State Operation",
                "scale": size,
                "difficulty": difficulty,
                "title": "ColorMagic",
                "graph": graph
            }
            f.write(json.dumps(data) + '\n')


# 生成三个难度的文件
random.seed(42)  # 确保可重现性
create_jsonl_file("easy", 3, 2, "easy.jsonl")
create_jsonl_file("medium", 4, 3, "medium.jsonl") 
create_jsonl_file("hard", 5, 4, "hard.jsonl")
