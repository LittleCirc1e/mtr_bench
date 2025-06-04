import json
import random
import json
import random

def check_valid_rectangle(colored_cells):
    # 检查是否存在满足条件的矩形
    cells = [(eval(k)[0], eval(k)[1]) for k in colored_cells.keys()]
    for i in range(len(cells)):
        for j in range(i+1, len(cells)):
            x1, y1 = cells[i]
            x2, y2 = cells[j]
            # 检查另外两个顶点
            if (x1, y2) in cells and (x2, y1) in cells:
                # 检查颜色是否都不同
                colors = {colored_cells[str((x1,y1))], 
                         colored_cells[str((x1,y2))],
                         colored_cells[str((x2,y1))], 
                         colored_cells[str((x2,y2))]}
                if len(colors) == 4:
                    return True
    return False

def generate_initial_coloring(size):
    while True:
        colored_cells = {}
        cells = [(x+1, y+1) for x in range(size) for y in range(size)]
        num_colored = random.randint(size, 2*size-1)
        chosen_cells = random.sample(cells, num_colored)
        
        # 确保一半的格子颜色相同
        same_color = random.randint(1, 2*size)
        num_same = num_colored
        
        for i, cell in enumerate(chosen_cells):
            if i < num_same:
                color = same_color
            else:
                color = random.randint(1, 2*size)
                while color == same_color:  # 避免重复
                    color = random.randint(1, 2*size)
            colored_cells[str(cell)] = color
            
        # 检查是否存在满足条件的矩形
        if not check_valid_rectangle(colored_cells):
            return colored_cells

def create_prompt(size, colored_cells):
    # 创建初始染色描述
    coloring_description = "Initially colored cells:\n"
    for cell, color in colored_cells.items():
        cell = cell.strip('()').split(',')
        x, y = int(cell[0]), int(cell[1])
        coloring_description += f"- Cell at position ({x}, {y}) is colored with color {color}\n"

    # 原来的base_prompt内容保持不变
    base_prompt = f"""Let's play the Grid Coloring Game! Find a special rectangular pattern on the grid.

Rules:
1. Game Setup:
   - I have a {size}*{size} grid
   - {coloring_description}

2. Game Mechanics:
   - You can make up to 10 moves
   - Each move: Choose an uncolored cell by specifying coordinates (x,y)
   - I will respond by coloring that cell with a color of my choice (1 to {2*size})
   - Your goal: Find 4 colored cells that form a valid rectangle

3. Victory Conditions:
   A valid rectangle must:
   - Have all 4 cells colored
   - Have different colors in all 4 cells
   - Form a rectangle with sides parallel to grid lines
   
Instructions:
- For each move, format your query as: "My Choice: x y" (where 1=<x,y=<{size})
- When you find a valid rectangle, submit your answer as: "My Answer: x1 x2 y1 y2"
   where (x1,y1), (x1,y2), (x2,y1), (x2,y2) are the coordinates of your rectangle
- Give your reasoning before making each move
- Wait for my response (color number) before making your next move

Example Interaction:
Given a 3*3 grid with initial coloring:
- Cell at position (1,1) has color 1
- Cell at position (2,2) has color 2
- Cell at position (3,3) has color 3

You: 'My Choice: 1 2'

I: 'Cell (1,2) colored with color 4'

You: 'My Choice: 2 1'

I: 'Cell (2,1) colored with color 5'

You: 'My Answer: 1 2 1 2'

I: 'Win!'

Remember:
- Use exact format: "My Choice: x y" for queries
- Use exact format: "My Answer: x1 x2 y1 y2" for final answer
- Explain your reasoning before making a choice
- Wait for my color response before next move
- Choosing already colored cell = invalid move = immediate loss
- All 4 cells in rectangle must have different colors

Ready to start? Make your first query!"""
    return base_prompt

# 其余代码保持不变

def generate_jsonl(filename, size, num_entries, difficulty):
    with open(filename, 'w') as f:
        for i in range(num_entries):
            colored_cells = generate_initial_coloring(size)
            entry = {
                "question_id": i + 1,
                "prompt": create_prompt(size, colored_cells),
                "type": "Strategic Gaming",
                "scale": size,
                "difficulty": difficulty,
                "title": "GridColoring",
                "colored_cells": colored_cells,
                "turns":10
            }
            f.write(json.dumps(entry) + '\n')

# 生成 easy.jsonl (size=5)
generate_jsonl('easy.jsonl', 30, 30, "easy")

# 生成 medium.jsonl (size=10)
generate_jsonl('medium.jsonl', 20, 30, "medium")

# 生成 hard.jsonl (size=15)
generate_jsonl('hard.jsonl', 10, 30, "hard")

