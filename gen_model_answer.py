import argparse
import json
import os
import random
from itertools import product  
from tqdm import tqdm
from vllm import LLM, SamplingParams
from conversation import get_conversation_template
from game_handlers import get_game_handler

def load_questions(question_file: str):
    """Load questions from a file."""
    questions = []
    with open(question_file, "r") as ques_file:
        for line in ques_file:
            if line.strip():
                try:
                    questions.append(json.loads(line))
                except json.JSONDecodeError as e:
                    print(f"Failed to parse line in {question_file}: {e}")
    return questions

def run_static_eval_vllm(
    llm,
    sampling_params,
    model_id,
    questions,
    answer_file,
    think_mode,
    max_round,
    existing_answers
):
    """Handle static questions (information_query type)"""
    active_questions = []
    question_states = {}
    for question in questions:
        question_id = question["question_id"]
        game_type = question.get("title", "").split(".")[0].strip()
        
        # Skip if we already have a correct answer
        if question_id in existing_answers:
            turns = existing_answers[question_id]["turns"]
            game_handler = get_game_handler(game_type=game_type, question=question)
            if turns and game_handler.is_complete(turns[-1]["result"]):
                continue
            # Determine the next round based on existing turns
            current_round = len(turns) + 1
        else:
            game_handler = get_game_handler(
                game_type=game_type,
                question=question
            )
            current_round = 1
        
        question_states[question_id] = {
            "handler": game_handler,
            "current_round": current_round,
            "turns": existing_answers.get(question_id, {}).get("turns", [])
        }
        active_questions.append(question)
    
    # Main loop: Process all rounds starting from the next round
    for round_num in range(1, max_round + 1):
        if not active_questions:
            break
            
        print(f"Processing round {round_num}...")
        prompts = []
        question_ids = []
        
        for question in active_questions[:]:
            question_id = question["question_id"]
            state = question_states[question_id]
            
            # Skip rounds that have already been processed
            if state["current_round"] > round_num:
                continue
            
            conv = get_conversation_template(model_id)
            prompt_content = question["prompt"]
            ready_index = prompt_content.find("\n\nReady to start")
            if ready_index != -1:
                prompt_content = (
                    prompt_content[:ready_index] + 
                    f"\n- You have {max_round} attempts to find the answer, which means you need to output your answer in the {max_round}-th round or before this round." +
                    prompt_content[ready_index:]
                )
            conv.append_message(conv.roles[0], prompt_content)
            conv.append_message(conv.roles[0], prompt_content)
            
            for turn in state["turns"]:
                conv.append_message(conv.roles[1], turn["output"])
                conv.append_message(conv.roles[0], turn["feedback"])
            
            if think_mode:
                conv.append_message(conv.roles[1], "<think>\n")
            else:
                conv.append_message(conv.roles[1], None)
            
            prompt = conv.get_prompt()
            prompts.append(prompt)
            question_ids.append(question_id)
        
        if not prompts:
            continue  # No prompts to process in this round
        
        # Batch generate answers with exception handling
        try:
            outputs = llm.generate(prompts, sampling_params, use_tqdm=False)
        except Exception as e:
            print(f"Batch generation failed on round {round_num}: {e}")
            # Switch to individual processing
            outputs = []
            for i, prompt in enumerate(prompts):
                question_id = question_ids[i]
                state = question_states[question_id]
                try:
                    individual_output = llm.generate([prompt], sampling_params, use_tqdm=False)
                    if not individual_output:
                        raise ValueError("No output returned for individual prompt.")
                    outputs.append(individual_output[0])
                except Exception as e_prompt:
                    print(f"Individual generation failed for question {question_id}: {e_prompt}")
                    # Remove from active_questions
                    active_questions = [q for q in active_questions if q["question_id"] != question_id]
                    continue  # Proceed to next prompt
                
        # Process outputs (both batch and individual)
        for i, output in enumerate(outputs):
            question_id = question_ids[i]
            state = question_states.get(question_id)
            if not state:
                continue  # This question was removed due to an error
            
            try:
                raw_text = output.outputs[0].text.strip()
                generated_text = raw_text.split("</think>")[-1].strip()
                result, feedback = state["handler"].parse_response(generated_text)
            except Exception as parse_e:
                print(f"Failed to parse response for question {question_id}: {parse_e}")
                result, feedback = None, "Error parsing response"
            
            turn = {
                "round": round_num,
                "raw_output": raw_text,
                "output": generated_text,
                "result": result,
                "feedback": feedback
            }
            state["turns"].append(turn)
            
            try:
                with open(answer_file, "a") as fout:
                    ans_json = {
                        "question_id": question_id,
                        "turns": state["turns"]
                    }
                    fout.write(json.dumps(ans_json) + "\n")
            except Exception as file_e:
                print(f"Failed to write answer for question {question_id}: {file_e}")
            
            if state["handler"].is_complete(result):
                active_questions = [q for q in active_questions if q["question_id"] != question_id]
            elif "invalid" in feedback.lower() or "win" in feedback.lower() or "lose" in feedback.lower():
                active_questions = [q for q in active_questions if q["question_id"] != question_id]
            else:
                # Increment the current_round only if the question is still active
                state["current_round"] += 1

def run_dynamic_eval_vllm(
    llm,
    sampling_params,
    model_id,
    questions,
    answer_file,
    think_mode,
    max_round,
    existing_answers
):
    """Handle dynamic questions (dynamic_adaptation type)"""
    active_questions = []
    question_states = {}
    
    for question in questions:
        question_id = question["question_id"]
        game_type = question.get("title", "").split(".")[0].strip()

        if question_id in existing_answers:
            turns = existing_answers[question_id]["turns"]
            game_handler = get_game_handler(game_type=game_type, question=question)
            if turns and game_handler.is_complete(turns[-1]["result"]):
                continue
            # Determine the next round
            current_round = len(turns) + 1
        else:
            game_handler = get_game_handler(
                game_type=game_type,
                question=question
            )
            current_round = 1

        question_states[question_id] = {
            "handler": game_handler,
            "current_round": current_round,
            "turns": existing_answers.get(question_id, {}).get("turns", [])
        }
        active_questions.append(question)
    
    # Main loop
    for round_num in range(1, max_round + 1):
        if not active_questions:
            break
            
        print(f"Processing round {round_num}...")
        prompts = []
        question_ids = []
        
        for question in active_questions[:]:
            question_id = question["question_id"]
            state = question_states[question_id]
            
            # Skip rounds that have already been processed
            if state["current_round"] > round_num:
                continue
            
            if len(state["turns"]) >= max_round:
                continue
                
            conv = get_conversation_template(model_id)
            prompt_content = question["prompt"]
            ready_index = prompt_content.find("\n\nReady to start")
            if ready_index != -1:
                prompt_content = (
                    prompt_content[:ready_index] + 
                    f"\n- You have {max_round} attempts to find the answer, which means you need to output your answer in the {max_round}-th round or before this round." +
                    prompt_content[ready_index:]
                )
            conv.append_message(conv.roles[0], prompt_content)
            
            for turn in state["turns"]:
                conv.append_message(conv.roles[1], turn["output"])
                conv.append_message(conv.roles[0], turn["feedback"])
            
            if think_mode:
                conv.append_message(conv.roles[1], "<think>\n")
            else:
                conv.append_message(conv.roles[1], None)
            
            prompt = conv.get_prompt()
            prompts.append(prompt)
            question_ids.append(question_id)
        
        if not prompts:
            continue  # No prompts to process in this round
        
        # Batch generate answers with exception handling
        try:
            outputs = llm.generate(prompts, sampling_params, use_tqdm=False)
        except Exception as e:
            print(f"Batch generation failed on round {round_num}: {e}")
            # Switch to individual processing
            outputs = []
            for i, prompt in enumerate(prompts):
                question_id = question_ids[i]
                state = question_states[question_id]
                try:
                    individual_output = llm.generate([prompt], sampling_params, use_tqdm=False)
                    if not individual_output:
                        raise ValueError("No output returned for individual prompt.")
                    outputs.append(individual_output[0])
                except Exception as e_prompt:
                    print(f"Individual generation failed for question {question_id}: {e_prompt}")
                    # Remove from active_questions
                    active_questions = [q for q in active_questions if q["question_id"] != question_id]
                    continue  # Proceed to next prompt
            
        # Process outputs (both batch and individual)
        for i, output in enumerate(outputs):
            question_id = question_ids[i]
            state = question_states.get(question_id)
            if not state:
                continue  # This question was removed due to an error
            
            try:
                raw_text = output.outputs[0].text.strip()
                generated_text = raw_text.split("</think>")[-1].strip()
                result, feedback = state["handler"].parse_response(generated_text)
            except Exception as parse_e:
                print(f"Failed to parse response for question {question_id}: {parse_e}")
                result, feedback = None, "Error parsing response"
            
            turn = {
                "round": round_num,
                "raw_output": raw_text,
                "output": generated_text,
                "result": result,
                "feedback": feedback
            }
            state["turns"].append(turn)
            
            try:
                with open(answer_file, "a") as fout:
                    ans_json = {
                        "question_id": question_id,
                        "turns": state["turns"]
                    }
                    fout.write(json.dumps(ans_json) + "\n")
            except Exception as file_e:
                print(f"Failed to write answer for question {question_id}: {file_e}")
            
            if state["handler"].is_complete(result):
                active_questions = [q for q in active_questions if q["question_id"] != question_id]
            elif "invalid" in feedback.lower() or "win" in feedback.lower() or "lose" in feedback.lower():
                active_questions = [q for q in active_questions if q["question_id"] != question_id]
            else:
                # Increment the current_round only if the question is still active
                state["current_round"] += 1

def run_game_eval_vllm(
    llm,
    sampling_params,
    model_id,
    questions,
    answer_file,
    think_mode,
    existing_answers
):
    """Handle strategic game type questions (strategic_game type) using vLLM"""
    active_questions = []
    question_states = {}
    
    for question in questions:
        question_id = question["question_id"]
        game_type = question.get("title", "").strip()
        max_turns = question.get("turns", 0)  # Assuming 'turns' is an integer representing max turns
        
        # Check for existing answers
        if question_id in existing_answers:
            existing_turns = existing_answers[question_id].get("turns", [])
            
            # Check if all rounds are completed or last feedback is Invalid
            if len(existing_turns) >= max_turns or (existing_turns and existing_turns[-1].get("feedback") == "Invalid"):
                continue
            
            current_turn = len(existing_turns) + 1
        else:
            current_turn = 1
        
        try:
            game_handler = get_game_handler(
                game_type=game_type,
                question=question
            )
        except Exception as handler_e:
            print(f"Failed to get game handler for question {question_id}: {handler_e}")
            continue
        
        question_states[question_id] = {
            "handler": game_handler,
            "current_turn": current_turn,
            "turns": existing_answers.get(question_id, {}).get("turns", [])
        }
        active_questions.append(question)
    
    # Main loop
    while active_questions:
        print(f"Remaining questions: {len(active_questions)}")
        prompts = []
        question_ids = []
        
        for question in active_questions[:]:
            question_id = question["question_id"]
            state = question_states[question_id]
            max_turns = question.get("turns", 0)
            
            # Skip if maximum turns reached
            if len(state["turns"]) >= max_turns:
                continue
            
            conv = get_conversation_template(model_id)
            prompt_content = question["prompt"]
            conv.append_message(conv.roles[0], prompt_content)
            
            for turn in state["turns"]:
                conv.append_message(conv.roles[1], turn["output"])
                conv.append_message(conv.roles[0], turn["feedback"])
            
            if think_mode:
                conv.append_message(conv.roles[1], "<think>\n")
            else:
                conv.append_message(conv.roles[1], None)
            
            prompt = conv.get_prompt()
            prompts.append(prompt)
            question_ids.append(question_id)
        
        if not prompts:
            break  # No prompts to process
        
        # Batch generate answers with exception handling
        try:
            outputs = llm.generate(prompts, sampling_params, use_tqdm=False)
        except Exception as e:
            print(f"Batch generation failed during game evaluation: {e}")
            # Switch to individual processing
            outputs = []
            for i, prompt in enumerate(prompts):
                question_id = question_ids[i]
                state = question_states[question_id]
                try:
                    individual_output = llm.generate([prompt], sampling_params, use_tqdm=False)
                    if not individual_output:
                        raise ValueError("No output returned for individual prompt.")
                    outputs.append(individual_output[0])
                except Exception as e_prompt:
                    print(f"Individual generation failed for question {question_id}: {e_prompt}")
                    # Remove from active_questions
                    active_questions = [q for q in active_questions if q["question_id"] != question_id]
                    continue  # Proceed to next prompt
            
        # Process outputs (both batch and individual)
        for i, output in enumerate(outputs):
            question_id = question_ids[i]
            state = question_states.get(question_id)
            if not state:
                continue  # This question was removed due to an error
            
            try:
                raw_text = output.outputs[0].text.strip()
                generated_text = raw_text.split("</think>")[-1].strip()
                result, feedback = state["handler"].parse_response(generated_text)
            except Exception as parse_e:
                print(f"Failed to parse response for question {question_id}: {parse_e}")
                result, feedback = None, "Error parsing response"
            
            turn = {
                "round": state["current_turn"],
                "raw_output": raw_text,
                "output": generated_text,
                "result": result,
                "feedback": feedback
            }
            state["turns"].append(turn)
            
            try:
                with open(answer_file, "a") as fout:
                    ans_json = {
                        "question_id": question_id,
                        "turns": state["turns"]
                    }
                    fout.write(json.dumps(ans_json) + "\n")
            except Exception as file_e:
                print(f"Failed to write answer for question {question_id}: {file_e}")
            
            if "invalid" in feedback.lower() or "win" in feedback.lower() or "lose" in feedback.lower() or len(state["turns"]) >= max_turns:
                active_questions = [q for q in active_questions if q["question_id"] != question_id]
            else:
                # Increment the current_turn only if the question is still active
                state["current_turn"] += 1

def run_eval(
    llm,
    sampling_params,
    model_id,
    category,
    game_types,
    difficulties,  # Changed from single difficulty to list
    max_rounds,    # Changed from single max_round to list
    question_file_template,
    answer_file_template,
    eval_file_template,
    max_new_token,
    seed,
    think_mode
):
    params_info = (
        f"model_id: {model_id}\n"
        f"category: {category}\n"
        f"game_types: {game_types}\n"
        f"difficulties: {difficulties}\n"  # Added difficulties info
        f"max_rounds: {max_rounds}\n"        # Added max_rounds info
        f"question_file_template: {question_file_template}\n"
        f"answer_file_template: {answer_file_template}\n"
        f"eval_file_template: {eval_file_template}\n"
        f"max_new_token: {max_new_token}\n"
        f"seed: {seed}\n"
        f"think_mode: {think_mode}\n"
        f"sampling_params: seed={sampling_params.seed}, temperature={sampling_params.temperature}, max_tokens={sampling_params.max_tokens}, stop={sampling_params.stop}\n"
    )
    print("开始运行 run_eval，传入的参数如下：")
    print(params_info)
    
    # Iterate over all combinations of game_type, difficulty, and max_round
    for game_type, difficulty, max_round in product(game_types, difficulties, max_rounds):
        print(f"Processing combination - Game Type: {game_type}, Difficulty: {difficulty}, Max Round: {max_round}")
        
        question_file = question_file_template.format(
            category=category,
            game_type=game_type,
            difficulty=difficulty  # Updated to use current difficulty
        )
        answer_file = answer_file_template.format(
            category=category,
            game_type=game_type,
            difficulty=difficulty,   # Updated to use current difficulty
            model_id=model_id,
            max_round=max_round      # Updated to use current max_round
        )
        eval_file = eval_file_template.format(
            category=category,
            game_type=game_type,
            difficulty=difficulty,   # Updated to use current difficulty
            max_round=max_round,     # Updated to use current max_round
            model_id=model_id
        )
        
        # Load questions
        if not os.path.exists(question_file):
            print(f"Question file not found: {question_file}")
            continue  # Skip this combination if question file doesn't exist
        questions = load_questions(question_file)
        if not questions:
            print(f"No questions to process in file: {question_file}")
            continue  # Skip if no questions
        
        random.shuffle(questions)
        os.makedirs(os.path.dirname(answer_file), exist_ok=True)
        os.makedirs(os.path.dirname(eval_file), exist_ok=True)
        
        # Load existing answers
        existing_answers = {}
        if os.path.exists(answer_file):
            with open(answer_file, "r") as fin:
                for line in fin:
                    if line.strip():
                        try:
                            ans = json.loads(line)
                            qid = ans["question_id"]
                            existing_answers[qid] = ans
                        except json.JSONDecodeError as e:
                            print(f"Failed to parse existing answer line in {answer_file}: {e}")
        
        print(f"Starting evaluation for combination - Game Type: {game_type}, Difficulty: {difficulty}, Max Round: {max_round}")
        
        if category == "information_query":
            run_static_eval_vllm(
                llm=llm,
                sampling_params=sampling_params,
                model_id=model_id,
                questions=questions,
                answer_file=answer_file,
                think_mode=think_mode,
                max_round=max_round,  # Pass current max_round
                existing_answers=existing_answers
            )
        elif category == "dynamic_adaptation":
            run_dynamic_eval_vllm(
                llm=llm,
                sampling_params=sampling_params,
                model_id=model_id,
                questions=questions,
                answer_file=answer_file,
                think_mode=think_mode,
                max_round=max_round,  # Pass current max_round
                existing_answers=existing_answers
            )
        elif category == "state_operation":
            run_dynamic_eval_vllm(
                llm=llm,
                sampling_params=sampling_params,
                model_id=model_id,
                questions=questions,
                answer_file=answer_file,
                think_mode=think_mode,
                max_round=max_round,  # Pass current max_round
                existing_answers=existing_answers
            )
        elif category == "strategic_gaming":
            run_game_eval_vllm(
                llm=llm,
                sampling_params=sampling_params,
                model_id=model_id,
                questions=questions,
                answer_file=answer_file,
                think_mode=think_mode,
                existing_answers=existing_answers
            )
        else:
            print(f"Unknown category: {category}")
            continue  # Skip unknown categories
        
        try:
            reorg_answer_file(answer_file)
            print(f"Successfully reorganized answer file: {answer_file}")
        except Exception as e:
            print(f"Failed to reorganize answer file {answer_file}: {e}")
        
        # Run answer evaluation
        try:
            from answer_evaluator import evaluate_answers
            evaluate_answers(
                question_file=question_file,
                answer_file=answer_file,
                eval_file=eval_file,
                game_type=game_type
            )
            print(f"Successfully evaluated answers for combination - Game Type: {game_type}, Difficulty: {difficulty}, Max Round: {max_round}")
        except Exception as e:
            print(f"Failed to evaluate answers for combination - Game Type: {game_type}, Difficulty: {difficulty}, Max Round: {max_round}: {e}")

def reorg_answer_file(answer_file):
    """Sort by question id and de-duplication"""
    answers = {}
    try:
        with open(answer_file, "r") as fin:
            for l in fin:
                if l.strip():
                    try:
                        qid = json.loads(l)["question_id"]
                        answers[qid] = l.strip()
                    except json.JSONDecodeError as e:
                        print(f"Failed to parse line during reorganization in {answer_file}: {e}")
        qids = sorted(
            answers.keys(),
            key=lambda x: int(x) if isinstance(x, str) and x.isdigit() else x
        )
        with open(answer_file, "w") as fout:
            for qid in qids:
                fout.write(answers[qid] + "\n")
    except Exception as e:
        print(f"Error while reorganizing answer file {answer_file}: {e}")
        raise e

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-path", type=str, required=True, help="Path to the model")
    parser.add_argument("--model-id", type=str, required=True, help="ID of the model")
    parser.add_argument("--category", type=str, default="information_query", help="Category of questions")
    parser.add_argument("--game-type", type=str, nargs='+', required=True, help="Types of the game(s)")
    parser.add_argument("--difficulty", type=str, nargs='+', default=["easy"], help="Difficulty level")  # Modified to accept multiple difficulties
    parser.add_argument("--max-new-token", type=int, default=16384, help="Maximum number of new tokens")
    parser.add_argument("--seed", type=int, default=1234, help="Random seed")
    parser.add_argument("--tensor-parallel-size", type=int, default=8, help="Tensor parallel size")
    parser.add_argument("--think-mode", type=bool, default=False)
    parser.add_argument("--max-round", type=int, nargs='+', default=[10], help="Maximum number of rounds")  # Modified to accept multiple max_rounds
    args = parser.parse_args()
    
    # Define file path templates
    question_file_template = os.path.join(
        "/home/data/lanlin.lxy/cf_trans/problem",
        "{category}",
        "{game_type}",
        "{difficulty}.jsonl"
    )

    answer_file_template = os.path.join(
        "/home/data/lanlin.lxy/cf_trans/model_answer",
        "{category}",
        "{game_type}",
        "{difficulty}",
        "{max_round}",
        "{model_id}.jsonl"
    )

    eval_file_template = os.path.join(
        "/home/data/lanlin.lxy/cf_trans/evaluation",
        "{category}",
        "{game_type}",
        "{difficulty}",
        "{max_round}",
        "{model_id}_eval.json"
    )

    # Initialize vLLM once
    try:
        llm = LLM(
            model=args.model_path,
            tensor_parallel_size=args.tensor_parallel_size
        )
        print(f"Successfully initialized LLM with model path: {args.model_path}")
    except Exception as e:
        print(f"Failed to initialize LLM with model path {args.model_path}: {e}")
        raise e

    sampling_params = SamplingParams(
        seed=args.seed,
        temperature=0,
        max_tokens=args.max_new_token,
        stop=["</im_end>"],
    )

    # Run evaluation for each combination of game_type, difficulty, and max_round
    try:
        run_eval(
            llm=llm,
            sampling_params=sampling_params,
            model_id=args.model_id,
            category=args.category,
            game_types=args.game_type,
            difficulties=args.difficulty,         # Pass list of difficulties
            max_rounds=args.max_round,           # Pass list of max_rounds
            question_file_template=question_file_template,
            answer_file_template=answer_file_template,
            eval_file_template=eval_file_template,
            max_new_token=args.max_new_token,
            seed=args.seed,
            think_mode=args.think_mode
        )
    except Exception as e:
        print(f"Evaluation run failed: {e}")