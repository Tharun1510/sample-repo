import re

def calculate_levenshtein_distance(s1: str, s2: str) -> float:
    """
    Calculates the Levenshtein distance between two strings and returns a similarity percentage.
    """
    if not s1 or not s2:
        return 0.0

    len_s1 = len(s1)
    len_s2 = len(s2)
    
    # Create the matrix
    dp = [[0 for _ in range(len_s2 + 1)] for _ in range(len_s1 + 1)]
    
    # Initialize matrix
    for i in range(len_s1 + 1):
        dp[i][0] = i
    for j in range(len_s2 + 1):
        dp[0][j] = j
        
    # Calculate distance
    for i in range(1, len_s1 + 1):
        for j in range(1, len_s2 + 1):
            if s1[i - 1] == s2[j - 1]:
                cost = 0
            else:
                cost = 1
            dp[i][j] = min(
                dp[i - 1][j] + 1,      # Deletion
                dp[i][j - 1] + 1,      # Insertion
                dp[i - 1][j - 1] + cost # Substitution
            )
            
    distance = dp[len_s1][len_s2]
    max_len = max(len_s1, len_s2)
    
    # Convert distance to similarity percentage
    if max_len == 0:
        return 100.0
    
    similarity = ((max_len - distance) / max_len) * 100
    return round(similarity, 2)

def calculate_cyclomatic_complexity(code_chunk: str) -> int:
    """
    Calculates a proxy for McCabe's Cyclomatic Complexity by counting control flow statements.
    Base complexity is 1. We add 1 for every branch.
    """
    if not code_chunk:
        return 1
        
    complexity = 1
    
    # Keywords that add a branch to the control flow graph
    branch_keywords = [
        r'\bif\b', 
        r'\belif\b', 
        r'\belse\b', 
        r'\bfor\b', 
        r'\bwhile\b', 
        r'\bcatch\b', 
        r'\bexcept\b',
        r'\bcase\b',
        r'&&', 
        r'\|\|', 
        r'\band\b', 
        r'\bor\b',
        r'\?' # Ternary
    ]
    
    for pattern in branch_keywords:
        matches = re.findall(pattern, code_chunk)
        complexity += len(matches)
        
    return complexity
