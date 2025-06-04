import json
import random
from itertools import combinations

def get_base_prompt(scale):
    return f"""Let's play Bitwise Comparison Game! Your task is to find two positions in a hidden permutation that maximize their XOR value.

Rules:
1. There is a hidden permutation of {scale} numbers (0 to {scale-1})
2. Each position contains a unique number from 0 to {scale-1}
3. You can make comparison queries between OR operations:
   - Each query compares (pa|pb) with (pc|pd)
   - | denotes bitwise OR operation
   - You'll receive '<', '=' or '>' as response

Query Types:
1. To make a comparison query:
   Format: 'My Query: a b c d'
   where:
   - a,b,c,d are positions in array (0-based indexing)
   Example: 'My Query: 0 2 3 1'
   Response will be one of: '<', '=', '>'

2. To submit final answer:
   Format: 'My Answer: i j'
   where i and j are the positions with maximum XOR value
   Example: 'My Answer: 3 2'

Instructions:
1. Make queries based on previous comparisons
2. Use exactly the formats shown above
3. Explain your reasoning before each query

Remember:
- All positions contain unique numbers from 0 to {scale-1}
- Position indices start from 0
- Think carefully about which positions to compare
- Use your queries wisely to find maximum XOR pair

Ready to start? Make your first query!"""

def find_max_xor_indices(numbers):
    max_xor = 0
    max_pair = (0, 0)
    for i in range(len(numbers)):
        for j in range(i + 1, len(numbers)):
            xor = numbers[i] ^ numbers[j]
            if xor > max_xor:
                max_xor = xor
                max_pair = (i, j)
    return max_pair

def generate_unique_permutation(scale):
    return random.sample(range(scale), scale)

def create_jsonl(filename, scale, difficulty, num_entries=50):
    used_permutations = set()
    question_id = 1
    
    with open(filename, 'w') as f:
        while question_id <= num_entries:
            # 生成随机排列
            numbers = generate_unique_permutation(scale)
            numbers_tuple = tuple(numbers)
            
            # 确保不重复
            if numbers_tuple in used_permutations:
                continue
                
            used_permutations.add(numbers_tuple)
            
            # 找出最大XOR对应的位置
            i, j = find_max_xor_indices(numbers)
            
            data = {
                "question_id": question_id,
                "prompt": get_base_prompt(scale),
                "type": "Information Query",
                "feedback": "Indirect Value Response",
                "scale": scale,
                "difficulty": difficulty,
                "title": "BitCompare",
                "list": numbers,
                "answer": [i, j]  # 存储最大XOR值对应的索引对
            }
            f.write(json.dumps(data) + '\n')
            question_id += 1

def main():
    # 创建三个不同难度的文件
    create_jsonl('easy.jsonl', 5, 'easy')
    create_jsonl('medium.jsonl', 7, 'medium')
    create_jsonl('hard.jsonl', 9, 'hard')

if __name__ == "__main__":
    main()
