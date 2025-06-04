import json
import random

# 基础prompt模板
# 使用 ASCII 替代符号 <=
base_prompt = """Let's play Binary Number Guessing! Your task is to guess the original hidden number by performing subtraction operations.

Rules:
1. There is a hidden positive integer n (1 <= n <= 500)
2. You will be told the number of 1s in its binary representation
3. For each operation, you can:
   - Subtract any positive integer x from the current number
   - After subtraction, you'll be told the new count of 1s in binary
   - If you try to subtract a number larger than current n, you will get a response of "Invalid"
4. Your goal is to guess the current number after all of your operations

Instructions:
1. For each operation, format your response as:
   "My Operation: X" where X is the number you want to subtract
   - If X is valid (not larger than current n), you'll receive the count of 1s in the new binary number
   - If X is invalid (larger than current n or invalid format), you'll receive "Invalid"
2. When you want to guess the current number:
   "My Answer: N" where N is your guess
   - If correct, you'll receive "Correct"
   - If wrong, you'll receive "Incorrect"
   - If invalid format, you'll receive "Invalid"
3. Give your reasoning before each operation

Example Interaction:
- Original number = 3  (binary: 11, count of 1s: 2)
- You: "My Operation: 1"
- Me: "1" (current number is 2, binary: 10)
- You: "My Operation: 1"
- Me:  "1" (current number is 1, binary: 1)
- You: "My Answer: 1"
- Me: "Correct" ((current number is 1, correct!)

Remember:
- Don't subtract more than the current number
- Use exact format for operations and answer

Ready to start? Make your first query!"""

# 生成50个不同的答案（假设答案范围在1-500之间）
answers = random.sample(range(1, 501), 50)

# 创建JSONL文件
with open('hard.jsonl', 'w', encoding="utf-8") as f:
    for i in range(50):
        data = {
            "question_id": str(i + 1),
            "prompt": base_prompt,
            "type": "Dynamic Adaptation",
            "feedback": "Indirect Value Response",
            "difficulty": "hard",
            "title": "BitGuessing",
            "answer": answers[i]
        }
        f.write(json.dumps(data) + '\n')

print("File created successfully!")
print(f"Generated 50 problems with answers: {answers}")
