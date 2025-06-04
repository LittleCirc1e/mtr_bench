import random
import json
from typing import List, Dict
import math
def generate_convex_polygon(n: int) -> List[List[int]]:
    """生成凸多边形的顶点"""
    # 生成中心点周围的随机点
    angles = sorted([random.uniform(0, 2*3.14159) for _ in range(n)])
    radius = random.randint(5, 10)
    points = []
    
    for angle in angles:
        x = int(10 + radius * math.cos(angle))
        y = int(10 + radius * math.sin(angle))
        points.append([x, y])
        
    return points

def generate_game_prompt(n: int, points: List[List[int]]) -> str:
    # 转换点为字符串格式
    points_str = "\n".join(f"     ({x},{y})" for x, y in points)
    
    prompt = f"""Let's play the Pizza Slice Game! Your task is to eat as little spinach pizza as possible by strategically choosing vertices. The player who eats less total area wins!

Rules:
1. Game Setup:
   - Pizza shape: {n}-vertex convex polygon
   - Vertices:
{points_str}
   - You play first, I play second
   - Total {(n-2)} turns to complete

2. Game Mechanics:
   - Players take turns choosing vertices
   - When chosen, player eats triangle formed by:
     * The chosen vertex
     * Its two neighboring edges
   - After each choice, pizza loses one vertex
   - Game ends when all pizza is eaten
   - Each vertex can only be chosen once

3. Area Calculation Example:
   If you choose vertex 1 (x1,y1):
   - Triangle area = |(x2-x1)(y3-y1) - (x3-x1)(y2-y1)|/2
   - Where (x2,y2) and (x3,y3) are neighboring vertices
   - Area adds to your total eaten amount
   - Player with smaller total area wins!

Instructions:
- For each turn - Choose vertex with: 'My Choice: X'
  where X is vertex index (1 to {n})
- Give your reasoning before each choice

Example Round:
You: 'My Choice: 1'
Me: '3'
You: 'My Choice: 2'
Me: '4'

Result: Add up areas of your triangles and compare with mine to determine winner!

Remember:
- Use exact format: 'My Choice: X'
- Choose only available vertices
- Aim to eat LESS total area than opponent
- Invalid move = automatic loss
- Victory = eating smaller total area than opponent

Ready to start? Make your first query!"""
    return prompt

def generate_jsonl(n: int, num_examples: int, difficulty: str):
    filename = f"{difficulty}.jsonl"
    
    with open(filename, 'w') as f:
        for i in range(num_examples):
            points = generate_convex_polygon(n)
            points_dict = {f"{j+1}": points[j] for j in range(n)}
            
            data = {
                "prompt": generate_game_prompt(n, points),
                "type": "Strategic Gaming",
                "scale": n,
                "difficulty": difficulty,
                "title": "PizzaSlice",
                "question_id": i + 1,
                "points": points_dict,
                "turns": (n-2)/2  # 除以2是因为双方轮流
            }
            
            f.write(json.dumps(data) + '\n')

# Generate files for different difficulties
difficulties = {
    "easy": 6,
    "medium": 8,
    "hard": 12
}

for diff, n in difficulties.items():
    generate_jsonl(n, 30, diff)
