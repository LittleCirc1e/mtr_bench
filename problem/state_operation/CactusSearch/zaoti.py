import json
import random

def generate_cactus_graph(n):
    """生成一个仙人掌图的边集合，确保至少有4条路径"""
    edges = []
    # 确保图是连通的，先生成一个基本环/路径
    base = list(range(1, n+1))
    path = []
    # 随机决定是环还是路径
    if random.choice([True, False]):
        # 生成环
        path = base + [1]
    else:
        # 生成路径
        path = base
    edges.append(path)
    
    # 确保至少添加3条额外的边或小路径，保持仙人掌性质
    remaining = random.randint(3, max(3, min(5, n-2)))  # 确保至少3条，但不超过合理范围
    
    # 为了避免重复边，保存已有的边
    used_edges = set()
    for i in range(len(path)-1):
        used_edges.add((path[i], path[i+1]))
        used_edges.add((path[i+1], path[i]))
    if len(path) > 2 and path[0] == path[-1]:  # 如果是环
        used_edges.add((path[-2], path[-1]))
        used_edges.add((path[-1], path[-2]))
    
    # 添加额外的边
    attempts = 0
    while len(edges) < remaining + 1 and attempts < 100:  # +1是因为已经有一条基本路径
        start = random.randint(1, n-1)
        end = random.randint(start+1, n)
        
        # 检查这条边是否已存在
        if (start, end) not in used_edges:
            edges.append([start, end])
            used_edges.add((start, end))
            used_edges.add((end, start))
        attempts += 1
    
    # 如果还不够4条路径，添加更多边直到达到要求
    while len(edges) < 4:
        for i in range(1, n):
            for j in range(i+1, n+1):
                if (i, j) not in used_edges:
                    edges.append([i, j])
                    used_edges.add((i, j))
                    used_edges.add((j, i))
                    if len(edges) >= 4:
                        break
            if len(edges) >= 4:
                break
    
    return edges


def create_prompt(n: int, graph: dict) -> str:
    # 获取具体的图信息
    m = graph["m"]
    paths = graph["paths"]
    
    # 构建路径描述
    path_descriptions = []
    for i, path in enumerate(paths, 1):
        if len(path) == 2:
            path_descriptions.append(f"Path {i}: a direct edge between vertices {path[0]} and {path[1]}")
        else:
            path_descriptions.append(f"Path {i}: a path of length {len(path)-1} through vertices {' -> '.join(map(str, path))}")
    
    paths_text = "\n   ".join(path_descriptions)

    return f"""Let's play Cactus Search Game! Your task is to find a secret vertex in a cactus graph through strategic guessing.

Rules:
1. The game is played on a cactus graph with {n} vertices (numbered from 1 to {n})
2. A secret vertex v has been chosen
3. After each incorrect guess, you'll be told which adjacent vertex leads closer to v

Game Setup:
This cactus graph consists of {n} vertices and {m} distinct paths:
   {paths_text}

Each path represents a sequence of connected vertices, where consecutive vertices are connected by edges.
The graph is structured as a cactus, meaning each edge belongs to at most one cycle.

Query Format:
1. To make a guess:
   Format: 'My Guess: x'
   where x is the vertex number (1 =< x =< {n})
   Example: 'My Guess: 3'

2. System Response:
   - If correct: 'FOUND'
   - If incorrect: 'GO w' (w is adjacent vertex closer to target)

Example Interaction:
You: 'My Guess: 3'
System: 'GO 4'
You: 'My Guess: 4'
System: 'FOUND'

Instructions:
1. Make guesses based on previous responses
2. Use exactly the format shown above
3. Explain your reasoning before each guess

Remember:
- Each vertex is numbered from 1 to {n}
- The graph structure is fixed as described above
- Adjacent vertices in paths are directly connected
- Use responses wisely to navigate towards target

Ready to start? Make your first query!"""

def generate_jsonl(difficulty: str, n: int, num_examples: int):
    filename = f"{difficulty}.jsonl"
    
    with open(filename, 'w') as f:
        for i in range(num_examples):
            edges = generate_cactus_graph(n)
            graph = {
                "n": n,
                "m": len(edges),
                "paths": edges
            }
            
            data = {
                "question_id": i + 1,
                "prompt": create_prompt(n, graph),  # 传入graph参数
                "type": "State Operation",
                "scale": n,
                "difficulty": difficulty,
                "title": "CactusSearch",
                "graph": graph
            }
            
            f.write(json.dumps(data) + '\n')

# 为三个难度生成文件
settings = {
    "easy": 10,
    "medium": 12,
    "hard": 15
}

if __name__ == "__main__":
    random.seed(42)  # 设置随机种子以保证可重现性
    
    for diff, n in settings.items():
        generate_jsonl(diff, n, 30)
