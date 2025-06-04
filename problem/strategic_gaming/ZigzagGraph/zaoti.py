
import random
import json

def generate_game_prompt(n, edge_weights):
    # 生成边的描述文本
    edge_desc = []
    for i in range(1, n+1):
        weights = []
        for j in range(n):
            weights.append(edge_weights[f"{i}-{j+n+1}"])
        edge_desc.append(f"     Node {i}: {weights} to nodes {','.join(str(x) for x in range(n+1, 2*n+1))}")
    
    prompt = f"""Let's play the Zigzag Graph Game! Your task is to win this game by strategically moving through the graph while following increasing or decreasing edge weights.

Rules:
1. Game Setup:
   - Graph: {n}*{n} bipartite graph
   - Left nodes: {', '.join(str(x) for x in range(1, n+1))}
   - Right nodes: {', '.join(str(x) for x in range(n+1, 2*n+1))}
   - Edge weights:
     {chr(10).join(edge_desc)}
   - All edge weights are distinct

2. Game Mechanics:
   - You choose "decreasing" mode and I choose "increasing" mode
   - You place token on one node and then I place token on one node
   - Players take turns moving token to adjacent unvisited nodes:
     * Must move from opponent's last chosen node
     * Edge weight must be less than last used edge (for you)
     * Edge weight must be greater than last used edge (for me)
   - Cannot visit same node twice

3. Victory Conditions:
   - Player loses if unable to make a valid move from opponent's node
   - Game ends when no legal moves remain

Instructions:
- Format your move as: 'My Choice: X' where X is the node number (1-{2*n})
- Give your reasoning before each move
- Wait for my response before your next move

Example Round:
Initial placement:
You: 'My Choice: 2'
- Placing token at node 2

I: 'My Choice: 5'
- Moving from node 2 to node 5 with edge weight 8

You: 'My Choice: 3'
- Moving from node 5 to node 3 with edge weight 6
- Following decreasing rule: 6 < 8

I: 'My Choice: 6'
- Moving from node 3 to node 6 with edge weight 9
- Following increasing rule: 9 > 6

Remember:
- Use exact format: 'My Choice: X'
- Must move from opponent's last node
- Follow decreasing weight rule
- Invalid move = automatic loss

Ready to start? Make your first query!"""
    return prompt

def generate_edge_weights(n):
    """生成不重复的边权重"""
    edge_weights = {}
    weights = list(range(1, n*n + 1))
    random.shuffle(weights)
    
    idx = 0
    for i in range(1, n+1):
        for j in range(n+1, 2*n+1):
            edge_weights[f"{i}-{j}"] = weights[idx]  # 修改键的格式 
            idx += 1
            
    return edge_weights

def generate_jsonl(n, num_examples, difficulty):
    filename = f"{difficulty}.jsonl"
    
    with open(filename, 'w') as f:
        for i in range(num_examples):
            edge_weights = generate_edge_weights(n)
            
            data = {
                "prompt": generate_game_prompt(n, edge_weights),
                "type": "Strategic Gaming",
                "scale": n,
                "difficulty": difficulty,
                "title": "ZigzagGraph",
                "question_id": i + 1,
                "edge_weights": edge_weights,
                "turns": 2*n
            }
            
            f.write(json.dumps(data) + '\n')

# Generate files for different difficulties
difficulties = {
    "easy": 5,
    "medium": 8,
    "hard": 12
}

for diff, n in difficulties.items():
    generate_jsonl(n, 30, diff)
