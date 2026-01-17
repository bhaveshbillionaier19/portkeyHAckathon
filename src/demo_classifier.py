def demo_classify(text: str) -> str:
    """
    Simple keyword-based classification for demo.
    Maps to evaluation result categories: knowledge, math, code, business
    
    Args:
        text: Input text to classify
        
    Returns:
        Category string matching evaluation results
    """
    text_lower = text.lower()
    
    # Math keywords and patterns - CHECK FIRST
    if any(word in text_lower for word in ['math', 'calculate', 'equation', 'solve', 'algebra', 'geometry']):
        return 'math'
    # Check for multiplication/division/operators
    if any(op in text for op in ['*', '×', '/', '÷', '+', '-', '=']):
        return 'math'
    # Check for patterns like 2x2, 3x5, etc (number X number)
    import re
    if re.search(r'\d+\s*[xX]\s*\d+', text):
        return 'math'
    # Check for hexadecimal, binary, decimal
    if any(word in text_lower for word in ['hexa', 'hex', 'binary', 'decimal', 'octal']):
        return 'math'
    
    # Code keywords
    if any(word in text_lower for word in ['code', 'python', 'javascript', 'program', 'function', 'class', 'def', 'algorithm', 'write code']):
        return 'code'
    
    # Business keywords
    if any(word in text_lower for word in ['business', 'market', 'strategy', 'sales', 'profit', 'revenue', 'company']):
        return 'business'
    
    # Science/Knowledge keywords - map to 'knowledge' category
    if any(word in text_lower for word in ['dna', 'photosynthesis', 'biology', 'chemistry', 'physics', 'science']):
        return 'knowledge'
    
    # Default to knowledge (general questions)
    return 'knowledge'
