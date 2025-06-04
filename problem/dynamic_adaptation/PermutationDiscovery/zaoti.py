import json
import random

def get_base_prompt(n):
    return f"""Let's play Permutation Discovery Game! Your task is to find a hidden permutation through dynamic queries.

Rules:
1. There are two permutations of length {n}:
   - p: hidden permutation you need to discover
   - q: visible permutation that changes after each query
2. Initially, q is [1,2,...,{n}]
3. After each query, q changes following this rule:
   - For each position i: q'[i] = q[p[i]]
4. Your goal is to discover permutation p

Query Types:
1. To ask about q's value:
   Format: 'My Query: i'
   where:
   - i is a position (1-based indexing)
   Example: 'My Query: 3'
   Response will be the value at position i in current q

2. To submit final answer:
   Format: 'My Answer: p1 p2 ... p{n}'
   where p1 to p{n} form your guessed permutation
   Example: 'My Answer: 4 2 1 3'

Example Interaction:
Initial q = [1,2,...,{n}]
You: 'My Query: 3'
Me: '3'
[q updates based on p]
You: 'My Query: 2'
Me: '2'
[q updates again]
You: 'My Answer: 4 2 1 3'

Instructions:
1. Make queries based on previous results
2. Use exactly the formats shown above
3. Explain your reasoning before each query
4. Watch how q changes after each query

Remember:
- q starts as [1,2,...,{n}]
- Position indices start from 1
- q changes after every query
- Think carefully about which positions to query

Ready to start? Make your first query!"""

def generate_permutation(n):
    """生成1到n的随机排列"""
    perm = list(range(1, n + 1))
    random.shuffle(perm)
    return perm

def calculate_next_q(current_q, p):
    """根据p计算下一个q"""
    n = len(p)
    next_q = [0] * n
    for i in range(n):
        next_q[i] = current_q[p[i]-1]  # p[i]-1因为p中的值是1-based
    return next_q

def create_jsonl(filename, n, difficulty):
    used_permutations = set()
    
    with open(filename, 'w') as f:
        for i in range(1, 31):
            # 生成不重复的p排列
            while True:
                p = generate_permutation(n)
                p_tuple = tuple(p)
                if p_tuple not in used_permutations:
                    used_permutations.add(p_tuple)
                    break
            
            # 初始q
            initial_q = list(range(1, n + 1))
            
            # 生成一些示例q的变化
            example_states = []
            current_q = initial_q.copy()
            for _ in range(3):  # 存储前3次变化的状态
                current_q = calculate_next_q(current_q, p)
                example_states.append(current_q.copy())
            
            data = {
                "question_id": i,
                "prompt": get_base_prompt(n),
                "type": "Dynamic Adaptation",
                "feedback": "Indirect Value Response",
                "scale": n,
                "difficulty": difficulty,
                "title": "PermutationDiscovery",
                "p": p,                         # 隐藏的排列
                "q": initial_q      # 初始q
            }
            
            f.write(json.dumps(data) + '\n')

def main():
    # 创建三个不同难度的文件
    #create_jsonl('test.jsonl', 3, 'easy')
    create_jsonl('medium.jsonl', 5, 'medium')
    create_jsonl('hard.jsonl', 6, 'hard')

if __name__ == "__main__":
    main()
