"""
Universal Model Client
Unified interface for OpenAI, Anthropic, Google Gemini, and Groq APIs
"""

from openai import OpenAI
from anthropic import Anthropic
import google.generativeai as genai
from groq import Groq
import time
from typing import Tuple, Dict, Any
from src.config import (
    OPENAI_API_KEY,
    ANTHROPIC_API_KEY,
    GOOGLE_API_KEY,
    GROQ_API_KEY,
    MODELS
)


class ModelClient:
    """Universal client for all LLM providers."""
    
    def __init__(self, model_name: str):
        """
        Initialize the appropriate API client based on model name.
        
        Args:
            model_name: Key from MODELS dict (e.g., 'gpt-4o', 'claude-sonnet-4')
        """
        self.model_name = model_name
        self.model_config = MODELS.get(model_name)
        
        if not self.model_config:
            raise ValueError(f"Unknown model: {model_name}")
        
        self.provider = self.model_config["provider"]
        
        # Initialize the appropriate client
        if self.provider == "openai":
            self.client = OpenAI(api_key=OPENAI_API_KEY)
        elif self.provider == "anthropic":
            self.client = Anthropic(api_key=ANTHROPIC_API_KEY)
        elif self.provider == "google":
            genai.configure(api_key=GOOGLE_API_KEY)
            self.client = genai.GenerativeModel(self.model_config.get("model_id", "gemini-2.0-flash-exp"))
        elif self.provider == "groq":
            self.client = Groq(api_key=GROQ_API_KEY)
    
    def generate(self, prompt: str, max_tokens: int = 1024, temperature: float = 0.7) -> Tuple[str, Dict[str, Any]]:
        """
        Generate a response from the model.
        
        Args:
            prompt: The input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
        
        Returns:
            Tuple of (response_text, metadata_dict)
            Metadata includes: latency_ms, tokens_input, tokens_output, refused
        """
        start_time = time.time()
        
        try:
            if self.provider == "openai":
                response_text, metadata = self._call_openai(prompt, max_tokens, temperature)
            elif self.provider == "anthropic":
                response_text, metadata = self._call_anthropic(prompt, max_tokens, temperature)
            elif self.provider == "google":
                response_text, metadata = self._call_google(prompt, max_tokens, temperature)
            elif self.provider == "groq":
                response_text, metadata = self._call_groq(prompt, max_tokens, temperature)
            else:
                raise ValueError(f"Unknown provider: {self.provider}")
            
            # Calculate latency
            latency_ms = int((time.time() - start_time) * 1000)
            metadata["latency_ms"] = latency_ms
            
            # Detect refusals
            metadata["refused"] = self._is_refusal(response_text)
            
            return response_text, metadata
            
        except Exception as e:
            # Return failed metadata on error
            latency_ms = int((time.time() - start_time) * 1000)
            return None, {
                "latency_ms": latency_ms,
                "tokens_input": 0,
                "tokens_output": 0,
                "refused": False,
                "error": str(e)
            }
    
    def _call_openai(self, prompt: str, max_tokens: int, temperature: float) -> Tuple[str, Dict]:
        """Call OpenAI API."""
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        response_text = response.choices[0].message.content
        
        metadata = {
            "tokens_input": response.usage.prompt_tokens,
            "tokens_output": response.usage.completion_tokens,
        }
        
        return response_text, metadata
    
    def _call_anthropic(self, prompt: str, max_tokens: int, temperature: float) -> Tuple[str, Dict]:
        """Call Anthropic API."""
        model_id = self.model_config.get("model_id", "claude-sonnet-4-20250514")
        
        response = self.client.messages.create(
            model=model_id,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_text = response.content[0].text
        
        metadata = {
            "tokens_input": response.usage.input_tokens,
            "tokens_output": response.usage.output_tokens,
        }
        
        return response_text, metadata
    
    def _call_google(self, prompt: str, max_tokens: int, temperature: float) -> Tuple[str, Dict]:
        """Call Google Gemini API."""
        generation_config = {
            "max_output_tokens": max_tokens,
            "temperature": temperature,
        }
        
        response = self.client.generate_content(
            prompt,
            generation_config=generation_config
        )
        
        response_text = response.text
        
        # Gemini doesn't always provide token counts, estimate if needed
        try:
            tokens_input = response.usage_metadata.prompt_token_count
            tokens_output = response.usage_metadata.candidates_token_count
        except:
            # Rough estimation: ~4 chars per token
            tokens_input = len(prompt) // 4
            tokens_output = len(response_text) // 4
        
        metadata = {
            "tokens_input": tokens_input,
            "tokens_output": tokens_output,
        }
        
        return response_text, metadata
    
    def _call_groq(self, prompt: str, max_tokens: int, temperature: float) -> Tuple[str, Dict]:
        """Call Groq API (Llama models)."""
        model_id = self.model_config.get("model_id", "llama-3.3-70b-versatile")
        
        response = self.client.chat.completions.create(
            model=model_id,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        response_text = response.choices[0].message.content
        
        metadata = {
            "tokens_input": response.usage.prompt_tokens,
            "tokens_output": response.usage.completion_tokens,
        }
        
        return response_text, metadata
    
    def _is_refusal(self, text: str) -> bool:
        """
        Detect if the response is a refusal.
        
        Args:
            text: Response text to check
        
        Returns:
            True if the response appears to be a refusal
        """
        if not text:
            return False
        
        text_lower = text.lower()
        
        # Common refusal phrases
        refusal_phrases = [
            "i cannot",
            "i can't",
            "i apologize",
            "i'm sorry",
            "i am sorry",
            "i'm not able",
            "i am not able",
            "i don't have the ability",
            "i cannot assist",
            "i can't help",
            "i'm unable to",
            "i am unable to",
            "as an ai",
            "as a language model",
            "i don't feel comfortable",
            "i'm not comfortable",
            "against my guidelines",
            "not appropriate",
            "i shouldn't"
        ]
        
        for phrase in refusal_phrases:
            if phrase in text_lower:
                return True
        
        return False
    
    def calculate_cost(self, tokens_input: int, tokens_output: int) -> float:
        """
        Calculate cost for token usage.
        
        Args:
            tokens_input: Number of input tokens
            tokens_output: Number of output tokens
        
        Returns:
            Cost in USD
        """
        input_cost = (tokens_input / 1000) * self.model_config["input_cost"]
        output_cost = (tokens_output / 1000) * self.model_config["output_cost"]
        
        return round(input_cost + output_cost, 6)
