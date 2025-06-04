import json
import random

def create_prompt(n):
    return """Let's play Find the Hidden Number Game! Your task is to discover a hidden number through a series of queries and guesses.

Rules:
1. There is a hidden number x between 1 and {n}
2. For each query, you can ask about a set of numbers:
   - You choose any non-empty set of numbers
   - System will tell you if x is in that set ("YES") or not ("NO")
   - WARNING: Responses might be lies!
   - BUT: At least one answer out of any two consecutive queries is truthful
3. For guesses:
   - You can directly guess what x is
   - Guesses are always answered truthfully
   - A correct guess ends the game

Query Types:
1. To make a set query:
   Format: 'My Query: k n1 n2 ... nk'
   where:
   - k is the size of your set
   - n1 to nk are the numbers in your set
   Example: 'My Query: 3 1 2 3'

2. To make a guess:
   Format: 'My Answer: x'
   Example: 'My Answer: 2'

Example Interaction:
You: 'My Query: 3 1 2 3'
Me: 'YES'
You: 'My Query: 2 4 5'
Me: 'YES'
You: 'My Answer: 4'
Me: 'Correct'

Important Notes:
- At least one of any two consecutive queries is truthful
- Guesses are always answered truthfully
- Plan your strategy carefully!

Ready to start? Make your first query!""".format(n=n)

def create_data(n: int, difficulty: str) -> list:
    """创建所有可能的题目数据"""
    all_data = []
    used_answers = set()
    
    # 计算需要生成多少条数据
    num_entries = n  # 对于每个n值生成2条数据
    
    for i in range(1, num_entries + 1):
        # 确保answer不重复
        available_answers = set(range(1, n+1)) - used_answers
        if not available_answers:
            used_answers.clear()
            available_answers = set(range(1, n+1))
        answer = random.choice(list(available_answers))
        used_answers.add(answer)
        
        data = {
            "question_id": i,
            "prompt": create_prompt(n),
            "type": "Dynamic Adaptation",
            "feedback": "Direct Value Response",
            "scale": n,
            "difficulty": difficulty,
            "title": "FindHidden",
            "answer": answer
        }
        all_data.append(data)
    return all_data

def create_file(difficulty: str):
    """创建每个难度的文件"""
    filename = f"{difficulty}.jsonl"
    all_data = []
    
    if difficulty == "easy":
        # 生成n=19和n=20的数据
        all_data.extend(create_data(19, difficulty))
        all_data.extend(create_data(20, difficulty))
    elif difficulty == "medium":
        # 生成n=30的数据
        all_data.extend(create_data(30, difficulty))
    else:  # hard
        # 生成n=40的数据
        all_data.extend(create_data(40, difficulty))
    
    # 如果数据超过30条，随机抽取30条
    if len(all_data) > 30:
        all_data = random.sample(all_data, 30)
    
    # 重新分配question_id
    for i, data in enumerate(all_data, 1):
        data["question_id"] = i
    
    # 写入文件
    with open(filename, 'w') as f:
        for data in all_data:
            f.write(json.dumps(data) + '\n')

# 创建三个难度的文件
for diff in ["easy", "medium", "hard"]:
    create_file(diff)

print("Generated jsonl files successfully!")
