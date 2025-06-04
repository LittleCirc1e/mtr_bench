import json


# 基础prompt模板，使用{k}和{min_value}、{max_value}作为占位符
base_prompt_template="""Let's play Password Breaker! Your task is to hack into the RPD database by guessing the correct password.

Rules:
1. The password is always between MIN_VALUE = {min_value} and MAX_VALUE = {max_value} (inclusive)
2. After each guess, you'll receive one of these responses:
 - Correct: Correct password, you've successfully broken in!
 - Incorrect: Wrong password, and the system has changed the password
 - Invalid: Invalid guess

Important Mechanics:
- The system uses base-{k} operations (k={k})
- When you guess wrong (y), if the current password was x:
  * First convert both x and y to base-{k} numbers
  * Perform digit-by-digit base-{k} XOR:
    For each digit position i: result[i] = (x[i] + y[i]) mod {k}
  * Convert result back to decimal to get z
  * Map z to range [0,{max_value}-{min_value}] by taking mod ({max_value}-{min_value}+1)
  * Add {min_value} to get the new password between [{min_value},{max_value}]

Example:
With k=2, if x=6 (base-2: [1,1,0]) and y=5 (base-2: [1,0,1]):
1. XOR digits: [1,1,0] XOR [1,0,1] = [(1+1)mod2, (1+0)mod2, (0+1)mod2] = [0,1,1]
2. Convert [0,1,1] to decimal: z = 3
3. Map to range: z = (3 mod ({max_value}-{min_value}+1)) + {min_value}

Example Interaction:
- Original password = 5
- You: \"My Guess: 3\"
- Me: \"Incorrect\" (wrong, password changes by XOR mechanism)
- You: \"My Guess: 5\"
- Me: \"Incorrect\" (wrong, password changes by XOR mechanism)
- You: \"My Guess: 8\"
- Me: \"Correct\" (correct!)

Instructions:
1. Make your guess based on previous responses
2. Format your response as 'My guess: X', and X is a number between {min_value} and {max_value}
3. Give your reasoning before making each guess

Remember:
- Always end your response with "My guess: X', and X is a number between {min_value} and {max_value}
- Any deviation from this format will result in an invalid guess

Ready to start? Make your first query!"""

with open('easy.jsonl', 'w') as f:
    count = 0
    k = 2
    
    # 计算需要多少组区间来生成50条数据
    # 每个区间5个数，所以需要10组区间
    for group in range(10):  # 0-9共10组
        # 计算当前组的min_value和max_value
        min_value = group * 10 + 1  # 1, 6, 11, 16, ...
        max_value = min_value + 9  # 5, 10, 15, 20, ...
        
        # 在当前区间内生成数据
        for answer in range(min_value, max_value + 1):
            if count >= 50:  # 确保只生成50条数据
                break
                        
            # 使用当前值格式化prompt
            current_prompt = base_prompt_template.format(
                k=k,
                min_value=min_value,
                max_value=max_value
            )
            
            data = {
                "question_id": str(count + 1),
                "prompt": current_prompt,
                "type": "Dynamic Adaptation",
                "feedback": "Direct Value Response",
                "k": k,
                "min_value": min_value,
                "max_value": max_value,
                "difficulty": "easy",
                "title": "RPD",
                "answer": answer
            }
            f.write(json.dumps(data) + '\n')
            count += 1
        
        if count >= 50:
            break

print("File created successfully!")
print(f"Generated {count} problems")
