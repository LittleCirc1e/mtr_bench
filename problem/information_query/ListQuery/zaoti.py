import json
import random

def get_base_prompt(scale):
    return f"""Let's play Linked List Query Game! Your task is to find a specific value in a sorted linked list through queries.

Rules:
1. There is a hidden sorted linked list with {scale} elements
2. Each element has a value and a next pointer (pointing to the next element's index)
3. You can make two types of queries:
   - VALUE query: you will get both value and next pointer at position i
   - ANSWER submission: you will get a feedback of 'Correct' or 'Incorrect'

Query Types:
1. To make a value query:
   Format: 'My Query: i'
   where:
   - i is the position in list (1-based indexing)
   Example: 'My Query: 1'

2. To submit final answer:
   Format: 'My Answer: ans'
   where ans is either:
   - The minimum value in the list
   Example: 'My Answer: 80'

Example Interaction:
List length = {scale}, start = 3, x = 80
You: 'My Query: 1'
Me: 'value=97, next=-1'
You: 'My Query: 3'
Me: 'value=16, next=2'
You: 'My Answer: 80'
Me: 'Correct'

Instructions:
1. Make queries to explore the linked list
2. Use exactly the formats shown above
3. Explain your reasoning before each query/answer

Remember:
- Following next pointers, values are in increasing order
- You need to find minimum value of the list
- Position indices start from 1
- Think carefully about which positions to query

Ready to start? Make your first query!"""

def generate_linked_list(size, max_val):
    # Generate random sorted values
    values = sorted(random.sample(range(1, max_val), size))
    
    # Generate positions for values (randomly placed)
    positions = list(range(1, size + 1))
    random.shuffle(positions)
    
    # Create a mapping from value index to position
    value_to_pos = {i: pos for i, pos in enumerate(positions)}
    
    # Create nodes
    nodes = {}
    for i in range(size):
        current_pos = value_to_pos[i]
        next_pos = value_to_pos[i + 1] if i < size - 1 else -1
        
        nodes[str(current_pos)] = {
            "value": values[i],
            "next": next_pos
        }
    
    return nodes, values[0]  # Return both the nodes and the minimum value

def create_jsonl(filename, scale, difficulty, max_val):
    with open(filename, 'w') as f:
        for i in range(1, 51):
            linked_list, min_value = generate_linked_list(scale, max_val)
            data = {
                "question_id": i,
                "prompt": get_base_prompt(scale),
                "type": "Information Query",
                "feedback": "Direct Value Response",
                "scale": scale,
                "difficulty": difficulty,
                "title": "ListQuery",
                "list": linked_list,
                "answer": min_value
            }
            f.write(json.dumps(data) + '\n')

def main():
    # Create easy.jsonl (scale=5)
    #create_jsonl('easy.jsonl', 5, 'easy', 100)
    
    # Create medium.jsonl (scale=8)
    create_jsonl('medium.jsonl', 9, 'medium', 200)
    
    # Create hard.jsonl (scale=11)
    #create_jsonl('hard.jsonl', 11, 'hard', 500)

if __name__ == "__main__":
    main()
