import random
import json
from collections import defaultdict

def generate_valid_graph(n):
    """生成符合要求的图"""
    # 首先生成一个基础环确保连通性
    edges = [(i, (i+1)%n) for i in range(n)]
    
    # 添加额外的边直到达到要求（每边都在长度<=5的环中）
    possible_edges = []
    for i in range(n):
        for j in range(i+2, min(i+4, n)):
            possible_edges.append((i, j))
    
    # 随机添加边，但保持度数<=3
    degree = defaultdict(int)
    for u, v in edges:
        degree[u] += 1
        degree[v] += 1
    
    random.shuffle(possible_edges)
    for u, v in possible_edges:
        if len(edges) >= min(3*n, 2*n):  # 控制边的数量
            break
        if degree[u] < 3 and degree[v] < 3:
            edges.append((u, v))
            degree[u] += 1
            degree[v] += 1
    
    # 将节点编号调整为1-based
    edges = [(u+1, v+1) for u, v in edges]
    return edges

def generate_game_prompt(n, edges):
    edge_desc = "\n".join(f"   - Edge: ({u}-{v})" for u, v in edges)
    
    prompt = f"""Let's play the Bee Chase Game! Your task is to catch Nastya by strategically moving three bees on a special honeycomb graph.

Rules:
1. Game Setup:
   - Graph: {n} vertices connected by {len(edges)} edges
   - Edges:
{edge_desc}
   - You control 3 bees
   - I control Nastya
   - Each vertex connects to at most 3 others
   - Each edge is part of a cycle of length ≤ 5

2. Game Mechanics:
   - First round:
     * You place 3 bees on any vertices
     * I place Nastya on a different vertex
   - Each subsequent round:
     * You move each bee (or keep in place)
     * I move Nastya along one edge
   - Movement rules:
     * Can only move along edges
     * Multiple bees can share same vertex
     * Nastya must move each turn
     * All moves must be valid graph moves

3. Victory Conditions:
   - You win if any bee reaches same vertex as Nastya
   - You lose if not caught after {n} moves
   - Game ends immediately upon catch

Instructions:
- Format your moves as: 'My Choice: X Y Z'
  where X, Y, Z are vertex numbers for three bees
- Give your reasoning before each move
- Wait for my response (Nastya's new position) before next move

Example Round:
Initial placement:
You: 'My Choice: 1 2 3'
- Placing bees at vertices 1,2,3

I: '5'
- Nastya appears at vertex 5

You: 'My Choice: 2 3 4'
- Moving bees to surround Nastya

I: '6'
- Nastya moves to vertex 6
Result: You catch Nastya!

Remember:
- Use exact format: 'My Choice: X Y Z'
- Choose only valid vertex numbers
- Plan moves to trap Nastya
- Invalid move = immediate loss
- Maximum {n} moves to win

Ready to start? Make your first query!"""
    return prompt

def generate_jsonl(n, num_examples, difficulty):
    filename = f"{difficulty}.jsonl"
    
    with open(filename, 'w') as f:
        for i in range(num_examples):
            edges = generate_valid_graph(n)
            
            data = {
                "prompt": generate_game_prompt(n, edges),
                "type": "Strategic Gaming",
                "scale": n,
                "difficulty": difficulty,
                "title": "BeeChase",
                "question_id": i + 1,
                "graph": edges,
                "turns": n
            }
            
            f.write(json.dumps(data) + '\n')

# Generate files for different difficulties
difficulties = {
    "easy": 10,
    "medium": 20,
    "hard": 40
}

for diff, n in difficulties.items():
    generate_jsonl(n, 30, diff)
