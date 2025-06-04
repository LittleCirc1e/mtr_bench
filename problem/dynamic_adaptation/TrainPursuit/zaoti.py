import json
import random
from itertools import product

def get_base_prompt(n, k):
    return f"""Let's play Train Pursuit Game! Your task is to find a moving train on a circular railway through range queries.

Rules:
1. There is a train hidden at one of {n} stations (numbered 1 to {n})
2. The train moves circularly:
   - Can move up to {k} stations after each query
   - After station {n}, continues from station 1
   - Example: at station {n}, moving 2 stations means going to station 2
3. You can make range queries to find the train
4. Each query must be in valid format or you'll get 'Invalid' response

Query Types:
1. To make a range query:
   Format: 'My Query: l r'
   where:
   - l and r are station numbers (1-based indexing)
   - l =< r =< {n}
   Example: 'My Query: 3 5'
   Response will be:
   - 'Yes' if train is in this range
   - 'No' if train is not in this range
   - 'Invalid' if query format is incorrect

2. To catch the train:
   Format: 'My Answer: x'
   where x is the station you think the train is now at
   Example: 'My Answer: 5'

Example Movement:
If train is at station 1 and moves 2 stations:
- First move: station 1 → station 3
- Second move: station 3 → station 5

Instructions:
1. Make queries based on previous results
2. Use exactly the formats shown above
3. Explain your reasoning before each query
4. Remember circular movement pattern

Remember:
- Train is at a station numbered 1 to {n}
- Train moves up to {k} stations circularly
- Query format must be exact
- Need to find exact location to win
- Invalid queries will receive 'Invalid' response

Ready to start? Make your first query!"""

def generate_valid_combinations():
    # n的可能值：5到15
    # k的可能值：1到n-1
    valid_combinations = []
    for n in range(2, 10):
        for k in range(1, min(5, n)):  # k不超过5且不超过n-1
            valid_combinations.append((n, k))
    return valid_combinations

def create_jsonl(filename, combinations, difficulty):
    used_cases = set()
    
    with open(filename, 'w') as f:
        for i in range(1, 31):
            # 随机选择一个未使用的n,k组合
            while True:
                n, k = random.choice(combinations)
                pos = random.randint(1, n)
                case = (n, k, pos)
                if case not in used_cases:
                    used_cases.add(case)
                    break
            
            data = {
                "question_id": i,
                "prompt": get_base_prompt(n, k),
                "type": "Dynamic Adaptation",
                "feedback": "Indirect Value Response",
                "scale": n,
                "difficulty": difficulty,
                "title": "TrainPursuit",
                "answer": pos,
                "n": n,
                "k": k
            }
            
            f.write(json.dumps(data) + '\n')

def main():
    # 生成所有有效的(n,k)组合
    all_combinations = generate_valid_combinations()
    
    # 根据难度分配不同范围的组合
    easy_combinations = [(n, k) for n, k in all_combinations if n <= 5]
    medium_combinations = [(n, k) for n, k in all_combinations if 5 < n <= 7]
    hard_combinations = [(n, k) for n, k in all_combinations if 7 < n <= 9]
    
    # 创建三个难度的文件
    create_jsonl('easy.jsonl', easy_combinations, 'easy')
    create_jsonl('medium.jsonl', medium_combinations, 'medium')
    create_jsonl('hard.jsonl', hard_combinations, 'hard')

if __name__ == "__main__":
    main()
