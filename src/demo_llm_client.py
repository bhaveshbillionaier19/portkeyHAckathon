"""
Demo LLM Client - Mock responses for hackathon demo
Works without Portkey virtual keys
"""

import time

# Mock responses for different categories
DEMO_RESPONSES = {
    'science': "DNA (deoxyribonucleic acid) is a molecule that carries genetic instructions for the development, functioning, growth and reproduction of all known organisms. It consists of two strands forming a double helix structure.",
    'math': "Let me help you with that calculation!\n\nFor mathematical operations and conversions:\n- I can perform arithmetic (addition, multiplication, division)\n- Convert between number systems (decimal, hexadecimal, binary)\n- Solve equations and formulas\n\nWhat specific calculation would you like me to help with?",
    'code': """def reverse_string(s):
    return s[::-1]

# Example usage:
text = "Hello World"
reversed_text = reverse_string(text)
print(reversed_text)  # Output: dlroW olleH""",
    'logic': "If A > B and B > C, then by the transitive property, A > C. This is a fundamental principle of logical reasoning.",
    'business': "To increase market share, focus on: 1) Customer retention through quality service, 2) Competitive pricing strategy, 3) Brand differentiation, 4) Digital marketing optimization.",
    'tech': "Cloud computing offers scalability, cost-efficiency, and flexibility. Major providers include AWS, Google Cloud, and Azure, each with unique strengths in different areas.",
    'home': "For energy-efficient homes, consider: LED lighting, smart thermostats, proper insulation, energy-star appliances, and solar panels for long-term savings.",
    'default': "This is a helpful response demonstrating the smart routing system. The classifier identified your prompt category and routed it to the optimal model."
}

class DemoLLMClient:
    """Demo client with mock responses for hackathon presentation"""
    
    def __init__(self, model_name: str, api_key: str = None):
        """
        Initialize demo client.
        
        Args:
            model_name: Model name ('gpt', 'claude', 'gemini')
            api_key: Not used in demo mode
        """
        self.model_name = model_name
        self.model_display = {
            'gpt': 'GPT-4o',
            'claude': 'Claude Sonnet 4',
            'gemini': 'Gemini 1.5 Flash'
        }.get(model_name, model_name)
    
    def generate(self, prompt: str, max_tokens: int = 500):
        """
        Generate mock response.
        
        Returns:
            Tuple of (response_text, metadata)
        """
        start_time = time.time()
        time.sleep(0.5)  # Simulate API latency
        
        # Determine category from prompt keywords
        prompt_lower = prompt.lower()
        category = 'default'
        
        # Greetings
        if prompt_lower.strip() in ['hi', 'hello', 'hey', 'greetings']:
            response_text = f"Hello! I'm your AI assistant powered by {self.model_display}. I can help you with science, coding, math, logic, business, and more. What would you like to know?"
            category = 'greeting'
        
        # Try to calculate simple math expressions
        elif category != 'greeting':
            import re
            # Replace 'x' with '*' for calculation
            calc_text = prompt.replace('x', '*').replace('X', '*')
            # Check if it's a simple math expression
            if re.match(r'^[\d\s\+\-\*/\(\)\.]+$', calc_text):
                try:
                    result = eval(calc_text)
                    response_text = f"The answer is: **{result}**\n\nCalculation: {prompt} = {result}"
                    category = 'math'
                except:
                    pass
        
        # If not calculated yet, use category responses
        if category != 'greeting' and 'response_text' not in locals():
            if any(word in prompt_lower for word in ['dna', 'photosynthesis', 'science', 'biology', 'chemistry']):
                category = 'science'
            elif any(word in prompt_lower for word in ['code', 'python', 'javascript', 'program', 'function']):
                category = 'code'
            elif any(word in prompt_lower for word in ['math', 'calculate', 'equation', 'solve']):
                category = 'math'
            elif any(word in prompt_lower for word in ['logic', 'reasoning', 'if', 'then']):
                category = 'logic'
            elif any(word in prompt_lower for word in ['business', 'market', 'strategy', 'sales']):
                category = 'business'
            
            response_text = DEMO_RESPONSES.get(category, DEMO_RESPONSES['default'])
        
        # Simulate realistic metrics
        tokens_in = len(prompt.split()) * 1.3
        tokens_out = len(response_text.split()) * 1.3
        latency_ms = int((time.time() - start_time) * 1000)
        
        # Cost varies by model
        cost_per_1k = {
            'gpt': 0.005,
            'claude': 0.003,
            'gemini': 0.002
        }.get(self.model_name, 0.003)
        
        cost = ((tokens_in + tokens_out) / 1000) * cost_per_1k
        
        metadata = {
            "latency_ms": latency_ms,
            "tokens_input": int(tokens_in),
            "tokens_output": int(tokens_out),
            "total_tokens": int(tokens_in + tokens_out),
            "cost_usd": round(cost, 6),
            "model": self.model_display
        }
        
        return response_text, metadata
