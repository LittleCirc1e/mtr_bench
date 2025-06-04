import json
import random
from typing import List, Set

def generate_unique_answers(array_length: int, count: int) -> List[str]:
    """生成指定长度的不重复答案列表"""
    answers = set()
    while len(answers) < count:
        nums = [str(random.randint(0, 3)) for _ in range(array_length)]
        answer = ''.join(nums)
        answers.add(answer)
    return list(answers)

def create_prompt(array_length: int) -> str:
    return f"""Let's play Bitwise Query Game! Your task is to discover the hidden array through bitwise operations.

Rules:
1. There is a hidden array of {array_length} integers
2. Each element in the array is between 0 and {array_length-1} inclusive
3. You can ask three types of queries about any two positions i and j:
   - AND query: returns the bitwise AND of elements at positions i and j
   - OR query: returns the bitwise OR of elements at positions i and j
   - XOR query: returns the bitwise XOR of elements at positions i and j

Query Types:
1. To make a query:
   Format: 'My Query: OPERATION i j'
   where:
   - OPERATION is one of: AND, OR, XOR
   - i and j are positions in array (1-based indexing)
   Example: 'My Query: OR 1 2'

2. To submit final answer:
   Format: 'My Answer: a1 a2 ... a{array_length}'
   where a1 to a{array_length} are your guessed array elements
   Example: 'My Answer: 0 0 2 3'

Example Interaction:
Array length = {array_length}
You: 'My Query: OR 1 2'
Me: '0' (result of OR operation)
You: 'My Query: OR 2 3'
Me: '2' (result of OR operation)
You: 'My Query: XOR 2 4'
Me: '3' (result of XOR operation)
You: 'My Answer: 0 0 2 3'

Instructions:
1. Make queries based on previous results
2. Use exactly the formats shown above
3. Explain your reasoning before each query

Remember:
- All array elements are between 0 and {array_length-1}
- Position indices start from 1
- Think carefully about which operations to use
- Use your queries wisely to gather maximum information

Ready to start? Make your first query!"""

def create_jsonl_file(filename: str, array_length: int, count: int = 30):
    """创建JSONL文件"""
    # 生成不重复的答案
    answers = generate_unique_answers(array_length, count)
    
    with open(filename, 'w') as f:
        for i in range(count):
            data = {
                "question_id": str(i + 1),
                "prompt": create_prompt(array_length),
                "type": "Information Query",
                "feedback": "Indirect Value Response",
                "scale": array_length,
                "difficulty": filename.split('.')[0],  # easy/medium/hard
                "title": "BitQuery",
                "answer": answers[i]
            }
            f.write(json.dumps(data) + '\n')
    
    print(f"Created {filename} with {count} problems")

# 生成三个难度的文件
def main():
    difficulties = [
        ("easy.jsonl", 4),
        #("medium.jsonl", 8),
        #("hard.jsonl", 12)
    ]
    
    for filename, array_length in difficulties:
        create_jsonl_file(filename, array_length)

if __name__ == "__main__":
    main()
