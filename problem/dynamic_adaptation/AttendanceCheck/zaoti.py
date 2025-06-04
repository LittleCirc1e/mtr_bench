import json
import random

def create_prompt(n):
    return """Let's play the Attendance Check Game! Your task is to find the absent student through a series of range queries.

Rules:
1. There are {n} students (numbered 1 to {n})
2. Exactly one student is absent
3. You can make queries about ranges of students
4. Students might be dishonest in their responses

Query Types:
1. To make a range query:
   Format: 'My Query: l r'
   where:
   - l and r are the range boundaries (1 =< l =< r =< {n})
   Example: 'My Query: 1 4'
   Response will be number of students who raised hands

2. To mark absent students:
   Format: 'My Answer: a'
   where:
   - a is the student number you think is absent
   Example: 'My Answer: 3'

Response Types for Range Queries:
For a query (l,r), you'll get either r-l or r-l+1 students raising hands:
1. True Positive: r-l+1 present, r-l+1 raised
2. True Negative: r-l present, r-l raised
3. False Positive: r-l present, r-l+1 raised
4. False Negative: r-l+1 present, r-l raised

Important Rules:
1. Students will never answer honestly 3 times in a row
2. Students will never answer dishonestly 3 times in a row

Example Interaction:
You: 'My Query: 1 4'
Me: '3' (3 students raised hands)
You: 'My Query: 3 5'
Me: '2' (2 students raised hands)
You: 'My Answer: 2'
Me: 'Correct' 

Remember:
- Plan your queries carefully
- Students are strategically dishonest
- Use exactly the formats shown above
- Explain your reasoning before each query

Ready to start? Make your first query!""".format(n=n)

def create_file(n_range, difficulty):
    filename = f"{difficulty}.jsonl"
    used_configs = set()
    
    with open(filename, 'w') as f:
        question_id = 1
        while question_id <= 30:  # 生成30个问题
            # 随机选择一个n值
            n = random.choice(list(n_range))
            
            # 生成答案数组
            answer = [1] * n
            absent_student = random.randint(0, n-1)
            answer[absent_student] = 0
            
            # 检查配置是否重复
            config = (n, absent_student)
            if config not in used_configs:
                used_configs.add(config)
                
                data = {
                    "question_id": question_id,
                    "prompt": create_prompt(n),
                    "type": "Dynamic Adaptation",
                    "feedback": "Indirect Value Response",
                    "scale": n,
                    "difficulty": difficulty,
                    "title": "AttendanceCheck",
                    "answer": answer
                }
                f.write(json.dumps(data) + '\n')
                question_id += 1

# 创建三个文件
create_file(range(5, 10), "easy")      # 5-9个学生
create_file(range(10, 15), "medium")   # 10-14个学生
create_file(range(15, 20), "hard")     # 15-19个学生
