import json
import random

def get_base_prompt(n, k):
    return f"""Let's play Zero Finding Game! Your task is to find the {k}-th zero in a hidden binary array through range sum queries.

Rules:
1. There is a hidden array of {n} elements (all 0s and 1s)
2. You need to find the {k}-th zero
3. Each time you find a non-target zero (not {k}-th), it turns into 1
4. The game continues until you find the {k}-th zero

Query Types:
1. To make a range sum query:
   Format: 'My Query: l r'
   where:
   - l and r are positions (1-based indexing)
   - l ≤ r ≤ {n}
   Example: 'My Query: 4 6'
   Response will be the sum of elements in positions l to r

2. To submit temporary answer:
   Format: 'My Answer: x'
   where x is position of a non-{k}-th zero
   Example: 'My Answer: 5'

3. To submit final answer:
   Format: 'My Final Answer: x'
   where x is position of the {k}-th zero
   Example: 'My Final Answer: 3'

Example Interaction:
Finding 2nd zero:
You: 'My Query: 4 6'
Me: '1' (sum in range [4,6])
You: 'My Answer: 5'
Me: 'Correct! Non-target zero found and turned to 1'
You: 'My Final Answer: 3'
Me: 'Correct! You found the 2nd zero!'

Instructions:
1. Game Process:
   - Make queries to locate zeros
   - Use 'My Answer' for non-{k}-th zeros
   - Use 'My Final Answer' for the {k}-th zero
   - Array updates when non-target zeros are found
2. Use exactly the formats shown above
3. Explain your reasoning before each action

Remember:
- Array only contains 0s and 1s
- Position indices start from 1
- Non-target zeros turn into 1 when found
- Each query shows sum in range
- Use different formats for target and non-target zeros

Ready to start? Make your first query!"""

def find_kth_zero_position(array: list, k: int) -> int:
    """找到数组中第k个0的位置（从1开始计数）"""
    zero_count = 0
    for i, num in enumerate(array, 1):  # 从1开始计数
        if num == 0:
            zero_count += 1
            if zero_count == k:
                return i
    return -1  # 如果没有找到第k个0

def generate_binary_array(n: int, min_zeros: int) -> list:
    """生成随机二进制数组，确保至少有min_zeros个0"""
    # 确保至少有指定数量的0，但不超过n/2个0
    zero_count = random.randint(min_zeros, min(n//2, min_zeros + 3))
    arr = [0] * zero_count + [1] * (n - zero_count)
    random.shuffle(arr)
    return arr

def create_jsonl(filename: str, n: int, difficulty: str):
    used_combinations = set()
    
    with open(filename, 'w') as f:
        for i in range(1, 31):
            # 生成不同的数组和k值组合
            while True:
                # 确保至少有2个0，这样k可以有多个选择
                binary_array = generate_binary_array(n, min_zeros=20)
                zero_count = sum(1 for x in binary_array if x == 0)
                k = random.randint(1, zero_count)
                
                # 找到第k个0的位置
                kth_zero_pos = find_kth_zero_position(binary_array, k)
                
                # 创建用于判断重复的组合
                combination = (tuple(binary_array), k)
                
                if combination not in used_combinations:
                    used_combinations.add(combination)
                    break
            
            data = {
                "question_id": i,
                "prompt": get_base_prompt(n, k),
                "type": "Dynamic Adaptation",
                "feedback": "Indirect Value Response",
                "scale": n,
                "difficulty": difficulty,
                "title": "ZeroFinding",
                "list": binary_array,
                "k": k,
                "answer": kth_zero_pos
            }
            
            f.write(json.dumps(data) + '\n')

def main():
    # 创建三个不同难度的文件
    #create_jsonl('easy.jsonl', 10, 'easy')
    #create_jsonl('medium.jsonl', 50, 'medium')
    create_jsonl('hard.jsonl', 100, 'hard')

if __name__ == "__main__":
    main()
