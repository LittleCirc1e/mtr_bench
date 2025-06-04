import random
import json

def generate_game_prompt(n, initial_list, first_choice):
    prompt = f"""Let's play the Decreasing Game! Your goal is to strategically decrease array values and force your opponent into a position where they can't make a valid move.

Rules:
1. Game Setup:
   - You're given an array of positive integers
   - Players take turns selecting array elements
   - Initial array state: {initial_list}

2. Game Mechanics:
   - On each turn:
     * One player selects index i where a[i] > 0
     * Other player selects different index j where a[j] > 0
     * Both a[i] and a[j] decrease by min(a[i], a[j])
   - If a player cannot select a positive number, he loses
   - Game continues until someone wins

3. Turn Format:
   - I'll provide my index choice as: "My Choice: X"
   - You respond with your index choice as: "My Choice: Y"
   - After each round, both X and Y decrease by min(X, Y) 

Example Round:
Initial array: [4, 3, 2]
Me: "My Choice: 1" (selecting a[1] = 4)
You: "My Choice: 2" (selecting a[2] = 3)
- min(4,3) = 3 is subtracted
- New array: [1, 0, 2]

Instructions:
- Choose only indices with positive values
- Format your choice exactly as: "My Choice: X"
- Invalid moves result in immediate loss
- Think ahead about how your choice affects future moves

My first choice: "My Choice: {first_choice}"

Ready for your move!"""
    return prompt

def generate_jsonl(n, num_examples, difficulty):
    filename = f"{difficulty}.jsonl"
    
    with open(filename, 'w') as f:
        for i in range(num_examples):
            initial_list = [random.randint(1, 20) for _ in range(n)]
            first_choice = random.randint(1, n)
            
            data = {
                "question_id": i + 1,
                "prompt": generate_game_prompt(n, initial_list, first_choice),
                "type": "Strategic Gaming",
                "scale": n,
                "difficulty": difficulty,
                "title": "Decreasing Game",
                "initial_list":initial_list,
                "first_choice":first_choice,
                "turns": 2*n
            }
            
            f.write(json.dumps(data) + '\n')

# Generate files for different difficulties
difficulties = {
    "easy": 3,
    "medium": 5, 
    "hard": 7
}

for diff, n in difficulties.items():
    generate_jsonl(n, 30, diff)
