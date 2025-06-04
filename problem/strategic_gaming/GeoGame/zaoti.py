import json
import random
from typing import List, Tuple
from itertools import permutations

def calculate_distance(point1: Tuple[int, int], point2: Tuple[int, int]) -> int:
    """计算两点间的欧几里得距离的平方"""
    dx = point1[0] - point2[0]
    dy = point1[1] - point2[1]
    return dx * dx + dy * dy

def has_even_sum_combination(starting_point: Tuple[int, int], points: List[Tuple[int, int]]) -> bool:
    """检查是否存在一种组合使得距离和为偶数"""
    # 检查所有可能的6点排列
    for perm in permutations(points):
        total_distance = calculate_distance(starting_point, perm[0])  # 起点到第一个点
        
        # 计算相邻点之间的距离
        for i in range(len(perm)-1):
            distance = calculate_distance(perm[i], perm[i+1])
            total_distance += distance
        
        # 如果找到一个偶数和，返回True
        if total_distance % 2 == 0:
            return True
    
    return False

def generate_unique_points(num_points: int, max_coord: int = 10) -> List[Tuple[int, int]]:
    """生成不重复的点"""
    points = set()
    while len(points) < num_points:
        x = random.randint(0, max_coord)
        y = random.randint(0, max_coord)
        points.add((x, y))
    return list(points)

# def generate_valid_points() -> Tuple[Tuple[int, int], List[Tuple[int, int]]]:
#     """生成有效的点集（确保存在偶数和的组合）"""
#     while True:
#         all_points = generate_unique_points(5)  # 5个点：1个起始点和6个可选点
#         starting_point = all_points[0]
#         available_points = all_points[1:]
        
#         if has_even_sum_combination(starting_point, available_points):
#             return starting_point, available_points

# def format_prompt(starting_point: Tuple[int, int], points: List[Tuple[int, int]]) -> str:
#     base_prompt = """Let's play Geometric Distance Game! Your task is to win this game by choosing points and controlling the sum's parity.

# Rules:
# 1. Game Setup:
#    - Starting point: ({sx},{sy})
#    - Available points: 
#      Point 1: ({x1},{y1})
#      Point 2: ({x2},{y2})
#      Point 3: ({x3},{y3})
#      Point 4: ({x4},{y4})

# 2. Game Mechanics:
#    - Players take turns choosing one point
#    - Each point can only be chosen once
#    - After each choice, add the squared distance to sum:
#      * First turn: distance from ({sx},{sy}) to your choice
#      * Later turns: distance from opponent's last choice to your choice
#    - Game ends when all points are chosen
#    - You win if final sum is even

# 3. Distance Calculation Example:
#    If you choose (0,1):
#    - From (0,0): distance squared = (0-0)^2 + (1-0)^2 = 0 + 1 = 1
#    - Sum becomes 1

# Instructions:
# - For each turn - Choose a point and format your choice as: 'My Choice: X', where X is point index (1 to 4)
# - Give your reasoning before giving your choice

# Example Round:
# Given:
# - Starting point: (0,0)
# - Points: (1,0), (0,1), (1,1), (1,2)

# You: 'My Choice: 4'
# - Distance from (0,0) to (1,2): (1-0)^2 + (2-0)^2 = 1 + 4 = 5
# - Sum = 5

# Me: 'My Choice: 2'
# - Distance from (1,2) to (0,1): (0-1)^2 + (1-2)^2 = 1 + 1 = 2
# - Sum = 5 + 2 = 7

# You: 'My Choice: 3'
# - Distance from (0,1) to (1,1): (1-0)^2 + (1-1)^2 = 1 + 0 = 1
# - Sum = 7 + 1 = 8

# Me: 'My Choice: 1'
# - Distance from (1,1) to (1,0): (1-1)^2 + (0-1)^2 = 0 + 1 = 1
# - Sum = 8 + 1 = 9

# Result: You lose! (Final sum = 9 is odd)

# Remember:
# - Use exact format: 'My Choice: X'
# - Choose only available points (1-4)
# - Plan moves to make final sum even
# - Invaild move = automatic loss

# Ready to start? Make your first query!"""

#     return base_prompt.format(
#         sx=starting_point[0], sy=starting_point[1],
#         x1=points[0][0], y1=points[0][1],
#         x2=points[1][0], y2=points[1][1],
#         x3=points[2][0], y3=points[2][1],
#         x4=points[3][0], y4=points[3][1]
#     )


# def format_prompt(starting_point: Tuple[int, int], points: List[Tuple[int, int]]) -> str:
#     base_prompt = """Let's play Geometric Distance Game! Your task is to win this game by choosing points and controlling the sum's parity.

# Rules:
# 1. Game Setup:
#    - Starting point: ({sx},{sy})
#    - Available points: 
#      Point 1: ({x1},{y1})
#      Point 2: ({x2},{y2})
#      Point 3: ({x3},{y3})
#      Point 4: ({x4},{y4})
#      Point 5: ({x5},{y5})
#      Point 6: ({x6},{y6})

# 2. Game Mechanics:
#    - Players take turns choosing one point
#    - Each point can only be chosen once
#    - After each choice, add the squared distance to sum:
#      * First turn: distance from ({sx},{sy}) to your choice
#      * Later turns: distance from opponent's last choice to your choice
#    - Game ends when all points are chosen
#    - You win if final sum is even

# 3. Distance Calculation Example:
#    If you choose (0,1):
#    - From (0,0): distance squared = (0-0)^2 + (1-0)^2 = 0 + 1 = 1
#    - Sum becomes 1

# Instructions:
# - For each turn - Choose a point and format your choice as: 'My Choice: X', where X is point index (1 to 6)
# - Give your reasoning before giving your choice

# Example Round:
# Given:
# - Starting point: (0,0)
# - Points: (1,0), (0,1), (1,1), (1,2)

# You: 'My Choice: 4'
# - Distance from (0,0) to (1,2): (1-0)^2 + (2-0)^2 = 1 + 4 = 5
# - Sum = 5

# Me: 'My Choice: 2'
# - Distance from (1,2) to (0,1): (0-1)^2 + (1-2)^2 = 1 + 1 = 2
# - Sum = 5 + 2 = 7

# You: 'My Choice: 3'
# - Distance from (0,1) to (1,1): (1-0)^2 + (1-1)^2 = 1 + 0 = 1
# - Sum = 7 + 1 = 8

# Me: 'My Choice: 1'
# - Distance from (1,1) to (1,0): (1-1)^2 + (0-1)^2 = 0 + 1 = 1
# - Sum = 8 + 1 = 9

# Result: You lose! (Final sum = 9 is odd)


# Remember:
# - Use exact format: 'My Choice: X'
# - Choose only available points (1-6)
# - Plan moves to make final sum even
# - Invalid move = automatic loss

# Ready to start? Make your first query!"""

#     return base_prompt.format(
#         sx=starting_point[0], sy=starting_point[1],
#         x1=points[0][0], y1=points[0][1],
#         x2=points[1][0], y2=points[1][1],
#         x3=points[2][0], y3=points[2][1],
#         x4=points[3][0], y4=points[3][1],
#         x5=points[4][0], y5=points[4][1],
#         x6=points[5][0], y6=points[5][1]
#     )

# def generate_valid_points() -> Tuple[Tuple[int, int], List[Tuple[int, int]]]:
#     """生成有效的点集（确保存在偶数和的组合）"""
#     while True:
#         all_points = generate_unique_points(7)  # 7个点：1个起始点和6个可选点
#         starting_point = all_points[0]
#         available_points = all_points[1:]
        
#         if has_even_sum_combination(starting_point, available_points):
#             return starting_point, available_points


def format_prompt(starting_point: Tuple[int, int], points: List[Tuple[int, int]]) -> str:
    base_prompt = """Let's play Geometric Distance Game! Your task is to win this game by choosing points and controlling the sum's parity.

Rules:
1. Game Setup:
   - Starting point: ({sx},{sy})
   - Available points: 
     Point 1: ({x1},{y1})
     Point 2: ({x2},{y2})
     Point 3: ({x3},{y3})
     Point 4: ({x4},{y4})
     Point 5: ({x5},{y5})
     Point 6: ({x6},{y6})
     Point 7: ({x7},{y7})
     Point 8: ({x8},{y8})

2. Game Mechanics:
   - Players take turns choosing one point
   - Each point can only be chosen once
   - After each choice, add the squared distance to sum:
     * First turn: distance from ({sx},{sy}) to your choice
     * Later turns: distance from opponent's last choice to your choice
   - Game ends when all points are chosen
   - You win if final sum is even

3. Distance Calculation Example:
   If you choose (0,1):
   - From (0,0): distance squared = (0-0)^2 + (1-0)^2 = 0 + 1 = 1
   - Sum becomes 1

Instructions:
- For each turn - Choose a point and format your choice as: 'My Choice: X', where X is point index (1 to 8)
- Give your reasoning before giving your choice

Example Round:
Given:
- Starting point: (0,0)
- Points: (1,0), (0,1), (1,1), (1,2)

You: 'My Choice: 4'
- Distance from (0,0) to (1,2): (1-0)^2 + (2-0)^2 = 1 + 4 = 5
- Sum = 5

Me: 'My Choice: 2'
- Distance from (1,2) to (0,1): (0-1)^2 + (1-2)^2 = 1 + 1 = 2
- Sum = 5 + 2 = 7

You: 'My Choice: 3'
- Distance from (0,1) to (1,1): (1-0)^2 + (1-1)^2 = 1 + 0 = 1
- Sum = 7 + 1 = 8

Me: 'My Choice: 1'
- Distance from (1,1) to (1,0): (1-1)^2 + (0-1)^2 = 0 + 1 = 1
- Sum = 8 + 1 = 9

Result: You lose! (Final sum = 9 is odd)

Remember:
- Use exact format: 'My Choice: X'
- Choose only available points (1-8)
- Plan moves to make final sum even
- Invalid move = automatic loss

Ready to start? Make your first query!"""

    return base_prompt.format(
        sx=starting_point[0], sy=starting_point[1],
        x1=points[0][0], y1=points[0][1],
        x2=points[1][0], y2=points[1][1],
        x3=points[2][0], y3=points[2][1],
        x4=points[3][0], y4=points[3][1],
        x5=points[4][0], y5=points[4][1],
        x6=points[5][0], y6=points[5][1],
        x7=points[6][0], y7=points[6][1],
        x8=points[7][0], y8=points[7][1]
    )

def generate_valid_points() -> Tuple[Tuple[int, int], List[Tuple[int, int]]]:
    """生成有效的点集（确保存在偶数和的组合）"""
    while True:
        all_points = generate_unique_points(9)  # 9个点：1个起始点和8个可选点
        starting_point = all_points[0]
        available_points = all_points[1:]
        
        if has_even_sum_combination(starting_point, available_points):
            return starting_point, available_points

# 生成文件的代码保持不变
with open('hard.jsonl', 'w') as f:
    for i in range(50):
        # 生成有效的点集
        starting_point, available_points = generate_valid_points()

        data = {
            "question_id": str(i + 1),
            "prompt": format_prompt(starting_point, available_points),
            "type": "strategic_game",
            "available_points": available_points,
            "starting_point": starting_point,
            "difficulty": "hard",
            "title": "GeoGame",
            "turns": 8
        }
        f.write(json.dumps(data) + '\n')
        print(f"Generated valid data {i+1}/50")

print("File created successfully!")


with open('hard.jsonl', 'w') as f:
    for i in range(50):
        # 生成有效的点集
        starting_point, available_points = generate_valid_points()

        data = {
            "question_id": str(i + 1),
            "prompt": format_prompt(starting_point, available_points),
            "type": "strategic_game",
            "available_points": available_points,
            "starting_point": starting_point,
            "difficulty": "hard",
            "title": "GeoGame",
            "turns": 4
        }
        f.write(json.dumps(data) + '\n')
        print(f"Generated valid data {i+1}/50")

print("File created successfully!")
