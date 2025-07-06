import re
from abc import ABC, abstractmethod
from typing import Tuple, List, Dict, Optional
import random
from collections import defaultdict, deque
import math
from itertools import combinations
class GameHandler(ABC):
    @abstractmethod
    def parse_response(self, generated_text: str) -> Tuple[str, str]:
        """Parse response and return (result, feedback)"""
        pass
        
    @abstractmethod
    def is_complete(self, result: str) -> bool:
        """Check if the game is complete"""
        pass

class WordleHandler(GameHandler):
    def __init__(self, answer: str):
        self.answer = answer.upper()    
    def parse_response(self, generated_text: str) -> Tuple[str, str]:
        match = re.search(r'My Guess:\s*([A-Za-z]+)', generated_text)
        if not match:
            return "Invalid", "Your response must end with 'My Guess: [YOUR WORD]'"
            
        guess = match.group(1).upper()
        if len(guess) != len(self.answer):
            return guess, "The word you guess must have correct length."
                        
        return guess, self._generate_feedback(guess)
    
    def _generate_feedback(self, guess: str) -> str:
        feedback = ['W'] * len(self.answer)
        target_letters = list(self.answer)
        guess_letters = list(guess)
        
        # Process correct positions
        for i in range(len(self.answer)):
            if guess_letters[i] == target_letters[i]:
                feedback[i] = 'R'
                target_letters[i] = None
        
        # Process correct letters in wrong positions
        for i in range(len(self.answer)):
            if feedback[i] == 'R':
                continue
            if guess_letters[i] in target_letters:
                feedback[i] = 'G'
                target_index = target_letters.index(guess_letters[i])
                target_letters[target_index] = None
                
        return ''.join(feedback)
    
    def is_complete(self, result: str) -> bool:
        return result == self.answer

class ImpostorsHandler(GameHandler):
    def __init__(self, answer: str):
        self.answer = answer
        self.impostor_indices = [i+1 for i, val in enumerate(answer) if val == '0']
    
    def parse_response(self, generated_text: str) -> Tuple[str, str]:
        #query_match = re.search(r'My Query:\s*([1-12]),([1-12]),([1-12])', generated_text)
        query_match = re.search(r'My Query:\s*(\d+),(\d+),(\d+)', generated_text)
        if query_match:
            players = sorted([int(x) for x in query_match.groups()])
            if len(set(players)) != 3:
                return "Invalid", "-1"
            return f"Query:{','.join(map(str,players))}", self._evaluate_query(players)
            
        #answer_match = re.search(r'My Answer:\s*((?:[1-12],)*[1-12])', generated_text)
        answer_match = re.search(r'My Answer:\s*((?:\d+,)*\d+)', generated_text)
        if answer_match:
            try:
                indices = sorted([int(x) for x in answer_match.group(1).split(',')])
                return f"Answer:{','.join(map(str,indices))}", self._evaluate_answer(indices)
            except:
                return "Invalid", "-1"
                
        return "Invalid", "Invalid format"
    
    def _evaluate_query(self, players: List[int]) -> str:
        impostor_count = sum(1 for p in players if p in self.impostor_indices)
        return "0" if impostor_count > len(players) - impostor_count else "1"
    
    def _evaluate_answer(self, submitted_answer: List[int]) -> str:
        return "1" if set(submitted_answer) == set(self.impostor_indices) else "0"
    
    def is_complete(self, result: str) -> bool:
        if not result.startswith("Answer:"):
            return False
        return result.split(":")[1] == ','.join(map(str, self.impostor_indices))
        

class RPDHandler(GameHandler):
    def __init__(self, answer: int, k: int, min_value: int, max_value: int):
        self.current_password = answer
        self.old_password = answer
        self.k = k
        self.min_value = min_value
        self.max_value = max_value
        self.range_size = max_value - min_value + 1
        
    def parse_response(self, generated_text: str) -> Tuple[str, str]:
        match = re.search(r'My guess:\s*(\d+)', generated_text)
        if not match:
            return "Invalid", "Invalid"
            
        try:
            guess = int(match.group(1))
            if guess < self.min_value or guess > self.max_value:
                return "Invalid", "Invalid"
            
            #print("guess:", guess)
            #print("old password:", self.current_password)

            self.old_password = self.current_password
            
            # 检查是否猜对
            if guess == self.current_password:
                return f"Guess: {guess}", "Correct"
            
            # 如果猜错，计算新密码
            new_password = self._calculate_new_password(self.current_password, guess)
            self.current_password = new_password
            
            #print("new password:", self.current_password)
            return f"Guess: {guess}", "Incorrect"
            
        except ValueError:
            return "Invalid", "Invalid"

    def _calculate_new_password(self, x: int, y: int) -> int:
        """
        计算新密码：
        1. 将两个数按位进行k进制XOR
        2. 将结果映射到[min_value, max_value]范围
        """
        # 将x和y转换为k进制数的数字列表
        x_digits = self._to_base_k(x)
        y_digits = self._to_base_k(y)
        
        # 确保两个列表长度相同
        max_len = max(len(x_digits), len(y_digits))
        x_digits = [0] * (max_len - len(x_digits)) + x_digits
        y_digits = [0] * (max_len - len(y_digits)) + y_digits
        
        # 按位进行k进制XOR
        result_digits = []
        for dx, dy in zip(x_digits, y_digits):
            # k进制XOR运算: (dx + dy) mod k
            xor_result = (dx + dy) % self.k
            result_digits.append(xor_result)
            
        # 将k进制数转回十进制
        result = self._from_base_k(result_digits)
        #print("zhuanhuanqian",result)
        # 映射到指定范围
        return (result % self.range_size) + self.min_value
    
    def _to_base_k(self, num: int) -> List[int]:
        """将十进制数转换为k进制数的数字列表"""
        if num == 0:
            return [0]
        digits = []
        while num:
            digits.insert(0, num % self.k)
            num //= self.k
        return digits
    
    def _from_base_k(self, digits: List[int]) -> int:
        """将k进制数的数字列表转换为十进制数"""
        result = 0
        for digit in digits:
            result = result * self.k + digit
        return result
    
    def is_complete(self, result: str) -> bool:
        """检查是否已经猜对密码（与旧密码比较）"""
        if not result.startswith("Guess: "):
            return False
        try:
            guess = int(result.split(": ")[1])
            return guess == self.old_password
        except:
            return False

class BitGuessingHandler(GameHandler):
    def __init__(self, answer: int):
        self.original_number = answer  # 原始数字
        self.current_number = answer   # 当前数字（会随着减法变化）
        
    def parse_response(self, generated_text: str) -> Tuple[str, str]:
        """解析响应并返回结果和反馈"""
        # 检查是否是减法操作
        operation_match = re.search(r'My Operation:\s*(\d+)', generated_text)
        if operation_match:
            return self._handle_operation(operation_match.group(1))
            
        # 检查是否是猜测答案
        answer_match = re.search(r'My Answer:\s*(\d+)', generated_text)
        if answer_match:
            return self._handle_answer(answer_match.group(1))
            
        return "Invalid", "Invalid"
    
    def _handle_operation(self, x_str: str) -> Tuple[str, str]:
        """处理减法操作"""
        try:
            x = int(x_str)
            if x > self.current_number:
                return f"Operation: {x}", "Invalid"
            
            # 执行减法
            self.current_number -= x
            
            # 计算新数字的二进制中1的个数
            ones_count = bin(self.current_number).count('1')
            return f"Operation: {x}", str(ones_count)
            
        except ValueError:
            return "Invalid", "Invalid"
    
    def _handle_answer(self, guess_str: str) -> Tuple[str, str]:
        """处理猜测答案"""
        try:
            guess = int(guess_str)
            if guess == self.current_number:
                #print("current_number",self.current_number)
                #print("guess",guess)
                return f"Answer: {guess}", "Correct"
            else:
                return f"Answer: {guess}", "Incorrect"
                
        except ValueError:
            return "Invalid", "Invalid"
    
    def is_complete(self, result: str) -> bool:
        """检查游戏是否完成"""
        if not result.startswith("Answer: "):
            return False
        try:
            guess = int(result.split(": ")[1])
            return guess == self.current_number
        except:
            return False

class GeoGameHandler(GameHandler):
    def __init__(self, starting_point: List[int], available_points: List[List[int]], turns: int):
        self.starting_point = starting_point
        self.available_points = available_points
        self.total_turns = turns  # 总回合数（包括对手的回合）
        self.current_turn = 0
        self.used_points = set()  # 记录已使用的点
    def parse_response(self, generated_text: str) -> Tuple[str, str]:
        """解析响应并返回结果和反馈（对手的选择）"""
        match = re.search(r'My Choice:\s*(\d+)', generated_text)
        if not match:
            self.current_turn = self.total_turns
            return "Invalid", "Invalid"
            
        try:
            # 处理玩家的选择
            choice = int(match.group(1))
            if choice < 1 or choice > len(self.available_points):
                self.current_turn = self.total_turns
                return "Invalid", "Invalid"
            
            # 检查点是否已被使用
            if choice in self.used_points:
                self.current_turn = self.total_turns
                return "Invalid", "Invalid"
                
            # 记录这个点被使用
            self.used_points.add(choice)
            available_choices = [i+1 for i in range(len(self.available_points)) 
                                if i+1 not in self.used_points]
            opponent_choice = random.choice(available_choices)
                # 记录对手的选择并更新状态
            self.used_points.add(opponent_choice)
            self.current_turn += 1
            # 返回对手的选择作为反馈
            return f"Choice: {choice}", f"My Choice: {opponent_choice}"
        except ValueError:
            return "Invalid", "Invalid"
        
    def is_complete(self, result: str) -> bool:
        """检查游戏是否完成"""
        return self.current_turn >= self.total_turns

class MinMaxHandler(GameHandler):
    def __init__(self, array: str, min_pos: int, max_pos: int):
        """
        初始化处理器
        array: 字符串形式的数组，如"52877"
        min_pos: 最小值的位置（1-based）
        max_pos: 最大值的位置（1-based）
        """
        self.array = [int(x) for x in array]  # 转换为数字数组
        self.min_pos = min_pos  # 最小值位置
        self.max_pos = max_pos  # 最大值位置
        
    def parse_response(self, generated_text: str) -> Tuple[str, str]:
        """解析响应并返回结果和反馈"""
        # 检查是否是查询比较
        query_match = re.search(r'My Query:\s*(\d+)\s+(\d+)', generated_text)
        if query_match:
            return self._handle_query(query_match)
            
        # 检查是否是最终答案
        answer_match = re.search(r'My Answer:\s*(\d+)\s+(\d+)', generated_text)
        if answer_match:
            return self._handle_answer(answer_match)
            
        return "Invalid", "Invalid format. Use 'My Query: i j' or 'My Answer: i j'"
    
    def _handle_query(self, match) -> Tuple[str, str]:
        """处理比较查询"""
        try:
            i = int(match.group(1))
            j = int(match.group(2))
            
            # 验证位置范围
            if i < 1 or i > len(self.array) or j < 1 or j > len(self.array):
                return "Invalid", "Positions must be between 1 and 5"
                
            if i == j:
                return "Invalid", "Cannot compare same positions"
            
            # 进行比较
            val_i = self.array[i-1]  # 转换为0-based索引
            val_j = self.array[j-1]
            
            if val_i < val_j:
                compare_result = '<'
            elif val_i > val_j:
                compare_result = '>'
            else:
                compare_result = '='
                
            return f"Query: {i} {j}", compare_result
            
        except ValueError:
            return "Invalid", "Invalid position format"
    
    def _handle_answer(self, match) -> Tuple[str, str]:
        """处理最终答案"""
        try:
            min_guess = int(match.group(1))
            max_guess = int(match.group(2))
            
            # 验证位置范围
            if (min_guess < 1 or min_guess > len(self.array) or 
                max_guess < 1 or max_guess > len(self.array)):
                return "Invalid", "Positions must be between 1 and 5"
            
            # 检查答案是否正确
            is_correct = (min_guess == self.min_pos and max_guess == self.max_pos)
            
            return f"Answer: {min_guess} {max_guess}", "1" if is_correct else "0"
            
        except ValueError:
            return "Invalid", "Invalid position format"
    
    def is_complete(self, result: str) -> bool:
        """检查游戏是否完成"""
        if not result.startswith("Answer: "):
            return False
            
        try:
            # 提取猜测的位置
            parts = result.split(": ")[1].split()
            min_guess = int(parts[0])
            max_guess = int(parts[1])
            
            # 检查是否正确
            return min_guess == self.min_pos and max_guess == self.max_pos
            
        except (IndexError, ValueError):
            return False

class BitQueryHandler(GameHandler):
    def __init__(self, answer: str):
        self.array = [int(x) for x in answer]  # 转换为数字数组
        
    def parse_response(self, generated_text: str) -> Tuple[str, str]:
        """解析响应并返回结果和反馈"""
        # 检查是否是查询操作
        query_match = re.search(r'My Query:\s*(AND|OR|XOR)\s*(\d+)\s*(\d+)', generated_text)
        if query_match:
            return self._handle_query(query_match)
            
        # 检查是否是最终答案
        answer_match = re.search(r'My Answer:\s*([\d\s]+)', generated_text)
        if answer_match:
            return self._handle_answer(answer_match)
            
        return "Invalid", "Invalid format. Use 'My Query: OPERATION i j' or 'My Answer: a1 a2 ... an'"
    
    def _handle_query(self, match) -> Tuple[str, str]:
        """处理查询操作"""
        try:
            operation = match.group(1)
            i = int(match.group(2))
            j = int(match.group(3))
                                    
            # 验证位置范围
            if i < 1 or i > len(self.array) or j < 1 or j > len(self.array):
                return "Invalid", "Invalid position"
                
            if i == j:
                return "Invalid", "Cannot query same position"
            
            # 获取数值
            val_i = self.array[i-1]  # 转换为0-based索引
            val_j = self.array[j-1]
            
            # 执行位运算
            if operation == "AND":
                result = val_i & val_j
            elif operation == "OR":
                result = val_i | val_j
            else:  # XOR
                result = val_i ^ val_j
                
            return f"Query: {operation} {i} {j}", str(result)
            
        except Exception as e:
            return "Invalid", f"Invalid query format: {str(e)}"
    
    def _handle_answer(self, match) -> Tuple[str, str]:
        """处理最终答案"""
        try:
            # 解析答案
            guess = match.group(1).split()
            if len(guess) != len(self.array):
                return "Invalid", f"Answer must contain {len(self.array)} numbers"
            
            # 转换为数字并验证
            guess = [int(x) for x in guess]
            for x in guess:
                if x < 0 or x >= len(self.array):
                    return "Invalid", f"Numbers must be between 0 and {len(self.array)-1}"
            
            # 检查是否正确
            is_correct = all(g == a for g, a in zip(guess, self.array))
            return f"Answer: {' '.join(map(str, guess))}", "Correct" if is_correct else "Incorrect"
            
        except ValueError:
            return "Invalid", "Invalid answer format"
    
    def is_complete(self, result: str) -> bool:
        """检查游戏是否完成（答案正确）"""
        if not result.startswith("Answer: "):
            return False
            
        try:
            # 提取猜测的数组
            guess = [int(x) for x in result.split(": ")[1].split()]
            # 检查是否与答案匹配
            return all(g == a for g, a in zip(guess, self.array))
        except:
            return False

class LegendaryTreeHandler(GameHandler):
    def __init__(self, answer: List[str]):
        self.adj = defaultdict(list)
        self.edges = set()
        
        self.vertices = set()
        for edge in answer:
            v1, v2 = int(edge[0]), int(edge[1])
            self.vertices.add(v1)
            self.vertices.add(v2)
            self.adj[v1].append(v2)
            self.adj[v2].append(v1)
            self.edges.add(tuple(sorted([v1, v2])))
        self.n = len(self.vertices)

    def parse_response(self, generated_text: str) -> Tuple[str, str]:
        query_match = re.search(r'My Query: ([\d ]+) \| ([\d ]+) \| (\d+)', generated_text)
        if query_match:
            return self._handle_query(query_match)
            
        answer_match = re.search(r'My Answer: ((?:\d-\d)(?: \d-\d)*)', generated_text)
        if answer_match:
            return self._handle_answer(answer_match)
            
        return "Invalid", "Please use correct format"

    def _handle_query(self, match) -> Tuple[str, str]:
        try:
            S = set(int(x) for x in match.group(1).split())
            T = set(int(x) for x in match.group(2).split())
            v = int(match.group(3))
            
            if not (S and T):
                return "Invalid", "Sets cannot be empty"
            if not (S.issubset(self.vertices) and T.issubset(self.vertices)):
                return "Invalid", f"Vertices must be in range [1,{max(self.vertices)}]"
            if S.intersection(T):
                return "Invalid", "Sets must be disjoint"
            if v not in self.vertices:
                return "Invalid", f"Vertex {v} not in tree"
                
            count = self._count_paths_through_v(S, T, v)
            return f"{S}|{T}|{v}", str(count)
            
        except ValueError:
            return "Invalid", "Invalid numbers in query"

    def _handle_answer(self, match) -> Tuple[str, str]:
        try:
            submitted_edges = []
            edge_strs = match.group(1).split()
            
            if len(edge_strs) != self.n - 1:
                return str(edge_strs), "Incorrect"
                
            for edge_str in edge_strs:
                v1, v2 = map(int, edge_str.split('-'))
                if v1 not in self.vertices or v2 not in self.vertices:
                    return "Invalid", f"Vertices must be in range [1,{max(self.vertices)}]"
                submitted_edges.append(f"{v1}{v2}")
            
            # 返回提取的边值
            return str(submitted_edges), "Correct" if set(submitted_edges) == set(str(v1)+str(v2) for v1,v2 in self.edges) else "Incorrect"
            
        except ValueError:
            return "Invalid", "Invalid answer format"

    def _count_paths_through_v(self, S: set[int], T: set[int], v: int) -> int:
        def find_path(start: int, target: int) -> List[int]:
            if start == target:
                return [start]
                
            visited = set([start])
            parent = {start: None}
            queue = deque([start])
            
            while queue:
                curr = queue.popleft()
                if curr == target:
                    path = []
                    while curr is not None:
                        path.append(curr)
                        curr = parent[curr]
                    return path[::-1]
                    
                for next_v in self.adj[curr]:
                    if next_v not in visited:
                        visited.add(next_v)
                        parent[next_v] = curr
                        queue.append(next_v)
            return []

        count = 0
        for s in S:
            for t in T:
                path = find_path(s, t)
                if path and v in path:
                    count += 1
        return count

    def is_complete(self, result: str) -> bool:
        return result == "Correct"

class GuessMaxHandler(GameHandler):
    def __init__(self, array: List[int], subsets: Dict[str, List[int]], answer: List[int]):
        self.array = array
        self.subsets = subsets
        self.answer = answer
        
    def parse_response(self, generated_text: str) -> Tuple[str, str]:
        # 检查是否是查询，匹配最后一个My Query:后的内容
        query_matches = re.findall(r'My Query:\s*([\d\s]+)', generated_text, re.DOTALL)
        if query_matches:
            # 取最后一个匹配结果
            positions = [int(x) for x in query_matches[-1].split()]
            if not positions:
                return "Invalid", "Query must include at least one position"
            if any(p < 1 or p > 50 for p in positions):
                return "Invalid", "Positions must be between 1 and 50"
            return f"Query: {positions}", str(self._get_max_value(positions))
            
        # 检查是否是答案
        answer_matches = re.findall(r'My Answer:\s*([\d\s]+)', generated_text, re.DOTALL)
        if answer_matches:
            try:
                guess = [int(x) for x in answer_matches[-1].split()]
                if len(guess) != len(self.answer):
                    return "Invalid", f"Your answer must contain {len(self.answer)} numbers"
                return guess, "Correct" if guess == self.answer else "Incorrect"
            except ValueError:
                return "Invalid", "Invalid number format in answer"
                
        return "Invalid", "Response must be either 'My Query: ...' or 'My Answer: ...'"

    def _get_max_value(self, positions: List[int]) -> int:
        # 返回指定位置中的最大值
        return max(self.array[p-1] for p in positions)
    
    def is_complete(self, result: str) -> bool:
        # 如果结果是列表（而不是查询结果），则检查是否正确
        if isinstance(result, list):
            return result == self.answer
        return False

class LinkedListHandler(GameHandler):
    def __init__(self, linked_list: Dict[str, Dict], answer: int):
        self.linked_list = linked_list
        self.answer = answer
        
    def parse_response(self, generated_text: str) -> Tuple[str, str]:
        # Check for query
        query_match = re.search(r'My Query:\s*(\d+)', generated_text)
        if query_match:
            position = query_match.group(1)
            if position not in self.linked_list:
                return "Invalid", f"Position {position} is not valid"
            
            node = self.linked_list[position]
            return "Query", f"value={node['value']}, next={node['next']}"
            
        # Check for answer
        answer_match = re.search(r'My Answer:\s*(\d+)', generated_text)
        if answer_match:
            user_answer = int(answer_match.group(1))
            if user_answer == self.answer:
                return str(user_answer), "Correct"
            else:
                return str(user_answer), "Incorrect"
                
        return "Invalid", "Your response must be either 'My Query: [POSITION]' or 'My Answer: [VALUE]'"
    
    def is_complete(self, result: str) -> bool:
        try:
            return int(result) == self.answer
        except ValueError:
            return False

class BitCompareHandler(GameHandler):
    def __init__(self, list_values: List[int], answer: List[int]):
        self.list = list_values
        self.answer = answer
    
    def parse_response(self, generated_text: str) -> Tuple[str, str]:
        # 检查查询格式
        query_match = re.search(r'My Query:\s*(\d+)\s+(\d+)\s+(\d+)\s+(\d+)', generated_text)
        if query_match:
            a, b, c, d = map(int, query_match.groups())
            if not all(0 <= x < len(self.list) for x in [a, b, c, d]):
                return "Invalid", "All positions must be valid indices"
            
            # 计算OR操作的结果
            left_or = self.list[a] | self.list[b]
            right_or = self.list[c] | self.list[d]
            
            # 返回具体的OR值和比较结果
            result = f"{a} {b} {c} {d}"
            if left_or < right_or:
                feedback = "<"
            elif left_or > right_or:
                feedback = ">"
            else:
                feedback = "="
            
            return result, feedback
        
        # 检查答案格式
        answer_match = re.search(r'My Answer:\s*(\d+)\s+(\d+)', generated_text)
        if answer_match:
            i, j = map(int, answer_match.groups())
            if not (0 <= i < len(self.list) and 0 <= j < len(self.list)):
                return "Invalid", "Positions must be valid indices"
            
            # 检查是否正确
            if self._is_correct_answer(i, j):
                return f"{i} {j}", "Correct"
            else:
                return f"{i} {j}", "Incorrect"
                
        return "Invalid", "Your response must be either 'My Query: a b c d' or 'My Answer: i j'"
    
    def _is_correct_answer(self, i: int, j: int) -> bool:
        # 检查给定的位置对是否产生最大XOR值
        max_xor = self.list[self.answer[0]] ^ self.list[self.answer[1]]
        submitted_xor = self.list[i] ^ self.list[j]
        return submitted_xor == max_xor
    
    def is_complete(self, result: str) -> bool:
        try:
            i, j = map(int, result.split())
            return self._is_correct_answer(i, j)
        except:
            return False

class MedianQueryHandler(GameHandler):
    def __init__(self, list_values: List[int], answer: List[int]):
        self.list = list_values
        self.answer = sorted(answer)  # 排序以便比较
    
    def parse_response(self, generated_text: str) -> Tuple[str, str]:
        # 检查查询格式
        query_match = re.search(r'My Query:\s*(\d+)((?:\s+\d+)+)', generated_text)
        if query_match:
            k = int(query_match.group(1))
            positions = list(map(int, query_match.group(2).split()))
            
            # 验证查询格式
            if k != len(positions):
                return "Invalid", "Length k must match the number of positions"
            if k % 2 != 0 or k < 4 or k > len(self.list):
                return "Invalid", "Invalid subsequence length"
            if len(set(positions)) != len(positions):
                return "Invalid", "Positions must be distinct"
            if not all(1 <= p <= len(self.list) for p in positions):
                return "Invalid", "Invalid position indices"
            
            # 获取子序列并找到中位数
            subsequence = [self.list[p-1] for p in positions]
            sorted_subseq = sorted(subsequence)
            median1 = sorted_subseq[k//2 - 1]
            median2 = sorted_subseq[k//2]
            
            return f"{k} {' '.join(map(str, positions))}", f"{median1} {median2}"
        
        # 检查答案格式
        answer_match = re.search(r'My Answer:\s*(\d+)\s+(\d+)', generated_text)
        if answer_match:
            i, j = map(int, answer_match.groups())
            if not (1 <= i <= len(self.list) and 1 <= j <= len(self.list)):
                return "Invalid", "Position indices must be valid"
            
            # 检查答案是否正确
            submitted = sorted([i, j])
            if submitted == self.answer:
                return f"{i} {j}", "Correct"
            else:
                return f"{i} {j}", "Incorrect"
                
        return "Invalid", "Your response must be either 'My Query: k x1...xk' or 'My Answer: i j'"
    
    def is_complete(self, result: str) -> bool:
        try:
            i, j = map(int, result.split())
            return sorted([i, j]) == self.answer
        except:
            return False

class CircleQueryHandler(GameHandler):
    def __init__(self, center: List[int], radius: int):
        self.center = center
        self.radius = radius
    
    def parse_response(self, generated_text: str) -> Tuple[str, str]:
        # 检查查询格式
        query_match = re.search(r'My Query:\s*(-?\d+)\s+(-?\d+)', generated_text)
        if query_match:
            xq, yq = map(int, query_match.groups())
            
            # 验证查询点
            if xq == 0 and yq == 0:
                return "Invalid", "Query point cannot be origin (0,0)"
                
            # 计算射线到圆的距离
            distance = self._calculate_distance(xq, yq)
            return f"{xq} {yq}", f"{distance:.10f}"
        
        # 检查答案格式
        answer_match = re.search(r'My Answer:\s*(-?\d+)\s+(-?\d+)\s+(\d+)', generated_text)
        if answer_match:
            xc, yc, rc = map(int, answer_match.groups())
            
            # 验证答案
            if [xc, yc] == self.center and rc == self.radius:
                return f"{xc} {yc} {rc}", "Correct"
            else:
                return f"{xc} {yc} {rc}", "Incorrect"
                
        return "Invalid", "Your response must be either 'My Query: xq yq' or 'My Answer: xc yc rc'"
    
    def _calculate_distance(self, xq: int, yq: int) -> float:
        # 射线的方向向量
        dx, dy = xq, yq
        length = math.sqrt(dx*dx + dy*dy)
        ux, uy = dx/length, dy/length
        
        # 圆心到原点的向量
        vx, vy = self.center[0], self.center[1]
        
        # 计算投影
        proj = vx*ux + vy*uy
        
        if proj < 0:
            # 圆心在射线反方向
            dist = math.sqrt(vx*vx + vy*vy) - self.radius
        else:
            # 计算点到直线距离
            dist = abs(vx*yq - vy*xq) / length - self.radius
        
        return max(0, dist)
    
    def is_complete(self, result: str) -> bool:
        try:
            xc, yc, rc = map(int, result.split())
            return [xc, yc] == self.center and rc == self.radius
        except:
            return False

class TrainPursuitHandler(GameHandler):
    def __init__(self, initial_position: int, n: int, k: int):
        self.train_position = initial_position  # 当前位置
        self.n = n  # 车站总数
        self.k = k  # 最大移动距离
        self.last_query = None  # 记录上一次查询类型
        
    def parse_response(self, generated_text: str) -> Tuple[str, str]:
        # 检查范围查询
        query_match = re.search(r'My Query:\s*(\d+)\s+(\d+)', generated_text)
        if query_match:
            try:
                l, r = map(int, query_match.groups())
                # 验证查询范围
                if not (1 <= l <= r <= self.n):
                    return "Invalid", "Invalid"
                
                # 检查列车是否在范围内
                result = "Yes" if l <= self.train_position <= r else "No"
                self.last_query = "query"
                
                # 查询后移动列车
                self._move_train()
                
                return f"Query: {l} {r}", result
                
            except ValueError:
                return "Invalid", "Invalid"
        
        # 检查答案提交
        answer_match = re.search(r'My Answer:\s*(\d+)', generated_text)
        if answer_match:
            try:
                guess = int(answer_match.group(1))
                # 验证答案范围
                if not (1 <= guess <= self.n):
                    return "Invalid", "Invalid"
                    
                self.last_query = "answer"
                # 检查是否正确
                is_correct = (guess == self.train_position)
                
                if is_correct:
                    return f"Answer: {guess}", "Correct"
                else:
                    # 移动列车
                    self._move_train()
                    return f"Answer: {guess}", "Incorrect"
                    
            except ValueError:
                return "Invalid", "Invalid"
                
        return "Invalid", "Invalid"
    
    def _move_train(self):
        """移动列车"""
        # 随机决定移动距离
        steps = self.k
        # 计算新位置（考虑循环）
        self.train_position = ((self.train_position + steps - 1) % self.n) + 1
    
    def is_complete(self, result: str) -> bool:
        """检查游戏是否完成"""
        if not result.startswith("Answer: "):
            return False
        try:
            answer = int(result.split(": ")[1])
            return self.last_query == "answer" and answer == self.train_position
        except:
            return False

class MimicHuntHandler(GameHandler):
    def __init__(self, objects: List[int], mimic_pos: int):
        self.original_objects = objects.copy()  # 原始物品列表
        self.original_mimic_pos = mimic_pos    # 变形怪在原始列表中的位置
        self.current_type = objects[mimic_pos-1]  # 变形怪当前类型
        self.type_count = 1                    # 当前类型持续回合数
        
    def parse_response(self, generated_text: str) -> Tuple[str, str]:
        # 检查移除物品的请求
        remove_match = re.search(r'My Query:\s*-\s*(\d+)((?:\s+\d+)*)', generated_text)
        if remove_match:
            try:
                k = int(remove_match.group(1))
                if k > 0:
                    positions = list(map(int, remove_match.group(2).split()))
                    if len(positions) != k:
                        return "Invalid", "Invalid"
                    
                    # 验证位置的有效性
                    if not all(1 <= p <= len(self.original_objects) for p in positions):
                        return "Invalid", "Invalid"
                    if len(set(positions)) != len(positions):
                        return "Invalid", "Invalid"
                    
                    # 执行移除并返回剩余物品
                    return self._process_removal(positions)
                    
            except ValueError:
                return "Invalid", "Invalid"
        
        # 检查指认变形怪
        guess_match = re.search(r'My Answer:\s*(\d+)', generated_text)
        if guess_match:
            try:
                guess_pos = int(guess_match.group(1))
                if not (1 <= guess_pos <= len(self.original_objects)):
                    return "Invalid", "Invalid"
                
                # 检查原始位置是否正确
                success = (guess_pos == self.original_mimic_pos)
                return f"Answer: {guess_pos}", "Correct" if success else "Incorrect"
                
            except ValueError:
                return "Invalid", "Invalid"
                
        return "Invalid", "Invalid"

    def _process_removal(self, positions: List[int]) -> Tuple[str, str]:
        """处理移除物品的操作"""
        # 准备当前可见的物品列表
        remaining_objects = []
        removed_set = set(positions)
        
        # 收集未被移除的物品
        for i, obj in enumerate(self.original_objects, 1):
            if i not in removed_set:
                if i == self.original_mimic_pos:
                    remaining_objects.append(self.current_type)
                else:
                    remaining_objects.append(obj)
        
        # 打乱剩余物品的顺序
        random.shuffle(remaining_objects)
        
        # 如果变形怪没有被移除，可能需要变形
        if self.original_mimic_pos not in removed_set:
            self._transform_mimic()
        
        return "Remove: " + " ".join(map(str, positions)), str(remaining_objects)

    def _transform_mimic(self):
        """变形怪可能变形"""
        if self.type_count >= 2:
            # 必须变形
            new_type = random.randint(1, 9)
            while new_type == self.current_type:
                new_type = random.randint(1, 9)
            self.current_type = new_type
            self.type_count = 1
        else:
            self.type_count += 1
    
    def is_complete(self, result: str) -> bool:
        """检查是否成功找到变形怪"""
        if not result.startswith("Answer: "):
            return False
        try:
            guess_pos = int(result.split(": ")[1])
            return guess_pos == self.original_mimic_pos
        except:
            return False

class ZeroFindingHandler(GameHandler):
    def __init__(self, binary_list: List[int], k: int, answer: int):
        self.array = binary_list.copy()  # 当前数组状态
        self.k = k                       # 要找第k个0
        self.target_pos = answer         # 第k个0的位置
        self.found_zeros = set()         # 已找到的非目标0的位置
        
    def parse_response(self, generated_text: str) -> Tuple[str, str]:
        # 检查范围查询
        query_match = re.search(r'My Query:\s*(\d+)\s+(\d+)', generated_text)
        if query_match:
            try:
                l, r = map(int, query_match.groups())
                # 验证查询范围
                if not (1 <= l <= r <= len(self.array)):
                    return "Invalid", "Invalid"
                
                # 计算区间和
                range_sum = sum(self.array[l-1:r])
                return f"Query: {l} {r}", str(range_sum)
                
            except ValueError:
                return "Invalid", "Invalid"
        
        # 检查临时答案（非目标0）
        answer_match = re.search(r'My Answer:\s*(\d+)', generated_text)
        if answer_match:
            try:
                pos = int(answer_match.group(1))
                if not (1 <= pos <= len(self.array)):
                    return "Invalid", "Invalid"
                
                # 验证是否是未找到的0
                if pos in self.found_zeros or pos == self.target_pos:
                    return f"Answer: {pos}", "Incorrect"
                
                if self.array[pos-1] == 0:
                    self.array[pos-1] = 1  # 将找到的0变成1
                    self.found_zeros.add(pos)
                    return f"Answer: {pos}", "Correct"
                else:
                    return f"Answer: {pos}", "Incorrect"
                    
            except ValueError:
                return "Invalid", "Invalid"
        
        # 检查最终答案（目标0）
        final_match = re.search(r'My Final Answer:\s*(\d+)', generated_text)
        if final_match:
            try:
                pos = int(final_match.group(1))
                if not (1 <= pos <= len(self.array)):
                    return "Invalid", "Invalid"
                
                # 检查是否是目标位置
                success = (pos == self.target_pos)
                return f"Final: {pos}", "Correct" if success else "Incorrect"
                
            except ValueError:
                return "Invalid", "Invalid"
                
        return "Invalid", "Invalid"
    
    def is_complete(self, result: str) -> bool:
        """检查是否成功找到目标0"""
        if not result.startswith("Final: "):
            return False
        try:
            pos = int(result.split(": ")[1])
            return pos == self.target_pos
        except:
            return False

class PermutationDiscoveryHandler(GameHandler):
    def __init__(self, p: List[int], q: List[int]):
        self.p = p.copy()            # 隐藏的排列
        self.current_q = q.copy()    # 当前可见的排列
        self.n = len(p)              # 排列长度
        
    def parse_response(self, generated_text: str) -> Tuple[str, str]:
        # 检查查询格式
        query_match = re.search(r'My Query:\s*(\d+)', generated_text)
        if query_match:
            try:
                pos = int(query_match.group(1))
                # 验证位置的有效性
                if not (1 <= pos <= self.n):
                    return "Invalid", "Invalid"
                
                # 获取当前q中的值
                value = self.current_q[pos-1]
                
                # 更新q到下一个状态
                self._update_q()
                
                return f"Query: {pos}", str(value)
                
            except ValueError:
                return "Invalid", "Invalid"
        
        # 检查答案提交
        answer_match = re.search(r'My Answer:\s*([\d\s]+)', generated_text)
        if answer_match:
            try:
                guess = list(map(int, answer_match.group(1).split()))
                if len(guess) != self.n:
                    return "Invalid", "Invalid"
                if not all(1 <= x <= self.n for x in guess):
                    return "Invalid", "Invalid"
                if len(set(guess)) != self.n:
                    return "Invalid", "Invalid"
                
                # 检查是否正确
                success = (guess == self.p)
                return f"Answer: {' '.join(map(str, guess))}", "Correct" if success else "Incorrect"
                
            except ValueError:
                return "Invalid", "Invalid"
                
        return "Invalid", "Invalid"
    
    def _update_q(self):
        """更新q到下一个状态：q'[i] = q[p[i]]"""
        new_q = [0] * self.n
        for i in range(self.n):
            new_q[i] = self.current_q[self.p[i]-1]  # p[i]-1因为p中的值是1-based
        self.current_q = new_q
    
    def is_complete(self, result: str) -> bool:
        """检查是否成功找到隐藏的排列"""
        if not result.startswith("Answer: "):
            return False
        try:
            guess = list(map(int, result.split(": ")[1].split()))
            return guess == self.p
        except:
            return False


class MahjongDetectiveHandler(GameHandler):
    def __init__(self, answer: List[int], n: int):
        self.original_tiles = answer.copy()  # 原始牌组
        self.current_tiles = answer.copy()   # 当前牌组
        self.n = n                          # 数字范围1到n
        
    def parse_response(self, generated_text: str) -> Tuple[str, str]:
        # 检查添加牌的请求
        query_match = re.search(r'My Query:\s*\+\s*(\d+)', generated_text)
        if query_match:
            try:
                value = int(query_match.group(1))
                # 验证值的范围
                if not (1 <= value <= self.n):
                    return "Invalid", "Invalid"
                
                # 添加牌
                self.current_tiles.append(value)
                
                # 计算新的组合数
                triplets = self._count_triplets()
                straights = self._count_straights()
                
                return f"Add: {value}", f"{triplets} {straights}"
                
            except ValueError:
                return "Invalid", "Invalid"
        
        # 检查最终答案
        answer_match = re.search(r'My Answer:\s*([\d\s]+)', generated_text)
        if answer_match:
            try:
                final_counts = list(map(int, answer_match.group(1).split()))
                if len(final_counts) != self.n:
                    return "Invalid", "Invalid"
                
                # 验证每个数字的数量
                if not all(0 <= x <= self.n for x in final_counts):
                    return "Invalid", "Invalid"
                
                # 比较与当前状态是否匹配
                current_counts = self._count_tiles()
                success = (final_counts == current_counts)
                
                return f"Answer: {' '.join(map(str, final_counts))}", "Correct" if success else "Incorrect"
                
            except ValueError:
                return "Invalid", "Invalid"
                
        return "Invalid", "Invalid"
    
    def _count_triplets(self) -> int:
        """计算当前牌组中的刻子数"""
        triplets = 0
        for value in range(1, self.n + 1):
            count = self.current_tiles.count(value)
            if count >= 3:
                # 计算组合数
                triplets += len(list(combinations(range(count), 3)))
        return triplets
    
    def _count_straights(self) -> int:
        """计算当前牌组中的顺子数"""
        straights = 0
        # 对于每个可能的开始值
        for start in range(1, self.n - 1):
            mid = start + 1
            end = start + 2
            # 计算每个值的出现次数
            start_count = self.current_tiles.count(start)
            mid_count = self.current_tiles.count(mid)
            end_count = self.current_tiles.count(end)
            # 计算可能的组合数
            straights += start_count * mid_count * end_count
        return straights
    
    def _count_tiles(self) -> List[int]:
        """统计当前每个数字的数量"""
        counts = [0] * self.n
        for tile in self.current_tiles:
            counts[tile-1] += 1
        return counts
    
    def is_complete(self, result: str) -> bool:
        """检查是否成功完成游戏"""
        if not result.startswith("Answer: "):
            return False
        try:
            final_counts = list(map(int, result.split(": ")[1].split()))
            current_counts = self._count_tiles()
            return final_counts == current_counts
        except:
            return False


class HiddenNumberHandler(GameHandler):
    def __init__(self, answer: int):
        self.answer = answer
        self.last_query_response = None
        
    def parse_response(self, generated_text: str) -> Tuple[str, str]:
        # 找到最后一个符合格式的查询或回答
        query_matches = list(re.finditer(r'My Query:\s*(\d+(?:\s+\d+)+)', generated_text))
        guess_matches = list(re.finditer(r'My Answer:\s*(\d+)', generated_text))
        
        if query_matches:  # 处理最后一个查询
            last_query = query_matches[-1].group(1)
            try:
                numbers = [int(x) for x in last_query.split()]
                k = numbers[0]
                query_set = numbers[1:]
                
                if len(query_set) != k:
                    return "Invalid", "Number of elements doesn't match the specified size"
                
                response = self._generate_query_response(query_set)
                return f"Query:{','.join(map(str, query_set))}", response
            except ValueError:
                return "Invalid", "Invalid number format in query"
                
        if guess_matches:  # 处理最后一个猜测
            try:
                guess = int(guess_matches[-1].group(1))
                if guess == self.answer:
                    return  str(guess), "Correct"
                return  str(guess), "Incorrect"
            except ValueError:
                return "Invalid", "Invalid number in guess"
            
        return "Invalid", "Invalid format. Use 'My Query: k n1 n2...' or 'My Answer: x'"
        
    def _generate_query_response(self, query_set: List[int]) -> str:
        true_response = "YES" if self.answer in query_set else "NO"
        
        if self.last_query_response is None or self.last_query_response[0] == 'L':
            self.last_query_response = ('T', true_response)
            return true_response
            
        lie_response = "NO" if true_response == "YES" else "YES"
        response = random.choice([(True, true_response), (False, lie_response)])
        self.last_query_response = ('T' if response[0] else 'L', response[1])
        return response[1]
        
    def is_complete(self, result: str) -> bool:
        try:
            return int(result) == self.answer
        except ValueError:
            return False

class RotaryLockHandler(GameHandler):
    def __init__(self, answer: List[int], n: int = 5, m: int = 4):
        self.initial_positions = answer.copy()  # 初始相对位置
        self.current_positions = answer.copy()  # 当前相对位置
        self.n = n  # 圆环数量
        self.m = m  # 每个圆环上金属弧覆盖的区段数
        self.total_sections = n * m  # 每个圆环的总区段数
        
    def parse_response(self, generated_text: str) -> Tuple[str, str]:
        # 检查是否是旋转查询
        query_match = re.search(r'My Query:\s*(\d+)\s+(-?\d+)', generated_text)
        if query_match:
            try:
                ring = int(query_match.group(1))  # 要旋转的圆环编号
                direction = int(query_match.group(2))  # 旋转方向
                
                # 验证输入
                if not (0 <= ring < self.n and direction in [-1, 1]):
                    return "Invalid", "Invalid ring number or direction"
                    
                # 执行旋转
                self.current_positions[ring] = (self.current_positions[ring] + direction) % self.total_sections
                
                # 计算未被阻挡的激光数量
                unblocked = self._calculate_unblocked_lasers()
                return f"Rotation:{ring},{direction}", str(unblocked)
                
            except ValueError:
                return "Invalid", "Invalid number format in query"
                
        # 检查是否是最终答案
        answer_match = re.search(r'My Answer:\s*(\d+(?:\s+\d+)*)', generated_text)
        if answer_match:
            try:
                # 解析答案
                final_positions = [int(x) for x in answer_match.group(1).split()]
                
                # 验证答案格式
                if len(final_positions) != self.n - 1:  # 不包括参考环
                    return "Invalid", "Wrong number of positions"
                    
                # 验证各个位置是否在有效范围内
                if not all(0 <= pos < self.total_sections for pos in final_positions):
                    return "Invalid", "Position out of range"
                    
                # 检查答案是否正确
                if self._check_answer(final_positions):
                    return "Answer:" + ",".join(map(str, final_positions)), "Correct"
                return "Answer:" + ",".join(map(str, final_positions)), "Incorrect"
                
            except ValueError:
                return "Invalid", "Invalid number format in answer"
                
        return "Invalid", "Invalid format. Use 'My Query: x d' or 'My Answer: p1 p2...'"
        
    def _calculate_unblocked_lasers(self) -> int:
        """计算未被阻挡的激光数量"""
        # 初始化所有位置为未被阻挡
        unblocked = [True] * self.total_sections
        
        # 检查每个环的金属弧位置
        for ring, pos in enumerate(self.current_positions):
            # 计算该圆环金属弧覆盖的区段
            for i in range(self.m):
                section = (pos + i) % self.total_sections
                unblocked[section] = False
        
        # 计算未被阻挡的激光数量
        return sum(1 for x in unblocked if x)
        
    def _check_answer(self, final_positions: List[int]) -> bool:
        """检查答案是否正确"""
        # 将当前位置（经过旋转后的位置）与用户输入的位置比较
        current_positions = [pos % self.total_sections for pos in self.current_positions[1:]]
        return all(fp == cp for fp, cp in zip(final_positions, current_positions))
        
    def is_complete(self, result: str) -> bool:
        """检查游戏是否完成"""
        if not result.startswith("Answer:"):
            return False
        try:
            positions = [int(x) for x in result.split(":")[1].split(",")]
            return self._check_answer(positions)
        except:
            return False
            
class AttendanceCheckHandler(GameHandler):
    def __init__(self, answer: List[int]):
        self.answer = answer  # 出勤情况数组 [1,1,1,0,1...]
        self.n = len(answer)  # 学生总数
        self.last_two_responses = []  # 记录最近两次回答是否诚实
        
    def parse_response(self, generated_text: str) -> Tuple[str, str]:
        # 检查是否是范围查询
        query_match = re.search(r'My Query:\s*(\d+)\s+(\d+)', generated_text)
        if query_match:
            try:
                l = int(query_match.group(1))
                r = int(query_match.group(2))
                
                # 验证范围
                if not (1 <= l <= r <= self.n):
                    return "Invalid", "Invalid range"
                    
                # 计算范围内在场学生数
                present_students = sum(self.answer[l-1:r])
                expected_raised = r - l + 1
                
                # 决定是否说谎
                should_lie = self._decide_if_lie()
                actual_raised = present_students
                if should_lie:
                    # 如果在场人数等于预期，就少报一个；否则多报一个
                    if present_students == expected_raised:
                        actual_raised = present_students - 1
                    else:
                        actual_raised = present_students + 1
                
                self.last_two_responses.append(not should_lie)  # 记录是否诚实
                if len(self.last_two_responses) > 2:
                    self.last_two_responses.pop(0)
                    
                return f"Query:{l},{r}", str(actual_raised)
                
            except ValueError:
                return "Invalid", "Invalid number format in query"
                
        # 检查是否是最终答案
        answer_match = re.search(r'My Answer:\s*(\d+)', generated_text)
        if answer_match:
            try:
                guess = int(answer_match.group(1))
                if not (1 <= guess <= self.n):
                    return "Invalid", "Invalid student number"
                
                # 检查是否正确猜出缺席学生
                if self.answer[guess-1] == 0:
                    return f"Answer:{guess}", "Correct"
                return f"Answer:{guess}", "Incorrect"
                
            except ValueError:
                return "Invalid", "Invalid number format in answer"
                
        return "Invalid", "Invalid format. Use 'My Query: l r' or 'My Answer: a'"
        
    def _decide_if_lie(self) -> bool:
        """决定这次回答是否说谎"""
        if len(self.last_two_responses) < 2:
            return random.choice([True, False])
            
        # 不能连续3次诚实或说谎
        if all(self.last_two_responses):  # 之前两次都诚实
            return True  # 这次必须说谎
        elif not any(self.last_two_responses):  # 之前两次都说谎
            return False  # 这次必须诚实
        else:
            return random.choice([True, False])
        
    def is_complete(self, result: str) -> bool:
        """检查游戏是否完成"""
        if not result.startswith("Answer:"):
            return False
        try:
            guess = int(result.split(":")[1])
            return self.answer[guess-1] == 0
        except:
            return False

class KnightBattleHandler(GameHandler):
    def __init__(self, board_size: int, white_start: List[int], black_start: List[int], 
                 white_target: List[int], black_target: List[int]):
        self.board_size = board_size
        self.white_pos = white_start
        self.black_pos = black_start
        self.white_target = white_target
        self.black_target = black_target
        self.game_over = False
        
    def parse_response(self, generated_text: str) -> Tuple[str, str]:
        """解析玩家(白方)的移动并返回黑方的移动"""
        match = re.search(r'My Move:\s*(\d+)\s+(\d+)', generated_text)
        if not match:
            self.game_over = True
            return "Invalid", "Invalid format. Use 'My Move: x y'"
            
        try:
            # 解析白方移动
            new_x = int(match.group(1))
            new_y = int(match.group(2))
            
            # 验证移动是否合法
            if not self._is_valid_move(self.white_pos, [new_x, new_y]):
                self.game_over = True
                return "Invalid", "Invalid knight move"
                
            # 更新白方位置
            old_white_pos = self.white_pos.copy()
            self.white_pos = [new_x, new_y]
            
            # 检查白方是否获胜
            if self._is_white_win():
                self.game_over = True
                return f"Move: {new_x},{new_y}", "White wins!"
                
            # 生成黑方的移动（这里可以实现更智能的策略）
            black_moves = self._get_valid_moves(self.black_pos)
            if not black_moves:
                self.game_over = True
                return f"Move: {new_x},{new_y}", "Black has no valid moves"
                
            # 选择一个移动（这里使用简单的随机策略）
            new_black_pos = random.choice(black_moves)
            self.black_pos = new_black_pos
            
            # 检查黑方是否获胜
            if self._is_black_win():
                self.game_over = True
                return f"Move: {new_x},{new_y}", f"Black wins with {new_black_pos[0]},{new_black_pos[1]}"
                
            return f"Move: {new_x},{new_y}", f"{new_black_pos[0]} {new_black_pos[1]}"
            
        except ValueError:
            self.game_over = True
            return "Invalid", "Invalid number format"
            
    def _is_valid_move(self, start: List[int], end: List[int]) -> bool:
        """检查骑士移动是否合法"""
        dx = abs(end[0] - start[0])
        dy = abs(end[1] - start[1])
        if not (1 <= end[0] <= self.board_size and 1 <= end[1] <= self.board_size):
            return False
        return (dx == 1 and dy == 2) or (dx == 2 and dy == 1)
        
    def _get_valid_moves(self, pos: List[int]) -> List[List[int]]:
        """获取所有合法移动"""
        moves = []
        for dx, dy in [(1,2), (1,-2), (-1,2), (-1,-2), 
                       (2,1), (2,-1), (-2,1), (-2,-1)]:
            new_x = pos[0] + dx
            new_y = pos[1] + dy
            if 1 <= new_x <= self.board_size and 1 <= new_y <= self.board_size:
                moves.append([new_x, new_y])
        return moves
        
    def _is_under_attack(self, pos: List[int], attacker_pos: List[int]) -> bool:
        """检查位置是否被攻击"""
        return pos in self._get_valid_moves(attacker_pos)
        
    def _is_white_win(self) -> bool:
        """检查白方是否获胜"""
        # 吃掉黑方
        if self.white_pos == self.black_pos:
            return True
        # 到达目标点且安全    
        if (self.white_pos == self.white_target and 
            not self._is_under_attack(self.white_pos, self.black_pos)):
            return True
        return False
        
    def _is_black_win(self) -> bool:
        """检查黑方是否获胜"""
        # 吃掉白方
        if self.black_pos == self.white_pos:
            return True
        # 到达目标点且安全    
        if (self.black_pos == self.black_target and 
            not self._is_under_attack(self.black_pos, self.white_pos)):
            return True
        return False
        
    def is_complete(self, result: str) -> bool:
        """检查游戏是否结束"""
        return self.game_over

class PaperNumberHandler(GameHandler):
    def __init__(self, num_papers: int, max_number: int, turns: int, initial_value: int):
        self.num_papers = num_papers
        self.max_number = max_number
        self.max_turns = turns
        self.current_turn = 1
        self.papers = [None] * num_papers
        self.current_number = initial_value
        self.game_over = False
        
    def parse_response(self, generated_text: str) -> Tuple[str, str]:
        """解析玩家的选择并返回下一个数字"""
        match = re.search(r'My Choice:\s*(\d+)', generated_text)
        if not match:
            self.game_over = True
            return "Invalid", "Invalid format. Use 'My Choice: X'"
            
        try:
            position = int(match.group(1))
            
            # 验证位置是否合法
            if not 1 <= position <= self.num_papers:
                self.game_over = True
                return "Invalid", f"Invalid position. Choose between 1 and {self.num_papers}"
                
            # 更新纸张状态
            self.papers[position-1] = self.current_number
            
            # 检查是否获胜
            if self._is_winning_state():
                self.game_over = True
                return f"Position: {position}", "Win"
                
            # 更新回合数
            self.current_turn += 1
            
            # 检查是否达到最大回合数
            if self.current_turn > self.max_turns:
                self.game_over = True
                return f"Position: {position}", "Game Over - Max turns reached"
                
            # 生成下一个随机数字
            self.current_number = random.randint(1, self.max_number)
            return f"Position: {position}", str(self.current_number)
            
        except ValueError:
            self.game_over = True
            return "Invalid", "Invalid number format"
            
    def _is_winning_state(self) -> bool:
        """检查当前状态是否满足获胜条件"""
        # 检查是否所有纸张都有数字
        if None in self.papers:
            return False
            
        # 检查是否非递减序列
        for i in range(1, len(self.papers)):
            if self.papers[i] < self.papers[i-1]:
                return False
                
        return True
        
    def is_complete(self, result: str) -> bool:
        """检查游戏是否结束"""
        return self.game_over


class GridColoringHandler(GameHandler):
    def __init__(self, size: int, colored_cells: Dict[str, int], max_color: int):
        self.size = size
        self.colored_cells = colored_cells.copy()  # 已染色的格子
        self.max_color = max_color  # 最大颜色值
        self.moves_made = 0  # 已进行的移动次数
        self.game_over = False
        
    def parse_response(self, generated_text: str) -> Tuple[str, str]:
        """解析玩家的选择并返回反馈"""
        # 检查是否是最终答案
        answer_match = re.search(r'My Answer:\s*(\d+)\s+(\d+)\s+(\d+)\s+(\d+)', generated_text)
        if answer_match:
            return self._check_rectangle(answer_match)
            
        # 检查是否是选择格子
        choice_match = re.search(r'My Choice:\s*(\d+)\s+(\d+)', generated_text)
        if not choice_match:
            self.game_over = True
            return "Invalid", "Invalid format. Use 'My Choice: x y' or 'My Answer: x1 x2 y1 y2'"
            
        try:
            x = int(choice_match.group(1))
            y = int(choice_match.group(2))
            
            # 验证移动是否合法
            if not self._is_valid_choice(x, y):
                self.game_over = True
                return "Invalid", "Invalid move: Cell already colored or out of bounds"
                
            # 选择一个新的颜色（这里可以实现更智能的策略）
            new_color = self._choose_color()
            
            # 更新格子颜色
            self.colored_cells[f"({x}, {y})"] = new_color
            self.moves_made += 1
            
            # 检查是否达到最大移动次数
            if self.moves_made >= 10:
                self.game_over = True
                return f"My Choice: {x} {y}", "Maximum moves reached"
                
            return f"My Choice: {x} {y}", f"Cell ({x},{y}) colored with color {new_color}"
            
        except ValueError:
            self.game_over = True
            return "Invalid", "Invalid number format"
            
    def _is_valid_choice(self, x: int, y: int) -> bool:
        """检查选择是否合法"""
        if not (1 <= x <= self.size and 1 <= y <= self.size):
            return False
        return f"({x}, {y})" not in self.colored_cells
        
    def _choose_color(self) -> int:
        """选择一个新的颜色"""
        return random.randint(1, self.max_color)
        
    def _check_rectangle(self, match) -> Tuple[str, str]:
        """检查矩形是否有效"""
        try:
            x1 = int(match.group(1))
            x2 = int(match.group(2))
            y1 = int(match.group(3))
            y2 = int(match.group(4))
            
            # 检查坐标是否在范围内
            if not all(1 <= coord <= self.size for coord in [x1, x2, y1, y2]):
                self.game_over = True
                return "Invalid", "Coordinates out of bounds"
                
            # 获取四个角的颜色
            corners = [
                f"({x1}, {y1})",
                f"({x1}, {y2})",
                f"({x2}, {y1})",
                f"({x2}, {y2})"
            ]
            
            # 检查所有格子是否已染色
            if not all(corner in self.colored_cells for corner in corners):
                self.game_over = True
                return "Invalid", "Not all cells are colored"
                
            # 检查颜色是否都不同
            colors = {self.colored_cells[corner] for corner in corners}
            if len(colors) != 4:
                self.game_over = True
                return "Invalid", "Colors must be different"
                
            # 检查是否形成矩形
            if x1 == x2 or y1 == y2:
                self.game_over = True
                return "Invalid", "Not a valid rectangle"
                
            self.game_over = True
            return f"My Answer:{x1} {x2} {y1} {y2}", "Win"
            
        except ValueError:
            self.game_over = True
            return "Invalid", "Invalid number format"
            
    def is_complete(self, result: str) -> bool:
        """检查游戏是否结束"""
        return self.game_over

class GridSumHandler(GameHandler):
    def __init__(self, n: int, m: int, initial_grid: Dict[str, int]):
        self.n = n  # 行数
        self.m = m  # 列数
        self.grid = initial_grid.copy()  # 网格数字
        self.selected = set()  # 已选择的格子
        self.player_sum = 0  # LLM(先手)的数字和
        self.my_sum = 0  # 我(后手)的数字和
        self.total_rounds = (n * m) / 2  # 总回合数
        self.current_round = 0  # 当前回合数
        self.game_over = False
        
    def parse_response(self, generated_text: str) -> Tuple[str, str]:
        """解析LLM的选择并返回我的选择"""
        match = re.search(r'My Choice:\s*(\d+)\s+(\d+)', generated_text)
        if not match:
            self.game_over = True
            return "Invalid", "Invalid format. Use 'My Choice: x y'"
            
        try:
            # 解析LLM的选择
            x = int(match.group(1))
            y = int(match.group(2))
            llm_choice = f"({x}, {y})"
            
            # 验证格子是否合法
            if not self._is_valid_choice(llm_choice):
                self.game_over = True
                return "Invalid", "Invalid cell choice"
                
            # 验证是否相邻（第一次选择除外）
            if self.selected and not self._is_adjacent(llm_choice):
                self.game_over = True
                return "Invalid", "Cell must be adjacent to a previous selection"
            
            # 更新LLM的选择和分数
            self.selected.add(llm_choice)
            self.player_sum += self.grid[llm_choice]
            
            # 找出所有合法的格子供我选择
            valid_choices = []
            for i in range(1, self.n+1):
                for j in range(1, self.m+1):
                    cell = f"({i}, {j})"
                    if (cell not in self.selected and  # 未被选过
                        (not self.selected or self._is_adjacent(cell))):  # 第一次选择或相邻
                        valid_choices.append(cell)
            
            # 如果我没有合法选择，游戏结束
            if not valid_choices:
                self.game_over = True
                return f"My Choice: {x} {y}", "I have no valid moves. You win!"
            
            # 随机选择一个合法的格子
            my_choice = random.choice(valid_choices)
            my_x, my_y = map(int, my_choice.strip("()").split(","))
            
            # 更新我的选择和分数
            self.selected.add(my_choice)  
            self.my_sum += self.grid[my_choice]
            self.current_round += 1
            
            # 如果达到总回合数，比较分数
            if self.current_round == self.total_rounds:
                self.game_over = True
                if self.player_sum < self.my_sum:
                    return f"My Choice: {x} {y}", f"My Choice: {my_x} {my_y}\nYou lose! Your sum ({self.player_sum}) < My sum ({self.my_sum})"
                else:
                    return f"My Choice: {x} {y}", f"My Choice: {my_x} {my_y}\nYou win! Your sum ({self.player_sum}) >= My sum ({self.my_sum})"
            
            return f"My Choice: {x} {y}", f"My Choice: {my_x} {my_y}"
            
        except ValueError:
            self.game_over = True
            return "Invalid", "Invalid number format"
            
    def _is_valid_choice(self, cell: str) -> bool:
        """检查选择是否合法"""
        try:
            x, y = map(int, cell.strip("()").split(","))
            return (1 <= x <= self.n and 1 <= y <= self.m and 
                   cell not in self.selected)
        except:
            return False
                
    def _is_adjacent(self, cell: str) -> bool:
        """检查是否与任何已选格子相邻"""
        x, y = map(int, cell.strip("()").split(","))
        # 检查四个方向
        for dx, dy in [(0,1), (0,-1), (1,0), (-1,0)]:
            adj = f"({x+dx}, {y+dy})"
            if adj in self.selected:
                return True
        return False
        
    def is_complete(self, result: str) -> bool:
        """检查游戏是否结束"""
        return self.game_over

class DecreasingGameHandler(GameHandler):
    def __init__(self, initial_list: List[int], first_choice: int):
        self.array = initial_list.copy()
        self.last_choice = first_choice - 1  # 转换为0-based index
        self.game_over = False
        # 先执行第一步选择的结果
        self.valid_indices = [i for i, val in enumerate(self.array) if val > 0]
        
    def parse_response(self, generated_text: str) -> Tuple[str, str]:
        matches = list(re.finditer(r'My Choice:\s*(\d+)', generated_text))
        if not matches:
            self.game_over = True
            return "Invalid", "My Choice: Invalid format. Use 'My Choice: X'"
            
        # 使用最后一个匹配
        match = matches[-1]
            
        try:
            # 解析玩家选择（转换为0-based index）
            player_choice = int(match.group(1)) - 1
            
            if not self._is_valid_move(player_choice):
                self.game_over = True
                return "Invalid", f"Invalid move {player_choice + 1}"
                
            # 计算减少值并更新数组
            min_val = min(self.array[self.last_choice], self.array[player_choice])
            self.array[self.last_choice] -= min_val
            self.array[player_choice] -= min_val
            
            # 更新可选择的位置并检查系统是否有合法移动
            self.valid_indices = [i for i, val in enumerate(self.array) if val > 0]
            
            # 如果系统没有合法移动可选，玩家获胜
            if not self.valid_indices:
                self.game_over = True
                return f"My Choice: {player_choice + 1}", "You win!"
            
            # 随机选择下一步
            next_choice = random.choice(self.valid_indices)
            min_val = min(self.array[next_choice], self.array[player_choice])
            self.array[next_choice] -= min_val
            self.array[player_choice] -= min_val
            
            # 更新最后的选择
            self.last_choice = next_choice
            
            # 更新可选择的位置并检查玩家是否有合法移动
            self.valid_indices = [i for i, val in enumerate(self.array) if val > 0]
            
            # 如果玩家没有合法移动可选，系统获胜
            if not self.valid_indices:
                self.game_over = True
                return f"My Choice: {player_choice + 1}", f"My Choice: {next_choice + 1}\nYou lose!"
            
            # 返回当前状态
            return f"My Choice: {player_choice + 1}", f"My Choice: {next_choice + 1}"
        
        except (ValueError, IndexError):
            self.game_over = True
            return "Invalid", "My Choice: Invalid move format or index"

    def _is_valid_move(self, index: int) -> bool:
        """检查移动是否合法"""
        if not (0 <= index < len(self.array)):
            return False
        if index == self.last_choice:
            return False
        if self.array[index] <= 0:
            return False
        return True
        
    def is_complete(self, result: str) -> bool:
        """检查游戏是否结束"""
        return self.game_over

class AssiutChessHandler(GameHandler):
    def __init__(self, board_size: int, initial_position: str):
        self.board_size = board_size
        # 解析初始位置 "(x, y)" 格式
        x, y = map(int, re.findall(r'\d+', initial_position))
        self.king_pos = [x, y]
        self.queen_pos = None
        self.game_over = False
        
    def parse_response(self, generated_text: str) -> Tuple[str, str]:
        """解析玩家(皇后)的移动并返回国王的移动方向"""
        match = re.search(r'My Choice:\s*(\d+)\s+(\d+)', generated_text)
        if not match:
            self.game_over = True
            return "Invalid", "Invalid format. Use 'My Choice: x y'"
            
        try:
            # 解析皇后移动
            new_x = int(match.group(1))
            new_y = int(match.group(2))
            new_pos = [new_x, new_y]
            
            # 如果是第一步，设置皇后初始位置
            if self.queen_pos is None:
                if not self._is_valid_initial_pos(new_pos):
                    self.game_over = True
                    return "Invalid", "Invalid initial position"
                self.queen_pos = new_pos
            else:
                # 验证移动是否合法
                if not self._is_valid_move(self.queen_pos, new_pos):
                    self.game_over = True
                    return "Invalid", "Invalid queen move"
                self.queen_pos = new_pos
            
            # 检查是否直接抓住国王
            if self.queen_pos == self.king_pos:
                self.game_over = True
                return f"My Choice: {new_x} {new_y}", "Done"
            
            # 获取国王可能的移动方向
            valid_moves = self._get_king_valid_moves()
            
            # 如果国王无处可走，游戏结束
            if not valid_moves:
                self.game_over = True
                return f"My Choice: {new_x} {new_y}", "Done"
            
            # 随机选择一个方向移动国王
            direction, new_king_pos = random.choice(valid_moves)
            self.king_pos = new_king_pos
            
            return f"My Choice: {new_x} {new_y}", direction
            
        except ValueError:
            self.game_over = True
            return "Invalid", "Invalid number format"
            
    def _is_valid_initial_pos(self, pos: List[int]) -> bool:
        """检查初始位置是否合法"""
        return (1 <= pos[0] <= self.board_size and 
                1 <= pos[1] <= self.board_size and 
                pos != self.king_pos)
        
    def _is_valid_move(self, start: List[int], end: List[int]) -> bool:
        """检查皇后移动是否合法"""
        if not (1 <= end[0] <= self.board_size and 1 <= end[1] <= self.board_size):
            return False
        if start == end:
            return False
        # 检查是否在同一行、列或对角线
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        return (dx == 0 or dy == 0 or abs(dx) == abs(dy))
        
    def _get_king_valid_moves(self) -> List[Tuple[str, List[int]]]:
        """获取国王的所有合法移动"""
        moves = []
        directions = {
            'Right': (0, 1), 'Left': (0, -1), 'Up': (-1, 0), 'Down': (1, 0),
            'Down-Right': (1, 1), 'Down-Left': (1, -1), 
            'Up-Left': (-1, -1), 'Up-Right': (-1, 1)
        }
        
        for direction, (dx, dy) in directions.items():
            new_x = self.king_pos[0] + dx
            new_y = self.king_pos[1] + dy
            new_pos = [new_x, new_y]
            
            if (1 <= new_x <= self.board_size and 
                1 <= new_y <= self.board_size and 
                not self._is_attacked_by_queen(new_pos)):
                moves.append((direction, new_pos))
                
        return moves
        
    def _is_attacked_by_queen(self, pos: List[int]) -> bool:
        """检查位置是否被皇后攻击"""
        if pos == self.queen_pos:
            return True
        dx = pos[0] - self.queen_pos[0]
        dy = pos[1] - self.queen_pos[1]
        return (dx == 0 or dy == 0 or abs(dx) == abs(dy))
        
    def is_complete(self, result: str) -> bool:
        """检查游戏是否结束"""
        return self.game_over

class ZigzagGraphHandler(GameHandler):
    def __init__(self, n: int, edge_weights: Dict[str, int]):
        self.n = n  # 每边节点数
        self.edge_weights = edge_weights
        self.game_over = False
        self.visited = set()  # 记录已访问节点
        self.last_node = None # 记录上一个节点
        self.last_weight = None # 记录上一条边的权重
        self.mode = "decreasing" # 玩家是递减模式
        
    def parse_response(self, generated_text: str) -> Tuple[str, str]:
        """解析玩家的选择并返回游戏状态"""
        match = re.search(r'My Choice:\s*(\d+)', generated_text)
        if not match:
            self.game_over = True
            return "Invalid", "Invalid format. Use 'My Choice: X'"
            
        try:
            # 解析玩家选择
            node = int(match.group(1))
            
            # 验证移动是否合法
            if not self._is_valid_move(node):
                self.game_over = True
                return "Invalid", "Invalid move"
            
            # 更新游戏状态
            self.visited.add(node)
            
            # 如果不是第一步，检查边权重规则
            if self.last_node is not None:
                current_weight = self._get_edge_weight(self.last_node, node)
                if self.last_weight is not None and not self._check_weight_rule(current_weight):
                    self.game_over = True
                    return "Invalid", "Invalid weight sequence"
                self.last_weight = current_weight
            
            # 生成系统的下一步移动
            next_move = self._get_next_move(node)
            if next_move == -1:
                self.game_over = True
                return f"My Choice: {node}", "You win!"
            
            # 更新游戏状态
            self.visited.add(next_move)
            self.last_node = next_move
            current_weight = self._get_edge_weight(node, next_move)
            self.last_weight = current_weight
            
            return f"My Choice: {node}", f"My Choice: {next_move}"
            
        except ValueError:
            self.game_over = True
            return "Invalid", "Invalid number format"
            
    def _is_valid_move(self, node: int) -> bool:
        """检查移动是否合法"""
        if node in self.visited:
            return False
        if not (1 <= node <= 2 * self.n):
            return False
        if self.last_node is None:
            return True
        # 检查是否相邻
        edge_key = self._get_edge_key(self.last_node, node)
        return edge_key in self.edge_weights
        
    def _get_edge_weight(self, node1: int, node2: int) -> int:
        """获取边的权重"""
        edge_key = self._get_edge_key(node1, node2)
        return self.edge_weights[edge_key]
        
    def _get_edge_key(self, node1: int, node2: int) -> str:
        """获取边的键值"""
        if node1 > node2:
            node1, node2 = node2, node1
        return f"{node1}-{node2}"
        
    def _check_weight_rule(self, current_weight: int) -> bool:
        """检查权重规则"""
        if self.mode == "decreasing":
            return current_weight < self.last_weight
        return current_weight > self.last_weight
        
    def _get_next_move(self, current_node: int) -> int:
        """获取系统的下一步移动"""
        valid_moves = []
        for node in range(1, 2 * self.n + 1):
            if node not in self.visited:
                edge_key = self._get_edge_key(current_node, node)
                if edge_key in self.edge_weights:
                    weight = self.edge_weights[edge_key]
                    if self.last_weight is None or weight > self.last_weight:
                        valid_moves.append(node)
        
        if not valid_moves:
            return -1
        return random.choice(valid_moves)
        
    def is_complete(self, result: str) -> bool:
        """检查游戏是否结束"""
        return self.game_over

class BeeChaseHandler(GameHandler):
    def __init__(self, n: int, edges: List[List[int]]):
        self.n = n  # 顶点数量
        # 构建邻接表表示图
        self.graph = defaultdict(list)
        for u, v in edges:
            self.graph[u].append(v)
            self.graph[v].append(u)
            
        self.bee_positions = None  # 蜜蜂位置
        self.nastya_pos = None    # Nastya位置
        self.visited = set()      # 已访问节点
        self.game_over = False

    def parse_response(self, generated_text: str) -> Tuple[str, str]:
        """解析玩家的选择并返回游戏状态"""
        match = re.search(r'My Choice:\s*(\d+)\s+(\d+)\s+(\d+)', generated_text)
        if not match:
            self.game_over = True
            return "Invalid", "Invalid format. Use 'My Choice: X Y Z'"
            
        try:
            # 解析蜜蜂位置
            bee_pos = [int(match.group(i)) for i in range(1, 4)]
            
            # 第一轮：初始化蜜蜂位置
            if self.bee_positions is None:
                if not self._is_valid_initial_placement(bee_pos):
                    self.game_over = True
                    return "Invalid", "Invalid initial placement"
                    
                self.bee_positions = bee_pos
                # 随机选择Nastya的起始位置（不能与蜜蜂重叠）
                available = [i for i in range(1, self.n+1) if i not in bee_pos]
                if not available:
                    self.game_over = True
                    return "Invalid", "No valid position for Nastya"
                    
                self.nastya_pos = random.choice(available)
                return f"My Choice: {' '.join(map(str, bee_pos))}", f"{self.nastya_pos}"
                
            # 后续回合：移动蜜蜂
            if not self._is_valid_move(bee_pos):
                self.game_over = True
                return "Invalid", "Invalid bee movement"
                
            # 更新蜜蜂位置
            self.bee_positions = bee_pos
            
            # 检查是否抓住Nastya
            if self.nastya_pos in bee_pos:
                self.game_over = True
                return f"My Choice: {' '.join(map(str, bee_pos))}", "You win!"
                
            # 移动Nastya（选择一个合法的相邻位置）
            next_pos = self._move_nastya()
            if next_pos == -1:
                self.game_over = True
                return f"My Choice: {' '.join(map(str, bee_pos))}", "You win!"
                
            self.nastya_pos = next_pos
            
            # 检查Nastya是否被抓住
            if self.nastya_pos in bee_pos:
                self.game_over = True
                return f"My Choice: {' '.join(map(str, bee_pos))}", "You win!"
                
            return f"My Choice: {' '.join(map(str, bee_pos))}", f"{self.nastya_pos}"
            
        except ValueError:
            self.game_over = True
            return "Invalid", "Invalid number format"
            
    def _is_valid_initial_placement(self, positions: List[int]) -> bool:
        """检查初始放置是否合法"""
        return all(1 <= p <= self.n for p in positions)
        
    def _is_valid_move(self, new_positions: List[int]) -> bool:
        """检查移动是否合法"""
        if not all(1 <= p <= self.n for p in new_positions):
            return False
            
        # 检查每只蜜蜂的移动是否合法
        for old_pos, new_pos in zip(self.bee_positions, new_positions):
            if old_pos != new_pos and new_pos not in self.graph[old_pos]:
                return False
        return True
        
    def _move_nastya(self) -> int:
        """移动Nastya（选择一个不会被立即抓住的位置）"""
        available = []
        for next_pos in self.graph[self.nastya_pos]:
            if next_pos not in self.bee_positions:
                available.append(next_pos)
                
        if not available:
            return -1  # Nastya被困住了
        return random.choice(available)
        
    def is_complete(self, result: str) -> bool:
        """检查游戏是否结束"""
        return self.game_over

class PizzaSliceHandler(GameHandler):
    def __init__(self, n: int, points: Dict[str, List[int]]):
        self.n = n  # 顶点数量
        self.points = points  # 顶点坐标
        self.remaining = list(range(1, n+1))  # 剩余可选顶点
        self.eaten_areas = {"player": 0, "opponent": 0}  # 记录已吃面积
        self.last_choice = None  # 上一个选择
        self.game_over = False

    def parse_response(self, generated_text: str) -> Tuple[str, str]:
        """解析玩家的选择并返回游戏状态"""
        match = re.search(r'My Choice:\s*(\d+)', generated_text)
        if not match:
            self.game_over = True
            return "Invalid", "Invalid format. Use 'My Choice: X'"
            
        try:
            # 解析选择的顶点
            vertex = int(match.group(1))
            
            # 验证移动是否合法
            if vertex not in self.remaining:
                self.game_over = True
                return "Invalid", "Invalid vertex choice"
                
            # 计算玩家吃掉的三角形面积
            area = self._calculate_triangle_area(vertex)
            self.eaten_areas["player"] += area
            
            # 更新剩余顶点
            self.remaining.remove(vertex)
            if len(self.remaining) == 2:
                # 比较总面积确定胜负
                if self.eaten_areas["player"] < self.eaten_areas["opponent"]:
                    self.game_over = True
                    return f"My Choice: {vertex}", "You win!"
                else:
                    self.game_over = True
                    return f"My Choice: {vertex}", "You lose!"
            
            # 系统随机选择一个顶点（这里可以实现更智能的策略）
            opponent_choice = random.choice(self.remaining)
            opponent_area = self._calculate_triangle_area(opponent_choice)
            self.eaten_areas["opponent"] += opponent_area
            self.remaining.remove(opponent_choice)
            
            # 检查游戏是否结束
            if len(self.remaining) == 2:
                if self.eaten_areas["player"] < self.eaten_areas["opponent"]:
                    self.game_over = True
                    return f"My Choice: {vertex}", f"My Choice: {opponent_choice} You win!"
                else:
                    self.game_over = True
                    return f"My Choice: {vertex}", f"My Choice: {opponent_choice} You lose!"
            
            return f"My Choice: {vertex}", f"{opponent_choice}"
            
        except ValueError:
            self.game_over = True
            return "Invalid", "Invalid number format"
            
    def _calculate_triangle_area(self, vertex: int) -> float:
        """计算选定顶点形成的三角形面积"""
        vertices = list(self.remaining)  # 获取剩余顶点
        x1, y1 = self.points[str(vertex)]
        
        # 获取相邻的两个顶点
        idx = vertices.index(vertex)
        next_vertex = vertices[(idx + 1) % len(vertices)]
        prev_vertex = vertices[idx - 1]
        
        x2, y2 = self.points[str(next_vertex)]
        x3, y3 = self.points[str(prev_vertex)]
        
        # 计算三角形面积
        area = abs((x2-x1)*(y3-y1) - (x3-x1)*(y2-y1)) / 2
        return area
        
    def is_complete(self, result: str) -> bool:
        """检查游戏是否结束"""
        return self.game_over

class XORBreakHandler(GameHandler):
    def __init__(self, n: int):
        self.initial_number = n
        self.current_number = n
        self.game_over = False
        self.is_first_turn = True
        
    def parse_response(self, generated_text: str) -> Tuple[str, str]:
        """解析玩家的选择并返回系统的选择"""
        try:
            if self.is_first_turn:
                # 第一回合：解析分解的两个数
                match = re.search(r'Breaking into:\s*(\d+)\s+(\d+)', generated_text)
                if not match:
                    self.game_over = True
                    return "Invalid", "Invalid format. Use 'Breaking into: p1 p2'"
                
                p1 = int(match.group(1))
                p2 = int(match.group(2))
                
                # 验证分解是否合法
                if not self._is_valid_break(self.current_number, p1, p2):
                    self.game_over = True
                    return "Invalid", "Invalid break"
                    
                # 随机选择一个数字并尝试分解
                if p1 != 1 and p2 != 1:
                    chosen = random.choice([p1, p2])
                elif p1 == 1 and p2 != 1:
                    chosen = p2
                if p1 != 1 and p2 == 1:
                    chosen = p1
                break_pair = self._find_break_pair(chosen)
                
                self.is_first_turn = False
                self.current_number = chosen
                
                if not break_pair:
                    self.game_over = True
                    return f"Breaking into: {p1} {p2}", f"Choosing: {chosen} Cannot break further. You win!"
                    
                return f"Breaking into: {p1} {p2}", f"Choosing: {chosen} Breaking into: {break_pair[0]} {break_pair[1]}"
                
            else:
                # 后续回合：解析选择的数和分解
                match = re.search(r'Choosing:\s*(\d+)\s+Breaking into:\s*(\d+)\s+(\d+)', generated_text)
                if not match:
                    self.game_over = True
                    return "Invalid", "Invalid format. Use 'Choosing: p Breaking into: p1 p2'"
                    
                chosen = int(match.group(1))
                p1 = int(match.group(2))
                p2 = int(match.group(3))
                
                # 验证选择和分解是否合法
                if not self._is_valid_break(chosen, p1, p2):
                    self.game_over = True
                    return "Invalid", "Invalid break"
                    
                if p1 != 1 and p2 != 1:
                    next_chosen = random.choice([p1, p2])
                elif p1 == 1 and p2 != 1:
                    next_chosen = p2
                if p1 != 1 and p2 == 1:
                    next_chosen = p1

                break_pair = self._find_break_pair(next_chosen)
                
                self.current_number = next_chosen
                
                if not break_pair:
                    self.game_over = True
                    return f"Choosing: {chosen} Breaking into: {p1} {p2}", f"Choosing: {next_chosen} Cannot break further. You win!"
                    
                return f"Choosing: {chosen} Breaking into: {p1} {p2}", f"Choosing: {next_chosen} Breaking into: {break_pair[0]} {break_pair[1]}"
                
        except ValueError:
            self.game_over = True
            return "Invalid", "Invalid number format"
            
    def _is_valid_break(self, n: int, p1: int, p2: int) -> bool:
        """检查分解是否合法"""
        return (0 < p1 < n and 
                0 < p2 < n and 
                p1 ^ p2 == n)
                
    def _find_break_pair(self, n: int) -> Optional[Tuple[int, int]]:
        """找到一个合法的分解对，如果不存在返回None"""
        for p1 in range(1, n):
            p2 = p1 ^ n
            if 0 < p2 < n:
                return (p1, p2)
        return None
        
    def is_complete(self, result: str) -> bool:
        """检查游戏是否结束"""
        return self.game_over

class TreasureHuntHandler(GameHandler):
    def __init__(self, n: int, graph: List[List[int]]):
        self.n = n
        # 构建邻接表表示图
        self.adj = defaultdict(list)
        for u, v in graph:
            self.adj[u].append(v)
            self.adj[v].append(u)
            
        # 初始化状态
        self.current_pos = 1  # 起始位置
        self.flags = {1}  # 已放置旗子的位置
        self.game_over = False
        # 保存最后一次展示的邻居列表，用于确定选择
        self.last_neighbors = None
        
    def parse_response(self, generated_text: str) -> Tuple[str, str]:
        """解析玩家的选择并返回下一个状态"""
        match = re.search(r'My Choice:\s*(\d+)', generated_text)
        if not match:
            self.game_over = True
            return "Invalid", "Invalid format. Use 'My Choice: X'"
            
        try:
            # 解析选择的编号（从1开始）
            choice = int(match.group(1))
            
            # 如果是第一步，生成初始状态
            if self.last_neighbors is None:
                neighbors = list(self.adj[self.current_pos])
                random.shuffle(neighbors)  # 随机打乱顺序
                self.last_neighbors = neighbors
                
                # 构建初始信息
                info = [f"R {len(neighbors)}"]
                for v in neighbors:
                    deg = len(self.adj[v])
                    flag = 1 if v in self.flags else 0
                    info.extend([str(deg), str(flag)])
                return "Initial", " ".join(info)
            
            # 验证选择的合法性
            if choice < 1 or choice > len(self.last_neighbors):
                self.game_over = True
                return "Invalid", "Invalid choice number"
                
            # 移动到新位置（基于上一次展示的邻居列表）
            new_pos = self.last_neighbors[choice - 1]
            self.current_pos = new_pos
            
            # 放置旗子
            self.flags.add(new_pos)
            
            # 检查是否访问了所有节点
            if len(self.flags) == self.n:
                self.game_over = True
                return f"My Choice: {choice}", "Win"
            
            # 生成新的邻居列表
            next_neighbors = list(self.adj[new_pos])
            random.shuffle(next_neighbors)  # 随机打乱顺序
            self.last_neighbors = next_neighbors  # 保存这次的列表
            
            # 格式: R d deg1 flag1 deg2 flag2 ...
            info = [f"R {len(next_neighbors)}"]
            for v in next_neighbors:
                deg = len(self.adj[v])
                flag = 1 if v in self.flags else 0
                info.extend([str(deg), str(flag)])
                
            return f"My Choice: {choice}", " ".join(info)
            
        except (ValueError, IndexError) as e:
            self.game_over = True
            return "Invalid", f"Error: {str(e)}"
            
    def is_complete(self, result: str) -> bool:
        """检查游戏是否结束"""
        return self.game_over

class PalindromeConstructionHandler(GameHandler):
    def __init__(self, target: str, scale: int, turns: int):
        self.initial_data = target  # 前4轮要给出的字符串
        self.scale = scale         # 每轮给出的字符数
        self.current_pos = scale       # 当前位置
        self.current_turn = 1      # 当前回合
        self.current_string = target[:scale]   # 当前构造的字符串
        self.game_over = False
        self.total_length = len(target)+turns-4
        
    def parse_response(self, generated_text: str) -> Tuple[str, str]:
        """解析玩家的选择并返回游戏状态"""
        match = re.search(r'My Choice:\s*(\d+)\s+(\d+)', generated_text)
        if not match:
            self.game_over = True
            return "Invalid", "Invalid format. Use 'My Choice: l r'"
            
        try:
            # 解析选择的位置
            l = int(match.group(1))
            r = int(match.group(2))
            
            # 检查是否是"不交换"的选择
            if l == 0 and r == 0:
                pass  # 不进行交换
            else:
                # 验证位置是否合法
                if not (1 <= l <= len(self.current_string) and 1 <= r <= len(self.current_string)):
                    self.game_over = True
                    return "Invalid", "Invalid positions"
                    
                # 执行交换（转换为0-based索引）
                l -= 1
                r -= 1
                self.current_string = (self.current_string[:l] + 
                                     self.current_string[r] + 
                                     self.current_string[l+1:r] + 
                                     self.current_string[l] + 
                                     self.current_string[r+1:])
            
            # 生成新字符
            if self.current_turn <= 4:
                # 前4轮使用initial_data
                if self.current_pos < len(self.initial_data):
                    new_chars = self.initial_data[self.current_pos:
                                                self.current_pos + self.scale]
                    self.current_pos += self.scale
                else:
                    new_chars = 'a' * self.scale  # 如果initial_data用完了就用'a'
            else:
                # 之后的轮次随机生成
                new_chars = random.choice(['a', 'b'])
                
            # 更新状态
            self.current_string += new_chars
            self.current_turn += 1
            
            # 检查是否结束（这里可以根据需要设定结束条件）
            if len(self.current_string) >= self.total_length:  
                self.game_over = True
                if self._is_palindrome(self.current_string):
                    return f"My Choice: {l+1} {r+1}", "Win"
                else:
                    return f"My Choice: {l+1} {r+1}", "Lose"
            if l == 0 and r == 0:
                return f"My Choice: {l} {r}", new_chars
            else:
                return f"My Choice: {l+1} {r+1}", new_chars
                
        except ValueError:
            self.game_over = True
            return "Invalid", "Invalid number format"
            
    def _is_palindrome(self, s: str) -> bool:
        """检查字符串是否是回文"""
        return s == s[::-1]
        
    def is_complete(self, result: str) -> bool:
        """检查游戏是否结束"""
        return self.game_over

class CactusSearchHandler(GameHandler):
    def __init__(self, n: int, graph: Dict):
        self.n = n
        # 构建邻接表表示图
        self.adj = defaultdict(list)
        for path in graph['paths']:
            for i in range(len(path)-1):
                u, v = path[i], path[i+1]
                self.adj[u].append(v)
                self.adj[v].append(u)
        
        # 随机选择目标顶点
        self.target = random.randint(1, n)
        self.game_over = False
        
    def get_next_vertex(self, current: int) -> int:
        """返回从current到target路径上的下一个顶点"""
        # 使用BFS找到最短路径
        visited = {current}
        queue = [(current, [])]
        
        while queue:
            vertex, path = queue.pop(0)
            if vertex == self.target:
                if len(path) > 0:
                    return path[0]  # 返回路径上的第一个顶点
                return current
                
            for next_v in self.adj[vertex]:
                if next_v not in visited:
                    visited.add(next_v)
                    new_path = path + [next_v]
                    queue.append((next_v, new_path))
                    
        return current  # 不应该发生，因为图是连通的
        
    def parse_response(self, generated_text: str) -> Tuple[str, str]:
        """解析玩家的猜测并返回结果"""
        match = re.search(r'My Guess:\s*(\d+)', generated_text)
        if not match:
            self.game_over = True
            return "Invalid", "Invalid format. Use 'My Guess: X'"
            
        try:
            guess = int(match.group(1))
            
            # 验证猜测的合法性
            if guess < 1 or guess > self.n:
                self.game_over = True
                return "Invalid", f"Invalid vertex number. Must be between 1 and {self.n}"
                
            # 检查是否找到目标
            if guess == self.target:
                self.game_over = True
                return f"My Guess: {guess}", "Win"
            
            # 获取下一个应该访问的顶点
            next_v = self.get_next_vertex(guess)
            return f"My Guess: {guess}", f"GO {next_v}"
            
        except (ValueError, IndexError) as e:
            self.game_over = True
            return "Invalid", f"Error: {str(e)}"
            
    def is_complete(self, result: str) -> bool:
        """检查游戏是否结束"""
        return self.game_over

class VladikMazeHandler(GameHandler):
    def __init__(self, n: int, grids: List[List[str]]):
        self.n = n  # 行数
        self.m = len(grids[0])  # 列数
        self.grid = grids
        # 记录起点和当前位置
        self.current_pos = [1, 1]  # 1-based indexing
        self.game_over = False
        
        # 确保至少有一组按键交换
        # 策略1：随机一组一定交换，另一组随机
        if random.choice([True, False]):
            # L/R一定交换，U/D随机
            self.lr_swapped = True
            self.ud_swapped = random.choice([True, False])
        else:
            # U/D一定交换，L/R随机
            self.ud_swapped = True
            self.lr_swapped = random.choice([True, False])
        
        self.finish_pos = None
        for i in range(n):
            for j in range(self.m):
                if grids[i][j] == 'F':
                    self.finish_pos = [i+1, j+1]  # 转换为1-based indexing

    def get_next_position(self, move: str) -> List[int]:
        """根据移动方向和按键交换状态计算下一个位置"""
        x, y = self.current_pos
        
        # 根据交换状态处理实际移动方向
        actual_move = move
        if self.lr_swapped and move in ['L', 'R']:
            actual_move = 'L' if move == 'R' else 'R'
        if self.ud_swapped and move in ['U', 'D']:
            actual_move = 'U' if move == 'D' else 'D'
            
        # 计算新位置
        if actual_move == 'U':
            x -= 1
        elif actual_move == 'D':
            x += 1
        elif actual_move == 'L':
            y -= 1
        else:  # R
            y += 1
            
        # 检查是否在网格内
        if x < 1 or x > self.n or y < 1 or y > self.m:
            return self.current_pos  # 保持原位置
            
        return [x, y]
        
    def parse_response(self, generated_text: str) -> Tuple[str, str]:
        """解析玩家的移动并返回新状态"""
        match = re.search(r'My Move:\s*([UDLR])', generated_text)
        if not match:
            self.game_over = True
            return "Invalid", "Invalid format. Use 'My Move: X' where X is U, D, L, or R"
            
        try:
            move = match.group(1)
            # 计算新位置
            new_pos = self.get_next_position(move)
            
            # 转换为0-based indexing检查格子类型
            grid_x, grid_y = new_pos[0]-1, new_pos[1]-1
            cell = self.grid[grid_x][grid_y]
            
            # 如果是危险格子
            if cell == '*':
                self.game_over = True
                return f"My Move: {move}", "-1 -1 You lose!"
                
            # 如果到达终点
            if cell == 'F':
                self.game_over = True
                return f"My Move: {move}", f"{new_pos[0]} {new_pos[1]} You win!"
                
            # 更新当前位置
            self.current_pos = new_pos
            return f"My Move: {move}", f"{new_pos[0]} {new_pos[1]}"
            
        except (ValueError, IndexError) as e:
            self.game_over = True
            return "Invalid", f"Error: {str(e)}"
            
    def is_complete(self, result: str) -> bool:
        """检查游戏是否结束"""
        return self.game_over

class FindBiggestHandler(GameHandler):
    def __init__(self, grid_size: int, treasures: List[dict]):
        self.grid_size = grid_size
        self.treasures = treasures
        # 当前位置
        self.current_pos = [1, 1]  
        # 上一次方向是否错误
        self.last_dir_wrong = False
        # 游戏是否结束
        self.game_over = False
        
    def get_direction(self, x1: int, y1: int, x2: int, y2: int) -> str:
        """计算从(x1,y1)到(x2,y2)的大致方向"""
        dx = x2 - x1
        dy = y2 - y1
        if dx < 0:
            if dy < 0: return "NW"
            elif dy == 0: return "N"
            else: return "NE"
        elif dx == 0:
            if dy < 0: return "W"
            else: return "E"
        else:
            if dy < 0: return "SW"
            elif dy == 0: return "S"
            else: return "SE"
            
    def get_nearest_treasure(self, x: int, y: int) -> Tuple[dict, str]:
        """找到最近的宝藏及其方向"""
        min_dist = float('inf')
        nearest = None
        for t in self.treasures:
            dist = abs(t['x'] - x) + abs(t['y'] - y)
            if dist < min_dist:
                min_dist = dist
                nearest = t
        return nearest, self.get_direction(x, y, nearest['x'], nearest['y'])
        
    def parse_response(self, generated_text: str) -> Tuple[str, str]:
        """解析玩家的选择并返回下一个状态"""
        if self.game_over:
            return "Game Over", "Game already ended"
            
        match = re.search(r'My Choice:\s*(?:(\d+)\s+(\d+)|COLLECT)', generated_text)
        if not match:
            self.game_over = True
            return "Invalid", "Invalid format. Use 'My Choice: X Y' or 'My Choice: COLLECT'"
            
        # 处理收集命令
        if "COLLECT" in generated_text:
            x, y = self.current_pos
            # 检查当前位置是否有宝藏
            current_treasure = None
            for t in self.treasures:
                if t['x'] == x and t['y'] == y:
                    current_treasure = t
                    break
                    
            if not current_treasure:
                self.game_over = True
                return "My Choice: COLLECT", "Fail"
                
            # 检查是否是最高价值宝藏
            max_value = max(t['value'] for t in self.treasures)
            if current_treasure['value'] == max_value:
                self.game_over = True
                return "My Choice: COLLECT", "Win"
            else:
                self.game_over = True
                return "My Choice: COLLECT", "Lose"
                
        # 处理移动命令
        try:
            x = int(match.group(1))
            y = int(match.group(2))
            
            # 验证移动的合法性
            if x < 1 or x > self.grid_size or y < 1 or y > self.grid_size:
                return "Invalid", "INVALID_MOVE"
                
            # 验证是否是相邻格子
            dx = abs(x - self.current_pos[0])
            dy = abs(y - self.current_pos[1])
            if dx > 1 or dy > 1:
                return "Invalid", "INVALID_MOVE"
                
            # 更新位置
            self.current_pos = [x, y]
            
            # 检查是否有宝藏
            for t in self.treasures:
                if t['x'] == x and t['y'] == y:
                    return f"My Choice: {x} {y}", f"TREASURE {t['value']}"
                    
            # 获取最近宝藏的方向
            _, true_dir = self.get_nearest_treasure(x, y)
            
            # 处理磁场干扰
            if self.last_dir_wrong:
                self.last_dir_wrong = False
                return f"My Choice: {x} {y}", f"EMPTY {true_dir}"
            
            # 50%概率方向错误
            if random.random() < 0.5:
                self.last_dir_wrong = True
                # 随机选择一个错误方向
                all_dirs = ["N","NE","E","SE","S","SW","W","NW"]
                wrong_dirs = [d for d in all_dirs if d != true_dir]
                wrong_dir = random.choice(wrong_dirs)
                return f"My Choice: {x} {y}", f"EMPTY {wrong_dir}"
            else:
                self.last_dir_wrong = False
                return f"My Choice: {x} {y}", f"EMPTY {true_dir}"
                
        except (ValueError, IndexError) as e:
            return "Invalid", f"Error: {str(e)}"
            
    def is_complete(self, result: str) -> bool:
        """检查游戏是否结束"""
        return self.game_over

class SafepathFinderHandler(GameHandler):
    def __init__(self, grid_size: int, traps: List[List[int]]):
        self.grid_size = grid_size
        # 转换陷阱坐标为集合，方便查找
        self.traps = {(x, y) for x, y in traps}
        # 初始化状态
        self.current_pos = [1, 1]  # 起始位置
        self.game_over = False
        
    def count_adjacent_traps(self, x: int, y: int) -> int:
        """计算周围陷阱数量"""
        count = 0
        for dx in [-1,0,1]:
            for dy in [-1,0,1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if (nx, ny) in self.traps:
                    count += 1
        return count
        
    def is_valid_move(self, x: int, y: int) -> bool:
        """检查移动是否有效"""
        # 检查是否在网格内
        if x < 1 or x > self.grid_size or y < 1 or y > self.grid_size:
            return False
        # 检查是否是相邻格子（包括对角线）
        dx = abs(x - self.current_pos[0])
        dy = abs(y - self.current_pos[1])
        return dx <= 1 and dy <= 1 and (dx != 0 or dy != 0)
        
    def parse_response(self, generated_text: str) -> Tuple[str, str]:
        """解析玩家的选择并返回下一个状态"""
        match = re.search(r'My Choice:\s*(\d+)\s+(\d+)', generated_text)
        if not match:
            self.game_over = True
            return "Invalid", "Invalid format. Use 'My Choice: X Y'"
            
        try:
            # 解析选择的坐标
            x = int(match.group(1))
            y = int(match.group(2))
                        
            # 验证移动的合法性
            if not self.is_valid_move(x, y):
                self.game_over = True
                return "Invalid", "INVALID_MOVE"
                
            # 检查是否踩到陷阱
            if (x,y) in self.traps:
                self.game_over = True
                return f"My Choice: {x} {y}", "Lose"
                
            # 检查是否到达终点
            if x == self.grid_size and y == self.grid_size:
                self.game_over = True
                return f"My Choice: {x} {y}", "Win"
                
            # 更新当前位置
            self.current_pos = [x, y]
            
            # 计算新位置的危险等级
            danger_level = self.count_adjacent_traps(x, y)
            
            return f"My Choice: {x} {y}", f"DANGER_LEVEL {danger_level}"
            
        except (ValueError, IndexError) as e:
            self.game_over = True
            return "Invalid", f"Error: {str(e)}"
            
    def is_complete(self, result: str) -> bool:
        """检查游戏是否结束"""
        return self.game_over

class DarkMazeHandler(GameHandler):
    def __init__(self, grid_size: int, maze: Dict):
        self.grid_size = grid_size
        self.rooms = maze["rooms"]  # 房间及其墙壁信息
        self.current_pos = [1, 1]   # 起始位置
        self.game_over = False
        
        # 方向与坐标变化的映射
        self.dir_to_delta = {
            'N': (-1, 0),
            'E': (0, 1),
            'S': (1, 0),
            'W': (0, -1)
        }
        
    def parse_response(self, generated_text: str) -> Tuple[str, str]:
        """解析玩家的选择并返回下一个状态"""
        match = re.search(r'My Choice:\s*([NESW])', generated_text)
        if not match:
            self.game_over = True
            return "Invalid", "Invalid format. Use 'My Choice: X' where X is N, E, S, or W"
            
        try:
            direction = match.group(1)
                        
            # 获取移动方向对应的坐标变化
            dx, dy = self.dir_to_delta[direction]
            new_x = self.current_pos[0] + dx
            new_y = self.current_pos[1] + dy
            
            # 检查是否出界
            if (new_x < 1 or new_x > self.grid_size or 
                new_y < 1 or new_y > self.grid_size):
                return f"My Choice: {direction}", "INVALID"
            
            # 检查当前房间在该方向是否有墙
            current_room = self.rooms[f"{self.current_pos[0]},{self.current_pos[1]}"]
            if direction in current_room["walls"]:
                return f"My Choice: {direction}", "BLOCKED"
            
            # 更新位置
            self.current_pos = [new_x, new_y]
            
            # 检查是否到达终点
            if new_x == self.grid_size and new_y == self.grid_size:
                self.game_over = True
                return f"My Choice: {direction}", "WIN"
            
            return f"My Choice: {direction}", "MOVED"
            
        except (ValueError, KeyError) as e:
            self.game_over = True
            return "Invalid", f"Error: {str(e)}"
            
    def is_complete(self, result: str) -> bool:
        """检查游戏是否结束"""
        return self.game_over

class MagneticFieldHandler(GameHandler):
    def __init__(self, size: int, grid: List[List[str]]):
        self.size = size
        self.grid = grid
        self.current_pos = [1, 1]  # 1-based indexing
        self.game_over = False
        
        # 方向映射
        self.dir_to_delta = {
            'U': (-1, 0),
            'D': (1, 0),
            'L': (0, -1),
            'R': (0, 1)  # 修正右移的方向
        }
        
        # 磁场方向映射
        self.magnetic_dir = {
            'N': (-1, 0),
            'S': (1, 0),
            'E': (0, 1),
            'W': (0, -1)
        }
        
        # 添加磁场处理计数器的最大限制
        self.MAX_MAGNETIC_FIELD_COUNT = 20

    def is_valid_position(self, x: int, y: int) -> bool:
        """检查位置是否在网格内"""
        return 1 <= x <= self.size and 1 <= y <= self.size
        
    def get_next_position(self, cur_x: int, cur_y: int, dx: int, dy: int) -> Tuple[int, int]:
        """获取移动后的位置"""
        next_x = cur_x + dx
        next_y = cur_y + dy
        
        # 如果移动无效，保持原位
        if not self.is_valid_position(next_x, next_y):
            return cur_x, cur_y
            
        return next_x, next_y
        
    def process_magnetic_field(self, x: int, y: int, count: int = 0) -> Tuple[int, int]:
        """
        处理磁场效果，并增加处理次数的限制。
        
        Parameters:
            x (int): 当前 x 坐标
            y (int): 当前 y 坐标
            count (int): 当前递归深度或处理次数
        
        Returns:
            Tuple[int, int]: 最终的位置坐标
        """
        # 递增处理次数
        count += 1
        
        # 检查是否超过次数限制
        if count > self.MAX_MAGNETIC_FIELD_COUNT:
            self.game_over = True
            return -1, -1
        
        cell = self.grid[x-1][y-1]
        
        if cell not in self.magnetic_dir:  # 不是磁场
            return x, y
            
        # 获取磁场方向
        dx, dy = self.magnetic_dir[cell]
        next_x, next_y = self.get_next_position(x, y, dx, dy)
        
        # 如果下一个位置是危险区域
        if self.grid[next_x-1][next_y-1] == 'X':
            return -1, -1
            
        # 如果下一个位置也是磁场，继续处理
        if self.grid[next_x-1][next_y-1] in self.magnetic_dir:
            return self.process_magnetic_field(next_x, next_y, count)
            
        return next_x, next_y
        
    def parse_response(self, generated_text: str) -> Tuple[str, str]:
        """解析玩家的选择并返回下一个状态"""
        match = re.search(r'My Move:\s*([UDLR])', generated_text)
        if not match:
            self.game_over = True
            return "Invalid", "Invalid format. Use 'My Move: X' where X is U, D, L, or R"
        
        try:
            direction = match.group(1)
            
            # 获取移动方向对应的坐标变化
            dx, dy = self.dir_to_delta[direction]
            
            # 计算初始移动
            next_x, next_y = self.get_next_position(
                self.current_pos[0], 
                self.current_pos[1], 
                dx, dy
            )
            
            # 检查是否移动到危险区域
            if self.grid[next_x-1][next_y-1] == 'X':
                self.game_over = True
                return f"My Move: {direction}", "-1 -1 You lose!"
            
            # 处理磁场效果，并传入初始计数为 0
            final_x, final_y = next_x, next_y
            if self.grid[next_x-1][next_y-1] in self.magnetic_dir:
                final_x, final_y = self.process_magnetic_field(next_x, next_y)
                if final_x == -1:  # 被磁场推到危险区域或超过次数限制
                    self.game_over = True
                    return f"My Move: {direction}", "-1 -1 You lose!"
                
            # 更新位置
            self.current_pos = [final_x, final_y]
            
            # 检查是否到达终点
            if self.grid[final_x-1][final_y-1] == 'G':
                self.game_over = True
                return f"My Move: {direction}", "WIN"
                
            return f"My Move: {direction}", f"{final_x} {final_y}"
                
        except (ValueError, IndexError) as e:
            self.game_over = True
            return "Invalid", f"Error: {str(e)}"
                
    def is_complete(self, result: str) -> bool:
        """检查游戏是否结束"""
        return self.game_over

class ChemicalSynthesisHandler(GameHandler):
    def __init__(self, initial_compounds: List[str], target_compound: str):
        self.available_compounds = initial_compounds.copy()
        self.target = target_compound
        self.game_over = False
        
        # 固定的操作映射
        self.op_mapping = {
            '1': self._split,    
            '2': self._merge,    
            '3': self._swap,     
            '4': self._extract   
        }
        
    def _split(self, compound: str) -> List[str]:
        """将化合物分成两部分，可能在随机位置分裂"""
        if len(compound) <= 1:
            return [compound]
        
        # 随机决定是否进行不稳定分裂
        if random.random() < 0.4 and len(compound) > 2:  
            split_point = random.randint(1, len(compound)-1)
            return [compound[:split_point], compound[split_point:]]
        
        # 正常分裂（首元素和其余部分）
        return [compound[0], compound[1:]]
    
    def _merge(self, compound1: str, compound2: str) -> Optional[str]:
        """合并两个化合物，可能发生催化重排"""
        if not compound1 or not compound2:
            return None
        merged = compound1 + compound2                
        # 随机决定是否发生催化重排
        if random.random() < 0.4 and len(merged) > 2:
            # 随机交换相邻元素
            chars = list(merged)
            swap_pos = random.randint(0, len(chars)-2)
            chars[swap_pos], chars[swap_pos+1] = chars[swap_pos+1], chars[swap_pos]
            merged = ''.join(chars)
            
        return merged
    
    def _swap(self, compound: str) -> str:
        """交换元素，可能发生多次交换"""
        if len(compound) <= 1:
            return compound
            
        chars = list(compound)
        # 随机决定交换次数(1-2次)
        swaps = random.randint(1, 2) if random.random() < 0.4 else 1
        
        for _ in range(swaps):
            if len(chars) > 2:
                # 随机选择两个位置交换
                i, j = random.sample(range(len(chars)), 2)
                chars[i], chars[j] = chars[j], chars[i]
            else:
                chars.reverse()
                
        return ''.join(chars)
    
    def _extract(self, compound: str) -> str:
        """提取元素，可能随机提取"""
        if len(compound) <= 1:
            return compound
            
        # 随机决定是否提取随机位置
        if random.random() < 0.4:
            pos = random.randint(0, len(compound)-1)
            return compound[pos]
            
        return compound[-1]
        
    def parse_response(self, generated_text: str) -> Tuple[str, str]:
        """解析玩家的选择并返回下一个状态"""
        # 检查是否是合并操作（需要两个化合物）
        merge_match = re.search(r'My Move:\s*(\w+)\s+(\w+)\s+(\d+)', generated_text)
        if merge_match:
            compound1, compound2, operation = merge_match.groups()
            # 如果不是合并操作但使用了两个化合物
            if operation != '2':
                return "Wrong type", "Wrong type"
                
            # 验证化合物是否可用
            if compound1 not in self.available_compounds or compound2 not in self.available_compounds:
                self.game_over = True
                return "Invalid", "Invalid compound"
                
            # 执行合并操作
            result = self._merge(compound1, compound2)
            if result:
                self.available_compounds.append(result)
        else:
            # 单化合物操作
            single_match = re.search(r'My Move:\s*(\w+)\s+(\d+)', generated_text)
            if not single_match:
                return "Invalid", "Invalid format"
                
            compound, operation = single_match.groups()
            
            # 验证化合物是否可用
            if compound not in self.available_compounds:
                self.game_over = True
                return "Invalid", "Invalid compound"
                
            # 如果是合并操作但只提供了一个化合物
            if operation == '2':
                return "Wrong type", "Wrong type"
                                
            # 执行操作
            result = self.op_mapping[operation](compound)
            if isinstance(result, list):
                self.available_compounds.extend(result)
            else:
                self.available_compounds.append(result)
        
        # 检查是否达成目标
        if self.target in self.available_compounds:
            self.game_over = True
            return operation, "WIN"
        
        # 返回当前可用化合物
        compounds_str = sorted(list(set(self.available_compounds))) 
        return operation, f"Available: {' '.join(compounds_str)}"
            
    def is_complete(self, result: str) -> bool:
        """检查游戏是否结束"""
        return self.game_over

class ColorMagicHandler(GameHandler):
    def __init__(self, size: int, initial_state: List[List[str]], operations: dict):
        self.size = size
        self.initial_state = [row[:] for row in initial_state] 
        self.current_state = [row[:] for row in initial_state]
        self.operations = operations
        self.game_over = False
        
        # 映射操作编号到操作类型
        self.op_mapping = {
            2: 'alpha',
            1: 'beta',
            3: 'gamma'
        }
        
        # 预处理颜色变换映射
        self.color_rotations = {
            'RBY': {'R': 'B', 'B': 'Y', 'Y': 'R'},
            'BYR': {'B': 'Y', 'Y': 'R', 'R': 'B'},
            'RYB': {'R': 'Y', 'Y': 'B', 'B': 'R'},
            'BRY': {'B': 'R', 'R': 'Y', 'Y': 'B'},
            'swap': {'R': 'B', 'B': 'Y', 'Y': 'R'}
        }
        
    def get_adjacent_positions(self, pos):
        """获取相邻位置"""
        row, col = (pos-1) // self.size, (pos-1) % self.size
        adjacent = []
        for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < self.size and 0 <= new_col < self.size:
                adjacent.append((new_row, new_col))
        return adjacent
        
    def apply_operation(self, operation: str, position: int) -> None:
        """应用操作到指定位置"""
        row, col = (position-1) // self.size, (position-1) % self.size
        
        # 获取操作规则
        op_rules = self.operations[operation]
        
        # 应用中心格子规则
        if operation in ['alpha', 'beta']:
            center_rotation = self.color_rotations[op_rules['center']]
            curr_color = self.current_state[row][col]
            self.current_state[row][col] = center_rotation[curr_color]
            
        # 应用相邻格子规则
        adjacent = self.get_adjacent_positions(position)
        if op_rules['adjacent'] == 'swap':
            adjacent_rotation = self.color_rotations['swap']
        else:
            adjacent_rotation = self.color_rotations[op_rules['adjacent']]
            
        for adj_row, adj_col in adjacent:
            curr_color = self.current_state[adj_row][adj_col]
            self.current_state[adj_row][adj_col] = adjacent_rotation[curr_color]
            
    def state_to_string(self) -> str:
        """将当前状态转换为字符串表示"""
        rows = []
        for row in self.current_state:
            rows.append(" ".join(row))
        return "\n".join(rows)
        
    def check_win(self) -> bool:
        """检查是否所有格子都是同一种颜色"""
        if all(self.current_state[i][j] == "R"
                  for i in range(self.size)
                  for j in range(self.size)):
            return True
        elif all(self.current_state[i][j] == "Y"
                  for i in range(self.size)
                  for j in range(self.size)):
            return True
        elif all(self.current_state[i][j] == "B"
                  for i in range(self.size)
                  for j in range(self.size)):
            return True
        else:
            return False
        
    def parse_response(self, generated_text: str) -> Tuple[str, str]:
        """解析玩家的选择并返回新状态"""            
        match = re.search(r'My Move:\s*(\d+)\s+(\d+)', generated_text)
        if not match:
            self.game_over = True
            return "Invalid", "Invalid format. Use 'My Move: OPERATION POSITION'"
            
        try:
            operation = int(match.group(1))
            position = int(match.group(2))
            
            # 验证输入
            if operation not in [1,2,3] or position < 1 or position > self.size*self.size:
                self.game_over = True
                return "Invalid", "Invalid operation or position"
                
            # 应用操作
            op_type = self.op_mapping[operation]
            self.apply_operation(op_type, position)
            
            # 检查是否获胜
            if self.check_win():
                self.game_over = True
                return f"My Move: {operation} {position}", "Win\n" + self.state_to_string()
                
            return f"My Move: {operation} {position}", self.state_to_string()
            
        except (ValueError, IndexError) as e:
            self.game_over = True
            return "Invalid", f"Error: {str(e)}"
            
    def is_complete(self, result: str) -> bool:
        """检查游戏是否结束"""
        return self.game_over

class RainbowCandyHandler(GameHandler):
    def __init__(self, size: int, devices: Dict[str,str], target: str):
        self.size = size
        self.devices = devices
        self.target = target
        
        # 初始化状态
        self.current_pos = [1,1]  # 起始位置
        self.current_color = "W"  # 初始白色
        self.game_over = False
        
        # 移动方向映射
        self.directions = {
            "N": [-1,0],
            "S": [1,0], 
            "W": [0,-1],
            "E": [0,1]
        }
        
    def get_new_color(self, color: str, device: str) -> str:
        """获取经过设备后的新颜色"""
        if device == "W":
            return "W"
        elif device in ["R", "G", "B"]:
            if color == "W":  # 只有白色可以被染色
                return device
            elif color in ["R", "G", "B"]:  # 基础颜色可以混合
                # 颜色混合规则
                color_mix = {
                    ("R","G"): "Y",
                    ("G","B"): "C",
                    ("R","B"): "P" 
                }
                colors = tuple(sorted([color, device]))
                return color_mix.get(colors, color)
            # 混合颜色不能被染色机改变
            return color
        return color
        
    def parse_response(self, generated_text: str) -> Tuple[str, str]:
        """解析玩家的移动并返回新状态"""
        match = re.search(r'My Move:\s*([NSEW])', generated_text)
        if not match:
            self.game_over = True
            return "Invalid", "Invalid format. Use 'My Move: X' where X is N/S/E/W"
            
        try:
            direction = match.group(1)
            
            # 计算新位置
            dx, dy = self.directions[direction]
            new_x = self.current_pos[0] + dx
            new_y = self.current_pos[1] + dy
            
            # 检查是否超出边界
            if not (1 <= new_x <= self.size and 1 <= new_y <= self.size):
                self.game_over = True
                return "Invalid", "Invalid move: out of bounds"
                
            # 更新位置
            self.current_pos = [new_x, new_y]
            
            # 获取新位置的设备并更新颜色
            device = self.devices[f"{new_x},{new_y}"]
            self.current_color = self.get_new_color(self.current_color, device)
            
            # 检查是否到达终点
            if new_x == self.size and new_y == self.size:
                if self.current_color == self.target:
                    self.game_over = True
                    return direction, "WIN"  # 保持输入格式一致
                else:
                    return direction, f"{self.current_color}"  # 返回最终颜色
            
            # 返回新的颜色状态
            return direction, self.current_color
            
        except KeyError as e:
            self.game_over = True
            return "Invalid", f"Error: {str(e)}"
            
    def is_complete(self, result: str) -> bool:
        """检查游戏是否结束"""
        return self.game_over

def get_game_handler(game_type: str, question: Dict) -> GameHandler:
    if game_type == "RainbowCandy":
        graph = question["graph"]
        return RainbowCandyHandler(
            size=graph["size"],
            devices=graph["devices"],
            target=graph["target"]
        )
    elif game_type == "ChemicalSynthesis":
        return ChemicalSynthesisHandler(
            initial_compounds=question["initial_compounds"],
            target_compound=question["target_compound"]
        )
    elif game_type == "ColorMagic":
        return ColorMagicHandler(
            size=question["graph"]["size"],
            initial_state=question["graph"]["initial_state"],
            operations=question["graph"]["operations"]
        )
    elif game_type == "MagneticField":
        return MagneticFieldHandler(
            size=question["graph"]["size"],
            grid=question["graph"]["grid"]
        )
    elif game_type == "DarkMazeExplorer":
        return DarkMazeHandler(
            grid_size=question["scale"],
            maze=question["maze"]
        )
    elif game_type == "SafepathFinder":
        return SafepathFinderHandler(
            grid_size=question["scale"],
            traps=question["traps"]
        )
    elif game_type == "FindBiggest":
        return FindBiggestHandler(
            grid_size=question["graph"]["grid_size"],
            treasures=question["graph"]["treasures"]
        )

    elif game_type == "CactusSearch":
        return CactusSearchHandler(
            n=question["scale"],
            graph=question["graph"]
        )
    elif game_type == "VladikMaze":
        return VladikMazeHandler(
            n=question["scale"],  # 行数
            grids=question["grids"]  # 网格布局
        )
    elif game_type == "PalindromeConstruction5":
        return PalindromeConstructionHandler(
            target=question["initial_data"],
            scale=question["scale"],
            turns=question["turns"]
        )
    elif game_type == "PalindromeConstruction10":
        return PalindromeConstructionHandler(
            target=question["initial_data"],
            scale=question["scale"],
            turns=question["turns"]
        )
    elif game_type == "PalindromeConstruction15":
        return PalindromeConstructionHandler(
            target=question["initial_data"],
            scale=question["scale"],
            turns=question["turns"]
        )
    elif game_type == "TreasureHunt":
        return TreasureHuntHandler(
            n=question["scale"],
            graph=question["graph"]
        )
    elif game_type == "XORBreaking":
        return XORBreakHandler(
            n=question["initial_number"]
        )
    elif game_type == "PizzaSlice":
        return PizzaSliceHandler(
            n=question["scale"],
            points=question["points"]
        )
    elif game_type == "BeeChase":
        return BeeChaseHandler(
            n=question["scale"],
            edges=question["graph"]
        )

    elif game_type == "ZigzagGraph":
        return ZigzagGraphHandler(
            n=question["scale"],
            edge_weights=question["edge_weights"]
        )
    elif game_type == "DecreasingGame":
        return DecreasingGameHandler(
            initial_list=question["initial_list"],
            first_choice=question["first_choice"]
        )
    elif game_type == "AssiutGuess":
        return AssiutChessHandler(
            board_size=question["scale"],
            initial_position=question["initial_position"]
        )
    elif game_type == "GridSum":
        return GridSumHandler(
            n=question["scale"][0],
            m=question["scale"][1],
            initial_grid=question["initial_grid"]
        )
    elif game_type == "GridColoring":
        return GridColoringHandler(
            size=question["scale"],
            colored_cells=question["colored_cells"],
            max_color=question["scale"] * 2
        )
    elif game_type == "PaperNumber":
        return PaperNumberHandler(
            num_papers=question["scale"],
            max_number=question["max_number"],  # 根据题目规则
            turns=question["turns"],
            initial_value=question["initial_value"]
        )
    elif game_type == "KnightBattle":
        return KnightBattleHandler(
            board_size=question["scale"],
            white_start=question["answer"]["white_start"],
            black_start=question["answer"]["black_start"],
            white_target=question["answer"]["white_target"],
            black_target=question["answer"]["black_target"]
        )
    elif game_type == "FindHidden":
        return HiddenNumberHandler(answer=question["answer"])
    elif game_type == "AttendanceCheck":
        return AttendanceCheckHandler(answer=question["answer"])
    elif game_type == "RotaryLock":
        return RotaryLockHandler(
            answer=question["answer"],  
            n=question["n"],        
            m=question["m"]                     
        )
    elif game_type == "MahjongDetective":
        return MahjongDetectiveHandler(
            answer=question["answer"],
            n=question["scale"]
        )
    elif game_type == "PermutationDiscovery":
        return PermutationDiscoveryHandler(
            p=question["p"],
            q=question["q"]
        )
    elif game_type == "ZeroFinding":
        return ZeroFindingHandler(
            binary_list=question["list"],
            k=question["k"],
            answer=question["answer"]
        )
    elif game_type == "MimicHunt":
        return MimicHuntHandler(
            objects=question["list"],
            mimic_pos=question["answer"]
        )
    elif game_type == "TrainPursuit":
        return TrainPursuitHandler(
            initial_position=question["answer"],
            n=question["n"],
            k=question["k"]
        )
    elif game_type == "CircleFinding":
        return CircleQueryHandler(
            center=question["center"],
            radius=question["radius"]
        )
    elif game_type == "MedianQuery":
        return MedianQueryHandler(
            list_values=question["list"],
            answer=question["answer"]
        )
    elif game_type == "BitCompare":
        return BitCompareHandler(
            list_values=question["list"],
            answer=question["answer"]
        )
    elif game_type == "ListQuery":
        return LinkedListHandler(
            linked_list=question["list"],
            answer=question["answer"]
        )
    elif game_type == "BitQuery":
        return BitQueryHandler(answer=question["answer"])
    elif game_type == "LegendaryTree":
        return LegendaryTreeHandler(answer=question["answer"])
    elif game_type == "GeoGame":
        return GeoGameHandler(
            starting_point=question["starting_point"],
            available_points=question["available_points"],
            turns=question["turns"]
        )
    elif game_type == "BitGuessing":
        return BitGuessingHandler(answer=question["answer"])
    elif game_type == "RPD":
        return RPDHandler(
            answer=question["answer"],
            k=question["k"],
            min_value=question["min_value"],
            max_value=question["max_value"]
        )
    elif game_type == "Wordle":
        return WordleHandler(answer=question["answer"])
    elif game_type == "FindTheImpostors":
        return ImpostorsHandler(answer=question["answer"])
    elif game_type == "MinMax":
        return MinMaxHandler(
            array=question["answer"],     # 数组，如"52877"
            min_pos=question["min_pos"],  # 最小值位置
            max_pos=question["max_pos"]   # 最大值位置
        )
    elif game_type == "GuessMax":
        return GuessMaxHandler(
            array=question["array"],
            subsets=question["subsets"],
            answer=question["answer"]
        )
    else:
        raise ValueError(f"Unknown game type: {game_type}")
