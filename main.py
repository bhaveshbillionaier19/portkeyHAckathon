"""
Main Replay Engine
Runs all prompts through all models and saves responses
"""

import json
import os
from typing import List, Dict, Any
from src.models import ModelClient
from src.categorizer import PromptCategorizer
from src.utils import load_prompts, save_json, ensure_data_dir
from src.config import MODELS, RESPONSES_FILE


class ReplayEngine:
    """Engine for replaying prompts across multiple models."""
    
    def __init__(self):
        """Initialize the replay engine."""
        self.categorizer = PromptCategorizer()
        self.model_clients = {}
        
        # Initialize all model clients
        for model_name in MODELS.keys():
            try:
                self.model_clients[model_name] = ModelClient(model_name)
                print(f"✅ Initialized {model_name}")
            except Exception as e:
                print(f"⚠️  Failed to initialize {model_name}: {e}")
    
    def run_prompt_through_models(self, prompt: str, category: str) -> Dict[str, Any]:
        """
        Run a single prompt through all models.
        
        Args:
            prompt: The prompt text
            category: The prompt category
        
        Returns:
            Dictionary with prompt, category, and responses from all models
        """
        result = {
            "prompt": prompt,
            "category": category,
            "responses": {}
        }
        
        for model_name, client in self.model_clients.items():
            try:
                # Generate response
                response_text, metadata = client.generate(prompt)
                
                # Calculate cost
                cost = 0.0
                if response_text and "error" not in metadata:
                    cost = client.calculate_cost(
                        metadata.get("tokens_input", 0),
                        metadata.get("tokens_output", 0)
                    )
                
                # Store response data
                result["responses"][model_name] = {
                    "text": response_text,
                    "cost": cost,
                    "latency_ms": metadata.get("latency_ms", 0),
                    "tokens_input": metadata.get("tokens_input", 0),
                    "tokens_output": metadata.get("tokens_output", 0),
                    "refused": metadata.get("refused", False),
                    "error": metadata.get("error")
                }
                
            except Exception as e:
                print(f"⚠️  Error with {model_name}: {e}")
                result["responses"][model_name] = {
                    "text": None,
                    "cost": 0.0,
                    "latency_ms": 0,
                    "tokens_input": 0,
                    "tokens_output": 0,
                    "refused": False,
                    "error": str(e)
                }
        
        return result
    
    def replay_all(self, prompts: List[Dict[str, Any]], save_interval: int = 50):
        """
        Replay all prompts through all models.
        
        Args:
            prompts: List of prompt dictionaries
            save_interval: Save results every N prompts
        """
        ensure_data_dir()
        
        total_prompts = len(prompts)
        results = []
        
        print("\n" + "=" * 70)
        print(f"REPLAY ENGINE STARTING - {total_prompts} prompts x {len(self.model_clients)} models")
        print("=" * 70)
        
        for i, prompt_data in enumerate(prompts, 1):
            prompt_text = prompt_data.get("prompt", "")
            category = prompt_data.get("category", "unknown")
            
            print(f"\n[{i}/{total_prompts}] Processing: {prompt_text[:60]}...")
            print(f"Category: {category}")
            
            # Run through all models
            result = self.run_prompt_through_models(prompt_text, category)
            results.append(result)
            
            # Show quick summary
            for model_name, response_data in result["responses"].items():
                status = "✅" if response_data["text"] else "❌"
                cost = response_data["cost"]
                latency = response_data["latency_ms"]
                print(f"  {status} {model_name}: ${cost:.6f}, {latency}ms")
            
            # Save incrementally
            if i % save_interval == 0:
                print(f"\n💾 Saving checkpoint at {i} prompts...")
                save_json(RESPONSES_FILE, results)
                print(f"✅ Saved to {RESPONSES_FILE}")
        
        # Final save
        print("\n💾 Saving final results...")
        save_json(RESPONSES_FILE, results)
        
        print("\n" + "=" * 70)
        print("REPLAY ENGINE COMPLETE")
        print("=" * 70)
        
        # Show summary statistics
        self._print_summary(results)
    
    def _print_summary(self, results: List[Dict[str, Any]]):
        """Print summary statistics."""
        total_prompts = len(results)
        
        # Calculate totals per model
        model_stats = {}
        for model_name in self.model_clients.keys():
            total_cost = 0.0
            successful = 0
            refused = 0
            total_latency = 0
            
            for result in results:
                response_data = result["responses"].get(model_name, {})
                if response_data.get("text"):
                    successful += 1
                total_cost += response_data.get("cost", 0.0)
                if response_data.get("refused"):
                    refused += 1
                total_latency += response_data.get("latency_ms", 0)
            
            avg_latency = total_latency / total_prompts if total_prompts > 0 else 0
            
            model_stats[model_name] = {
                "total_cost": total_cost,
                "successful": successful,
                "refused": refused,
                "avg_latency_ms": int(avg_latency)
            }
        
        print("\n📊 Summary Statistics:")
        print(f"Total prompts processed: {total_prompts}")
        print(f"Total API calls: {total_prompts * len(self.model_clients)}")
        print("\nPer-Model Stats:")
        
        for model_name, stats in model_stats.items():
            print(f"\n  {model_name}:")
            print(f"    - Total cost: ${stats['total_cost']:.4f}")
            print(f"    - Successful: {stats['successful']}/{total_prompts}")
            print(f"    - Refused: {stats['refused']}")
            print(f"    - Avg latency: {stats['avg_latency_ms']}ms")
        
        # Grand total cost
        grand_total = sum(s["total_cost"] for s in model_stats.values())
        print(f"\n💰 Grand Total Cost: ${grand_total:.4f}")


def main():
    """Main execution."""
    print("=" * 70)
    print("COST-QUALITY OPTIMIZER - REPLAY ENGINE")
    print("=" * 70)
    
    # Load prompts
    print("\n📂 Loading prompts...")
    prompts = load_prompts()
    
    if not prompts:
        print("❌ No prompts found in data/prompts.json")
        print("Run 'python src/generate_data.py' first to generate prompts")
        return
    
    print(f"✅ Loaded {len(prompts)} prompts")
    
    # Check if prompts need categorization
    needs_categorization = any("category" not in p or not p["category"] for p in prompts)
    
    if needs_categorization:
        print("\n🏷️  Categorizing prompts...")
        categorizer = PromptCategorizer()
        prompt_texts = [p.get("prompt", "") for p in prompts]
        categories = categorizer.categorize_batch(prompt_texts)
        
        # Update prompts with categories
        for i, category in enumerate(categories):
            prompts[i]["category"] = category
        
        # Save updated prompts
        from src.utils import save_prompts
        save_prompts(prompts)
        print("✅ Categorization complete")
    
    # Initialize and run replay engine
    print("\n🚀 Initializing replay engine...")
    engine = ReplayEngine()
    
    # Ask for confirmation
    total_calls = len(prompts) * len(engine.model_clients)
    print(f"\n⚠️  About to make {total_calls} API calls")
    print(f"   ({len(prompts)} prompts × {len(engine.model_clients)} models)")
    
    # Auto-proceed for now (in production, add confirmation)
    print("\nStarting replay...\n")
    
    # Run the replay
    engine.replay_all(prompts, save_interval=50)
    
    print("\n✅ All done! Results saved to data/responses.json")


if __name__ == "__main__":
    main()
