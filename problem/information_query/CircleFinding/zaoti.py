import json
import random
import math

def get_base_prompt(max_coord):
    return f"""Let's play Circle Finding Game! Your task is to discover a hidden circle on a plane through ray-shooting queries.

Rules:
1. There is a hidden circle with center (xc, yc) and radius rc
2. All parameters are integers and |xc|, |yc|, |rc|  =< {max_coord}
3. The radius rc satisfies: 1 =< rc =< √(xc^2 + yc^2) - 1
4. You can shoot rays from origin (0,0) through any point (xq, yq) you specify

Query Types:
1. To shoot a ray:
   Format: 'My Query: xq yq'
   where:
   - xq, yq are integers with |xq|, |yq| ≤ {max_coord}
   - At least one of xq or yq must be non-zero
   Example: 'My Query: 0 -10'
   You'll receive the minimum distance from the ray to the circle
   (0.0 if the ray intersects the circle)

2. To submit final answer:
   Format: 'My Answer: xc yc rc'
   where xc, yc, rc are the circle's parameters
   Example: 'My Answer: 20 10 10'
   You'll receive the correctness of your answer.

Instructions:
1. Make queries based on previous results
2. Use exactly the formats shown above
3. Explain your reasoning before each query
4. All distances are precise to 10^-10

Remember:
- Circle parameters are integers
- Rays start from origin (0,0)
- Think carefully about ray directions
- Use geometric properties to deduce circle location
- Distance is 0 when ray intersects circle

Ready to start? Make your first query!"""

def generate_valid_circle(max_coord):
    while True:
        # 生成圆心坐标
        xc = random.randint(-max_coord, max_coord)
        yc = random.randint(-max_coord, max_coord)
        
        # 计算到原点的距离
        dist_to_origin = math.sqrt(xc*xc + yc*yc)
        
        # 生成有效半径
        if dist_to_origin > 1:  # 确保圆心不在原点
            max_radius = min(int(dist_to_origin - 1), max_coord)
            if max_radius >= 1:
                radius = random.randint(1, max_radius)
                return [xc, yc], radius

def create_jsonl(filename, max_coord, difficulty):
    used_circles = set()
    
    with open(filename, 'w') as f:
        for i in range(1, 31):
            # 生成不重复的圆
            while True:
                center, radius = generate_valid_circle(max_coord)
                circle_key = (tuple(center), radius)
                if circle_key not in used_circles:
                    used_circles.add(circle_key)
                    break
            
            data = {
                "question_id": i,
                "prompt": get_base_prompt(max_coord),
                "type": "Information Query",
                "feedback": "Indirect Value Response",
                "scale": max_coord,
                "difficulty": difficulty,
                "title": "CircleFinding",
                "center": center,
                "radius": radius
            }
            
            f.write(json.dumps(data) + '\n')

def main():
    # 创建三个不同难度的文件
    create_jsonl('easy.jsonl', 200, 'easy')
    create_jsonl('medium.jsonl', 1000, 'medium')
    create_jsonl('hard.jsonl', 1500, 'hard')

if __name__ == "__main__":
    main()
