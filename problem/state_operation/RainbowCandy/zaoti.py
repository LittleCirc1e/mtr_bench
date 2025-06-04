import json
import random
from collections import deque

def get_new_color(current_color, device):
    if device == "W":
        return "W"
    elif device in ["R", "G", "B"]:
        if current_color == "W":
            return device
        color_mix = {
            ("R", "G"): "Y",
            ("G", "B"): "C", 
            ("R", "B"): "P"
        }
        colors = tuple(sorted([current_color, device]))
        return color_mix.get(colors, current_color)
    return current_color

def generate_path(size, target_color):
    """先生成一条从起点到终点的可行路径，并确定必要的染色机器和至少一个漂白机"""
    path = []
    devices = {f"{i},{j}": "-" for i in range(1,size+1) for j in range(1,size+1)}
    devices["1,1"] = "-"  # 起点是漂白机

    # 随机生成一条从(1,1)到(size,size)的路径
    current = [1, 1]
    while current != [size, size]:
        directions = []
        if current[0] < size:
            directions.append([1, 0])
        if current[1] < size:
            directions.append([0, 1])
        dx, dy = random.choice(directions)
        current[0] += dx
        current[1] += dy
        path.append(tuple(current))

    # 确保路径中有足够的空位放置必要设备
    path_positions = path[:-1]  # 除去终点的路径位置

    # 放置必要的染色机器
    if target_color in ["R", "G", "B"]:
        # 基础颜色只需要一个染色机器
        place_pos = random.choice(path_positions)
        devices[f"{place_pos[0]},{place_pos[1]}"] = target_color
        path_positions.remove(place_pos)
    else:
        # 混合颜色需要两个染色机器
        color_pairs = {
            "Y": ["R", "G"],
            "C": ["G", "B"],
            "P": ["R", "B"]
        }
        colors = color_pairs[target_color]
        positions = random.sample(path_positions, 2)
        devices[f"{positions[0][0]},{positions[0][1]}"] = colors[0]
        devices[f"{positions[1][0]},{positions[1][1]}"] = colors[1]
        for pos in positions:
            path_positions.remove(pos)

    # 确保至少有一个额外的漂白机（除了起点）
    if path_positions:  # 如果路径上还有空位
        bleach_pos = random.choice(path_positions)
        devices[f"{bleach_pos[0]},{bleach_pos[1]}"] = "W"
        path_positions.remove(bleach_pos)

    return devices, path

def generate_valid_graph(size, difficulty):
    # 根据难度设置目标颜色
    if difficulty == "easy":
        target_colors = ["R", "G", "B", "Y"]
        fill_prob = 0.5
    elif difficulty == "medium":
        target_colors = ["Y", "C", "P"]
        fill_prob = 0.5
    else:
        target_colors = ["Y", "C", "P"]
        fill_prob = 0.5
    
    target = random.choice(target_colors)
    devices, path = generate_path(size, target)
    
    # 在剩余位置添加额外设备
    remaining_positions = [(i,j) for i in range(1,size+1) for j in range(1,size+1) 
                         if (i,j) not in [(p[0],p[1]) for p in path]]
    remaining_positions.remove((1,1))
    extra_devices = ["R", "G", "B"]  # 移除传送带，只保留染色机和漂白机
    for pos in remaining_positions:
        if random.random() < fill_prob:
            devices[f"{pos[0]},{pos[1]}"] = random.choice(extra_devices)
        else:
            devices[f"{pos[0]},{pos[1]}"] = "-"
            
    # 生成初始地图，RGB用X表示，W和-保持不变
    initial_map = {}
    for k, v in devices.items():
        if v in ["R", "G", "B"]:
            initial_map[k] = "X"
        else:  # W或-保持不变
            initial_map[k] = v
            
    return {
        "path": path,
        "size": size,
        "devices": devices,
        "target": target,
        "initial_map": initial_map
    }

def create_base_prompt(size, initial_map, target):
    return f"""Let's play Rainbow Candy Factory! Your task is to guide a candy through hidden devices to reach the destination with target color.

Rules:
1. Control a candy through a {size}x{size} factory grid
2. Start at (1,1) with white color (W), reach ({size},{size})
3. Hidden devices in cells by X:
   - Dye Machines: R(red), G(green), B(blue)
   - Empty cells (-)
4. Bleach Machine is shown as W(white) in the map and it can reset any color to white 
4. Each level gives a target color to achieve

Move Types:
1. To make a move:
   Format: 'My Move: Y'
   where:
   - Y is one of: N, E, S, W (directions)
   Example: 'My Move: E'

After each move you will receive your current candy color:
Example: 'R' means your candy is now Red

Color Rules:
- Initial color: White (W)
- Basic colors: Red (R), Green (G), Blue (B)
- Mixed colors: Yellow (Y), Cyan (C), Purple (P)
- Color mixing: R+G=Y, G+B=C, R+B=P
- Bleach Machine (W) resets ANY color back to White
- For Mixed colors, bleaching machine can make it White, but dyeing machine cannot change its color.

Example Interaction:
You: 'My Move: E'
Me: 'R'
You: 'My Move: S'
Me: 'W'
You: 'My Move: E'
Me: 'G'

Instructions:
1. Make moves based on color feedback
2. Use exactly the format shown above
3. Explain your reasoning before each move
4. Watch out for bleach machines that reset progress

Initial Map:
{initial_map}

Target Color:
{target}

Remember:
- Start at (1,1) with White color
- Cannot see machine types until encountered
- Bleach machines reset ALL colors to White
- You can go to the cell you've been to.
- Moving out of bounds will result in failure
- Must reach ({size},{size}) with target color

Ready to start? Make your first move!"""

def create_jsonl_files():
    configs = {
        "easy": {"size": 3, "count": 30},
        "medium": {"size": 4, "count": 30},
        "hard": {"size": 5, "count": 30}
    }
    
    for difficulty, config in configs.items():
        graphs = set()
        with open(f"{difficulty}.jsonl", "w") as f:
            count = 1
            while count <= config["count"]:
                graph = generate_valid_graph(config["size"], difficulty)
                graph_str = json.dumps(graph, sort_keys=True)
                
                if graph_str not in graphs:
                    graphs.add(graph_str)
                    # 格式化初始地图
                    initial_map = format_initial_map(graph)
                    data = {
                        "question_id": count,
                        "prompt": create_base_prompt(config["size"], initial_map, graph["target"]),
                        "type": "State Operation",
                        "scale": config["size"],
                        "difficulty": difficulty,
                        "title": "RainbowCandy",
                        "graph": {
                            "path":graph["path"],
                            "size": graph["size"],
                            "devices": graph["devices"],
                            "target": graph["target"]
                        }
                    }
                    f.write(json.dumps(data) + "\n")
                    count += 1

def format_initial_map(graph):
    """将初始地图格式化为字符串显示"""
    size = graph["size"]
    initial_map = graph["initial_map"]
    map_str = ""
    for i in range(1, size + 1):
        row = ""
        for j in range(1, size + 1):
            row += initial_map[f"{i},{j}"] + " "
        map_str += row.strip() + "\n"
    return map_str.strip()

if __name__ == "__main__":
    create_jsonl_files()
