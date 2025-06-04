import random
import json
from typing import List, Tuple

def find_valid_xor_pairs(n: int) -> List[Tuple[int, int]]:
    """找到所有满足条件的XOR对"""
    pairs = []
    # 寻找所有可能的p1
    for p1 in range(1, n):
        # 通过XOR计算对应的p2
        p2 = p1 ^ n
        # 检查p2是否满足条件
        if 0 < p2 < n:
            pairs.append((p1, p2))
    return pairs

def generate_game_prompt(n: int, example_pair: Tuple[int, int]) -> str:
    prompt = f"""Let's play the XOR Break Game! Your task is to win this game by strategically breaking numbers and forcing your opponent into a position where they can't make a valid move.

Rules:
1. Game Setup:
   - Initial number: {n}
   - You play first
   - I play second
   - Maximum 20 moves allowed

2. Game Mechanics:
   First Turn:
   - You break initial number p into two numbers p1 and p2
   - Must satisfy: 0 < p1,p2 < p and p1⊕p2 = p

   Subsequent Turns:
   - Active player does two actions:
     1. Choose one number (p1 or p2) from opponent's break
     2. Try to break chosen number into two new numbers
   - If player cannot break their chosen number, they lose
   - Game continues until someone can't break their number

3. XOR Calculation Example:
   Breaking 13:
   - Can choose 10 and 7 because:
     * 10 = 1010 in binary
     * 7 = 0111 in binary
     * 10⊕7 = 1101 = 13
   - Both numbers are less than 13
   - Both numbers are positive

Instructions:
First Turn Format:
- Your move: 'Breaking into: p1 p2'
- Example: 'Breaking into: 10 7'

Other Turns Format:
- Your move: 'Choosing: p Breaking into: p1 p2'
- My response: Either
  * 'Choosing: x Breaking into: y z'
  or
  * 'Choosing: x Cannot break further'

Example Round:
Initial number: 13

You: 'Breaking into: 10 7'
- Breaking 13 into 10⊕7
- Both numbers less than 13

Me: 'Choosing: 7 Breaking into: 3 4'
- Selected 7 and broke it into 3⊕4

You: 'Choosing: 3 Breaking into: 2 1'
- Selected 3 and broke it into 2⊕1

Me: 'Choosing: 1 Cannot break further'
- You win! 1 cannot be broken

Remember:
- Use exact format for moves
- Numbers must satisfy:
  * Less than current number
  * Greater than 0
  * XOR to current number
- Invalid break = automatic loss
- More than 20 moves = loss

Ready to start? Make your first query!"""
    return prompt

def generate_jsonl(max_n: int, num_examples: int, difficulty: str):
    filename = f"{difficulty}.jsonl"
    
    with open(filename, 'w') as f:
        for i in range(num_examples):
            # 生成一个随机数
            n = random.randint(2, max_n)  # 从2开始确保可以分解
            
            # 找到所有可能的XOR对
            pairs = find_valid_xor_pairs(n)
            if not pairs:  # 如果找不到有效对，重新生成数字
                continue
                
            # 随机选择一个示例对
            example_pair = random.choice(pairs)
            
            data = {
                "prompt": generate_game_prompt(n, example_pair),
                "type": "Strategic Gaming",
                "scale": n,
                "difficulty": difficulty,
                "title": "XORBreaking",
                "question_id": i + 1,
                "initial_number": n,
                "example_pair": list(example_pair),
                "turns": 20
            }
            
            f.write(json.dumps(data) + '\n')

# Generate files for different difficulties
difficulties = {
    #"easy": 100000,
    #"medium": 10000000,
    "hard": 100000000
}

if __name__ == "__main__":
    # Set random seed for reproducibility
    random.seed(42)
    
    # Generate files for each difficulty
    for diff, max_n in difficulties.items():
        generate_jsonl(max_n, 30, diff)
