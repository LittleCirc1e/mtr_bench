import json
import re
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple
from collections import deque

class GameEvaluator(ABC):
    @abstractmethod
    def evaluate_game(self, question: Dict, turns: List[Dict]) -> Tuple[bool, str]:
        """Evaluate if the game was successfully completed"""
        pass

class WordleEvaluator(GameEvaluator):
    def evaluate_game(self, question: Dict, turns: List[Dict]) -> Tuple[bool, str]:
        """Check if the last feedback is all R's"""
        if not turns:
            return False, "No turns played"
        
        last_turn = turns[-1]
        success = last_turn["feedback"] == "RRRR" or last_turn["feedback"] == "RRRRRRRR" or last_turn["feedback"] == "RRRRRRRRRRRR"
        detail = f"Final guess: {last_turn['result']}"
        return success, detail

class ImpostorsEvaluator(GameEvaluator):
    def evaluate_game(self, question: Dict, turns: List[Dict]) -> Tuple[bool, str]:
        """Find the last Answer turn and check if feedback is 0"""
        answer_turns = [
            turn for turn in turns 
            if turn["result"].startswith("Answer:")
        ]
        
        if not answer_turns:
            return False, "No answer submitted"
            
        last_answer = answer_turns[-1]
        success = last_answer["feedback"] == "1"
        detail = f"Final answer: {last_answer['result']}"
        return success, detail

class RPDEvaluator(GameEvaluator):
    def evaluate_game(self, question: Dict, turns: List[Dict]) -> Tuple[bool, str]:
        """
        评估RPD游戏是否成功完成
        注意：由于密码会动态变化，我们只需要验证是否在任何回合获得了成功的反馈
        不需要与原始密码比较
        """
        if not turns:
            return False, "No turns played"
        
        # 记录密码变化过程
        password_changes = []
        success_found = False
        
        for turn in turns:
            guess_match = re.search(r'Guess: (\d+)', turn["result"])
            if guess_match:
                guess = guess_match.group(1)
                feedback = turn["feedback"]
                password_changes.append(f"Guess {guess} -> Response {feedback}")
                
                if feedback == "Correct":
                    success_found = True
                    final_guess = guess
                    break
        
        if success_found:
            detail = f"Successfully broke in with password: {final_guess}\n"
            detail += f"Total attempts: {len(password_changes)}\n"
            detail += "Password change sequence:\n" + "\n".join(password_changes)
            return True, detail
        else:
            detail = f"Failed to break in after {len(turns)} attempts\n"
            detail += "Password change sequence:\n" + "\n".join(password_changes)
            return False, detail

class BitGuessingEvaluator(GameEvaluator):
    def evaluate_game(self, question: Dict, turns: List[Dict]) -> Tuple[bool, str]:
        """评估BitGuessing游戏是否成功完成"""
        if not turns:
            return False, "No turns played"
        
        # 记录操作和猜测过程
        operations = []
        success_found = False
        
        for turn in turns:
            if "Operation:" in turn["result"]:
                op_match = re.search(r'Operation: (\d+)', turn["result"])
                if op_match:
                    operation = op_match.group(1)
                    operations.append(f"Operation {operation} -> Response {turn['feedback']}")
            elif "Answer:" in turn["result"]:
                ans_match = re.search(r'Answer: (\d+)', turn["result"])
                if ans_match:
                    answer = ans_match.group(1)
                    operations.append(f"Answer {answer} -> {turn['feedback']}")
                    if turn["feedback"] == "Correct":
                        success_found = True
                        final_answer = answer
                        break
        
        if success_found:
            detail = f"Successfully guessed the number: {final_answer}\n"
            detail += f"Total operations: {len(operations)}\n"
            detail += "Operation sequence:\n" + "\n".join(operations)
            return True, detail
        else:
            detail = f"Failed to guess the number after {len(operations)} operations\n"
            detail += "Operation sequence:\n" + "\n".join(operations)
            return False, detail

class GeoGameEvaluator(GameEvaluator):
    def evaluate_game(self, question: Dict, turns: List[Dict]) -> Tuple[bool, str]:
        """
        评估GeoGame游戏是否获胜
        通过计算所有距离的和判断奇偶性
        """
        if not turns:
            return False, "No turns played"
        
        try:
            # 获取起始点和所有可用点
            starting_point = question["starting_point"]
            available_points = question["available_points"]
            
            # 记录选择的点的序列
            points_sequence = [starting_point]
            total_distance = 0
            completed_turns = 0
            
            # 解析所有回合的选择
            for turn in turns:
                # 从结果中提取选择的点的索引
                choice_match = re.search(r'Choice: (\d+)', turn["result"])
                if not choice_match:
                    return False, f"Invalid format after {completed_turns} valid turns"
                
                choice = int(choice_match.group(1)) - 1  # 转换为0-based索引
                points_sequence.append(available_points[choice])
                completed_turns += 1
                
                # 如果有对手的选择，也要添加
                opponent_match = re.search(r'Choice: (\d+)', turn["feedback"])
                if opponent_match:
                    opponent_choice = int(opponent_match.group(1)) - 1
                    points_sequence.append(available_points[opponent_choice])
                    completed_turns += 1
            
            # 计算总距离
            for i in range(1, len(points_sequence)):
                prev_point = points_sequence[i-1]
                curr_point = points_sequence[i]
                distance = self._calculate_distance(prev_point, curr_point)
                total_distance += distance
            
            # 判断胜负
            is_even = total_distance % 2 == 0
            
            # 构造详细信息
            detail = f"Completed turns: {completed_turns}\n"
            detail += f"Total distance sum: {total_distance}\n"
            detail += "Point sequence:\n"
            for i, point in enumerate(points_sequence):
                if i == 0:
                    detail += f"Start: ({point[0]},{point[1]})\n"
                else:
                    detail += f"Move {i}: ({point[0]},{point[1]})\n"
            detail += f"Final sum is {'even' if is_even else 'odd'}"
            
            return is_even, detail
            
        except Exception as e:
            return False, f"Error evaluating game: {str(e)}"
    
    def _calculate_distance(self, point1: List[int], point2: List[int]) -> int:
        """计算两点间的欧几里得距离的平方"""
        dx = point1[0] - point2[0]
        dy = point1[1] - point2[1]
        return dx * dx + dy * dy
        
class MinMaxEvaluator(GameEvaluator):
    def evaluate_game(self, question: Dict, turns: List[Dict]) -> Tuple[bool, str]:
        """
        评估MinMax游戏是否成功完成
        成功条件：提交的最终答案正确（feedback为"1"）
        """
        if not turns:
            return False, "No turns played"
        
        # 记录查询过程
        queries = []
        final_answer = None
        
        for turn in turns:
            if "Query" in turn["result"]:
                # 记录查询
                query_positions = turn["result"].split(": ")[1]
                comparison = turn["feedback"]
                queries.append(f"Compare {query_positions} -> {comparison}")
            elif "Answer" in turn["result"]:
                # 记录最终答案
                final_answer = turn
        
        # 构造详细信息
        detail = "Queries made:\n" + "\n".join(queries)
        
        if final_answer:
            answer_positions = final_answer["result"].split(": ")[1]
            success = final_answer["feedback"] == "1"
            detail += f"\nFinal answer: {answer_positions}"
            detail += f"\nResult: {'Correct' if success else 'Incorrect'}"
            detail += f"\nTotal queries: {len(queries)}"
            return success, detail
        else:
            return False, detail + "\nNo final answer submitted"
class BitQueryEvaluator(GameEvaluator):
    def evaluate_game(self, question: Dict, turns: List[Dict]) -> Tuple[bool, str]:
        """
        评估BitQuery游戏是否成功完成
        检查：
        最终答案是否正确 (feedback为"1")
        """
        if not turns:
            return False, "No turns played"
        
        # 记录查询历史和答案
        queries = []
        final_answer = None
        query_count = 0
        
        for turn in turns:
            if "Query:" in turn["result"]:
                # 记录查询
                operation, positions = turn["result"].split(": ")[1].split(" ", 1)
                result = turn["feedback"]
                queries.append(f"{operation} {positions} -> {result}")
                query_count += 1
                
            elif "Answer:" in turn["result"]:
                # 记录最终答案
                final_answer = turn
                
        # 构造详细信息
        detail = f"Queries made {query_count}:\n"
        detail += "\n".join(queries)
        
        # 检查最终答案
        if final_answer:
            answer_array = final_answer["result"].split(": ")[1]
            success = final_answer["feedback"] == "1" or final_answer["feedback"] == "Correct"
            detail += f"\nFinal answer: {answer_array}"
            detail += f"\nResult: {'Correct' if success else 'Incorrect'}"
            return success, detail
        else:
            return False, detail + "\nNo final answer submitted"

class LegendaryTreeEvaluator(GameEvaluator):
    def evaluate_game(self, question: Dict, turns: List[Dict]) -> Tuple[bool, str]:
        """Check if the last feedback is all R's"""
        if not turns:
            return False, "No turns played"
        
        last_turn = turns[-1]
        success = last_turn["feedback"] == "Correct"
        detail = f"Final guess: {last_turn['result']}"
        return success, detail

class GuessMaxEvaluator(GameEvaluator):
    def evaluate_game(self, question: Dict, turns: List[Dict]) -> Tuple[bool, str]:
        """检查游戏是否成功完成"""
        if not turns:
            return False, "No turns played"
        
        # 统计查询次数
        query_count = sum(1 for turn in turns if turn["result"] == "Query")
        
        # 获取最后一次答案尝试
        last_answer = None
        for turn in reversed(turns):
            if isinstance(turn["result"], list):
                last_answer = turn
                break
        
        if not last_answer:
            return False, "No answer attempted"
            
        # 检查是否成功（结果为"Correct"）
        success = last_answer["feedback"] == "Correct"
        
        # 生成详细信息
        detail = (f"Queries made: {query_count}, "
                 f"Final answer: {last_answer['result']}, "
                 f"Result: {last_answer['feedback']}")
        
        return success, detail

class LinkedListEvaluator(GameEvaluator):
    def evaluate_game(self, question: Dict, turns: List[Dict]) -> Tuple[bool, str]:
        """Check if the last turn is a correct answer submission"""
        if not turns:
            return False, "No turns played"
        
        last_turn = turns[-1]
        
        # 检查最后一步是否是提交答案（而不是查询）
        if not last_turn["result"].isdigit():
            return False, "Game did not end with an answer submission"
        
        success = last_turn["feedback"] == "Correct"
        detail = f"Final answer: {last_turn['result']}, Expected: {question['answer']}"
                    
        return success, detail

class BitCompareEvaluator(GameEvaluator):
    def evaluate_game(self, question: Dict, turns: List[Dict]) -> Tuple[bool, str]:
        """Check if the game was completed successfully within constraints"""
        if not turns:
            return False, "No turns played"
        
        # 检查最后一步是否是答案提交
        last_turn = turns[-1]
        if "Correct" not in last_turn["feedback"] and "Incorrect" not in last_turn["feedback"]:
            return False, "Game did not end with an answer submission"
        
        # 检查最后提交的答案是否正确
        success = last_turn["feedback"] == "Correct"
        
        # 生成详细信息
        detail = (f"Final answer: positions {last_turn['result']}")
        
        return success, detail

class MedianQueryEvaluator(GameEvaluator):
    def evaluate_game(self, question: Dict, turns: List[Dict]) -> Tuple[bool, str]:
        """Check if the game was completed successfully within constraints"""
        if not turns:
            return False, "No turns played"
        
        last_turn = turns[-1]
        if "Correct" not in last_turn["feedback"] and "Incorrect" not in last_turn["feedback"]:
            return False, "Game did not end with an answer submission"
            
        # 检查答案是否正确
        success = last_turn["feedback"] == "Correct"
        
        # 生成详细信息
        detail = (f"Final answer: positions {last_turn['result']}")
        
        return success, detail


class CircleQueryEvaluator(GameEvaluator):
    def evaluate_game(self, question: Dict, turns: List[Dict]) -> Tuple[bool, str]:
        """Check if the game was completed successfully within constraints"""
        if not turns:
            return False, "No turns played"
        
        # 检查查询次数
        query_count = sum(1 for turn in turns 
                         if len(turn["result"].split()) == 2)  # 查询结果有两个数
        
        # 检查最后一步是否是答案提交
        last_turn = turns[-1]
        if "Correct" not in last_turn["feedback"] and "Incorrect" not in last_turn["feedback"]:
            return False, "Game did not end with an answer submission"
        
        # 检查最后提交的答案是否正确
        success = last_turn["feedback"] == "Correct"
        
        # 获取提交的答案参数
        xc, yc, rc = map(int, last_turn["result"].split())
        
        # 验证答案参数是否在范围内
        max_coord = question["scale"]
        if max(abs(xc), abs(yc), abs(rc)) > max_coord:
            return False, f"Parameters exceed allowed range: ±{max_coord}"
        
        # 生成详细信息
        detail = (f"Final answer: center=({xc},{yc}), radius={rc}, "
                 f"Queries used: {query_count}")
        
        return success, detail

class TrainPursuitEvaluator(GameEvaluator):
    def evaluate_game(self, question: Dict, turns: List[Dict]) -> Tuple[bool, str]:
        """Check if the game was completed successfully"""
        if not turns:
            return False, "No turns played"
        
        # 检查最后一步是否是答案提交
        last_turn = turns[-1]
        if "Answer:" not in last_turn["result"]:
            return False, "Game did not end with an answer submission"
            
        # 计算查询次数和答案尝试次数
        query_count = sum(1 for turn in turns if "Query:" in turn["result"])
        answer_count = sum(1 for turn in turns if "Answer:" in turn["result"])
        
        # 检查最后提交的答案是否正确
        success = last_turn["feedback"] == "Correct"
        
        # 生成详细信息
        detail = (f"Queries used: {query_count}, "
                 f"Answer attempts: {answer_count}, "
                 f"Final answer: {last_turn['result'].split(': ')[1]}")
        
        return success, detail

class MimicHuntEvaluator(GameEvaluator):
    def evaluate_game(self, question: Dict, turns: List[Dict]) -> Tuple[bool, str]:
        """Check if the game was completed successfully"""
        if not turns:
            return False, "No turns played"
        
        # 检查最后一步是否是答案提交
        last_turn = turns[-1]
        if "Answer:" not in last_turn["result"]:
            return False, "Game did not end with an answer submission"
            
        # 统计移除操作的次数和答案提交次数
        removal_count = sum(1 for turn in turns if "Remove:" in turn["result"])
        answer_count = sum(1 for turn in turns if "Answer:" in turn["result"])
        
        # 检查最后提交的答案是否正确
        success = last_turn["feedback"] == "Correct"
        
        # 生成详细信息
        detail = (f"Removals: {removal_count}, "
                 f"Answer attempts: {answer_count}, "
                 f"Final position guess: {last_turn['result'].split(': ')[1]}")
        
        return success, detail

class ZeroFindingEvaluator(GameEvaluator):
    def evaluate_game(self, question: Dict, turns: List[Dict]) -> Tuple[bool, str]:
        """Check if the game was completed successfully"""
        if not turns:
            return False, "No turns played"
        
        # 检查最后一步是否是最终答案
        last_turn = turns[-1]            
        # 统计查询和答案
        query_count = sum(1 for turn in turns if "Query:" in turn["result"])
        temp_answer_count = sum(1 for turn in turns if "Answer:" in turn["result"])
        
        # 检查最后提交的答案是否正确
        success = last_turn["feedback"] == "Correct"
        
        # 生成详细信息
        detail = (f"Queries used: {query_count}, "
                 f"Non-target zeros found: {temp_answer_count}")
        
        return success, detail

class PermutationDiscoveryEvaluator(GameEvaluator):
    def evaluate_game(self, question: Dict, turns: List[Dict]) -> Tuple[bool, str]:
        """Check if the game was completed successfully"""
        if not turns:
            return False, "No turns played"
        
        # 检查最后一步是否是答案提交
        last_turn = turns[-1]
        if "Answer:" not in last_turn["result"]:
            return False, "Game did not end with an answer submission"
            
        # 统计查询次数
        query_count = sum(1 for turn in turns if "Query:" in turn["result"])
        
        # 检查最后提交的答案是否正确
        success = last_turn["feedback"] == "Correct"
        
        # 获取提交的排列
        try:
            submitted_perm = list(map(int, last_turn["result"].split(": ")[1].split()))
            # 生成详细信息
            detail = (f"Queries used: {query_count}, "
                     f"Final permutation: {' '.join(map(str, submitted_perm))}")
        except:
            detail = f"Queries used: {query_count}, Invalid final submission"
        
        return success, detail

class MahjongDetectiveEvaluator(GameEvaluator):
    def evaluate_game(self, question: Dict, turns: List[Dict]) -> Tuple[bool, str]:
        """Check if the game was completed successfully"""
        if not turns:
            return False, "No turns played"
        
        # 检查最后一步是否是最终答案
        last_turn = turns[-1]
            
        # 统计查询和答案
        query_count = sum(1 for turn in turns if "Add:" in turn["result"])
        temp_answer_count = sum(1 for turn in turns if "Answer:" in turn["result"])
        
        # 检查最后提交的答案是否正确
        success = last_turn["feedback"] == "Correct"
        
        # 生成详细信息
        detail = (f"Queries used: {query_count}, "
                    f"Answer found: {temp_answer_count}")
        
        return success, detail

class HiddenNumberEvaluator(GameEvaluator):
    def evaluate_game(self, question: Dict, turns: List[Dict]) -> Tuple[bool, str]:
        """Check if the game was completed successfully"""
        if not turns:
            return False, "No turns played"
        
        # 检查最后一步是否是最终答案
        last_turn = turns[-1]
        # 统计查询和答案
        query_count = sum(1 for turn in turns if "Query:" in turn["result"])
        temp_answer_count = sum(1 for turn in turns if "Answer:" in turn["result"])
        
        # 检查最后提交的答案是否正确
        success = last_turn["feedback"] == "Correct"
        
        # 生成详细信息
        detail = (f"Queries used: {query_count}, "
                    f"Answer found: {temp_answer_count}")
        
        return success, detail

class RotaryLockEvaluator(GameEvaluator):
    def evaluate_game(self, question: Dict, turns: List[Dict]) -> Tuple[bool, str]:
        """Check if the game was completed successfully"""
        if not turns:
            return False, "No turns played"
        
        # 检查最后一步是否是最终答案
        last_turn = turns[-1]            
        # 统计查询和答案
        query_count = sum(1 for turn in turns if "Rotation:" in turn["result"])
        temp_answer_count = sum(1 for turn in turns if "Answer:" in turn["result"])
        
        # 检查最后提交的答案是否正确
        success = last_turn["feedback"] == "Correct"
        
        # 生成详细信息
        detail = (f"Queries used: {query_count}, "
                    f"Answer found: {temp_answer_count}")
        
        return success, detail

class AttendanceCheckEvaluator(GameEvaluator):
    def evaluate_game(self, question: Dict, turns: List[Dict]) -> Tuple[bool, str]:
        """检查是否成功找到缺席学生"""
        if not turns:
            return False, "No turns played"
        
        # 获取正确答案（缺席学生的编号）
        answer = question["answer"]
        absent_student = answer.index(0) + 1  # 转换为1-based编号
        
        # 找到最后一次答案提交
        final_answer = None
        for turn in reversed(turns):
            if turn["result"].startswith("Answer:"):
                final_answer = int(turn["result"].split(":")[1])
                break
        
        if final_answer is None:
            return False, "No answer submitted"
            
        # 检查答案是否正确
        success = (final_answer == absent_student)
        detail = (f"Absent student: {absent_student}, "
                 f"Final guess: {final_answer}, "
                 f"Result: {'Correct' if success else 'Incorrect'}")
        
        return success, detail

class KnightBattleEvaluator(GameEvaluator):
    def evaluate_game(self, question: Dict, turns: List[Dict]) -> Tuple[bool, str]:
        """评估KnightBattle游戏是否获胜"""
        if not turns:
            return False, "No turns played"
            
        try:
            # 获取初始设置
            board_size = question["scale"]
            white_pos = question["answer"]["white_start"]
            black_pos = question["answer"]["black_start"]
            white_target = question["answer"]["white_target"]
            black_target = question["answer"]["black_target"]
            
            # 跟踪移动序列和胜负
            move_sequence = []
            won_by_capture = False
            won_by_target = False
            invalid_move = False
            current_turn = 0
            
            # 解析所有回合的移动
            for turn in turns:
                current_turn += 1
                
                # 解析白方移动
                move_match = re.search(r'Move:\s*(\d+),(\d+)', turn["result"])
                if not move_match:
                    invalid_move = True
                    break
                    
                white_x = int(move_match.group(1))
                white_y = int(move_match.group(2))
                
                # 验证移动的合法性
                if not self._is_valid_move(white_pos, [white_x, white_y], board_size):
                    invalid_move = True
                    break
                
                # 记录移动
                move_sequence.append(f"Turn {current_turn} - White: ({white_x},{white_y})")
                white_pos = [white_x, white_y]
                
                # 检查是否赢得游戏
                if white_pos == black_pos:  # 吃掉黑骑士
                    won_by_capture = True
                    break
                elif (white_pos == white_target and  # 到达目标点且安全
                      not self._is_under_attack(white_pos, black_pos, board_size)):
                    won_by_target = True
                    break
                
                # 解析黑方移动
                if "Invalid" in turn.get("feedback", ""):  # 检查是否有Invalid反馈
                    return False, f"Lost: Invalid move at turn {current_turn}\n" + "\n".join(move_sequence)
                
                if turn["feedback"] != "White wins!":  # 如果游戏还没结束
                    try:
                        black_x, black_y = map(int, turn["feedback"].split())
                        black_pos = [black_x, black_y]
                        move_sequence.append(f"Turn {current_turn} - Black: ({black_x},{black_y})")
                        
                        # 检查黑方是否获胜
                        if black_pos == white_pos:  # 黑方吃掉白骑士
                            return False, f"Lost: Captured by Black Knight at turn {current_turn}\n" + "\n".join(move_sequence)
                        elif (black_pos == black_target and  # 黑方到达目标且安全
                              not self._is_under_attack(black_pos, white_pos, board_size)):
                            return False, f"Lost: Black Knight reached target safely at turn {current_turn}\n" + "\n".join(move_sequence)
                    except:
                        pass  # 游戏可能已经结束
            
            # 构造详细信息
            detail = "Game Result:\n"
            if invalid_move:
                return False, f"Lost: Invalid move at turn {current_turn}\n" + "\n".join(move_sequence)
            elif won_by_capture:
                detail += f"Won by capturing Black Knight at turn {current_turn}\n"
            elif won_by_target:
                detail += f"Won by reaching target safely at turn {current_turn}\n"
            else:
                return False, "Game incomplete or lost\n" + "\n".join(move_sequence)
            
                            # 检查是否达到350回合
            if current_turn > 14:
                return False, "Draw: Exceeded 15 turns\n" + "\n".join(move_sequence)

            detail += "Move sequence:\n" + "\n".join(move_sequence)
            return True, detail
            
        except Exception as e:
            return False, f"Error evaluating game: {str(e)}"
            
    def _is_valid_move(self, start: List[int], end: List[int], board_size: int) -> bool:
        """检查骑士移动是否合法"""
        dx = abs(end[0] - start[0])
        dy = abs(end[1] - start[1])
        if not (1 <= end[0] <= board_size and 1 <= end[1] <= board_size):
            return False
        return (dx == 1 and dy == 2) or (dx == 2 and dy == 1)
        
    def _is_under_attack(self, pos: List[int], attacker_pos: List[int], board_size: int) -> bool:
        """检查位置是否被攻击"""
        dx = abs(pos[0] - attacker_pos[0])
        dy = abs(pos[1] - attacker_pos[1])
        return (dx == 1 and dy == 2) or (dx == 2 and dy == 1)

class PaperNumberEvaluator(GameEvaluator):
    def evaluate_game(self, question: Dict, turns: List[Dict]) -> Tuple[bool, str]:
        """评估PaperNumber游戏是否获胜"""
        if not turns:
            return False, "No turns played"
            
        try:
            # 获取初始设置
            num_papers = question["scale"]
            max_turns = question["turns"]
            papers = [None] * num_papers
            current_number = question["initial_value"]
            
            # 跟踪移动序列和游戏状态
            move_sequence = []
            current_turn = 0
            invalid_move = False
            
            # 解析所有回合的移动
            for turn in turns:
                current_turn += 1
                
                # 解析玩家选择
                position_match = re.search(r'Position:\s*(\d+)', turn["result"])
                if not position_match:
                    invalid_move = True
                    break
                    
                position = int(position_match.group(1))
                
                # 验证位置的合法性
                if not 1 <= position <= num_papers:
                    invalid_move = True
                    break
                
                # 更新纸张状态
                papers[position-1] = current_number
                move_sequence.append(f"Turn {current_turn} - Placed {current_number} at position {position}")
                
                # 检查是否赢得游戏
                if self._is_winning_state(papers):
                    return True, f"Won at turn {current_turn}!\nFinal sequence: {papers}\nMove sequence:\n" + "\n".join(move_sequence)
                
                # 获取下一个数字（如果游戏还没结束）
                if "Invalid" in turn.get("feedback", ""):
                    return False, f"Lost: Invalid move at turn {current_turn}\n" + "\n".join(move_sequence)
                    
                try:
                    if turn["feedback"] not in ["Win", 
                                              "Game Over - Max turns reached"]:
                        current_number = int(turn["feedback"])
                except:
                    pass  # 游戏可能已经结束
            
            # 检查游戏结果
            if invalid_move:
                return False, f"Lost: Invalid move at turn {current_turn}\n" + "\n".join(move_sequence)
            elif current_turn >= max_turns:
                return False, f"Lost: Failed to create non-decreasing sequence in {max_turns} turns\n" + \
                            f"Final sequence: {papers}\n" + "\n".join(move_sequence)
            
            return False, "Game incomplete\n" + "\n".join(move_sequence)
            
        except Exception as e:
            return False, f"Error evaluating game: {str(e)}"
            
    def _is_winning_state(self, papers: List[int]) -> bool:
        """检查当前状态是否满足获胜条件"""
        # 检查是否所有纸张都有数字
        if None in papers:
            return False
            
        # 检查是否非递减序列
        for i in range(1, len(papers)):
            if papers[i] < papers[i-1]:
                return False
                
        return True

class GridColoringEvaluator(GameEvaluator):
    def evaluate_game(self, question: Dict, turns: List[Dict]) -> Tuple[bool, str]:
        """评估GridColoring游戏是否获胜"""
        if not turns:
            return False, "No turns played"
            
        try:
            # 记录移动序列
            move_sequence = []
            current_turn = 0
            
            # 跟踪每个回合的移动
            for turn in turns:
                current_turn += 1
                
                # 检查是否是选择格子的移动
                choice_match = re.search(r'My Choice:\s*(\d+)\s+(\d+)', turn["result"])
                if choice_match:
                    x = int(choice_match.group(1))
                    y = int(choice_match.group(2))
                    try:
                        split_feedback = turn["feedback"]
                        move_sequence.append(f"Turn {current_turn} - {split_feedback}")
                    except:
                        if "Invalid" in turn["feedback"]:
                            return False, f"Lost: Invalid move at turn {current_turn}\n" + "\n".join(move_sequence)
                    continue
                
                # 检查是否是最终答案
                answer_match = re.search(r'My Answer:\s*(\d+)\s+(\d+)\s+(\d+)\s+(\d+)', turn["result"])
                if answer_match:
                    x1, x2, y1, y2 = map(int, [answer_match.group(i) for i in range(1, 5)])
                    move_sequence.append(f"Turn {current_turn} - Final Answer: ({x1},{y1}), ({x1},{y2}), ({x2},{y1}), ({x2},{y2})")
                    
                    # 简单检查最后的feedback是否是Win
                    if turn["feedback"] == "Win":
                        return True, "Win!\n" + "\n".join(move_sequence)
                    else:
                        return False, f"Lost: Invalid rectangle\n" + "\n".join(move_sequence)

            return False, "Game incomplete\n" + "\n".join(move_sequence)
            
        except Exception as e:
            return False, f"Error evaluating game: {str(e)}"

class GridGameEvaluator(GameEvaluator):
    def evaluate_game(self, question: Dict, turns: List[Dict]) -> Tuple[bool, str]:
        """评估GridGame游戏是否获胜"""
        if not turns:
            return False, "No turns played"
            
        try:
            # 获取初始设置
            n, m = question["scale"]
            initial_grid = question["initial_grid"]
            selected = set()  # 已选择的格子
            player_sum = 0  # LLM(先手)的数字和
            my_sum = 0  # 后手的数字和
            move_sequence = []
            current_turn = 0
            
            # 跟踪每个回合的移动
            for turn in turns:
                current_turn += 1
                
                # 解析LLM的选择
                match = re.search(r'My Choice:\s*(\d+)\s+(\d+)', turn["result"])
                if not match:
                    return False, f"Lost: Invalid format at turn {current_turn}\n" + "\n".join(move_sequence)

                # 获取LLM的选择
                x = int(match.group(1))
                y = int(match.group(2))
                llm_choice = f"({x}, {y})"
                
                # 验证格子是否合法
                if not (1 <= x <= n and 1 <= y <= m):
                    return False, f"Lost: Position out of bounds at turn {current_turn}\n" + "\n".join(move_sequence)
                
                if llm_choice in selected:
                    return False, f"Lost: Cell already selected at turn {current_turn}\n" + "\n".join(move_sequence)
                
                # 验证是否相邻（第一次选择除外）
                if selected and not self._is_adjacent(llm_choice, selected, n, m):
                    return False, f"Lost: Cell must be adjacent to previous selection at turn {current_turn}\n" + "\n".join(move_sequence)
                
                # 记录LLM的选择
                selected.add(llm_choice)
                player_sum += initial_grid[llm_choice]
                move_sequence.append(f"Turn {current_turn} - LLM chooses {llm_choice}, value: {initial_grid[llm_choice]}")
                
                # 获取我的响应（在feedback中）
                if "Invalid" in turn["feedback"]:
                    return False, f"Lost: Invalid move at turn {current_turn}\n" + "\n".join(move_sequence)

                # 解析反馈中的我的选择
                my_match = re.search(r'My Choice:\s*(\d+)\s+(\d+)', turn["feedback"])
                if my_match:
                    my_x, my_y = int(my_match.group(1)), int(my_match.group(2))
                    my_choice = f"({my_x}, {my_y})"                        
                    selected.add(my_choice)
                    my_sum += initial_grid[my_choice]
                    move_sequence.append(f"Turn {current_turn} - I choose {my_choice}, value: {initial_grid[my_choice]}")

            if player_sum < my_sum:
                return True, f"Won! LLM sum ({player_sum}) < I sum ({my_sum})\n" + "\n".join(move_sequence)
            else:
                return False, f"Lost! LLM sum ({player_sum}) >= I sum ({my_sum})\n" + "\n".join(move_sequence)
            
            return False, "Game incomplete\n" + "\n".join(move_sequence)
            
        except Exception as e:
            return False, f"Error evaluating game: {str(e)}"
            
    def _is_adjacent(self, cell: str, selected: set, n: int, m: int) -> bool:
        """检查格子是否与任何已选格子相邻"""
        x, y = map(int, cell.strip("()").split(","))
        # 检查四个方向
        for dx, dy in [(0,1), (0,-1), (1,0), (-1,0)]:
            new_x, new_y = x + dx, y + dy
            if 1 <= new_x <= n and 1 <= new_y <= m:
                adj = f"({new_x}, {new_y})"
                if adj in selected:
                    return True
        return False

class DecreasingGameEvaluator(GameEvaluator):
    def evaluate_game(self, question: Dict, turns: List[Dict]) -> Tuple[bool, str]:
        """评估Decreasing Game游戏是否获胜"""
        if not turns:
            return False, "No turns played"
            
        try:
            # 记录移动序列，从系统的第一步选择开始
            move_sequence = [f"Turn 0 - System chose: {question['first_choice']}"]
            current_turn = 0
            
            # 跟踪每个回合的移动
            for turn in turns:
                current_turn += 1
                
                # 解析玩家的选择
                choice_match = re.search(r'My Choice:\s*(\d+)', turn["result"])
                if not choice_match:
                    return False, f"Lost: Invalid format at turn {current_turn}\n" + "\n".join(move_sequence)
                
                player_choice = int(choice_match.group(1))
                move_sequence.append(f"Turn {current_turn} - Player chose: {player_choice}")
                
                # 处理反馈
                if "Invalid" in turn["feedback"]:
                    return False, f"Lost: Invalid move at turn {current_turn}\n" + "\n".join(move_sequence)
                elif "win" in turn["feedback"].lower():
                    return True, "Win!\n" + "\n".join(move_sequence)
                elif "lose" in turn["feedback"].lower():
                    return False, f"Lost: Game over\n" + "\n".join(move_sequence)
                else:
                    # 记录系统的选择
                    system_match = re.search(r'My Choice:\s*(\d+)', turn["feedback"])
                    if system_match:
                        system_choice = int(system_match.group(1))
                        move_sequence.append(f"Turn {current_turn} - System chose: {system_choice}")
            
            return False, "Game incomplete\n" + "\n".join(move_sequence)
            
        except Exception as e:
            return False, f"Error evaluating game: {str(e)}"

class AssiutChessEvaluator(GameEvaluator):
    def evaluate_game(self, question: Dict, turns: List[Dict]) -> Tuple[bool, str]:
        """评估AssiutChess游戏是否获胜"""
        if not turns:
            return False, "No turns played"
            
        try:
            # 记录移动序列
            move_sequence = []
            current_turn = 0
            
            # 跟踪每个回合的移动
            for turn in turns:
                current_turn += 1
                
                # 检查玩家的选择
                choice_match = re.search(r'My Choice:\s*(\d+)\s+(\d+)', turn["result"])
                if not choice_match:
                    return False, f"Lost: Invalid format at turn {current_turn}\n" + "\n".join(move_sequence)
                
                x = int(choice_match.group(1))
                y = int(choice_match.group(2))
                
                # 记录移动
                move_sequence.append(f"Turn {current_turn} - Queen moved to: ({x},{y})")
                
                # 处理反馈
                if "Invalid" in turn["feedback"]:
                    return False, f"Lost: Invalid move at turn {current_turn}\n" + "\n".join(move_sequence)
                
                # 记录国王的移动方向
                if turn["feedback"] != "Done":
                    move_sequence.append(f"Turn {current_turn} - King moved: {turn['feedback']}")
                
                # 检查是否获胜
                if turn["feedback"] == "Done":
                    return True, "Win!\n" + "\n".join(move_sequence)
                    
            return False, "Game incomplete\n" + "\n".join(move_sequence)
            
        except Exception as e:
            return False, f"Error evaluating game: {str(e)}"

class ZigzagGraphEvaluator(GameEvaluator):
    def evaluate_game(self, question: Dict, turns: List[Dict]) -> Tuple[bool, str]:
        """评估ZigzagGraph游戏是否获胜"""
        if not turns:
            return False, "No turns played"
            
        try:
            # 记录移动序列
            move_sequence = []
            current_turn = 0
                        
            # 跟踪每个回合的移动
            for turn in turns:
                current_turn += 1
                
                # 解析玩家的选择
                choice_match = re.search(r'My Choice:\s*(\d+)', turn["result"])
                if not choice_match:
                    return False, f"Lost: Invalid format at turn {current_turn}\n" + "\n".join(move_sequence)
                
                # 获取玩家选择的节点
                node = int(choice_match.group(1))                
                move_sequence.append(f"Turn {current_turn} - Player chose: {node}")
                
                # 处理系统的移动（如果有）
                if "feedback" in turn:
                    if "win" in turn["feedback"].lower():
                        return True, "Win!\n" + "\n".join(move_sequence)
                    elif "invalid" in turn["feedback"].lower():
                        return False, f"Lost: {turn['feedback']}\n" + "\n".join(move_sequence)
                    else:
                        # 解析系统的选择
                        system_match = re.search(r'My Choice:\s*(\d+)', turn["feedback"])
                        if system_match:
                            system_node = int(system_match.group(1))
                            move_sequence.append(f"Turn {current_turn} - System chose: {system_node}")
                
            return False, "Game incomplete\n" + "\n".join(move_sequence)
            
        except Exception as e:
            return False, f"Error evaluating game: {str(e)}"

class BeeChaseEvaluator(GameEvaluator):
    def evaluate_game(self, question: Dict, turns: List[Dict]) -> Tuple[bool, str]:
        """评估BeeChase游戏是否获胜"""
        if not turns:
            return False, "No turns played"
            
        try:
            # 记录移动序列
            move_sequence = []
            current_turn = 0
            
            # 跟踪每个回合的移动
            for turn in turns:
                current_turn += 1
                
                # 解析玩家的选择
                choice_match = re.search(r'My Choice:\s*(\d+)\s+(\d+)\s+(\d+)', turn["result"])
                if not choice_match:
                    return False, f"Lost: Invalid format at turn {current_turn}\n" + "\n".join(move_sequence)
                
                # 获取蜜蜂位置
                bee_pos = [int(choice_match.group(i)) for i in range(1, 4)]
                move_sequence.append(f"Turn {current_turn} - Bees at: {bee_pos}")
                
                # 处理反馈
                if "invalid" in turn["feedback"].lower():
                    return False, f"Lost: Invalid move at turn {current_turn}\n" + "\n".join(move_sequence)
                    
                # 检查是否获胜
                if "win" in turn["feedback"].lower():
                    return True, "Win!\n" + "\n".join(move_sequence)
                    
                # 记录Nastya的位置
                if turn["feedback"].isdigit():
                    nastya_pos = int(turn["feedback"])
                    move_sequence.append(f"Turn {current_turn} - Nastya at: {nastya_pos}")
                
            return False, "Game incomplete\n" + "\n".join(move_sequence)
            
        except Exception as e:
            return False, f"Error evaluating game: {str(e)}"

class PizzaSliceEvaluator(GameEvaluator):
    def evaluate_game(self, question: Dict, turns: List[Dict]) -> Tuple[bool, str]:
        """评估PizzaSlice游戏是否获胜"""
        if not turns:
            return False, "No turns played"
            
        try:
            # 记录移动序列和面积
            move_sequence = []
            player_area = 0
            opponent_area = 0
            current_turn = 0
            remaining = list(range(1, question["scale"] + 1))
            points = question["points"]
            
            # 跟踪每个回合的移动
            for turn in turns:
                current_turn += 1
                
                # 解析玩家的选择
                choice_match = re.search(r'My Choice:\s*(\d+)', turn["result"])
                if not choice_match:
                    return False, f"Lost: Invalid format at turn {current_turn}\n" + "\n".join(move_sequence)
                
                # 获取玩家选择的顶点
                vertex = int(choice_match.group(1))
                if vertex not in remaining:
                    return False, f"Lost: Invalid vertex choice at turn {current_turn}\n" + "\n".join(move_sequence)
                    
                # 记录移动
                move_sequence.append(f"Turn {current_turn} - Player chose vertex {vertex}")
                remaining.remove(vertex)
                
                # 处理系统反馈
                if "Invalid" in turn["feedback"]:
                    return False, f"Lost: Invalid move at turn {current_turn}\n" + "\n".join(move_sequence)
                elif "win" in turn["feedback"].lower():
                    return True, "Win!\n" + "\n".join(move_sequence)
                elif "lose" in turn["feedback"].lower():
                    return False, f"Lost: Ate more area\n" + "\n".join(move_sequence)
                else:
                    # 解析系统的选择
                    try:
                        opponent_vertex = int(turn["feedback"])
                        if opponent_vertex not in remaining:
                            return False, f"Lost: Invalid system move at turn {current_turn}\n" + "\n".join(move_sequence)
                        remaining.remove(opponent_vertex)
                        move_sequence.append(f"Turn {current_turn} - System chose vertex {opponent_vertex}")
                    except ValueError:
                        pass
            
            return False, "Game incomplete\n" + "\n".join(move_sequence)
            
        except Exception as e:
            return False, f"Error evaluating game: {str(e)}"

class XORBreakEvaluator(GameEvaluator):
    def evaluate_game(self, question: Dict, turns: List[Dict]) -> Tuple[bool, str]:
        """评估XORBreak游戏是否获胜"""
        if not turns:
            return False, "No turns played"
            
        try:
            # 记录移动序列
            move_sequence = []
            current_turn = 0
            is_first_turn = True
            
            # 跟踪每个回合的移动
            for turn in turns:
                current_turn += 1
                
                if is_first_turn:
                    # 第一回合格式: Breaking into: p1 p2
                    match = re.search(r'Breaking into:\s*(\d+)\s+(\d+)', turn["result"])
                    if not match:
                        return False, f"Lost: Invalid format at turn {current_turn}\n" + "\n".join(move_sequence)
                        
                    p1, p2 = map(int, [match.group(i) for i in range(1, 3)])
                    move_sequence.append(f"Turn {current_turn} - Breaking {question['initial_number']} into: {p1} {p2}")
                    is_first_turn = False
                    
                else:
                    # 后续回合格式: Choosing: p Breaking into: p1 p2
                    match = re.search(r'Choosing:\s*(\d+)\s+Breaking into:\s*(\d+)\s+(\d+)', turn["result"])
                    if not match:
                        return False, f"Lost: Invalid format at turn {current_turn}\n" + "\n".join(move_sequence)
                        
                    p, p1, p2 = map(int, [match.group(i) for i in range(1, 4)])
                    move_sequence.append(f"Turn {current_turn} - Choosing {p} and breaking into: {p1} {p2}")
                
                # 检查反馈
                if "Invalid" in turn["feedback"]:
                    return False, f"Lost: Invalid move at turn {current_turn}\n" + "\n".join(move_sequence)
                elif "win" in turn["feedback"].lower():
                    return True, "Win!\n" + "\n".join(move_sequence)
                else:
                    # 记录系统的选择
                    move_sequence.append(f"Turn {current_turn} - {turn['feedback']}")
                
            return False, "Game incomplete\n" + "\n".join(move_sequence)
            
        except Exception as e:
            return False, f"Error evaluating game: {str(e)}"

class TreasureHuntEvaluator(GameEvaluator):
    def evaluate_game(self, question: Dict, turns: List[Dict]) -> Tuple[bool, str]:
        """评估游戏是否成功完成"""
        if not turns:
            return False, "No turns played"
            
        try:
            # 记录游戏过程
            move_sequence = []
            current_turn = 0
            
            # 跟踪每个回合
            for turn in turns:
                current_turn += 1
                
                # 记录玩家的选择
                choice_match = re.search(r'My Choice:\s*(\d+)', turn["result"])
                if choice_match:
                    choice = int(choice_match.group(1))
                    move_sequence.append(f"Turn {current_turn} - Selected choice {choice}")
                
                # 检查是否获胜
                if "win" in turn["feedback"].lower():
                    return True, "Win!\n" + "\n".join(move_sequence)
                    
                # 检查是否失败
                if "invalid" in turn["feedback"].lower():
                    return False, f"Lost: Invalid move\n" + "\n".join(move_sequence)
            
            return False, "Game incomplete\n" + "\n".join(move_sequence)
            
        except Exception as e:
            return False, f"Error evaluating game: {str(e)}"

class PalindromeConstructionEvaluator(GameEvaluator):
    def evaluate_game(self, question: Dict, turns: List[Dict]) -> Tuple[bool, str]:
        """Check if the palindrome construction game was completed successfully"""
        if not turns:
            return False, "No turns played"
        
        # 检查是否完成了所有回合
        expected_turns = question["turns"] 
        if len(turns) < expected_turns:
            return False, f"Game incomplete: {len(turns)}/{expected_turns} turns played"
            
        # 检查最后一轮是否获胜
        last_turn = turns[-1]
        success = last_turn["feedback"] == "Win"
        
        # 生成简单的详细信息
        detail = f"Turns played: {len(turns)}/{expected_turns}"
        
        return success, detail

class CactusSearchEvaluator(GameEvaluator):
    def evaluate_game(self, question: Dict, turns: List[Dict]) -> Tuple[bool, str]:
        """Check if the cactus search game was completed successfully"""
        if not turns:
            return False, "No turns played"
        
        # 检查最后一步是否找到目标
        last_turn = turns[-1]
        if "Guess:" not in last_turn["result"]:
            return False, "Game did not end with a guess"
            
        # 计算猜测次数
        guess_count = sum(1 for turn in turns if "Guess:" in turn["result"])
        
        # 检查是否成功找到目标
        success = last_turn["feedback"] == "Win"
        
        # 生成详细信息
        detail = (f"Guesses made: {guess_count}, "
                 f"Final guess: {last_turn['result'].split(': ')[1]}, "
                 f"Result: {'Success' if success else 'Failed'}")
        
        return success, detail

class VladikMazeEvaluator(GameEvaluator):
    def evaluate_game(self, question: Dict, turns: List[Dict]) -> Tuple[bool, str]:
        """Check if the maze game was completed successfully"""
        if not turns:
            return False, "No turns played"
        
        # 检查最后一步的状态
        last_turn = turns[-1]
        if "Move:" not in last_turn["result"]:
            return False, "Game did not end with a move"
            
        # 计算移动次数和是否遇到危险
        move_count = len(turns)
        hit_danger = any(turn["feedback"] == "-1 -1" for turn in turns)
        
        # 通过最后一步的位置判断是否成功到达终点
        success = "win" in last_turn["feedback"].lower()
        
        # 生成详细信息
        detail = (f"Moves made: {move_count}, "
                 f"Hit danger: {'Yes' if hit_danger else 'No'}, "
                 f"Final position: {last_turn['feedback']}")
        
        return success, detail

class FindBiggestEvaluator(GameEvaluator):
    def evaluate_game(self, question: Dict, turns: List[Dict]) -> Tuple[bool, str]:
        """Check if the game was completed successfully"""
        if not turns:
            return False, "No turns played"
        
        # 检查最后一步
        last_turn = turns[-1]
        if "COLLECT" not in last_turn["result"]:
            return False, "Game did not end with a collection attempt"
            
        # 计算移动次数和收集尝试次数
        move_count = sum(1 for turn in turns if "Choice:" in turn["result"] and "COLLECT" not in turn["result"])
        collect_count = sum(1 for turn in turns if "COLLECT" in turn["result"])
        treasure_found = sum(1 for turn in turns if "TREASURE" in turn["feedback"])
        
        # 检查是否胜利
        success = last_turn["feedback"] == "Win"
        
        # 生成详细信息
        detail = (f"Moves made: {move_count}, "
                 f"Treasures found: {treasure_found}, "
                 f"Collection attempts: {collect_count}")
        
        return success, detail

class SafepathFinderEvaluator(GameEvaluator):
    def evaluate_game(self, question: Dict, turns: List[Dict]) -> Tuple[bool, str]:
        """Check if the game was completed successfully"""
        if not turns:
            return False, "No turns played"
        
        # 检查最后一步的结果
        last_turn = turns[-1]
        
        # 计算统计信息
        move_count = len(turns)  # 总移动次数
        valid_moves = sum(1 for turn in turns if "DANGER_LEVEL" in turn["feedback"])  # 有效移动次数
        invalid_moves = sum(1 for turn in turns if "INVALID_MOVE" in turn["feedback"])  # 无效移动次数
        
        # 检查是否成功到达终点
        success = "Win" in last_turn["feedback"]
        
        # 记录最后位置（从最后一个有效移动获取）
        final_pos = "unknown"
        for turn in reversed(turns):
            if "Choice:" in turn["result"]:
                try:
                    x, y = map(int, turn["result"].split(": ")[1].split())
                    final_pos = f"({x},{y})"
                    break
                except:
                    pass
        
        # 生成详细信息
        detail = (f"Total moves: {move_count}, "
                 f"Valid moves: {valid_moves}, "
                 f"Invalid moves: {invalid_moves}, "
                 f"Final position: {final_pos}")
        
        return success, detail

class DarkMazeEvaluator(GameEvaluator):
    def evaluate_game(self, question: Dict, turns: List[Dict]) -> Tuple[bool, str]:
        """检查游戏是否成功完成"""
        if not turns:
            return False, "No turns played"
        
        # 检查最后一步
        last_turn = turns[-1]
        
        # 统计移动信息
        total_moves = len(turns)
        valid_moves = sum(1 for turn in turns if "MOVED" in turn["feedback"])
        blocked_moves = sum(1 for turn in turns if "BLOCKED" in turn["feedback"])
        invalid_moves = sum(1 for turn in turns if "INVALID" in turn["feedback"])
        
        # 检查是否到达终点
        success = "WIN" in last_turn["feedback"]
        
        # 获取最后移动方向
        final_move = last_turn["result"].split(": ")[1] if ": " in last_turn["result"] else "unknown"
        
        # 生成详细信息
        detail = (f"Total moves: {total_moves}, "
                 f"Valid moves: {valid_moves}, "
                 f"Blocked moves: {blocked_moves}, "
                 f"Invalid moves: {invalid_moves}, "
                 f"Final move: {final_move}")
        
        return success, detail

class MagneticFieldEvaluator(GameEvaluator):
    def evaluate_game(self, question: Dict, turns: List[Dict]) -> Tuple[bool, str]:
        """检查游戏是否成功完成"""
        if not turns:
            return False, "No turns played"
        
        # 检查最后一步
        last_turn = turns[-1]
        
        # 统计移动
        total_moves = len(turns)
        valid_moves = sum(1 for turn in turns 
                         if not ("invaild" in turn["feedback"].lower()))
        failed_moves = sum(1 for turn in turns if "invaild" in turn["feedback"].lower())
        
        # 检查是否胜利
        success = last_turn["feedback"] == "WIN"
        
        # 生成详细信息
        detail = (f"Total moves: {total_moves}, "
                 f"Valid moves: {valid_moves}, "
                 f"Failed moves: {failed_moves}")
        
        return success, detail

class ChemicalSynthesisEvaluator(GameEvaluator):
    def evaluate_game(self, question: Dict, turns: List[Dict]) -> Tuple[bool, str]:
        """检查游戏是否成功完成"""
        if not turns:
            return False, "No turns played"
        
        # 统计各种操作
        total_moves = len(turns)
        valid_moves = 0       # 有效的操作次数
        invalid_moves = 0     # 非法操作次数
        compounds_created = set()  # 创建过的化合物
        success = False      # 是否达到目标
        
        # 分析每一步
        for turn in turns:
            if "invalid" in turn["feedback"].lower():
                invalid_moves += 1
            else:
                valid_moves += 1
                # 提取创建的化合物
                if "Available:" in turn["feedback"]:
                    compounds = turn["feedback"].split("Available: ")[1].split()
                    compounds_created.update(compounds)
                    
            # 检查是否在任意步骤获胜
            if "win" in turn["feedback"].lower():
                success = True
        
        # 生成详细信息
        details = (f"Total moves: {total_moves}, "
                  f"Valid moves: {valid_moves}, "
                  f"Invalid moves: {invalid_moves}, "
                  f"Unique compounds created: {len(compounds_created)}")
                  
        return success, details
        


class ColorMagicEvaluator(GameEvaluator):
    def evaluate_game(self, question: Dict, turns: List[Dict]) -> Tuple[bool, str]:
        if not turns:
            return False, "No turns played"
        
        success = False
        detail = ""
        move_count = 0
        winning_turn = None

        # 遍历所有回合，寻找包含"win"的反馈
        for turn in turns:
            # 统计包含"Move:"的回合数作为操作次数
            if "Move:" in turn.get("result", ""):
                move_count += 1
            
            # 检查当前回合的反馈是否包含"win"
            if "win" in turn.get("feedback", "").lower():
                success = True
                winning_turn = turn
                break  # 一旦找到胜利回合，停止搜索

        if success and winning_turn:
            # 获取胜利回合的反馈信息的最后三行作为最终状态
            final_state = winning_turn["feedback"].split("\n")[-3:]
            detail = (f"Moves used: {move_count}, "
                      f"Final state:\n" + "\n".join(final_state))
        else:
            # 如果没有任何回合达到胜利，使用最后一个回合的反馈作为最终状态
            last_turn = turns[-1]
            # 统计所有回合中包含"Move:"的回合数作为操作次数
            move_count = sum(1 for turn in turns if "Move:" in turn.get("result", ""))
            final_state = last_turn["feedback"].split("\n")[-3:]
            detail = (f"Moves used: {move_count}, "
                      f"Final state:\n" + "\n".join(final_state))
        
        return success, detail

class RainbowCandyEvaluator(GameEvaluator):
    def evaluate_game(self, question: Dict, turns: List[Dict]) -> Tuple[bool, str]:
        """Check if the game was completed successfully"""
        if not turns:
            return False, "No turns played"
        
        # 检查最后一步的结果
        last_turn = turns[-1]
        success = False
        # 计算总移动次数
        move_count = len(turns)
        
        # 收集颜色变化序列
        color_sequence = []
        for turn in turns:
            if "invalid"  not in turn["feedback"].lower():
                color_sequence.append(turn["feedback"])
            if "win" in turn["feedback"].lower():
                success = True        
        # 生成详细信息
        if success:
            result = "Success"
        elif "invalid" in last_turn["feedback"].lower():
            result = "Invalid move"
        else:
            result = f"Wrong color: {last_turn['feedback']}"
            
        detail = (f"Moves used: {move_count}, "
                 f"Color sequence: {' -> '.join(color_sequence)}, "
                 f"Result: {result}")
        
        return success, detail

def get_evaluator(game_type: str) -> GameEvaluator:
    """Factory function to create appropriate evaluator"""
    evaluators = {
        "Wordle": WordleEvaluator,
        "FindTheImpostors": ImpostorsEvaluator,
        "RPD": RPDEvaluator,
        "BitGuessing":  BitGuessingEvaluator,
        "GeoGame": GeoGameEvaluator,
        "MinMax": MinMaxEvaluator,
        "BitQuery": BitQueryEvaluator,
        "LegendaryTree": LegendaryTreeEvaluator,
        "GuessMax":GuessMaxEvaluator,
        "ListQuery":LinkedListEvaluator,
        "BitCompare":BitCompareEvaluator,
        "MedianQuery":MedianQueryEvaluator,
        "CircleFinding":CircleQueryEvaluator,
        "TrainPursuit":TrainPursuitEvaluator,
        "MimicHunt":MimicHuntEvaluator,
        "ZeroFinding":ZeroFindingEvaluator,
        "PermutationDiscovery":PermutationDiscoveryEvaluator,
        "MahjongDetective":MahjongDetectiveEvaluator,
        "FindHidden":HiddenNumberEvaluator,
        "RotaryLock":RotaryLockEvaluator,
        "AttendanceCheck":AttendanceCheckEvaluator,
        "KnightBattle":KnightBattleEvaluator,
        "PaperNumber":PaperNumberEvaluator,
        "GridColoring":GridColoringEvaluator,
        "GridGame":GridGameEvaluator,
        "DecreasingGame":DecreasingGameEvaluator,
        "AssiutChess":AssiutChessEvaluator,
        "ZigzagGraph":ZigzagGraphEvaluator,
        "BeeChase":BeeChaseEvaluator,
        "PizzaSlice":PizzaSliceEvaluator,
        "XORBreaking":XORBreakEvaluator,
        "TreasureHunt":TreasureHuntEvaluator,
        "PalindromeConstruction5":PalindromeConstructionEvaluator,
        "PalindromeConstruction10":PalindromeConstructionEvaluator,
        "PalindromeConstruction15":PalindromeConstructionEvaluator,
        "CactusSearch":CactusSearchEvaluator,
        "VladikMaze":VladikMazeEvaluator,
        "FindBiggest":FindBiggestEvaluator,
        "SafepathFinder":SafepathFinderEvaluator,
        "DarkMaze":DarkMazeEvaluator,
        "MagneticField":MagneticFieldEvaluator,
        "ChemicalSynthesis":ChemicalSynthesisEvaluator,
        "ColorMagic":ColorMagicEvaluator,
        "RainbowCandy":RainbowCandyEvaluator
    }
    
    if game_type not in evaluators:
        raise ValueError(f"Unknown game type: {game_type}")
    
    return evaluators[game_type]()
def evaluate_answers(
    question_file: str,
    answer_file: str,
    eval_file: str,
    game_type: str
):
    """Evaluate answers and generate statistics"""
    # Load questions and answers
    with open(question_file) as f:
        questions = {q["question_id"]: q for q in [json.loads(l) for l in f]}
    
    with open(answer_file) as f:
        answers = {int(a["question_id"]): a for a in [json.loads(l) for l in f]}
    
    # Get appropriate evaluator
    evaluator = get_evaluator(game_type)
    
    # Evaluate each game
    results = []
    success_count = 0
    total_count = 0
    
    for qid, question in questions.items():
        if qid not in answers:
            result = {
                "question_id": qid,
                "success": False,
                "detail": "No answer found",
                "num_turns": 0
            }
        else:
            success, detail = evaluator.evaluate_game(
                question, 
                answers[qid]["turns"]
            )
            result = {
                "question_id": qid,
                "success": success,
                "detail": detail,
                "num_turns": len(answers[qid]["turns"])
            }
            
            if success:
                success_count += 1
            total_count += 1
            
        results.append(result)
    
    # Calculate statistics
    accuracy = success_count / total_count if total_count > 0 else 0
    avg_turns = sum(r["num_turns"] for r in results) / len(results) if results else 0
    
    # Save evaluation results
    eval_result = {
        "game_type": game_type,
        "total_questions": total_count,
        "successful_games": success_count,
        "accuracy": accuracy,
        "average_turns": avg_turns,
        "detailed_results": results
    }
    
    with open(eval_file, 'w') as f:
        json.dump(eval_result, f, indent=2)
    
    print(f"\nEvaluation Results for {game_type}:")
    print(f"Total Questions: {total_count}")
    print(f"Successful Games: {success_count}")
    print(f"Accuracy: {accuracy:.2%}")
    print(f"Average Turns: {avg_turns:.2f}")
