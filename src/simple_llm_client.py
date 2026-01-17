"""
Simple Model Wrapper for Chat Endpoint
Uses Portkey with @provider syntax for routing
"""

import os
from portkey_ai import Portkey

# Model name mapping to Portkey format (from config.py)
MODEL_MAP = {
    'gpt': '@openai/gpt-4o',
    'gemini': '@google/gemini-1.5-flash',  # Will work if Google virtual key is configured
    'claude': '@anthropic/claude-sonnet-4-20250514'
}

class SimpleLLMClient:
    """Simple LLM client for chat endpoint using Portkey"""
    
    def __init__(self, model_name: str, api_key: str = None):
        """
        Initialize with simple model name.
        
        Args:
            model_name: Simple name like 'gpt', 'claude', 'gemini'
            api_key: Portkey API key (optional, loads from env)
        """
        if api_key is None:
            api_key = os.getenv("PORTKEY_API_KEY")
            if not api_key:
                raise ValueError("PORTKEY_API_KEY not found")
        
        self.simple_name = model_name
        self.portkey_model = MODEL_MAP.get(model_name, model_name)
        self.portkey = Portkey(api_key=api_key)
    
    def generate(self, prompt: str, max_tokens: int = 500):
        """
        Generate response using Portkey.
        
        Returns:
            Tuple of (response_text, metadata)
        """
        import time
        start_time = time.time()
        
        try:
            messages = [
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": prompt}
            ]
            
            # Use Portkey's @provider/model syntax
            response = self.portkey.chat.completions.create(
                model=self.portkey_model,
                messages=messages,
                max_tokens=max_tokens
            )
            
            latency_ms = int((time.time() - start_time) * 1000)
            response_text = response.choices[0].message.content
            
            usage = response.usage if hasattr(response, 'usage') else None
            tokens_in = usage.prompt_tokens if usage else 0
            tokens_out = usage.completion_tokens if usage else 0
            
            # Simple cost estimate
            cost = ((tokens_in + tokens_out) / 1000) * 0.01
            
            metadata = {
                "latency_ms": latency_ms,
                "tokens_input": tokens_in,
                "tokens_output": tokens_out,
                "total_tokens": tokens_in + tokens_out,
                "cost_usd": cost,
                "model": self.portkey_model
            }
            
            return response_text, metadata
            
        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            return None, {
                "latency_ms": latency_ms,
                "tokens_input": 0,
                "tokens_output": 0,
                "total_tokens": 0,
                "cost_usd": 0,
                "error": str(e)
            }
