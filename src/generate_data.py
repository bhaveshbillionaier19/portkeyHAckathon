"""
Data Generation Script
Generates 50 diverse prompts for each category using Claude
"""

import json
import os
from src.models import ModelClient
from src.config import CATEGORIES, DATA_DIR, PROMPTS_FILE

def generate_prompts_for_category(category: str, count: int = 50) -> list:
    """
    Generate diverse prompts for a specific category using Claude.
    
    Args:
        category: The category name (e.g., 'code', 'math', 'creative')
        count: Number of prompts to generate
    
    Returns:
        List of prompt strings
    """
    print(f"\n🎯 Generating {count} prompts for category: {category}")
    print("-" * 60)
    
    # Use Claude Sonnet 4 for generation
    client = ModelClient("claude-sonnet-4")
    
    generation_prompt = f"""Generate exactly {count} diverse, challenging prompts for {category} tasks.

CATEGORY: {category}

REQUIREMENTS:
- Each prompt should be a realistic user query
- Vary difficulty from beginner to expert
- Cover different sub-domains within {category}
- Make them practical and useful
- Each prompt should be 1-3 sentences

OUTPUT FORMAT:
Return ONLY a JSON array of strings, nothing else. No markdown, no explanations.
Example format: ["prompt 1", "prompt 2", "prompt 3"]

Generate {count} prompts now:"""

    try:
        response_text, metadata = client.generate(
            prompt=generation_prompt,
            max_tokens=4000,
            temperature=0.8  # Higher temperature for diversity
        )
        
        if not response_text:
            print(f"❌ Failed to generate prompts: {metadata.get('error')}")
            return []
        
        # Parse JSON response
        # Handle potential markdown code blocks
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        prompts = json.loads(response_text)
        
        print(f"✅ Generated {len(prompts)} prompts")
        print(f"📊 Cost: ${client.calculate_cost(metadata['tokens_input'], metadata['tokens_output']):.4f}")
        print(f"⏱️  Latency: {metadata['latency_ms']}ms")
        
        # Show sample
        if prompts:
            print(f"\nSample prompt: {prompts[0][:100]}...")
        
        return prompts
        
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse JSON response: {e}")
        print(f"Response preview: {response_text[:200]}...")
        return []
    except Exception as e:
        print(f"❌ Error: {e}")
        return []


def generate_all_prompts() -> list:
    """
    Generate prompts for all categories.
    
    Returns:
        List of prompt dictionaries with category labels
    """
    all_prompts = []
    
    print("=" * 60)
    print("PROMPT GENERATION STARTING")
    print("=" * 60)
    
    for category in CATEGORIES:
        prompts = generate_prompts_for_category(category, count=50)
        
        # Add category label to each prompt
        for prompt_text in prompts:
            all_prompts.append({
                "prompt": prompt_text,
                "category": category
            })
    
    print("\n" + "=" * 60)
    print(f"GENERATION COMPLETE: {len(all_prompts)} total prompts")
    print("=" * 60)
    
    # Show category breakdown
    print("\nCategory breakdown:")
    category_counts = {}
    for p in all_prompts:
        cat = p["category"]
        category_counts[cat] = category_counts.get(cat, 0) + 1
    
    for cat, count in category_counts.items():
        print(f"  - {cat}: {count} prompts")
    
    return all_prompts


def save_prompts(prompts: list):
    """
    Save prompts to JSON file.
    
    Args:
        prompts: List of prompt dictionaries
    """
    # Ensure data directory exists
    os.makedirs(DATA_DIR, exist_ok=True)
    
    with open(PROMPTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(prompts, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Saved to: {PROMPTS_FILE}")


def main():
    """Main execution."""
    prompts = generate_all_prompts()
    
    if prompts:
        save_prompts(prompts)
        print("\n✅ Data generation complete!")
    else:
        print("\n❌ No prompts generated")


if __name__ == "__main__":
    main()
