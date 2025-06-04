import json
import random

def get_base_prompt(n):
    return f"""Let's play Mimic Hunt Game! Your task is to find a shape-shifting creature among objects through careful observation and removal.

Rules:
1. There are {n} objects in a room, each with a type number (1-9)
2. One object is a mimic that can transform into any type
3. The mimic cannot stay the same type for more than 2 stages

Query Types:
1. To remove objects:
   Format: 'My Query: - k x1 x2 ... xk'
   where:
   - k is number of objects to remove
   - x1 to xk are positions (1-based indexing)
   Example: 'My Query: - 2 1 5'
   Response will be:
   - Remaining objects' types after mixing

2. To identify mimic:
   Format: 'My Answer: i'
   where i is the position of suspected mimic
   Example: 'My Answer: 3'

Example Interaction:
Objects: [1,1,2,2,3]
You: 'My Query: - 2 1 5'
Me: [2,1,2] (remaining objects after mixing)
You: 'My Query: - 4 1 2 3 4'
Me: [2] (remaining objects after mixing)
You: 'My Answer: 5'
Me: 'Correct'

Instructions:
1. Each stage:
   - Observe current objects
   - Either remove some objects or guess mimic
   - After removal, objects are mixed and mimic may change
2. Use exactly the formats shown above
3. Explain your reasoning before each action
4. Remember mimic's transformation rules

Remember:
- Object types are numbers 1-9
- Position indices start from 1
- Mimic can't stay same type >2 stages

Ready to start? Make your first query!"""

def generate_object_list(n):
    # 生成1-9之间的随机数列表
    return [random.randint(1, 9) for _ in range(n)]

def create_jsonl(filename, n, difficulty):
    used_combinations = set()
    
    with open(filename, 'w') as f:
        for i in range(1, 31):
            # 生成不重复的列表和答案组合
            while True:
                # 生成物品列表
                obj_list = generate_object_list(n)
                # 随机选择变形怪位置
                mimic_pos = random.randint(1, n)
                
                # 转换为元组以便比较
                combination = (tuple(obj_list), mimic_pos)
                if combination not in used_combinations:
                    used_combinations.add(combination)
                    break
            
            data = {
                "question_id": i,
                "prompt": get_base_prompt(n),
                "type": "Dynamic Adaptation",
                "feedback": "Indirect Value Response",
                "scale": n,
                "difficulty": difficulty,
                "title": "MimicHunt",
                "list": obj_list,
                "answer": mimic_pos
            }
            
            f.write(json.dumps(data) + '\n')

def main():
    # 创建三个不同难度的文件
    create_jsonl('easy.jsonl', 5, 'easy')
    create_jsonl('medium.jsonl', 10, 'medium')
    create_jsonl('hard.jsonl', 20, 'hard')

if __name__ == "__main__":
    main()
