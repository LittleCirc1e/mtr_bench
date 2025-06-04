import json
import random

def generate_array(k):
    """生成一个长度为50的数组，只有一个最大值"""
    # 生成一个最大值(41-50)
    max_value = random.randint(41, 50)
    
    # 生成其余的值(1-40)，确保都小于max_value
    other_values = random.choices(range(1, 40), k=49)  # 重复使用这些小值填充
    
    # 组合并打乱
    array = [max_value] + other_values
    random.shuffle(array)
    return array, [max_value]  # 返回数组和最大值列表

def generate_subsets(k, n=50, array=None, max_values=None):
    """为每个密码位生成k个不相交的子集"""
    all_positions = set(range(1, n+1))
    subsets = {}
    remaining = list(all_positions)
    
    # 找出最大值的位置
    max_pos = array.index(max_values[0]) + 1  # 转换为1-based索引
    
    # 随机决定哪个子集包含最大值位置
    max_value_subset = random.randint(1, k)
    
    # 生成k个子集
    for i in range(k):
        subset_index = i + 1
        
        if subset_index == max_value_subset:
            # 这个子集需要包含最大值位置
            other_positions = [pos for pos in remaining if pos != max_pos]
            if len(other_positions) > 0:
                # 随机选择1或2个其他位置
                size = min(2, len(other_positions))
                if size > 0:
                    extra = random.sample(other_positions, size)
                    subset = sorted([max_pos] + extra)
                else:
                    subset = [max_pos]
            else:
                subset = [max_pos]
        else:
            # 其他子集随机生成
            if len(remaining) < 2:  # 确保有足够的位置
                raise ValueError("Not enough remaining positions")
                
            size = min(3, len(remaining))  # 取最小值避免范围错误
            if size < 2:  # 如果剩余位置不足2个
                raise ValueError("Not enough remaining positions")
                
            subset = sorted(random.sample(remaining, 2))  # 固定取2个位置
        
        subsets[f"S{subset_index}"] = subset
        # 更新剩余位置
        remaining = [x for x in remaining if x not in subset]
    
    return subsets


def calculate_password(array, subsets, k, max_values):
    """根据数组和子集计算密码"""
    password = []
    max_value = max_values[0]
    
    for i in range(k):
        excluded = set(subsets[f"S{i+1}"])
        included = [array[j-1] for j in range(1, 51) if j not in excluded]
        current_max = max(included)
        password.append(current_max)
    
    return password


def create_prompt(k, subsets):
    subset_desc = ", ".join([f"S{i+1}={subsets[f'S{i+1}']}" for i in range(k)])
    return f"""Let's play Guess The Maximums!

Rules:
1. Hidden array A[1...50] contains numbers from 1 to 50
2. You need to guess {k} numbers forming the password
3. For password position i, you are given Si = subset of positions to exclude
4. Password[i] = max value among all positions EXCEPT those in Si

Your subsets are:
{subset_desc}

Password Example:
For n=4, k=2, if:
S1 = {{1,3}}, S2 = {{2,4}}
And hidden array A = [3,1,2,4]
Then:
- Password[1] ignores positions 1,3 (S1)
  So looks at A[2]=1, A[4]=4
  Password[1] = 4
- Password[2] ignores positions 2,4 (S2)
  So looks at A[1]=3, A[3]=2
  Password[2] = 3
Therefore, the answer is "4 3".

Interaction format:
1. Your Query: 
- Format: \"My Query: x1 x2 ... xm\"
- xi = positions you want to query (1=<m<50) 
- You'll receive the maximum value at these positions

2. Your Answer:
- Format: \"My Answer: p1 p2 ... p{k}\"
- pi = your guess for each password slot
- You'll receive \"Correct\" or \"Incorrect\"

Simple Example Interaction:
Given: n=4, k=2, S1 = {{1,3}}, S2 = {{2,4}}, A = [3,1,2,4](hidden), Answer = [4,3](hidden)
You: \"My Query: 2 4\"
Me: \"4\"
You: \"My Query: 1 3\"
Me: \"3\"
You: \"My Answer: 4 3\"
Me: \"Correct\"

Remember:
- Explain your reasoning before each query/answer
- Use exactly the formats shown above

Ready to start? Make your first query!"""

def create_jsonl_file(filename, k, difficulty):
    with open(filename, 'w') as f:
        for i in range(50):
            while True:
                try:
                    array, max_values = generate_array(k)
                    subsets = generate_subsets(k, array=array, max_values=max_values)
                    password = calculate_password(array, subsets, k, max_values)
                    break
                except ValueError:
                    continue
            
            data = {
                "prompt": create_prompt(k, subsets),
                "type": "Information Query",
                "feedback": "Indirect Value Response",
                "scale": k,
                "difficulty": difficulty,
                "title": "GuessMax",
                "question_id": i + 1,
                "array": array,
                "subsets": subsets,
                "answer": password
            }
            f.write(json.dumps(data) + '\n')

def main():
    create_jsonl_file('easy.jsonl', k=7, difficulty='easy')
    create_jsonl_file('medium.jsonl', k=10, difficulty='medium')
    create_jsonl_file('hard.jsonl', k=16, difficulty='hard')
    print("Files generated successfully!")

if __name__ == "__main__":
    main()
