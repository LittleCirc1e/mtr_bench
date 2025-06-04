import re

class FindTheImpostors:
    def __init__(self, answer: str):
        """
        Initialize with answer string (e.g., "110101" where 1=crewmate, 0=impostor)
        """
        self.answer = answer
        self.impostor_indices = [i+1 for i, val in enumerate(answer) if val == '0']
    
    def parse_query(self, generated_text: str) -> tuple[str, str]:
        """Extract and validate query/answer from generated text"""
        # Check for query format
        query_match = re.search(r'My Query:\s*([1-12]),([1-12]),([1-12])', generated_text)
        if query_match:
            players = sorted([int(query_match.group(1)), int(query_match.group(2)), int(query_match.group(3))])
            # Validate query
            if len(set(players)) != 3:
                return "Invalid", "-1 (Query must contain 3 different players)"
            return "Query", self._evaluate_query(players)
        
        # Check for answer format
        answer_match = re.search(r'My Answer:\s*((?:[1-12],)*[1-12])', generated_text)
        if answer_match:
            try:
                answer = sorted([int(x) for x in answer_match.group(1).split(',')])
                # Validate answer length (2-4 impostors)
                if not (2 <= len(answer) <= 4):
                    return "Invalid", "0 (Number of impostors must be 2-4)"
                return "Answer", self._evaluate_answer(answer)
            except:
                return "Invalid", "0 (Invalid answer format)"
        
        return "Invalid", "-1 (Response must be 'My Query: a,b,c' or 'My Answer: x1,x2..')"
    
    def _evaluate_query(self, players: list[int]) -> str:
        """Evaluate a query about 3 players (0=more impostors, 1=more crewmates)"""
        impostor_count = sum(1 for p in players if self.answer[p-1] == '0')
        crewmate_count = 3 - impostor_count
        return "0" if impostor_count > crewmate_count else "1"
    
    def _evaluate_answer(self, submitted_answer: list[int]) -> str:
        """Check if submitted answer matches actual impostors (1=correct, 0=wrong)"""
        return "1" if set(submitted_answer) == set(self.impostor_indices) else "0"

# 使用示例
if __name__ == "__main__":
    game = FindTheImpostors(answer="110101")  # 玩家1,3,5是impostor
    
    # 测试查询
    print(game.parse_query("My Query: 1,2,3"))  # 应返回 ("Query", "0") (1和3是impostor，多于crewmate)
    print(game.parse_query("My Query: 2,4,6"))  # 应返回 ("Query", "1") (全是crewmate)
    
    # 测试答案
    print(game.parse_query("My Answer: 1,3,5"))  # 应返回 ("Answer", "1") (正确)
    print(game.parse_query("My Answer: 1,2,3"))  # 应返回 ("Answer", "0") (错误)
    
    # 测试无效输入
    print(game.parse_query("My Query: 1,1,2"))  # 应返回 ("Invalid", "-1...")
    print(game.parse_query("Random text"))      # 应返回 ("Invalid", "-1...")