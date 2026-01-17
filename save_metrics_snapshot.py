"""
Extract and Save All Current Metrics
Creates a comprehensive snapshot of all metrics from current evaluation
"""

import json
from datetime import datetime

# Load evaluation results
with open('data/real_evaluation_results.json') as f:
    results = json.load(f)

# Extract all metrics
current_metrics = {
    "snapshot_timestamp": datetime.now().isoformat(),
    "total_questions": results['total_questions'],
    "models_evaluated": results['models'],
    
    "quality_metrics": {},
    "cost_metrics": results.get('cost_metrics', {}),
    "refusal_metrics": results.get('refusal_metrics', {}),
    "guardrail_statistics": results.get('guardrail_statistics', {}),
    "performance_metrics": {},
    "category_statistics": results.get('category_statistics', {}),
    "recommendations": results.get('recommendations', {})
}

# Extract quality metrics per model
for model in results['models']:
    quality_scores = []
    for cat_stats in results.get('category_statistics', {}).values():
        if model in cat_stats:
            quality_scores.append(cat_stats[model]['average_score'])
    
    if quality_scores:
        current_metrics['quality_metrics'][model] = {
            "avg_score_5": round(sum(quality_scores) / len(quality_scores), 2),
            "min_score": round(min(quality_scores), 2),
            "max_score": round(max(quality_scores), 2),
            "num_categories": len(quality_scores)
        }

# Add performance analysis if available
if 'performance_analysis' in results:
    perf_data = results['performance_analysis']
    
    for model, metrics in perf_data.get('performance_metrics', {}).items():
        current_metrics['performance_metrics'][model] = {
            "accuracy": metrics['accuracy'],
            "precision": metrics['precision'],
            "fpr": metrics['fpr']
        }

# Save comprehensive metrics snapshot
with open('data/current_metrics_snapshot.json', 'w') as f:
    json.dump(current_metrics, f, indent=2)

print("="*70)
print("METRICS SNAPSHOT SAVED")
print("="*70)

print(f"\n📊 Snapshot created: {current_metrics['snapshot_timestamp']}")
print(f"Questions evaluated: {current_metrics['total_questions']}")
print(f"Models: {', '.join(current_metrics['models_evaluated'])}")

print("\n📁 Files created:")
print("  ✅ data/metrics_documentation.json - Metric definitions")
print("  ✅ data/current_metrics_snapshot.json - Current values")

print("\n💡 Use these files to:")
print("  - Understand what each metric means")
print("  - Compare performance over time")
print("  - Generate reports")
print("  - Share results with stakeholders")

# Print summary
print("\n📈 Current Performance Summary:")
for model in current_metrics['models_evaluated']:
    if model in current_metrics['quality_metrics']:
        quality = current_metrics['quality_metrics'][model]
        cost = current_metrics['cost_metrics'].get(model, {})
        perf = current_metrics['performance_metrics'].get(model, {})
        
        print(f"\n{model.upper()}:")
        print(f"  Quality: {quality['avg_score_5']:.2f}/5")
        if cost:
            print(f"  Cost: ${cost.get('cost_per_question', 0):.6f}/question")
        if perf:
            print(f"  Accuracy: {perf['accuracy']:.1%}")
            print(f"  Precision: {perf['precision']:.1%}")
            print(f"  FPR: {perf['fpr']:.1%}")

print("\n" + "="*70)
