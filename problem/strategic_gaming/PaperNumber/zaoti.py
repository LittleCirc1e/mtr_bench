import json

difficulties = [
    {"file": "easy.jsonl", "scale": 5, "turns": 10},
    {"file": "medium.jsonl", "scale": 10, "turns": 20}, 
    {"file": "hard.jsonl", "scale": 15, "turns": 30}
]

base_prompt = """Let's play the Paper Number Game!

Rules:
1. Game Setup:
   - {scale} blank papers in a line, numbered 1 to {scale} from left to right
   - Game lasts {turns} rounds
   - Numbers range from 1 to {max_number}

2. Game Mechanics:
   - System provides one number (1 to {max_number}) each round
   - You must choose which paper to write the number on
   - You can overwrite existing numbers on papers
   - Game ends after {turns} rounds or when winning condition is met

3. Winning Condition:
   - All papers must have numbers written
   - Numbers must be in non-decreasing order from left to right
   - Win immediately when condition is met
   - Lose if not achieved after {turns} rounds

Your Task:
- Each round, you will receive a number
- You must decide which paper to write it on
- Format your response as: 'My Choice: X', where X is paper position (1 to {scale})
- Explain your reasoning before each choice

Example Round:
Given:
Me: '2'
You: "I'll place 2 on first paper to leave room for larger numbers"
'My Choice: 1'
- Paper state: [2,_,_...]

Me: '1'
You: "I'll place 1 on second paper temporarily"
'My Choice: 2'
- Paper state: [2,1,_...]

Me: '3'
You: "I'll replace 1 with 3 to achieve non-decreasing order"
'My Choice: 2'
- Paper state: [2,3,_...]

Remember:
- Use exact format: 'My Choice: X'
- Choose valid paper positions (1 to {scale})
- Aim for non-decreasing sequence
- Invalid move = automatic loss

Ready to start? Make your first query!
The first number I give you is: {initial_value}"""

for diff in difficulties:
    with open(diff["file"], "w") as f:
        # 对每个max_number (5-9)
        question_id = 1
        for max_number in range(5, 10):
            # 对每个initial_value (1到max_number)
            for initial_value in range(1, max_number + 1):
                data = {
                    "question_id": question_id,
                    "prompt": base_prompt.format(
                        scale=diff["scale"],
                        turns=diff["turns"],
                        max_number=max_number,
                        initial_value=initial_value
                    ),
                    "type": "Strategic Gaming", 
                    "scale": diff["scale"],
                    "difficulty": diff["file"].split(".")[0],
                    "title": "PaperNumber",
                    "turns": diff["turns"],
                    "initial_value": initial_value,
                    "max_number": max_number
                }
                f.write(json.dumps(data) + "\n")
                question_id += 1

print("Generated jsonl files successfully!")
