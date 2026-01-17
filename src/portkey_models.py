"""
Portkey Model Client
Unified client for Portkey-enabled models (Grok, Claude 4.5, GPT Realtime, etc.)
"""

import time
import os
from typing import Dict, Any, Tuple, Optional
from portkey_ai import Portkey


class PortkeyModelClient:
    """
    Client for Portkey AI models with unified interface.
    Supports: Grok Vision, Claude Sonnet 4.5, GPT Realtime, and more.
    """
    
    def __init__(self, model_name: str, api_key: str = None):
        """
        Initialize Portkey model client.
        
        Args:
            model_name: Name of the model ('gemini', 'claude', 'gpt')
            api_key: Portkey API key (optional, loads from env if not provided)
        """
        if api_key is None:
            api_key = os.getenv("PORTKEY_API_KEY")
            if not api_key:
                raise ValueError("PORTKEY_API_KEY not found in environment")
        self.model_name = model_name
        self.portkey = Portkey(api_key=api_key)
        self.provider = self._extract_provider(model_name)
    
    def _extract_provider(self, model_name: str) -> str:
        """Extract provider from Portkey model name."""
        if "@" in model_name:
            return model_name.split("@")[1].split("/")[0]
        return "unknown"
    
    def generate(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> Tuple[Optional[str], Dict[str, Any]]:
        """
        Generate response using Portkey model.
        
        Args:
            prompt: The input prompt
            max_tokens: Maximum tokens to generate
            temperature: Temperature for sampling
        
        Returns:
            Tuple of (response_text, metadata)
        """
        start_time = time.time()
        
        try:
            # Format messages for chat completion
            messages = [
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": prompt}
            ]
            
            # Call Portkey API
            response = self.portkey.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            # Calculate latency
            latency_ms = int((time.time() - start_time) * 1000)
            
            # Extract response
            response_text = response.choices[0].message.content
            
            # Get token usage
            usage = response.usage if hasattr(response, 'usage') else None
            tokens_input = usage.prompt_tokens if usage else 0
            tokens_output = usage.completion_tokens if usage else 0
            
            # Check for refusal
            refused = self._is_refusal(response_text)
            
            # Calculate cost
            cost_usd = self.calculate_cost(tokens_input, tokens_output)
            
            metadata = {
                "latency_ms": latency_ms,
                "tokens_input": tokens_input,
                "tokens_output": tokens_output,
                "total_tokens": tokens_input + tokens_output,
                "cost_usd": cost_usd,
                "refused": refused,
                "error": None,
                "provider": self.provider,
                "model": self.model_name
            }
            
            return response_text, metadata
        
        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            
            return None, {
                "latency_ms": latency_ms,
                "tokens_input": 0,
                "tokens_output": 0,
                "refused": False,
                "error": str(e),
                "provider": self.provider,
                "model": self.model_name
            }
    
    def _is_refusal(self, text: str) -> bool:
        """Check if response is a refusal."""
        if not text:
            return False
        
        refusal_phrases = [
            "i cannot", "i can't", "i'm not able",
            "i am not able", "i apologize", "sorry",
            "i'm sorry", "i am sorry", "against my",
            "i must decline", "i won't", "i will not",
            "cannot provide", "can't provide"
        ]
        
        text_lower = text.lower()
        return any(phrase in text_lower for phrase in refusal_phrases)
    
    def calculate_cost(self, tokens_input: int, tokens_output: int) -> float:
        """
        Calculate cost based on token usage.
        Note: Portkey pricing varies by provider, using estimates.
        """
        # Pricing estimates (per 1K tokens)
        pricing = {
            "grok": {"input": 0.00005, "output": 0.00015},
            "anthropic": {"input": 0.003, "output": 0.015},
            "openai": {"input": 0.0025, "output": 0.01},
            "google": {"input": 0.0, "output": 0.0},
        }
        
        provider_pricing = pricing.get(self.provider, {"input": 0.001, "output": 0.003})
        
        cost_input = (tokens_input / 1000) * provider_pricing["input"]
        cost_output = (tokens_output / 1000) * provider_pricing["output"]
        
        return cost_input + cost_output


# Example usage
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    api_key = os.getenv("PORTKEY_API_KEY", "")
    
    if not api_key:
        print("❌ PORTKEY_API_KEY not found in .env")
        exit(1)
    
    # Test all three models
    models = [
        "@grok/grok-vision-beta",
        "@anthropic/claude-sonnet-4-5-20250929",
        "@openai/gpt-realtime-mini-2025-10-06"
    ]
    
    test_prompt = "Explain the concept of machine learning in one sentence."
    
    print("=" * 70)
    print("TESTING PORTKEY MODELS")
    print("=" * 70)
    
    for model in models:
        print(f"\n📊 Testing {model}...")
        
        client = PortkeyModelClient(model, api_key)
        response, metadata = client.generate(test_prompt, max_tokens=100)
        
        if response:
            print(f"✅ Response: {response[:100]}...")
            print(f"   Latency: {metadata['latency_ms']}ms")
            print(f"   Tokens: {metadata['tokens_input']} in, {metadata['tokens_output']} out")
            print(f"   Cost: ${client.calculate_cost(metadata['tokens_input'], metadata['tokens_output']):.6f}")
        else:
            print(f"❌ Error: {metadata['error']}")
