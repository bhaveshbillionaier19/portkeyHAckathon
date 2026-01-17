"""
Recommendation Engine
Analyzes cost-quality trade-offs and provides optimization recommendations
"""

from typing import Dict, Any, List, Tuple


class TradeOffAnalyzer:
    """
    Analyzes trade-offs between cost, quality, speed, and safety.
    Provides recommendations for optimal model selection.
    """
    
    def __init__(self):
        """Initialize the analyzer."""
        pass
    
    def analyze(
        self,
        category_stats: Dict[str, Any],
        cost_metrics: Dict[str, Any],
        refusal_metrics: Dict[str, Any],
        guardrail_stats: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Analyze all metrics and generate recommendations.
        
        Args:
            category_stats: Quality scores by category
            cost_metrics: Cost and performance data
            refusal_metrics: Refusal statistics
            guardrail_stats: Safety check results
        
        Returns:
            Dictionary with analysis and recommendations
        """
        # Aggregate model stats
        model_stats = self._aggregate_model_stats(
            category_stats, cost_metrics, refusal_metrics, guardrail_stats
        )
        
        # Find Pareto frontier
        pareto_optimal = self._find_pareto_frontier(model_stats)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(model_stats, pareto_optimal)
        
        # Calculate trade-off scenarios
        scenarios = self._calculate_scenarios(model_stats)
        
        return {
            'model_stats': model_stats,
            'pareto_optimal': pareto_optimal,
            'recommendations': recommendations,
            'scenarios': scenarios
        }
    
    def _aggregate_model_stats(
        self,
        category_stats: Dict,
        cost_metrics: Dict,
        refusal_metrics: Dict,
        guardrail_stats: Dict = None
    ) -> Dict[str, Any]:
        """Aggregate all stats per model."""
        models = {}
        
        # Get quality scores
        for category, model_scores in category_stats.items():
            for model, scores in model_scores.items():
                if model not in models:
                    models[model] = {
                        'quality_scores': [],
                        'categories_evaluated': 0
                    }
                models[model]['quality_scores'].append(scores['average_score'])
                models[model]['categories_evaluated'] += 1
        
        # Calculate average quality
        for model in models:
            scores = models[model]['quality_scores']
            avg = sum(scores) / len(scores)
            models[model]['avg_quality'] = round(avg, 2)
            # Calculate standard deviation
            variance = sum((x - avg) ** 2 for x in scores) / len(scores) if len(scores) > 1 else 0
            models[model]['quality_std'] = round(variance ** 0.5, 2)
        
        # Add cost metrics
        for model, cost_data in cost_metrics.items():
            if model in models:
                models[model]['cost_per_question'] = cost_data['cost_per_question']
                models[model]['total_cost'] = cost_data['total_cost_usd']
                models[model]['avg_latency_ms'] = cost_data['avg_latency_ms']
        
        # Add refusal metrics
        for model, refusal_data in refusal_metrics.items():
            if model in models:
                models[model]['refusal_rate'] = refusal_data['refusal_rate']
        
        # Add guardrail stats if available
        if guardrail_stats:
            for model, guard_data in guardrail_stats.items():
                if model in models:
                    models[model]['safety_pass_rate'] = guard_data.get('overall_pass_rate', 1.0)
        
        # Calculate value scores
        for model in models:
            # Value = Quality / Cost (higher is better)
            cost = models[model].get('cost_per_question', 0.001)
            quality = models[model]['avg_quality']
            models[model]['value_score'] = round(quality / max(cost, 0.000001), 2)
            
            # Reliability score (quality - refusal penalty - safety penalty)
            reliability = quality
            reliability -= models[model].get('refusal_rate', 0) * 5  # Penalize refusals
            if guardrail_stats:
                safety_pass = models[model].get('safety_pass_rate', 1.0)
                reliability -= (1 - safety_pass) * 5  # Penalize safety failures
            models[model]['reliability_score'] = round(max(0, reliability), 2)
        
        return models
    
    def _find_pareto_frontier(self, model_stats: Dict) -> List[str]:
        """
        Find Pareto optimal models (models not dominated by any other).
        A model is Pareto optimal if no other model is better in all dimensions.
        """
        models_list = list(model_stats.keys())
        pareto_optimal = []
        
        for model_a in models_list:
            is_dominated = False
            
            for model_b in models_list:
                if model_a == model_b:
                    continue
                
                # Check if model_b dominates model_a
                # (better or equal in all dimensions, strictly better in at least one)
                quality_better = model_stats[model_b]['avg_quality'] >= model_stats[model_a]['avg_quality']
                cost_better = model_stats[model_b]['cost_per_question'] <= model_stats[model_a]['cost_per_question']
                refusal_better = model_stats[model_b].get('refusal_rate', 0) <= model_stats[model_a].get('refusal_rate', 0)
                
                quality_strictly = model_stats[model_b]['avg_quality'] > model_stats[model_a]['avg_quality']
                cost_strictly = model_stats[model_b]['cost_per_question'] < model_stats[model_a]['cost_per_question']
                
                if (quality_better and cost_better and refusal_better and (quality_strictly or cost_strictly)):
                    is_dominated = True
                    break
            
            if not is_dominated:
                pareto_optimal.append(model_a)
        
        return pareto_optimal
    
    def _generate_recommendations(self, model_stats: Dict, pareto_optimal: List[str]) -> List[Dict]:
        """Generate actionable recommendations."""
        recommendations = []
        
        # 1. Best Overall Value
        best_value = max(model_stats.items(), key=lambda x: x[1]['value_score'])
        recommendations.append({
            'type': 'best_value',
            'model': best_value[0],
            'reasoning': f"Highest quality/cost ratio: {best_value[1]['value_score']:.0f}x",
            'metrics': {
                'quality': best_value[1]['avg_quality'],
                'cost': best_value[1]['cost_per_question'],
                'value': best_value[1]['value_score']
            }
        })
        
        # 2. Highest Quality
        best_quality = max(model_stats.items(), key=lambda x: x[1]['avg_quality'])
        recommendations.append({
            'type': 'highest_quality',
            'model': best_quality[0],
            'reasoning': f"Top quality score: {best_quality[1]['avg_quality']:.2f}/5",
            'metrics': {
                'quality': best_quality[1]['avg_quality'],
                'cost': best_quality[1]['cost_per_question']
            }
        })
        
        # 3. Most Cost-Effective
        cheapest = min(model_stats.items(), key=lambda x: x[1]['cost_per_question'])
        recommendations.append({
            'type': 'most_cost_effective',
            'model': cheapest[0],
            'reasoning': f"Lowest cost: ${cheapest[1]['cost_per_question']:.6f} per question",
            'metrics': {
                'quality': cheapest[1]['avg_quality'],
                'cost': cheapest[1]['cost_per_question']
            }
        })
        
        # 4. Most Reliable
        most_reliable = max(model_stats.items(), key=lambda x: x[1]['reliability_score'])
        recommendations.append({
            'type': 'most_reliable',
            'model': most_reliable[0],
            'reasoning': f"Highest reliability (low refusals, high safety): {most_reliable[1]['reliability_score']:.2f}/5",
            'metrics': {
                'quality': most_reliable[1]['avg_quality'],
                'refusal_rate': most_reliable[1].get('refusal_rate', 0),
                'reliability': most_reliable[1]['reliability_score']
            }
        })
        
        # 5. Pareto Optimal Set
        if len(pareto_optimal) > 1:
            recommendations.append({
                'type': 'pareto_optimal_set',
                'models': pareto_optimal,
                'reasoning': f"These {len(pareto_optimal)} models are not dominated by any other (best trade-offs)",
                'note': 'Choose based on your priority: quality vs cost'
            })
        
        return recommendations
    
    def _calculate_scenarios(self, model_stats: Dict) -> Dict[str, Any]:
        """Calculate different usage scenarios."""
        scenarios = {}
        
        # Scenario 1: Budget-constrained ($10/month)
        budget = 10.0  # $10 budget
        scenarios['budget_constrained'] = []
        
        for model, stats in model_stats.items():
            cost_per_q = stats['cost_per_question']
            max_questions = int(budget / cost_per_q) if cost_per_q > 0 else 999999
            scenarios['budget_constrained'].append({
                'model': model,
                'max_questions': max_questions,
                'avg_quality': stats['avg_quality'],
                'total_quality_points': max_questions * stats['avg_quality']
            })
        
        # Sort by total quality points
        scenarios['budget_constrained'].sort(
            key=lambda x: x['total_quality_points'],
            reverse=True
        )
        
        # Scenario 2: Quality-constrained (need 4.0/5 minimum)
        min_quality = 4.0
        scenarios['quality_constrained'] = []
        
        for model, stats in model_stats.items():
            if stats['avg_quality'] >= min_quality:
                scenarios['quality_constrained'].append({
                    'model': model,
                    'quality': stats['avg_quality'],
                    'cost_per_question': stats['cost_per_question'],
                    'estimated_1000q_cost': stats['cost_per_question'] * 1000
                })
        
        # Sort by cost
        scenarios['quality_constrained'].sort(
            key=lambda x: x['cost_per_question']
        )
        
        # Scenario 3: Hybrid strategy (use cheap for simple, expensive for complex)
        if len(model_stats) >= 2:
            models_by_cost = sorted(model_stats.items(), key=lambda x: x[1]['cost_per_question'])
            cheap_model = models_by_cost[0]
            quality_model = max(model_stats.items(), key=lambda x: x[1]['avg_quality'])
            
            # Assume 70% simple (cheap), 30% complex (quality)
            hybrid_cost = (0.7 * cheap_model[1]['cost_per_question'] + 
                          0.3 * quality_model[1]['cost_per_question'])
            hybrid_quality = (0.7 * cheap_model[1]['avg_quality'] + 
                             0.3 * quality_model[1]['avg_quality'])
            
            scenarios['hybrid_strategy'] = {
                'cheap_model': {'name': cheap_model[0], 'percentage': 70},
                'quality_model': {'name': quality_model[0], 'percentage': 30},
                'estimated_cost_per_question': round(hybrid_cost, 6),
                'estimated_avg_quality': round(hybrid_quality, 2),
                'savings_vs_quality_only': round(
                    (quality_model[1]['cost_per_question'] - hybrid_cost) / 
                    quality_model[1]['cost_per_question'] * 100, 1
                )
            }
        
        return scenarios


# Example usage
if __name__ == "__main__":
    # Mock data
    category_stats = {
        'math': {
            'gpt': {'average_score': 4.5, 'num_questions': 50},
            'claude': {'average_score': 4.3, 'num_questions': 50}
        },
        'code': {
            'gpt': {'average_score': 4.2, 'num_questions': 50},
            'claude': {'average_score': 4.4, 'num_questions': 50}
        }
    }
    
    cost_metrics = {
        'gpt': {'cost_per_question': 0.00005, 'total_cost_usd': 0.005, 'avg_latency_ms': 1200},
        'claude': {'cost_per_question': 0.00003, 'total_cost_usd': 0.003, 'avg_latency_ms': 1500}
    }
    
    refusal_metrics = {
        'gpt': {'refusal_rate': 0.02, 'total_refusals': 2},
        'claude': {'refusal_rate': 0.01, 'total_refusals': 1}
    }
    
    analyzer = TradeOffAnalyzer()
    results = analyzer.analyze(category_stats, cost_metrics, refusal_metrics)
    
    print("="*70)
    print("RECOMMENDATION ENGINE RESULTS")
    print("="*70)
    
    print("\n📊 Model Statistics:")
    for model, stats in results['model_stats'].items():
        print(f"\n{model}:")
        print(f"  Quality: {stats['avg_quality']:.2f}/5")
        print(f"  Cost: ${stats['cost_per_question']:.6f}")
        print(f"  Value Score: {stats['value_score']:.0f}x")
        print(f"  Reliability: {stats['reliability_score']:.2f}")
    
    print(f"\n✅ Pareto Optimal: {', '.join(results['pareto_optimal'])}")
    
    print("\n💡 Recommendations:")
    for rec in results['recommendations']:
        print(f"\n{rec['type'].upper()}:")
        print(f"  Model: {rec.get('model', rec.get('models'))}")
        print(f"  Reason: {rec['reasoning']}")
