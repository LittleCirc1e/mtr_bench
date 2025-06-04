import random
import json

def generate_string(length: int) -> str:
    """生成随机ab字符串"""
    return ''.join(random.choice(['a', 'b']) for _ in range(length))

def create_example_game(num_chars_per_turn: int) -> str:
    if num_chars_per_turn == 1:
        # Easy难度示例 (1字符/轮前4轮，第5轮1字符，最终5字符)
        return """Starting: t is empty

Turn 1: (One character revealed)
Me: 'a'
Current t: "a"
You: 'My Choice: 0 0'
(no swap needed)

Turn 2: (One character revealed)
Me: 'b'
Current t: "ab"
You: 'My Choice: 1 2'
(swap to make "ba")

Turn 3: (One character revealed)
Me: 'b'
Current t: "bab"
You: 'My Choice: 0 0'
(already good pattern)

Turn 4: (One character revealed)
Me: 'a'
Current t: "baba"
You: 'My Choice: 0 0'
(keeping pattern)

Turn 5: (One character revealed)
Me: 'b'
Current t: "babab"
You: 'My Choice: 0 0'
(perfect palindrome achieved)"""

    elif num_chars_per_turn == 2:
        # Medium难度示例 (2字符/轮前4轮，第5轮1字符，最终9字符)
        return """Starting: t is empty

Turn 1: (Two characters revealed)
Me: 'ab'
Current t: "ab"
You: 'My Choice: 0 0'
(keep for now)

Turn 2: (Two characters revealed)
Me: 'ba'
Current t: "abba"
You: 'My Choice: 0 0'
(already a palindrome)

Turn 3: (Two characters revealed)
Me: 'ab'
Current t: "abbaab"
You: 'My Choice: 5 6'
(adjust end part)

Turn 4: (Two characters revealed)
Me: 'ba'
Current t: "abbaabba"
You: 'My Choice: 0 0'
(maintaining pattern)

Turn 5: (One character revealed)
Me: 'a'
Current t: "abbaabbaa"
You: 'My Choice: 0 1'
(adjust for pattern)"""

    else:  # num_chars_per_turn == 3
        # Hard难度示例 (3字符/轮前4轮，第5轮1字符，最终13字符)
        return """Starting: t is empty

Turn 1: (Three characters revealed)
Me: 'aba'
Current t: "aba"
You: 'My Choice: 0 0'
(already good pattern)

Turn 2: (Three characters revealed)
Me: 'bab'
Current t: "ababab"
You: 'My Choice: 4 6'
(adjust for pattern)

Turn 3: (Three characters revealed)
Me: 'aba'
Current t: "ababababa"
You: 'My Choice: 0 0'
(maintaining pattern)

Turn 4: (Three characters revealed)
Me: 'bab'
Current t: "ababababab"
You: 'My Choice: 8 10'
(adjusting for palindrome)

Turn 5: (One character revealed)
Me: 'a'
Current t: "ababababababa"
You: 'My Choice: 0 0'
(perfect palindrome achieved)"""

def create_prompt(difficulty: str, num_chars_per_turn: int, total_chars: int, initial_chars: str) -> str:
    example_game = create_example_game(num_chars_per_turn)
    
    # 显示前scale个字符
    preview = initial_chars[:num_chars_per_turn]
    
    return f"""Let's play the Palindrome Construction Game! Your task is to create a palindrome by strategically swapping characters as they are revealed.

Rules:
1. Game Setup:
   - First 4 turns: I reveal {num_chars_per_turn} character(s) each turn
   - Later Turns: I reveal 1 character
   - Only characters 'a' and 'b' are used
   - Your string t starts with: '{preview}'

2. Game Mechanics:
   Each Turn Flow:
   1. I reveal new character(s):
      - Turns 1-4: {num_chars_per_turn} character(s) per turn
      - Later Turns: 1 character
   2. All new characters are added to the end of t
   3. You can either:
      - Swap any two positions in current t
      - Or do nothing (keep t as is)

   Final Goal:
   - Make t a palindrome when game ends
   - A palindrome reads the same forwards and backwards
   - Examples: "aba", "ababa", "ababababa"

3. Move Format:
   After I reveal character(s):
   - To swap: 'My Choice: l r'
     where l,r are positions in t (1-based)
   - To keep as is: 'My Choice: 0 0'

Example Game:
{example_game}

Remember:
- First 4 turns: {num_chars_per_turn} character(s) per turn
- Later Turns: 1 character
- Use exact format 'My Choice: X Y'
- Valid positions are 1 to current length
- Wait for my reveal before moving
- Final string must be palindrome

Ready to start? Make your first query!
First {num_chars_per_turn} characters: '{preview}'"""

def generate_jsonl(difficulty: str, num_chars_per_turn: int, total_chars: int, num_examples: int):
    filename = f"{difficulty}.jsonl"
    
    with open(filename, 'w') as f:
        for i in range(num_examples):
            initial_data = generate_string(total_chars)
            
            data = {
                "question_id": i + 1,
                "prompt": create_prompt(difficulty, num_chars_per_turn, total_chars, initial_data),
                "type": "State Operation",
                "scale": num_chars_per_turn,
                "difficulty": difficulty,
                "title": "PalindromeConstruction5",
                "initial_data": initial_data,
                "turns": 5
            }
            
            f.write(json.dumps(data) + '\n')
# 修改settings中的total_chars计算
settings = {
    "easy": (1, 4),    # 每轮1字符前4轮+1字符=5
    "medium": (2, 8),  # 每轮2字符前4轮+1字符=9
    "hard": (3, 12)    # 每轮3字符前4轮+1字符=13
}
if __name__ == "__main__":
    # 设置随机种子以保证可重现性
    random.seed(42)
    
    # 生成三个难度的文件
    for diff, (chars_per_turn, total_chars) in settings.items():
        generate_jsonl(diff, chars_per_turn, total_chars, 30)
