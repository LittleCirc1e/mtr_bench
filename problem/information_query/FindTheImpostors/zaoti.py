import random
import json

def generate_unique_answer(existing_answers):
    while True:
        # 生成12位0和1的字符串
        answer = ''.join(random.choice(['0', '1']) for _ in range(12))
        zero_count = answer.count('0')
        # 确保0的数量在4-8之间且答案唯一
        if 4 <= zero_count <= 8 and answer not in existing_answers:
            return answer

# 创建50条记录
records = []
existing_answers = set()  # 用于存储已生成的答案以确保唯一性

for i in range(1, 51):  # 从1到50
    answer = generate_unique_answer(existing_answers)
    existing_answers.add(answer)  # 将新答案添加到集合中
    
    record = {
        "question_id": i,  # 新增的递增ID
        # "prompt": "Let's play Find the Impostors! Your task is to identify all impostors among 6 players.\n\nRules:\n1. There are 6 player\n2. Some players are impostors (k) and others are crewmates (6-k)\n3. The number of impostors k is between 2 and 4\n\nQuery Types:\n1. Ask about three players:\n - Format: \"My Query: a,b,c\" (three different player numbers)\n - Response will be:\n * 0: if there are more impostors than crewmates among these three\n * 1: if there are more crewmates or equal numbers\n * -1: if query is invalid\n\n2. Submit final answer:\n - Format: \"My Answer: x1,x2,... xk\"\n (k is number of impostors, followed by their indices)\n - Response will be:\n * 0 if incorrect\n * 1 if correct\n\nExample interaction:\nYou: \"My Query: 1,2,3\"\nMe: \"0\" (means more impostors in this group)\n\nYou: \"My Query: 3,4,5\"\nMe: \"1\" (means more crewmates in this group)\n\nYou: \"My Answer: 1,2,3,4\"\nMe: 1 (if correct)\n\nInstructions:\n1. You must explain your reasoning before each query\n2. Format your responses exactly as shown above\n\nRemember:\n- Player numbers must be between 1 and 6\n- All three numbers in a query must be different\n\nReady to start? Make your first query!",
        #"prompt": "Let's play Find the Impostors! Your task is to identify all impostors among 9 players.\n\nRules:\n1. There are 9 player\n2. Some players are impostors (k) and others are crewmates (9-k)\n3. The number of impostors k is between 3 and 6\n\nQuery Types:\n1. Ask about three players:\n - Format: \"My Query: a,b,c\" (three different player numbers)\n - Response will be:\n * 0: if there are more impostors than crewmates among these three\n * 1: if there are more crewmates or equal numbers\n * -1: if query is invalid\n\n2. Submit final answer:\n - Format: \"My Answer: x1,x2,... xk\"\n (k is number of impostors, followed by their indices)\n - Response will be:\n * 0 if incorrect\n * 1 if correct\n\nExample interaction:\nYou: \"My Query: 1,2,3\"\nMe: \"0\" (means more impostors in this group)\n\nYou: \"My Query: 3,4,5\"\nMe: \"1\" (means more crewmates in this group)\n\nYou: \"My Answer: 1,2,3,4\"\nMe: 1 (if correct)\n\nInstructions:\n1. You must explain your reasoning before each query\n2. Format your responses exactly as shown above\n\nRemember:\n- Player numbers must be between 1 and 9\n- All three numbers in a query must be different\n\nReady to start? Make your first query!",
        "prompt": "Let's play Find the Impostors! Your task is to identify all impostors among 12 players.\n\nRules:\n1. There are 12 player\n2. Some players are impostors (k) and others are crewmates (12-k)\n3. The number of impostors k is between 4 and 8\n\nQuery Types:\n1. Ask about three players:\n - Format: \"My Query: a,b,c\" (three different player numbers)\n - Response will be:\n * 0: if there are more impostors than crewmates among these three\n * 1: if there are more crewmates or equal numbers\n * -1: if query is invalid\n\n2. Submit final answer:\n - Format: \"My Answer: x1,x2,... xk\"\n (k is number of impostors, followed by their indices)\n - Response will be:\n * 0 if incorrect\n * 1 if correct\n\nExample interaction:\nYou: \"My Query: 1,2,3\"\nMe: \"0\" (means more impostors in this group)\n\nYou: \"My Query: 3,4,5\"\nMe: \"1\" (means more crewmates in this group)\n\nYou: \"My Answer: 1,2,3,4\"\nMe: 1 (if correct)\n\nInstructions:\n1. You must explain your reasoning before each query\n2. Format your responses exactly as shown above\n\nRemember:\n- Player numbers must be between 1 and 12\n- All three numbers in a query must be different\n\nReady to start? Make your first query!",
        "type": "Information Query",
        "feedback": "Indirect Value Response",
        "scale": 12,
        "answer": answer,
        "title": "FindTheImpostors"
    }
    records.append(record)

# 写入JSONL文件
with open('hard.jsonl', 'w') as f:
    for record in records:
        f.write(json.dumps(record) + '\n')

print(f"JSONL文件已生成，共50条记录，question_id从1到50，每条记录的answer都不同。")