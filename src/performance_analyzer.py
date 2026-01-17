"""
Model Performance Analyzer
Calculates accuracy, precision, FPR and provides shift recommendations
"""

from typing import Dict, Any, List
import json


class ModelPerformanceAnalyzer:
    """
    Analyzes model performance and provides detailed shift recommendations.
    
    Metrics:
    - Accuracy: Quality score / Max possible score (how correct/helpful)
    - Precision: (Good responses) / (Good + Unsafe responses)
    - FPR: (Unsafe responses) / (Total responses)
    """
    
    def __init__(self, evaluation_results: Dict[str, Any]):
        """Initialize with evaluation results."""
        self.results = evaluation_results
        self.models = evaluation_results['models']
    
    def calculate_metrics(self) -> Dict[str, Any]:
        """Calculate accuracy, precision, and FPR for each model."""
        metrics = {}
        
        for model in self.models:
            # Get quality scores (accuracy proxy)
            quality_scores = self._get_quality_scores(model)
            
            # Get safety metrics (for precision and FPR)
            safety_metrics = self._get_safety_metrics(model)
            
            # Calculate metrics
            accuracy = self._calculate_accuracy(quality_scores)
            precision = self._calculate_precision(safety_metrics, quality_scores)
            fpr = self._calculate_fpr(safety_metrics)
            
            metrics[model] = {
                'accuracy': accuracy,
                'precision': precision,
                'fpr': fpr,
                'quality_scores': quality_scores,
                'safety_metrics': safety_metrics
            }
        
        return metrics
    
    def _get_quality_scores(self, model: str) -> List[float]:
        """Get all quality scores for a model."""
        scores = []
        for cat_stats in self.results.get('category_statistics', {}).values():
            if model in cat_stats:
                # Collect individual scores
                for _ in range(cat_stats[model]['num_questions']):
                    scores.append(cat_stats[model]['average_score'])
        return scores
    
    def _get_safety_metrics(self, model: str) -> Dict[str, int]:
        """Get safety metrics for a model."""
        guardrails = self.results.get('guardrail_statistics', {}).get(model, {})
        refusals = self.results.get('refusal_metrics', {}).get(model, {})
        
        return {
            'total_responses': guardrails.get('total_checks', 0),
            'safe_responses': guardrails.get('total_passed', 0),
            'unsafe_responses': guardrails.get('total_checks', 0) - guardrails.get('total_passed', 0),
            'pii_found': guardrails.get('pii_found', 0),
            'toxicity_flagged': guardrails.get('toxicity_flagged', 0),
            'safety_flagged': guardrails.get('safety_flagged', 0),
            'refusals': refusals.get('total_refusals', 0)
        }
    
    def _calculate_accuracy(self, quality_scores: List[float]) -> float:
        """
        Accuracy = Average quality score / Max score (5.0)
        Measures how correct and helpful the model is.
        """
        if not quality_scores:
            return 0.0
        
        avg_score = sum(quality_scores) / len(quality_scores)
        accuracy = avg_score / 5.0  # Normalize to 0-1
        return round(accuracy, 4)
    
    def _calculate_precision(self, safety_metrics: Dict[str, int], quality_scores: List[float]) -> float:
        """
        Precision = Good responses / (Good + Bad responses)
        Good = High quality (>= 4.0) AND safe
        Bad = Low quality OR unsafe
        """
        total = len(quality_scores)
        if total == 0:
            return 0.0
        
        # Count high quality responses (>= 4.0 out of 5)
        high_quality_count = sum(1 for score in quality_scores if score >= 4.0)
        
        # Adjust for safety issues
        unsafe_count = safety_metrics['unsafe_responses']
        good_responses = max(0, high_quality_count - unsafe_count)
        
        # Precision = TP / (TP + FP)
        # TP = good responses, FP = bad responses (low quality or unsafe)
        precision = good_responses / total if total > 0 else 0.0
        return round(precision, 4)
    
    def _calculate_fpr(self, safety_metrics: Dict[str, int]) -> float:
        """
        False Positive Rate = Unsafe responses / Total responses
        Measures how often model produces unsafe/unwanted content.
        """
        total = safety_metrics['total_responses']
        if total == 0:
            return 0.0
        
        unsafe = safety_metrics['unsafe_responses']
        fpr = unsafe / total
        return round(fpr, 4)
    
    def generate_shift_recommendations(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate detailed shift recommendations based on metrics."""
        recommendations = []
        
        # Analyze by category
        for category, cat_models in self.results.get('category_statistics', {}).items():
            category_analysis = self._analyze_category(category, cat_models, metrics)
            if category_analysis:
                recommendations.extend(category_analysis)
        
        # Overall recommendations
        overall_rec = self._generate_overall_recommendation(metrics)
        if overall_rec:
            recommendations.insert(0, overall_rec)
        
        return recommendations
    
    def _analyze_category(self, category: str, cat_models: Dict, metrics: Dict) -> List[Dict]:
        """Analyze performance by category and generate shift recommendations."""
        recommendations = []
        
        # Get metrics for this category
        category_metrics = {}
        for model in cat_models.keys():
            if model in metrics:
                category_metrics[model] = {
                    'quality': cat_models[model]['average_score'],
                    'accuracy': metrics[model]['accuracy'],
                    'precision': metrics[model]['precision'],
                    'fpr': metrics[model]['fpr']
                }
        
        if len(category_metrics) < 2:
            return []
        
        # Find best model
        best_overall = max(category_metrics.items(), 
                          key=lambda x: (x[1]['quality'] * 0.4 + 
                                       x[1]['accuracy'] * 0.3 + 
                                       x[1]['precision'] * 0.2 - 
                                       x[1]['fpr'] * 0.1))
        
        # Find current leader by quality alone
        best_quality = max(category_metrics.items(), key=lambda x: x[1]['quality'])
        
        # Check if shift is recommended
        if best_overall[0] != best_quality[0]:
            # Calculate improvements
            quality_diff = ((best_overall[1]['quality'] - best_quality[1]['quality']) / 
                           best_quality[1]['quality'] * 100)
            precision_diff = ((best_overall[1]['precision'] - best_quality[1]['precision']) / 
                             max(best_quality[1]['precision'], 0.01) * 100)
            fpr_diff = ((best_quality[1]['fpr'] - best_overall[1]['fpr']) / 
                       max(best_quality[1]['fpr'], 0.01) * 100)
            
            recommendations.append({
                'type': 'category_shift',
                'category': category,
                'from_model': best_quality[0],
                'to_model': best_overall[0],
                'reason': self._generate_shift_reason(
                    best_quality, best_overall, 
                    quality_diff, precision_diff, fpr_diff
                ),
                'metrics_improvement': {
                    'quality': quality_diff,
                    'precision': precision_diff,
                    'fpr_reduction': fpr_diff
                }
            })
        
        return recommendations
    
    def _generate_shift_reason(self, current, recommended, quality_diff, precision_diff, fpr_diff) -> str:
        """Generate human-readable shift reason."""
        current_model, current_metrics = current
        recommended_model, rec_metrics = recommended
        
        reasons = []
        
        # Quality
        if abs(quality_diff) > 5:
            if quality_diff > 0:
                reasons.append(f"✅ {abs(quality_diff):.1f}% higher quality")
            else:
                reasons.append(f"⚠️ {abs(quality_diff):.1f}% lower quality")
        
        # Precision
        if precision_diff > 10:
            reasons.append(f"✅ {precision_diff:.1f}% better precision (more reliable)")
        elif precision_diff < -10:
            reasons.append(f"⚠️ {abs(precision_diff):.1f}% lower precision")
        
        # FPR
        if fpr_diff > 20:
            reasons.append(f"✅ {fpr_diff:.1f}% fewer unsafe responses")
        elif fpr_diff < -20:
            reasons.append(f"❌ {abs(fpr_diff):.1f}% more unsafe responses")
        
        reason_text = " | ".join(reasons) if reasons else "Balanced trade-off"
        return f"Switch from {current_model} to **{recommended_model}**: {reason_text}"
    
    def _generate_overall_recommendation(self, metrics: Dict) -> Dict[str, Any]:
        """Generate overall model recommendation."""
        # Find best balanced model
        model_scores = {}
        for model, model_metrics in metrics.items():
            # Weighted score: Quality 40%, Accuracy 30%, Precision 20%, FPR penalty 10%
            score = (model_metrics['accuracy'] * 0.4 +
                    model_metrics['precision'] * 0.3 +
                    (1 - model_metrics['fpr']) * 0.3)
            model_scores[model] = score
        
        best_model = max(model_scores.items(), key=lambda x: x[1])
        
        return {
            'type': 'overall_recommendation',
            'model': best_model[0],
            'score': best_model[1],
            'reason': f"Best overall balance of accuracy ({metrics[best_model[0]]['accuracy']:.2%}), "
                     f"precision ({metrics[best_model[0]]['precision']:.2%}), "
                     f"and safety (FPR: {metrics[best_model[0]]['fpr']:.2%})",
            'metrics': metrics[best_model[0]]
        }
    
    def generate_detailed_report(self) -> Dict[str, Any]:
        """Generate complete performance report."""
        metrics = self.calculate_metrics()
        recommendations = self.generate_shift_recommendations(metrics)
        
        return {
            'performance_metrics': metrics,
            'shift_recommendations': recommendations,
            'summary': self._generate_summary(metrics, recommendations)
        }
    
    def _generate_summary(self, metrics: Dict, recommendations: List) -> Dict[str, Any]:
        """Generate executive summary."""
        return {
            'total_models_analyzed': len(metrics),
            'total_recommendations': len(recommendations),
            'best_accuracy': max(metrics.items(), key=lambda x: x[1]['accuracy']),
            'best_precision': max(metrics.items(), key=lambda x: x[1]['precision']),
            'lowest_fpr': min(metrics.items(), key=lambda x: x[1]['fpr']),
            'categories_analyzed': len(set(r['category'] for r in recommendations if r['type'] == 'category_shift'))
        }


# Example usage
if __name__ == "__main__":
    # Load real evaluation results
    with open('data/real_evaluation_results.json') as f:
        results = json.load(f)
    
    analyzer = ModelPerformanceAnalyzer(results)
    report = analyzer.generate_detailed_report()
    
    print("="*70)
    print("MODEL PERFORMANCE ANALYSIS")
    print("="*70)
    
    print("\n📊 PERFORMANCE METRICS:")
    for model, metrics in report['performance_metrics'].items():
        print(f"\n{model.upper()}:")
        print(f"  Accuracy:  {metrics['accuracy']:.2%} (quality score / max)")
        print(f"  Precision: {metrics['precision']:.2%} (good responses / total)")
        print(f"  FPR:       {metrics['fpr']:.2%} (unsafe responses / total)")
    
    print("\n" + "="*70)
    print("💡 SHIFT RECOMMENDATIONS:")
    print("="*70)
    
    for rec in report['shift_recommendations']:
        if rec['type'] == 'overall_recommendation':
            print(f"\n🏆 OVERALL BEST: {rec['model']}")
            print(f"   {rec['reason']}")
        elif rec['type'] == 'category_shift':
            print(f"\n📂 {rec['category'].upper()}:")
            print(f"   {rec['reason']}")
    
    print("\n" + "="*70)
    print(f"✅ Analysis complete: {report['summary']['total_recommendations']} recommendations generated")
    print("="*70)
