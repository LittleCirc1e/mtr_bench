

import random
import json
from typing import List, Dict, Set
from collections import defaultdict
def create_prompt(n: int, graph: List[List[int]]) -> str:
    return f"""Let's play the Treasure Hunt Game! Your task is to explore an enchanted forest where a mischievous wizard keeps scrambling the junction numbers to confuse you.

Rules:
1. Game Setup:
   - Enchanted forest with {n} junctions
   - Each junction contains a treasure
   - You start at junction 1
   - Initial flag placed at starting junction
   - Junctions are connected by fixed paths

2. Game Mechanics:
   What You Can See:
   - At each junction, you can only see:
     * Number of paths at each connected junction
     * Whether you've placed a flag there
   
   The Wizard's Trick:
   - The wizard hides real junction numbers
   - Each time you visit a junction, connected junctions are shown in random order
   - Though connections stay the same, you can't identify specific junctions
   - Must use path counts and flags to navigate

3. Information Format:
   I provide: 'R d deg1 flag1 deg2 flag2 ... degd flagd'
   - R: you're at current junction
   - d: number of connected junctions
   - degi: number of paths at connected junction i
   - flagi: flag status at connected junction i (0=no, 1=yes)
   Example: 'R 3 2 1 4 0 3 0' means:
   - 3 connected junctions
   - First has 2 paths and is flagged
   - Second has 4 paths and no flag
   - Third has 3 paths and no flag

Instructions:
- Format your move as: 'My Choice: X'
  where X is from 1 to d (position in current list)
- Give your reasoning before each choice
- Wait for my response before next move

Example Round:
Starting at junction 1:

Me: 'R 2 2 0 2 0'
- Two connected junctions
- Both have 2 paths
- Neither has your flag

You: 'My Choice: 1'
- Moving to first listed junction

Me: 'R 2 2 0 2 1'
- Two connected junctions shown
- One leads back (has your flag)
- One is unexplored (no flag)

You: 'My Choice: 1'
- Moving to unflagged junction

Remember:
- Real junction numbers are hidden
- Connected junctions appear in random order each visit
- Use path counts and flags to track progress
- Must visit all junctions
- Invalid move = automatic loss

Ready to start? Make your first query!"""


def generate_connected_graph(n: int, max_edges_per_vertex: int = 50) -> List[List[int]]:
    """生成符合要求的连通图"""
    while True:  # 持续尝试直到生成合适的图
        edges = set()
        # 随机生成一个生成树来确保连通性
        vertices = {0}
        remaining = set(range(1, n))
        
        # Prim算法生成随机生成树
        while remaining:
            u = random.choice(list(vertices))
            v = random.choice(list(remaining))
            edges.add((min(u, v), max(u, v)))
            vertices.add(v)
            remaining.remove(v)
        
        # 计算初始度数
        degrees = defaultdict(int)
        for u, v in edges:
            degrees[u] += 1
            degrees[v] += 1
        
        # 随机添加额外的边
        max_edges = min(n*(n-1)//2, 25*n)
        target_edges = random.randint(n + n//2, max_edges)  # 确保足够的边数
        
        attempts = 100  # 尝试添加边的次数
        while len(edges) < target_edges and attempts > 0:
            u = random.randint(0, n-1)
            v = random.randint(0, n-1)
            if u != v and (min(u,v), max(u,v)) not in edges:
                if degrees[u] < max_edges_per_vertex and degrees[v] < max_edges_per_vertex:
                    edges.add((min(u,v), max(u,v)))
                    degrees[u] += 1
                    degrees[v] += 1
            attempts -= 1
        
        # 验证图的质量
        if len(edges) >= n and all(degrees[v] > 1 for v in range(n)):
            # 转换为1-based索引并返回
            return [[u+1, v+1] for u,v in sorted(edges)]
            
def generate_jsonl(n: int, num_examples: int, difficulty: str):
    filename = f"{difficulty}.jsonl"
    seen_graphs = set()  # 用于检查图的唯一性
    
    with open(filename, 'w') as f:
        while len(seen_graphs) < num_examples:
            graph = generate_connected_graph(n)
            # 将图转换为可哈希的格式
            graph_key = tuple(tuple(edge) for edge in sorted(graph))
            
            if graph_key not in seen_graphs:
                seen_graphs.add(graph_key)
                
                data = {
                    "prompt": create_prompt(n, graph),
                    "type": "State Operation",
                    "feedback": "Indirect Value Response",
                    "scale": n,
                    "difficulty": difficulty,
                    "title": "TreasureHunt",
                    "question_id": len(seen_graphs),
                    "graph": graph
                }
                
                f.write(json.dumps(data) + '\n')
# Generate files for different difficulties
difficulties = {
    "easy": 6,
    "medium": 7,
    "hard": 8
}

if __name__ == "__main__":
    # Set random seed for reproducibility
    random.seed(42)
    
    # Generate files for each difficulty
    for diff, n in difficulties.items():
        generate_jsonl(n, 30, diff)
