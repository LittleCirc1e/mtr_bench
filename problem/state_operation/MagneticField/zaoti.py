import json
import random
from typing import List, Dict, Set, Tuple
from collections import deque

def create_prompt(size: int, grid: List[List[str]], danger_zones: List[Tuple[int, int]]) -> str:
    # Create a display grid (convert NESW to 1234)
    display_grid = []
    direction_map = {'N': '1', 'E': '2', 'S': '3', 'W': '4'}
    for row in grid:
        new_row = []
        for cell in row:
            if cell in direction_map:
                new_row.append(direction_map[cell])
            else:
                new_row.append(cell)
        display_grid.append(new_row)

    # Build grid string representation with coordinates
    grid_str = "  " + " ".join(str(i+1) for i in range(size)) + "  (column)\n"  # Column coordinates
    for i in range(size):
        grid_str += f"{i+1} {' '.join(display_grid[i])} \n"
    grid_str += "(row)\n"

    # Build description for each position
    position_str = "Grid positions:\n"
    for i in range(size):
        for j in range(size):
            val = display_grid[i][j]
            pos_desc = f"({i+1},{j+1}): "
            if val == ".":
                pos_desc += "Neutral space"
            elif val == "X":
                pos_desc += "Danger zone"
            elif val == "G":
                pos_desc += "Goal"
            else:
                pos_desc += f"Magnetic field type {val}"
            position_str += pos_desc + "\n"

    base_prompt = f"""Let's play Magnetic Field Explorer! Your task is to navigate through a grid with mysterious magnetic forces.

Rules:
1. Game Field:
   - A {size} * {size} grid with:
     * Numbers (1-4) - Different types of magnetic fields
     * "." - Neutral space
     * "X" - Danger zone (avoid these)
     * "G" - Goal (reach here to win)
   - Start: (1, 1) (top-left corner)
   - Goal: ({size}, {size}) (bottom-right corner)

2. Magnetic Fields:
   - Four types of magnetic fields (1-4)
   - Each number represents a unique direction (North, South, East, or West)
   - You'll discover the direction of each number through movement
   - Same number always means same direction
   - When you enter a magnetic field:
     * You will be forced to move one step in its direction
     * If that step would hit a boundary, you stay on the magnetic field
     * If that step would hit a danger zone, you lose
     * If that step would hit another magnetic field, you move there and it activates

3. Movement Rules:
   - Basic moves: U(up), D(down), L(left), R(right)
   - Movement sequence for each turn:
     1. You move one step in your chosen direction
     2. If you land on:
        - Magnetic field: Move one step in its direction unless that step would hit a boundary
        - Danger zone: You lose
        - Neutral space: Stay there
     3. If magnetic field pushed you to another magnetic field, repeat step 2

Current Grid Layout (with coordinates):
{grid_str}
{position_str}

Move Format:
1. To make a move:
   Format: 'My Move: X'
   where X is one of: U, D, L, R
   Example: 'My Move: R'

2. System Response:
   Format: 'x y'
   - Shows your final position coordinates
   - (-1, -1) if you hit danger zone

Remember:
- Each number (1-4) represents a fixed direction
- Figure out what direction each number represents
- Magnetic fields activate when you land on them
- Avoid danger zones (X)
- Reach goal (G) to win
- You don't necessarily need to figure out or pass through the magnetic fields; your goal is only to reach the target zone ({size}, {size}) safely.

Ready to start? Make your first move!"""
    return base_prompt

def check_path_exists(grid: List[List[str]], size: int) -> bool:
    """Use BFS to check if there exists a feasible path from start to goal."""
    def get_next_positions(x: int, y: int) -> List[Tuple[int, int]]:
        """Get all reachable positions from the current position, considering magnetic field effects."""
        positions = []
        # Check four basic directions
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            nx, ny = x + dx, y + dy
            # Check boundary
            if not (0 <= nx < size and 0 <= ny < size):
                continue
            # Check danger zone    
            if grid[nx][ny] == 'X':
                continue
            current_cell = grid[nx][ny]
            if current_cell == '.' or current_cell == 'G':
                positions.append((nx, ny))
            elif current_cell in 'NESW':
                # Calculate magnetic field effect
                mag_dx, mag_dy = {
                    'N': (-1, 0),
                    'E': (0, 1),
                    'S': (1, 0),
                    'W': (0, -1)
                }[current_cell]
                final_x, final_y = nx + mag_dx, ny + mag_dy
                # Check if the pushed position is valid
                if (0 <= final_x < size and 0 <= final_y < size and 
                    grid[final_x][final_y] != 'X'):
                    positions.append((final_x, final_y))
                else:
                    positions.append((nx, ny))
        return positions

    # BFS search
    visited = set()
    queue = deque([(0, 0)])
    visited.add((0, 0))
    
    while queue:
        x, y = queue.popleft()
        if x == size-1 and y == size-1:
            return True
        for next_x, next_y in get_next_positions(x, y):
            if (next_x, next_y) not in visited:
                queue.append((next_x, next_y))
                visited.add((next_x, next_y))
    return False

def generate_grid(size: int, magnet_count: int = None) -> Tuple[List[List[str]], List[Tuple[int, int]]]:
    """
    Generates a grid with specified number of magnetic fields.
    magnet_count: Number of magnetic fields to place. If None, defaults to size - 2.
    """
    if magnet_count is None:
        magnet_count = size 

    while True:  # Continuously generate until a valid grid is found
        grid = [["." for _ in range(size)] for _ in range(size)]
        
        # Set start and goal positions
        grid[0][0] = "."
        grid[size-1][size-1] = "G"
        
        # Ensure there are size-2 danger zones, with at least one on the diagonal
        diagonal_positions = [(i, i) for i in range(1, size-1)]
        x_diagonal = random.choice(diagonal_positions) if diagonal_positions else (0, 0)
        grid[x_diagonal[0]][x_diagonal[1]] = "X"
        danger_positions = {x_diagonal}
        
        # Place remaining danger zones up to size-2
        while len(danger_positions) < size - 2:
            x = random.randint(0, size-1)
            y = random.randint(0, size-1)
            if (x, y) != (0, 0) and (x, y) != (size-1, size-1) and (x, y) not in danger_positions:
                grid[x][y] = "X"
                danger_positions.add((x, y))
        
        # Place magnetic fields limited to magnet_count
        directions = ['N', 'E', 'S', 'W']
        available = [(x, y) for x in range(size) for y in range(size) 
                    if grid[x][y] == "." and (x, y) != (0, 0)]
        
        if len(available) >= magnet_count:
            magnet_positions = random.sample(available, magnet_count)
            for pos in magnet_positions:
                grid[pos[0]][pos[1]] = random.choice(directions)
            
            # Check if a feasible path exists
            if check_path_exists(grid, size):
                danger_zones = [(x+1, y+1) for x, y in danger_positions]
                return grid, danger_zones
        
        # If no feasible path or not enough positions, regenerate

def verify_grid(grid: List[List[str]], size: int) -> bool:
    # Check start and goal positions
    if grid[0][0] != "." or grid[size-1][size-1] != "G":
        return False
    
    # Count dangers and magnets
    danger_count = sum(1 for row in grid for cell in row if cell == "X")
    magnet_count = sum(1 for row in grid for cell in row if cell in "NESW")
    
    # Verify counts
    if danger_count != size - 2:
        return False
    
    # Verify at least one 'X' on the diagonal
    has_diagonal_x = False
    for i in range(1, size-1):
        if grid[i][i] == "X":
            has_diagonal_x = True
            break
    if not has_diagonal_x and size > 2:
        return False
    
    # Verify if a feasible path exists
    if not check_path_exists(grid, size):
        return False
    
    return True

def create_test_case(question_id: int, size: int, difficulty: str, magnet_count: int) -> Dict:
    grid, danger_zones = generate_grid(size, magnet_count)
    return {
        "question_id": question_id,
        "prompt": create_prompt(size, grid, danger_zones),
        "type": "State Operation",
        "scale": size,
        "difficulty": difficulty,
        "title": "MagneticField",
        "graph": {
            "size": size,
            "grid": grid,
            "danger_zones": danger_zones
        }
    }

def generate_file(difficulty: str, size: int, filename: str, extra_magnet_cases: int = 0):
    seen_grids = set()
    max_test_cases = 30
    primary_magnet_count = size 
    extra_cases_magnet_count = primary_magnet_count + 1  # For easy, size=3: 1 + 1 = 2 magnets
    
    with open(filename, 'w') as f:
        for i in range(1, max_test_cases + 1):
            attempts = 0
            while True:
                if attempts > 1000:
                    raise Exception(f"Too many attempts to generate a unique grid for test case {i}.")
                # Determine magnet_count based on the test case index
                if i > (max_test_cases - extra_magnet_cases):
                    current_magnet_count = extra_cases_magnet_count
                else:
                    current_magnet_count = primary_magnet_count
                test_case = create_test_case(i, size, difficulty, current_magnet_count)
                grid_str = str(test_case["graph"]["grid"])
                if grid_str not in seen_grids and verify_grid(test_case["graph"]["grid"], size):
                    seen_grids.add(grid_str)
                    f.write(json.dumps(test_case) + '\n')
                    break
                attempts += 1

# Generate files with updated constraints
# For 'easy', size=3, generate 24 cases with 1 magnetic field and 6 cases with 2 magnetic fields
generate_file("easy", 3, "easy_add.jsonl", extra_magnet_cases=6)

# For 'medium' and 'hard', keep as before (assuming sizes=4 and 5 respectively)
generate_file("medium", 4, "medium_add.jsonl")
generate_file("hard", 5, "hard_add.jsonl")
