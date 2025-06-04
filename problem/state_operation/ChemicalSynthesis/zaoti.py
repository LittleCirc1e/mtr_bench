import json
import random
from typing import List, Dict, Set, Tuple

def create_prompt(size: int, init_compounds: List[str], target: str) -> str:
    return f"""Let's play Chemical Synthesis! Your task is to create compound {target} through different operations in an unstable environment.

Rules:
1. Basic Setup:
   - Initial compounds: {', '.join(init_compounds)}
   - Goal: Create {target}
   - Four types of operations (1,2,3,4)
   - Element order matters (ABC ≠ CBA)
   - After each operation, resulting compounds and original compounds can be used

2. Operation Types (numbers 1-4 each correspond to one of these):
   SPLIT: 
   - Usually breaks a compound into two parts of its first element and the other elements
   - Sometimes splits at a random position due to instability
   - Example: ABC -> A + BC (normal) or AB + C (unstable)
   - Format: 'My Move: X N' (X is a compound, and N=1/2/3/4)
   
   MERGE:
   - Combines two compounds into one
   - May cause a catalytic reaction that changes element order
   - Result usually keeps elements in order, but might rearrange
   - Example: AB + CD -> ABCD (normal) or ACBD (catalytic)
   - Format: 'My Move: X Y N' (X,Y are two compounds, and N=1/2/3/4)
   
   SWAP:
   - Exchanges elements within a compound
   - High energy might cause multiple swaps
   - Example: ABC -> CBA (normal) or BAC (partial)
   - Format: 'My Move: X N'  (X is a compound, and N=1/2/3/4)
   
   EXTRACT:
   - Takes out one element from a compound
   - Usually the last element, but might extract a random element
   - Example: ABC -> C (normal) or B (unstable)
   - Format: 'My Move: X N' (X is a compound, and N=1/2/3/4)

3. Operation Format and Responses:
   Single Compound Operations (SPLIT, SWAP, EXTRACT):
   - Format: 'My Move: X N'
   Example: 'My Move: BC 1'

   MERGE Operation:
   - Format: 'My Move: X Y N'
   Example: 'My Move: AB CD 2' 

   System Responses:
   - Valid query: "Available: [list of unrepeated available compounds]"
   - Invalid query: "Wrong type"/"Invalid format"/"Invalid compound"
   - Success: "WIN"
   
4. Current State:
Available Compounds: {init_compounds}

Important Notes:
- Element order matters (ABC ≠ CBA)
- Operations are consistent but their numbers (1-4) are unknown
- Chemical instability may cause unexpected results
- Goal compound must match exactly (including element order)
- Can only operate on currently available compounds
- System will return "Wrong type" if:
  * Using single-element compounds for SPLIT/SWAP/EXTRACT
  * Using wrong number of compounds for operation

Example Valid Interactions:
Initial: 'ABC AB D'
You: 'My Move: ABC 1'
Me: 'Available: ABC A BC AB D'      (normal split)
You: 'My Move: AB D 2'
Me: 'Available: ABC A BC AB D DAB'   (unstable merge)

Example Invalid Interactions:
You: 'My Move: A B 1'        (invalid: single element for SPLIT)
Me: 'Wrong type'
You: 'My Move: AB 2'       (invalid: MERGE needs two compounds)
Me: 'Wrong type'

Goal: Create {target} (exact order matters)

Ready to start! Make your move using the correct format!"""

def generate_case(
    size: int, 
    num_elements: int, 
    num_compounds: int, 
    min_steps: int, 
    scale: int
) -> Tuple[List[str], str]:
    """
    生成初始化合物和目标化合物，确保需要至少 min_steps 步进行合成，并且目标化合物不在初始化合物中。
    scale 表示目标化合物的长度（字母数量）。
    """
    elements = [chr(i) for i in range(65, 65 + num_elements)]  # A, B, C, ...

    while True:
        # 生成目标化合物，确保其长度为 scale
        target_elements = random.sample(elements, scale)
        target = ''.join(target_elements)
        target_set = set(target_elements)

        # 生成干扰元素
        non_target_elements = [e for e in elements if e not in target_set]
        num_non_target = max(3, scale // 2)  # 根据 scale 决定添加多少杂质元素
        if len(non_target_elements) < num_non_target:
            extra_elements = non_target_elements.copy()
        else:
            extra_elements = random.sample(non_target_elements, num_non_target)

        # 根据初始化合物数量和难度级别进行元素分配
        init_compounds = []
        remaining_target = target_elements.copy()

        if num_compounds == 2:  # easy - 至少5步
            # 将目标元素分成两部分，并在每个初始化化合物中添加至少一个杂质元素
            mid = max(1, len(remaining_target) // 2)
            compound1 = ''.join(remaining_target[:mid] + [random.choice(extra_elements)])
            compound2 = ''.join(remaining_target[mid:] + [random.choice(extra_elements)])
            init_compounds = [compound1, compound2]

        elif num_compounds == 4:  # medium - 至少8步
            # 将目标元素分散到四个化合物中，每个化合物至少包含一个目标元素或一个杂质元素
            for i in range(num_compounds):
                if remaining_target:
                    elem = remaining_target.pop(0)
                    # 70%的概率添加一个杂质元素
                    if extra_elements and random.random() < 0.7:
                        elem += random.choice(extra_elements)
                else:
                    # 仅添加雑质元素
                    if extra_elements:
                        elem = random.choice(extra_elements)
                    else:
                        continue
                init_compounds.append(elem)
            # 如果需要，添加额外的杂质化合物
            while len(init_compounds) < num_compounds:
                if extra_elements:
                    new_compound = ''.join(random.sample(extra_elements, random.randint(2, 3)))
                    if new_compound not in init_compounds and new_compound != target:
                        init_compounds.append(new_compound)
                else:
                    break

        else:  # hard - 至少10步
            # 高度分散目标元素，混合杂质元素
            for elem in remaining_target[:min(3, len(remaining_target))]:
                if extra_elements and random.random() < 0.5:
                    elem += random.choice(extra_elements)
                init_compounds.append(elem)
            remaining = remaining_target[min(3, len(remaining_target)):]
            while remaining:
                if len(remaining) >= 2:
                    compound = ''.join(remaining[:2])
                    if extra_elements and random.random() < 0.5:
                        compound += random.choice(extra_elements)
                    remaining = remaining[2:]
                else:
                    compound = remaining.pop()
                    if extra_elements and random.random() < 0.5:
                        compound += random.choice(extra_elements)
                init_compounds.append(compound)
            # 添加额外的杂质化合物
            while len(init_compounds) < num_compounds:
                if extra_elements:
                    new_compound = ''.join(random.sample(extra_elements, random.randint(1, 2)))
                    if new_compound not in init_compounds and new_compound != target:
                        init_compounds.append(new_compound)
                else:
                    break

        # 添加剩余的杂质元素到一些化合物中
        for elem in extra_elements:
            if len(init_compounds) >= num_compounds:
                break
            new_compound = ''.join(random.sample(extra_elements, random.randint(1, 2)))
            if new_compound not in init_compounds and new_compound != target:
                init_compounds.append(new_compound)

        # 确保所有目标元素都包含在初始化合物中
        init_elements = set(''.join(init_compounds))
        if not target_set.issubset(init_elements):
            continue  # 如果不包含，重新生成

        # 确保目标化合物不在初始化合物中
        if target in init_compounds:
            continue  # 如果包含，重新生成

        # 进一步检查是否存在直接合成目标化合物的可能性
        # 例如，如果初始化化合物完全包含目标元素的子集，可以通过直接合并实现
        # 为简单起见，此处通过限制每个初始化化合物中目标元素的数量

        direct_merge_possible = False
        for i in range(len(init_compounds)):
            for j in range(i + 1, len(init_compounds)):
                merged = ''.join(sorted(init_compounds[i] + init_compounds[j]))
                if set(merged) == target_set and merged == target:
                    direct_merge_possible = True
                    break
            if direct_merge_possible:
                break

        if direct_merge_possible:
            continue  # 如果存在，可以直接合成目标，重新生成

        # 确保杂质元素存在，增加合成复杂性
        if not extra_elements:
            continue  # 若无杂质元素，重新生成

        return init_compounds, target

def create_test_case(
    question_id: int, 
    size: int, 
    num_elements: int, 
    num_compounds: int, 
    difficulty: str, 
    min_steps: int, 
    scale: int
) -> Dict:
    init_compounds, target = generate_case(size, num_elements, num_compounds, min_steps, scale)
    return {
        "question_id": question_id,
        "prompt": create_prompt(size, init_compounds, target),
        "type": "State Operation",
        "scale": scale,  # scale 现在对应目标化合物的长度
        "difficulty": difficulty,
        "title": "ChemicalSynthesis",
        "initial_compounds": init_compounds,
        "target_compound": target
    }

def generate_file(
    difficulty: str, 
    size: int, 
    num_elements: int, 
    num_compounds: int, 
    min_steps: int, 
    scale: int, 
    filename: str
):
    seen_cases = set()
    max_attempts = 10000  # 防止死循环
    with open(filename, 'w', encoding='utf-8') as f:
        for i in range(1, 31):
            attempts = 0
            while attempts < max_attempts:
                try:
                    test_case = create_test_case(
                        i, size, num_elements, num_compounds, 
                        difficulty, min_steps, scale
                    )
                    case_key = (
                        tuple(sorted(test_case["initial_compounds"])), 
                        test_case["target_compound"]
                    )
                    if case_key not in seen_cases:
                        seen_cases.add(case_key)
                        f.write(json.dumps(test_case, ensure_ascii=False) + '\n')
                        break
                except AssertionError:
                    pass  # 如果初始化合物不包含所有目标元素，重新生成
                attempts += 1
            if attempts == max_attempts:
                print(f"Failed to generate a unique case after {max_attempts} attempts for question {i}")

# 设置随机种子以确保结果可复现
random.seed(42)

# 生成三个难度的文件，确保初始化合物中不包含目标化合物
# 根据难度调整 scale 和 min_steps
# easy: scale=5, min_steps=5
# medium: scale=8, min_steps=8
# hard: scale=10, min_steps=10

# generate_file(
#     difficulty="easy",
#     size=8,
#     num_elements=12,       # 根据需要调整元素数量
#     num_compounds=6,       # 初始化合物数量
#     min_steps=6,           # 至少8步
#     scale=8,               # 目标化合物长度
#     filename="easy.jsonl"
# )

# generate_file(
#     difficulty="medium",
#     size=10,
#     num_elements=15,       # 根据需要调整元素数量
#     num_compounds=7,       # 初始化合物数量
#     min_steps=8,          # 至少10步
#     scale=10,              # 目标化合物长度
#     filename="medium.jsonl"
# )

# generate_file(
#     difficulty="hard",
#     size=15,
#     num_elements=20,       # 根据需要调整元素数量
#     num_compounds=10,       # 初始化合物数量
#     min_steps=8,          # 至少10步
#     scale=15,              # 目标化合物长度
#     filename="hard.jsonl"
# )


generate_file(
    difficulty="easy",
    size=4,
    num_elements=10,       # 根据需要调整元素数量
    num_compounds=4,       # 初始化合物数量
    min_steps=4,           # 至少8步
    scale=4,               # 目标化合物长度
    filename="easy.jsonl"
)


generate_file(
    difficulty="medium",
    size=6,
    num_elements=15,       # 根据需要调整元素数量
    num_compounds=6,       # 初始化合物数量
    min_steps=6,          # 至少10步
    scale=6,              # 目标化合物长度
    filename="medium.jsonl"
)

generate_file(
    difficulty="hard",
    size=7,
    num_elements=20,       # 根据需要调整元素数量
    num_compounds=7,       # 初始化合物数量
    min_steps=8,          # 至少10步
    scale=7,              # 目标化合物长度
    filename="hard.jsonl"
)
