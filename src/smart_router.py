"""
Smart Router - Selects best model based on category and evaluation results
"""

import json
import os
from typing import Dict, Any, Optional

class SmartRouter:
    """
    Routes prompts to the best model based on category and evaluation results.
    Detects model switches and explains reasoning.
    """
    
    def __init__(self, evaluation_results_path='data/real_evaluation_results.json'):
        """Load evaluation results and build routing table."""
        self.results = self._load_results(evaluation_results_path)
        self.category_best_models = self._build_routing_table()
        self.current_model = None
        
    def _load_results(self, path: str) -> Dict[str, Any]:
        """Load evaluation results from JSON file."""
        try:
            with open(path, 'r', encoding='utf-8') as f:  # Fixed: UTF-8 encoding
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def _build_routing_table(self) -> Dict[str, Dict]:
        """Build routing table: category -> best model with metrics."""
        routing = {}
        
        category_stats = self.results.get('category_statistics', {})
        
        for category, models_data in category_stats.items():
            # Find model with highest average score for this category
            best_model = None
            best_score = 0
            
            for model_name, stats in models_data.items():
                avg_score = stats.get('average_score', 0)
                if avg_score > best_score:
                    best_score = avg_score
                    best_model = model_name
            
            if best_model:
                routing[category] = {
                    'model': best_model,
                    'quality': best_score,
                    'metrics': models_data[best_model]
                }
        
        return routing
    
    def route(self, category: str) -> Dict[str, Any]:
        """
        Get best model for category and detect if switch needed.
        
        Returns:
            {
                'model': str,
                'category': str,
                'switched': bool,
                'reason': str (if switched),
                'metrics': dict
            }
        """
        if category not in self.category_best_models:
            # Fallback to most reliable model overall
            category = self._get_fallback_category()
        
        best_for_category = self.category_best_models[category]
        new_model = best_for_category['model']
        
        result = {
            'model': new_model,
            'category': category,
            'switched': False,
            'metrics': best_for_category['metrics']
        }
        
        # Check if model switched
        if self.current_model and self.current_model != new_model:
            result['switched'] = True
            result['reason'] = self._explain_switch(
                self.current_model,
                new_model,
                category,
                best_for_category
            )
        
        # Update current model
        self.current_model = new_model
        
        return result
    
    def _explain_switch(self, old_model: str, new_model: str, category: str, new_model_data: Dict) -> str:
        """Generate explanation for why model switched."""
        new_quality = new_model_data['quality']
        
        # Try to get old model's score for this category
        category_stats = self.results.get('category_statistics', {}).get(category, {})
        old_quality = category_stats.get(old_model, {}).get('average_score', 0)
        
        if old_quality > 0:
            improvement = ((new_quality - old_quality) / old_quality) * 100
            return (f"Switched from {old_model.upper()} to {new_model.upper()} - "
                   f"{abs(improvement):.1f}% {'higher' if improvement > 0 else 'lower'} quality "
                   f"for {category} questions ({new_model.upper()}: {new_quality:.2f}/5 vs "
                   f"{old_model.upper()}: {old_quality:.2f}/5)")
        else:
            return (f"Switched to {new_model.upper()} - "
                   f"Best model for {category} category ({new_quality:.2f}/5)")
    
    def _get_fallback_category(self) -> str:
        """Get category with most data as fallback."""
        if not self.category_best_models:
            return 'general'
        
        # Return first category as fallback
        return list(self.category_best_models.keys())[0]
    
    def get_model_comparison(self, category: str) -> Dict[str, Any]:
        """Get comparison of all models for a specific category."""
        category_stats = self.results.get('category_statistics', {}).get(category, {})
        
        comparison = {}
        for model, stats in category_stats.items():
            comparison[model] = {
                'quality': stats.get('average_score', 0),
                'min_score': stats.get('min_score', 0),
                'max_score': stats.get('max_score', 0),
                'question_count': stats.get('question_count', 0)
            }
        
        return comparison


# Example usage and testing
if __name__ == "__main__":
    router = SmartRouter()
    
    print("="*70)
    print("SMART ROUTER TEST")
    print("="*70)
    
    # Test routing for different categories
    test_categories = ['knowledge', 'code', 'logic']
    
    for category in test_categories:
        print(f"\n📂 Category: {category}")
        result = router.route(category)
        print(f"   Model: {result['model'].upper()}")
        print(f"   Quality: {result['metrics']['average_score']:.2f}/5")
        
        if result['switched']:
            print(f"   ⚡ {result['reason']}")
    
    # Show routing table
    print("\n" + "="*70)
    print("ROUTING TABLE:")
    print("="*70)
    for category, data in router.category_best_models.items():
        print(f"  {category:15} → {data['model']:10} ({data['quality']:.2f}/5)")
