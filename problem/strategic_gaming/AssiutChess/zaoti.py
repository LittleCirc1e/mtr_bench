import random
import json

def generate_game_prompt(n, initial_position):
    prompt = f"""Let's play Assiut Chess! Your task is to win this game by controlling a queen to trap the hidden king.

Rules:
1. Game Setup:
   - {n}*{n} chessboard (rows and columns from 1 to {n})
   - You control the queen, I control the hidden king
   - First, you place the queen anywhere on the board

2. Game Mechanics:
   - On each turn:
     * I move the king first (in one of 8 directions) 
     * I tell you which direction the king moved
     * You move the queen to any cell in straight or diagonal line
   - King's possible moves:
     * 'Right', 'Left', 'Up', 'Down'
     * 'Down-Right', 'Down-Left', 'Up-Left', 'Up-Right'
   - King's restrictions:
     * Cannot move out of the board
     * Cannot move to cells attacked by queen (same row, column, or diagonal)
   - Queen's restrictions:
     * Must move to a different cell each turn
     * Must move in straight or diagonal lines

3. Victory Conditions:
   - You win if the king has no valid moves
   - Game ends when 'Done' is received

Instructions:
- Format your moves as: 'My Choice: x y' (where 1=<x,y=<{n})
- Wait for king's movement direction before your next move
- Invalid move = automatic loss

Example Round:
Initial queen placement:
You: 'My Choice: 3 2'

I: 'Left'
You: 'My Choice: 3 3'

I: 'Right'
You: 'My Choice: 3 4'

I: 'Done'
Result: You win! King is trapped!

Remember:
- Use exact format: 'My Choice: x y'
- Choose valid queen moves only
- Plan moves to trap the king
- Invalid move = immediate loss
- You have maximun 20 moves

Ready to start? Make your first query!"""
    return prompt

def generate_jsonl(n, num_examples, difficulty):
    filename = f"{difficulty}.jsonl"
    
    with open(filename, 'w') as f:
        for i in range(num_examples):
            # Generate random initial king position
            king_x = random.randint(1, n)
            king_y = random.randint(1, n)
            initial_position = f"({king_x}, {king_y})"
            
            data = {
                "question_id": i + 1,
                "prompt": generate_game_prompt(n, initial_position),
                "type": "Strategic Gaming",
                "scale": n,
                "difficulty": difficulty,
                "title": "AssiutGuess",
                "initial_position": initial_position,
                "turns":20
            }
            
            f.write(json.dumps(data) + '\n')

# Generate files for different difficulties
difficulties = {
    "easy": 4,
    "medium": 6,
    "hard": 7
}

for diff, n in difficulties.items():
    generate_jsonl(n, 30, diff)
