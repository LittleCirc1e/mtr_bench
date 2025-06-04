import json
import random
import string

def generate_random_words(n=50, length=12):
    """生成n个不重复的length长度的大写字母字符串"""
    # 生成所有可能的大写字母组合
    all_words = set()
    while len(all_words) < n:
        word = ''.join(random.choices(string.ascii_uppercase, k=length))
        all_words.add(word)
    return list(all_words)

def update_file(input_file, output_file):
    # 生成50个随机词
    random_words = generate_random_words()
    
    # 读取并更新文件
    updated_lines = []
    with open(input_file, 'r') as f:
        for i, line in enumerate(f):
            data = json.loads(line)
            data['answer'] = random_words[i]
            data['difficulty'] = 'hard'
            data['scale'] = 12 # 更新answer
            data['prompt'] = "Let's play Letters Finding! Your task is to guess a 12-letter English word.\n\nRules:\n1. You must provide exactly ONE 12-letter English word as your guess\n2. After each guess, you'll receive feedback using these symbols:\n - R: Correct letter in the correct position\n - G: Correct letter but in the wrong position\n - W: Wrong letter, not in the word\n\nExample:\nIf the target word is ABCDUVWZGHIJ\n- Guess ACEFOPQMKLLM would get: RGWWWWWWWWWW\n (A is correct position, C is correct but wrong position, rest are wrong)\n\nInstructions:\n1. Make your guess based on previous feedback (if any)\n2. Guess only one word at a time and your response must end with 'My Guess: [YOUR 12-LETTER WORD]'\n3. Give your reasoning process before giving your guess\n\nRemember: \n- Each guess does not need to be a real English word, as long as it consists of exactly 12 letters.\n- The same letter can appear multiple times.\n\nReady to start? Make your first query!"
            updated_lines.append(json.dumps(data, ensure_ascii=False))
    
    # 写入新文件
    with open(output_file, 'w') as f:
        for line in updated_lines:
            f.write(line + '\n')

# 使用示例
input_file = "/cpfs01/user/lanlin.lxy/cf_trans/problem/information_query/Wordle/easy_old.jsonl"  # 原始文件路径
output_file = "/cpfs01/user/lanlin.lxy/cf_trans/problem/information_query/Wordle/hard.jsonl"  # 新文件路径
update_file(input_file, output_file)
