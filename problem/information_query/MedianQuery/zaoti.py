import json
import random
from typing import List, Tuple

def get_base_prompt(scale):
    return f"""Let's play Median Query Game! Your task is to find specific positions in a hidden permutation through median queries.

Rules:
1. There is a hidden permutation p of length {scale} (numbers 1 to {scale})
2. You can make queries about subsequences of even length
3. Each query returns the two middle values (medians) of your chosen subsequence
4. Your goal is to find positions of values {scale//2} and {scale//2+1}

Query Types:
1. To make a query:
   Format: 'My Query: k x1 x2 ... xk'
   where:
   - k is the length of subsequence (even number, 4 ≤ k ≤ {scale})
   - x1 to xk are distinct positions (1-based indexing)
   Example: 'My Query: {scale} 1 2 3 4 5 6'
   Response will be two numbers: the k/2-th and (k/2+1)-th smallest values in the subsequence

2. To submit final answer:
   Format: 'My Answer: i j'
   where i and j are positions of values {scale//2} and {scale//2+1}
   Example: 'My Answer: 3 6'

Instructions:
1. Make queries based on previous results
2. Use exactly the formats shown above
3. Explain your reasoning before each query

Remember:
- The permutation contains numbers 1 to {scale} exactly once
- Position indices start from 1
- Think carefully about which subsequences to query
- Use your queries wisely to locate the target positions
- Order of positions in final answer doesn't matter

Ready to start? Make your first query!"""

def generate_permutation(scale: int) -> Tuple[List[int], List[int]]:
    # 生成1到scale的随机排列
    perm = list(range(1, scale + 1))
    random.shuffle(perm)
    
    # 找到scale/2和scale/2+1的位置
    pos1 = perm.index(scale//2) + 1
    pos2 = perm.index(scale//2 + 1) + 1
    
    return perm, [pos1, pos2]

def create_jsonl(filename: str, scale: int, difficulty: str):
    used_perms = set()
    
    with open(filename, 'w') as f:
        for i in range(1, 51):
            # 生成不重复的排列
            while True:
                perm, answer = generate_permutation(scale)
                perm_tuple = tuple(perm)
                if perm_tuple not in used_perms:
                    used_perms.add(perm_tuple)
                    break
            
            data = {
                "question_id": i,
                "prompt": get_base_prompt(scale),
                "type": "Information Query",
                "feedback": "Indirect Value Response",
                "scale": scale,
                "difficulty": difficulty,
                "title": "MedianQuery",
                "list": perm,
                "answer": answer
            }
            
            f.write(json.dumps(data) + '\n')

def main():
    # 创建三个不同难度的文件
    #create_jsonl('easy.jsonl', 6, 'easy')
    #create_jsonl('medium.jsonl', 8, 'medium')
    create_jsonl('hard.jsonl', 15, 'hard')

if __name__ == "__main__":
    main()
