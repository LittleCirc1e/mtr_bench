import json

def add_question_id(input_file, output_file=None):
    """
    给JSONL文件每行添加自增的question_id
    :param input_file: 输入文件名
    :param output_file: 输出文件名（None则覆盖原文件）
    """
    if output_file is None:
        output_file = input_file
    
    with open(input_file, 'r') as f_in, open(output_file + '.tmp', 'w') as f_out:
        for idx, line in enumerate(f_in, start=1):
            if line.strip():  # 跳过空行
                data = json.loads(line)
                data['question_id'] = idx
                f_out.write(json.dumps(data) + '\n')
    
    # 替换原文件
    import os
    os.replace(output_file + '.tmp', output_file)

# 使用示例
add_question_id('hard.jsonl')