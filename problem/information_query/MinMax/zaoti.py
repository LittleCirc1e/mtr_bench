import json
import random
from typing import List, Set, Tuple

def generate_unique_array(length: int = 6) -> Tuple[str, int, int]:
    """生成一个length位数字字符串，确保只有一个最大值和一个最小值"""
    while True:
        # 生成length-2个中间数字（范围3-7）
        middle_nums = [random.randint(3, 7) for _ in range(length-2)]
        # 生成最小值（1-2）和最大值（8-9）
        min_num = random.randint(1, 2)
        max_num = random.randint(8, 9)
        
        # 将所有数字组合
        all_nums = [min_num] + middle_nums + [max_num]
        # 随机打乱顺序
        random.shuffle(all_nums)
        
        # 确认确实只有一个最大值和一个最小值
        if (all_nums.count(min(all_nums)) == 1 and 
            all_nums.count(max(all_nums)) == 1):
            # 找到最小值和最大值的位置（1-based）
            min_pos = all_nums.index(min(all_nums)) + 1
            max_pos = all_nums.index(max(all_nums)) + 1
            return (''.join(map(str, all_nums)), min_pos, max_pos)

def generate_unique_answers(n: int) -> List[Tuple[str, int, int]]:
    """生成n个不同的数组"""
    arrays = set()
    results = []
    while len(arrays) < n:
        array, min_pos, max_pos = generate_unique_array()
        if array not in arrays:
            arrays.add(array)
            results.append((array, min_pos, max_pos))
    return results

def create_jsonl_file(filename: str, num_entries: int = 50):
    """创建包含指定条目数的jsonl文件"""
    # 生成50个不同的数组
    array_data = generate_unique_answers(num_entries)
    
    # 基础prompt [保持不变]
    base_prompt = """Let's play Find Min Max! Your task is to find the minimum and maximum elements in a hidden array.

Rules:
1. You are given an array of length 6, but you cannot see its elements
2. You can only compare two elements by their positions (i and j)
3. After each comparison, you'll receive one of these responses:
 - '<': element at position i is less than element at position j
 - '=': element at position i equals element at position j
 - '>': element at position i is greater than element at position j

Example:
If we have an array of length 3:
- Query "1 2" would get:
 '>' (means element at position 1 is greater than element at position 2)
- Query "2 3" would get:
 '<' (means element at position 2 is less than element at position 3)

Query Types:
1. Ask about comparison:
 - Format: "My Query: i j" (i and j are positions to compare)
 - Response will be '<', '=' or '>'

2. Submit final answer:
 - Format: "My Answer: ! i j" (where i is minimum position, j is maximum position)
 - Response will be:
 * 1 if correct
 * 0 if incorrect

Instructions:
1. You must explain your reasoning before each query
2. Format your responses exactly as shown above
3. You can only compare two different positions at a time

Remember:
- Positions must be between 1 and 6
- Choose comparisons wisely to minimize queries

Ready to start? Make your first query!"""

    # 写入jsonl文件
    with open(filename, 'w', encoding='utf-8') as f:
        for i, (array, min_pos, max_pos) in enumerate(array_data):
            entry = {
                "question_id": i + 1,
                "prompt": base_prompt,
                "answer": array,
                "min_pos": min_pos,  # 保存最小值位置
                "max_pos": max_pos,  # 保存最大值位置
                "type": "Information Query",
                "feedback": "Indirect Value Response",
                "scale": 6,
                "difficulty": "medium",
                "title": "MinMax"
            }
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')

# 使用示例
output_file = "medium.jsonl"
create_jsonl_file(output_file)
