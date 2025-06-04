import json
import random

def create_prompt(n, m, x1, y1, x2, y2):
    target_white_x, target_white_y = n//2, m//2
    target_black_x, target_black_y = n//2 + 1, m//2
    
    return """Let's play the Knight Battle Game! You are the White Knight and will move first. Your task is to win by either capturing the Black Knight or reaching your target position safely.

Rules:
1. Game Setup:
   - Chessboard size: {n}*{m}
   - You (White Knight) start at: ({x1},{y1})
   - Opponent (Black Knight) starts at: ({x2},{y2})
   - Your target: ({tw_x},{tw_y})
   - Opponent's target: ({tb_x},{tb_y})

2. Knight's Movement Rules:
   From your current position (x,y), you can move to:
   1. Up 2, Right 1:    (x+1, y+2)
   2. Up 2, Left 1:     (x-1, y+2)
   3. Down 2, Right 1:  (x+1, y-2)
   4. Down 2, Left 1:   (x-1, y-2)
   5. Right 2, Up 1:    (x+2, y+1)
   6. Right 2, Down 1:  (x+2, y-1)
   7. Left 2, Up 1:     (x-2, y+1)
   8. Left 2, Down 1:   (x-2, y-1)
   * All moves must stay within board boundaries (1 to {n}, 1 to {m})

3. Victory Conditions:
   You win if either:
   - You move to Black Knight's position (capture)
   - You reach ({tw_x},{tw_y}) and Black Knight cannot attack this position
   * A position is under attack if opponent's knight can move there next turn

Game Format:
Format for each move: 'My Move: x y'
where x,y are your new coordinates
Example: 'My Move: 4 4'

Example Interaction:
You (at {x1},{y1}): 'My Move: 4 4'
- Moving to position (4,4)

Me: '6 3'
- Black Knight moves to (6,3)

You: 'My Move: 5 6'
- Moving to position (5,6)

Me: '5 1'
- Black Knight moves to (5,1)

Remember:
- You are White Knight and move first
- Use L-shaped movements only
- Use exact format: 'My Move: X Y'
- Stay within board boundaries
- Plan moves to either:
  * Capture Black Knight
  * Reach ({tw_x},{tw_y}) safely
- Invalid move = immediate loss
- You have at most 15 rounds to defeat the Black Knight

Ready to start? Make your first move!""".format(
        n=n, m=m, 
        x1=x1, y1=y1, 
        x2=x2, y2=y2,
        tw_x=target_white_x, tw_y=target_white_y,
        tb_x=target_black_x, tb_y=target_black_y
    )

def is_valid_position(x, y, n, m):
    return 1 <= x <= n and 1 <= y <= m

def generate_valid_positions(n, m):
    # 生成不同的起始位置
    while True:
        x1 = random.randint(1, n)
        y1 = random.randint(1, m)
        x2 = random.randint(1, n)
        y2 = random.randint(1, m)
        
        # 确保两个骑士不在同一位置，且不在目标位置
        if (x1,y1) != (x2,y2) and \
           (x1,y1) != (n//2,m//2) and \
           (x2,y2) != (n//2+1,m//2):
            return x1, y1, x2, y2

def create_file(n, difficulty):
    filename = f"{difficulty}.jsonl"
    used_configs = set()
    
    with open(filename, 'w') as f:
        for i in range(1, 31):
            # 生成不重复的配置
            while True:
                x1, y1, x2, y2 = generate_valid_positions(n, n)  # 使用正方形棋盘
                config = (x1, y1, x2, y2)
                if config not in used_configs:
                    used_configs.add(config)
                    break
            
            data = {
                "question_id": i,
                "prompt": create_prompt(n, n, x1, y1, x2, y2),
                "type": "Strategic Gaming",
                "scale": n,
                "difficulty": difficulty,
                "title": "KnightBattle",
                "answer": {
                    "white_start": [x1, y1],
                    "black_start": [x2, y2],
                    "white_target": [n//2, n//2],
                    "black_target": [n//2+1, n//2]
                },
                "turns":15
            }
            f.write(json.dumps(data) + '\n')

# 创建三个文件
create_file(6, "easy")     # 6x6棋盘
create_file(8, "medium")   # 8x8棋盘
create_file(15, "hard")    # 10x10棋盘
