import json
import random


def create_prompt(n, m=6):
    return """Let's play the Rotary Laser Lock Game! Your task is to discover the final relative positions of metal arcs after your rotations.

Rules:
1. Lock Structure:
   - {n} concentric rings numbered 0 to {n1}
   - Each ring has {total} sections (0 to {total1})
   - Each section can be empty or contain metal
   - Rings can rotate independently

2. Metal Arcs:
   - Each ring has one metal arc
   - Each arc covers exactly 6 consecutive sections
   - Arcs are solid and cannot be broken

3. Rotation Mechanics:
   - You can rotate any ring
   - Clockwise rotation: +1 section
   - Anticlockwise rotation: -1 section
   - Ring 0 is your reference ring

4. Laser Detection:
   - {total} lasers emit from center
   - One laser per section
   - Metal arcs block lasers
   - Display shows count of unblocked lasers

Query Format:
'My Query: x d'
- x: ring number (0 to {n1})
- d: direction (-1 or +1)
Example: 'My Query: 2 1' rotates ring 2 clockwise

Answer Format:
'My Answer: p1 p2 p3 p4'
- Each pi is final position of ring i relative to ring 0 (Excluding ring 0 and starting from ring 1)
- Positions range from 0 to {total1}

Example Round:
Initial state unknown, {total} sections per ring

You: 'My Query: 1 1'
- Rotating ring 1 clockwise
Me: '10'
- 10 lasers pass through

You: 'My Query: 2 -1'
- Rotating ring 2 anticlockwise
Me: '12'
- 12 lasers pass through

You: 'My Answer: 3 1 12 11'
- Final positions relative to ring 0
Me: 'Correct'

Remember:
- Each arc is exactly 6 sections long
- Track your rotations carefully
- All positions are mod {total}
- Invalid query/answer = immediate loss

Ready to start? Make your first query!""".format(
        n=n,
        n1=n-1,
        total=n*m,
        total1=n*m-1
    )

def create_file(n, difficulty):
    filename = f"{difficulty}.jsonl"
    used_answers = set()
    m = 6  # 固定m为6
    total_sections = n * m
    
    with open(filename, 'w') as f:
        for i in range(1, 31):
            # 生成不重复的初始位置序列
            while True:
                answer = [0] + [random.randint(0, total_sections-1) for _ in range(n-1)]
                answer_tuple = tuple(answer)
                if answer_tuple not in used_answers:
                    used_answers.add(answer_tuple)
                    break
            
            data = {
                "question_id": i,
                "prompt": create_prompt(n),
                "type": "Dynamic Adaptation",
                "feedback": "Indirect Value Response",
                "scale": n,
                "difficulty": difficulty,
                "title": "RotaryLock",
                "answer": answer,
                "n": n,
                "m": m
            }
            f.write(json.dumps(data) + '\n')

# 创建三个文件
#create_file(3, "easy")    
#create_file(4, "medium")  
create_file(5, "hard")   
