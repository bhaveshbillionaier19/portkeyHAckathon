"""
Prompt Categorizer
Auto-categorizes prompts using Claude Sonnet
"""

import json
from typing import List
from src.models import ModelClient
from src.config import CATEGORIES


class PromptCategorizer:
    """Categorizes prompts into predefined categories using Claude."""
    
    def __init__(self):
        """Initialize the categorizer with Claude Sonnet 4."""
        self.client = ModelClient("claude-sonnet-4")
        self.categories = CATEGORIES
    
    def categorize_batch(self, prompts: List[str], batch_size: int = 20) -> List[str]:
        """
        Categorize a batch of prompts.
        
        Args:
            prompts: List of prompt strings to categorize
            batch_size: Number of prompts to process at once
        
        Returns:
            List of category strings corresponding to input prompts
        """
        all_categories = []
        
        # Process in batches to avoid token limits
        for i in range(0, len(prompts), batch_size):
            batch = prompts[i:i + batch_size]
            batch_categories = self._categorize_single_batch(batch)
            all_categories.extend(batch_categories)
            
            print(f"Processed {min(i + batch_size, len(prompts))}/{len(prompts)} prompts")
        
        return all_categories
    
    def _categorize_single_batch(self, prompts: List[str]) -> List[str]:
        """
        Categorize a single batch of prompts.
        
        Args:
            prompts: List of prompt strings
        
        Returns:
            List of category strings
        """
        # Create numbered list of prompts
        prompts_text = "\n".join([f"{i+1}. {p}" for i, p in enumerate(prompts)])
        
        categorization_prompt = f"""Categorize each of the following prompts into EXACTLY ONE of these categories:
{', '.join(self.categories)}

CATEGORY DEFINITIONS:
- code: Programming, software development, debugging, algorithms
- math: Mathematical problems, calculations, equations, statistics
- creative: Creative writing, storytelling, poetry, brainstorming
- analysis: Data analysis, research, critical thinking, evaluation
- knowledge: Factual questions, explanations, definitions, how-to guides
- business: Business strategy, marketing, sales, management, finance

PROMPTS TO CATEGORIZE:
{prompts_text}

CRITICAL INSTRUCTIONS:
1. Output ONLY a valid JSON array of category strings
2. The array must have EXACTLY {len(prompts)} elements
3. Each element must be one of: {', '.join(self.categories)}
4. No markdown, no explanations, no extra text
5. Order must match the input prompts (1st category for 1st prompt, etc.)

OUTPUT FORMAT:
["category1", "category2", "category3", ...]

Categorize now:"""

        try:
            response_text, metadata = self.client.generate(
                prompt=categorization_prompt,
                max_tokens=1000,
                temperature=0.1  # Low temperature for consistency
            )
            
            if not response_text:
                print(f"⚠️ Categorization failed: {metadata.get('error')}")
                return ["unknown"] * len(prompts)
            
            # Parse JSON response
            # Handle potential markdown code blocks
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            categories = json.loads(response_text)
            
            # Validate response
            if len(categories) != len(prompts):
                print(f"⚠️ Category count mismatch: got {len(categories)}, expected {len(prompts)}")
                # Pad or truncate
                if len(categories) < len(prompts):
                    categories.extend(["unknown"] * (len(prompts) - len(categories)))
                else:
                    categories = categories[:len(prompts)]
            
            # Validate each category
            validated_categories = []
            for cat in categories:
                if cat in self.categories:
                    validated_categories.append(cat)
                else:
                    print(f"⚠️ Invalid category '{cat}', defaulting to 'knowledge'")
                    validated_categories.append("knowledge")
            
            return validated_categories
            
        except json.JSONDecodeError as e:
            print(f"⚠️ Failed to parse JSON: {e}")
            print(f"Response preview: {response_text[:200]}...")
            return ["unknown"] * len(prompts)
        except Exception as e:
            print(f"⚠️ Categorization error: {e}")
            return ["unknown"] * len(prompts)
    
    def categorize_single(self, prompt: str) -> str:
        """
        Categorize a single prompt.
        
        Args:
            prompt: The prompt string
        
        Returns:
            Category string
        """
        categories = self.categorize_batch([prompt])
        return categories[0] if categories else "unknown"


# Convenience function
def categorize_prompts(prompts: List[str]) -> List[str]:
    """
    Categorize a list of prompts.
    
    Args:
        prompts: List of prompt strings
    
    Returns:
        List of category strings
    """
    categorizer = PromptCategorizer()
    return categorizer.categorize_batch(prompts)
