import json
import random
from typing import List, Set


def generate_tree(n: int) -> List[str]:
    """生成一个有n个节点的随机树的边列表"""
    # 初始化边列表
    edges = []
    
    # 创建并查集用于检测环
    parent = list(range(n + 1))
    
    def find(x):
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]
    
    def union(x, y):
        px, py = find(x), find(y)
        if px != py:
            parent[px] = py
            return True
        return False
    
    # 生成n-1条边
    vertices = list(range(1, n + 1))
    while len(edges) < n - 1:
        v1 = random.randint(1, n)
        v2 = random.randint(1, n)
        
        # 确保不生成自环
        if v1 == v2:
            continue
            
        # 使用并查集检测是否会形成环
        if union(v1, v2):
            # 确保边的表示是小号在前
            edge = f"{min(v1, v2)}{max(v1, v2)}"
            if edge not in edges:  # 避免重复边
                edges.append(edge)
    
    return sorted(edges)  # 排序确保唯一性
def create_prompt(num_vertices: int) -> str:
    return f"""Let's play Legendary Tree! Your task is to discover the structure of a hidden tree through strategic queries.

Rules:
1. There is a hidden tree with {num_vertices} vertices (numbered 1 to {num_vertices})
2. You can ask questions to discover the tree's structure
3. For each question, you need to specify:
   - Set S: A group of vertices (at least one vertex)
   - Set T: Another group of vertices (at least one vertex)
   - Vertex v: Any vertex you choose
   Note: S and T must not have any common vertices

Query Format:
To make a query, write 'My Query: S T v' where:
- S is your first set of vertices (space-separated numbers)
- T is your second set of vertices (space-separated numbers)
- v is the vertex you want to check
For example: 'My Query: 1 2 | 3 | 2'

Response:
You will receive the number of vertex pairs (s,t) where:
- s is from set S
- t is from set T  
- The path from s to t passes through vertex v

Example Interaction:
You: 'My Query: 1 2 | 3 | 2'
Me: 2 (meaning 2 paths through vertex 2)

When ready to answer:
Submit 'My Answer: edge1 edge2 ...' where each edge is 'u-v'
For example: 'My Answer: 1-2 2-3'

Instructions:
1. Use queries to gather information about the tree
2. Format your queries exactly as shown above
3. Think carefully about which vertices to select

Remember:
- S and T must be non-empty and disjoint
- Use your queries wisely to gather maximum information
- Each edge in final answer should appear exactly once

Ready to start? Make your first query!"""
def create_jsonl_file(filename: str, num_vertices: int, count: int = 50):
    """创建JSONL文件"""
    used_trees = set()  # 用于确保树的唯一性
    
    with open(filename, 'w') as f:
        while len(used_trees) < count:
            # 生成树并验证边数是否正确
            tree = generate_tree(num_vertices)
            if len(tree) != num_vertices - 1:
                continue  # 如果边数不正确，重新生成
                
            # 检查是否是唯一的树
            tree_key = ','.join(sorted(tree))
            if tree_key in used_trees:
                continue
                
            used_trees.add(tree_key)
            
            data = {
                "question_id": str(len(used_trees)),
                "prompt": create_prompt(num_vertices),
                "type": "Information Query",
                "feedback": "Indirect Value Response",
                "scale": num_vertices,
                "difficulty": filename.split('.')[0],
                "title": "LegendaryTree",
                "answer": tree
            }
            f.write(json.dumps(data) + '\n')
    
    print(f"Created {filename} with {count} problems")

def main():
    difficulties = [
        ("easy.jsonl", 5),
        ("medium.jsonl", 6),
        ("hard.jsonl", 7)
    ]
    
    for filename, num_vertices in difficulties:
        create_jsonl_file(filename, num_vertices)

if __name__ == "__main__":
    main()