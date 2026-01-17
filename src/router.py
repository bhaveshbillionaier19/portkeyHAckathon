"""
Smart Router
Intelligently routes prompts to optimal models based on analysis
"""

import json
from typing import Dict, Any, Tuple, Optional
from src.models import ModelClient
from src.categorizer import PromptCategorizer
from src.utils import load_json


class SmartRouter:
    """
    Routes prompts to optimal models based on analysis insights.
    
    Supports multiple routing strategies:
    - best_value: Maximize quality/cost ratio (default)
    - best_quality: Highest quality score
    - lowest_cost: Cheapest option
    - fastest: Lowest latency
    """
    
    def __init__(self, analysis_file: str = "data/analysis.json"):
        """
        Initialize the router with analysis data.
        
        Args:
            analysis_file: Path to analysis.json
        """
        print(f"🚀 Initializing Smart Router...")
        
        # Load analysis
        self.analysis = load_json(analysis_file)
        if not self.analysis:
            raise ValueError(f"Could not load analysis from {analysis_file}")
        
        # Initialize categorizer
        self.categorizer = PromptCategorizer()
        
        # Build routing tables for each strategy
        self.routing_tables = self._build_routing_tables()
        
        # Cache model clients
        self.model_clients = {}
        
        print(f"✅ Router initialized with {len(self.routing_tables['best_value'])} categories")
        self._print_routing_table()
    
    def _build_routing_tables(self) -> Dict[str, Dict[str, str]]:
        """
        Build routing lookup tables for each strategy.
        
        Returns:
            Dictionary mapping strategy -> (category -> model_name)
        """
        tables = {
            "best_value": {},
            "best_quality": {},
            "lowest_cost": {},
            "fastest": {}
        }
        
        category_winners = self.analysis.get("category_winners", {})
        
        for category, winners in category_winners.items():
            # Best value (quality/cost ratio)
            tables["best_value"][category] = winners["best_value"]["model"]
            
            # Best quality
            tables["best_quality"][category] = winners["best_quality"]["model"]
            
            # Lowest cost
            tables["lowest_cost"][category] = winners["lowest_cost"]["model"]
            
            # Fastest
            tables["fastest"][category] = winners["fastest"]["model"]
        
        return tables
    
    def _get_model_client(self, model_name: str) -> ModelClient:
        """
        Get or create a model client.
        
        Args:
            model_name: Name of the model
        
        Returns:
            ModelClient instance
        """
        if model_name not in self.model_clients:
            self.model_clients[model_name] = ModelClient(model_name)
        
        return self.model_clients[model_name]
    
    def route_and_respond(
        self,
        prompt: str,
        strategy: str = "best_value"
    ) -> Tuple[Optional[str], Dict[str, Any]]:
        """
        Route a prompt to the optimal model and get response.
        
        Args:
            prompt: The user's prompt
            strategy: Routing strategy ('best_value', 'best_quality', 'lowest_cost', 'fastest')
        
        Returns:
            Tuple of (response_text, metadata)
            Metadata includes: model, category, cost, latency, routing_reason
        """
        # Validate strategy
        if strategy not in self.routing_tables:
            raise ValueError(f"Unknown strategy '{strategy}'. Must be one of: {list(self.routing_tables.keys())}")
        
        # Step 1: Categorize the prompt
        category = self.categorizer.categorize_single(prompt)
        
        # Step 2: Look up the best model for this category
        routing_table = self.routing_tables[strategy]
        selected_model = routing_table.get(category)
        
        if not selected_model:
            # Fallback to overall best value if category not found
            overall_stats = self.analysis.get("overall_stats", {})
            if strategy == "best_value":
                selected_model = max(overall_stats.items(), key=lambda x: x[1]["quality_cost_ratio"])[0]
            elif strategy == "best_quality":
                selected_model = max(overall_stats.items(), key=lambda x: x[1]["mean_total_score"])[0]
            elif strategy == "lowest_cost":
                selected_model = min(overall_stats.items(), key=lambda x: x[1]["mean_cost"])[0]
            else:  # fastest
                selected_model = min(overall_stats.items(), key=lambda x: x[1]["mean_latency_ms"])[0]
            
            routing_reason = f"Category '{category}' not in routing table, using overall {strategy}"
        else:
            routing_reason = f"Category '{category}' → {strategy} model"
        
        # Step 3: Get the model client
        client = self._get_model_client(selected_model)
        
        # Step 4: Call the model
        response_text, base_metadata = client.generate(prompt)
        
        # Step 5: Calculate cost
        cost = 0.0
        if response_text and "error" not in base_metadata:
            cost = client.calculate_cost(
                base_metadata.get("tokens_input", 0),
                base_metadata.get("tokens_output", 0)
            )
        
        # Step 6: Build enhanced metadata
        metadata = {
            **base_metadata,
            "model": selected_model,
            "category": category,
            "strategy": strategy,
            "routing_reason": routing_reason,
            "cost": cost
        }
        
        return response_text, metadata
    
    def route_batch(
        self,
        prompts: list,
        strategy: str = "best_value"
    ) -> list:
        """
        Route and process a batch of prompts.
        
        Args:
            prompts: List of prompt strings
            strategy: Routing strategy
        
        Returns:
            List of (response, metadata) tuples
        """
        results = []
        
        for prompt in prompts:
            response, metadata = self.route_and_respond(prompt, strategy)
            results.append((response, metadata))
        
        return results
    
    def get_routing_recommendation(self, prompt: str) -> Dict[str, Any]:
        """
        Get routing recommendations for a prompt across all strategies.
        
        Args:
            prompt: The user's prompt
        
        Returns:
            Dictionary with recommendations for each strategy
        """
        category = self.categorizer.categorize_single(prompt)
        
        recommendations = {
            "category": category,
            "strategies": {}
        }
        
        for strategy in self.routing_tables.keys():
            routing_table = self.routing_tables[strategy]
            model = routing_table.get(category, "unknown")
            
            # Get stats for this model
            model_stats = self.analysis["overall_stats"].get(model, {})
            
            recommendations["strategies"][strategy] = {
                "model": model,
                "estimated_cost": model_stats.get("mean_cost", 0.0),
                "estimated_quality": model_stats.get("mean_total_score", 0.0),
                "estimated_latency_ms": model_stats.get("mean_latency_ms", 0)
            }
        
        return recommendations
    
    def _print_routing_table(self):
        """Print the routing table for best_value strategy."""
        print("\n📋 Routing Table (Best Value Strategy):")
        for category, model in self.routing_tables["best_value"].items():
            print(f"  {category:12} → {model}")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get router statistics.
        
        Returns:
            Dictionary with routing statistics
        """
        return {
            "total_categories": len(self.routing_tables["best_value"]),
            "strategies_available": list(self.routing_tables.keys()),
            "models_in_use": list(set(
                model for table in self.routing_tables.values()
                for model in table.values()
            ))
        }


def main():
    """Demo of the Smart Router."""
    print("=" * 70)
    print("SMART ROUTER DEMO")
    print("=" * 70)
    
    # Initialize router
    router = SmartRouter()
    
    # Test prompts
    test_prompts = [
        "Write a Python function to calculate factorial",
        "Solve the equation: 2x^2 + 5x - 3 = 0",
        "Write a creative story about a time-traveling robot",
        "Analyze the pros and cons of renewable energy",
        "Explain how machine learning works",
        "Create a business plan for a food delivery startup"
    ]
    
    print("\n" + "=" * 70)
    print("ROUTING TEST PROMPTS")
    print("=" * 70)
    
    for prompt in test_prompts:
        print(f"\n📝 Prompt: {prompt[:60]}...")
        
        # Get recommendations
        recommendations = router.get_routing_recommendation(prompt)
        print(f"🏷️  Category: {recommendations['category']}")
        
        print("\n💡 Recommendations:")
        for strategy, info in recommendations['strategies'].items():
            print(f"  {strategy:15} → {info['model']:20} "
                  f"(cost: ${info['estimated_cost']:.6f}, "
                  f"quality: {info['estimated_quality']:.1f}/40)")
        
        # Route with best_value strategy
        print(f"\n🎯 Routing with 'best_value' strategy...")
        response, metadata = router.route_and_respond(prompt, strategy="best_value")
        
        if response:
            print(f"✅ Model: {metadata['model']}")
            print(f"   Reason: {metadata['routing_reason']}")
            print(f"   Cost: ${metadata['cost']:.6f}")
            print(f"   Latency: {metadata['latency_ms']}ms")
            print(f"   Response: {response[:100]}...")
        else:
            print(f"❌ Error: {metadata.get('error')}")
    
    # Show stats
    print("\n" + "=" * 70)
    print("ROUTER STATISTICS")
    print("=" * 70)
    stats = router.get_stats()
    print(f"Total categories: {stats['total_categories']}")
    print(f"Strategies: {', '.join(stats['strategies_available'])}")
    print(f"Models in use: {', '.join(stats['models_in_use'])}")


if __name__ == "__main__":
    main()
