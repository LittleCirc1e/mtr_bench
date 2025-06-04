import json
import random

def get_base_prompt(n):
    return f"""Let's play Mahjong Detective Game! Your task is to discover Yui's mysterious tile set through careful queries.

Rules:
1. There is a hidden set of Mahjong tiles
2. Each tile has a value from 1 to {n}
3. Each value appears at most {n} times
4. You need to find how many tiles of each value exist
5. You can add tiles to help your investigation

Special Combinations:
- Triplet: Three tiles with same value (e.g., {{2,2,2}})
- Straight: Three consecutive values (e.g., {{2,3,4}})
Note: Same-value tiles are treated as different pieces!

Query Types:
1. To add a tile:
   Format: 'My Query: + x'
   where:
   - x is the value of tile to add (1 to {n})
   Example: 'My Query: + 3'
   Response will be:
   - Number of triplets in new set
   - Number of straights in new set

2. To submit final answer:
   Format: 'My Answer: a1 a2 ... a{n}'
   where ai is number of tiles with value i AFTER ALL YOUR ADDITIONS
   Example: 'My Answer: 2 1 3 0 2 ...'

Example Interaction:
Initial set has:
- 1 triplet
- 6 straights

You: 'My Query: + 1'
Me: '2 9' (new set has 2 triplets, 9 straights)

You: 'My Query: + 1'
Me: '5 12' (new set has 5 triplets, 12 straights)

You: 'My Query: + 2'
Me: '5 24' (new set has 5 triplets, 24 straights)

You: 'My Query: + 5'
Me: '6 24' (new set has 6 triplets, 24 straights)

You: 'My Answer: 2 1 3 0 2 ...'
(This answer includes ALL tiles, including the ones you added!)

Instructions:
1. Make queries to add tiles strategically
2. Use exactly the formats shown above
3. Explain your reasoning before each addition
4. Watch how combinations change

Remember:
- Each value appears 0 to {n} times
- Same-value tiles count as different pieces
- Watch how triplets and straights change
- Your final answer must include your added tiles

Ready to start? Make your first query!"""

def generate_valid_answer(n):
    """生成有效的答案数组"""
    answer = []
    for _ in range(n):
        # 每个位置的数字在0到n之间
        value = random.randint(0, n)
        answer.append(value)
    return answer

def create_jsonl(filename, n, difficulty):
    used_answers = set()
    
    with open(filename, 'w') as f:
        for i in range(1, 31):
            # 生成不重复的答案
            while True:
                answer = generate_valid_answer(n)
                answer_tuple = tuple(answer)
                if answer_tuple not in used_answers:
                    used_answers.add(answer_tuple)
                    break
            
            data = {
                "question_id": i,
                "prompt": get_base_prompt(n),
                "type": "Dynamic Adaptation",
                "feedback": "Indirect Value Response",
                "scale": n,
                "difficulty": difficulty,
                "title": "MahjongDetective",
                "answer": answer
                }
            
            f.write(json.dumps(data) + '\n')

def main():
    # 创建三个不同难度的文件
    create_jsonl('easy.jsonl', 3, 'easy')
    create_jsonl('medium.jsonl', 6, 'medium')
    create_jsonl('hard.jsonl', 9, 'hard')

if __name__ == "__main__":
    main()
