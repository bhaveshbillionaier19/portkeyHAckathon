#!/usr/bin/env python
"""
Quick Results Viewer
Shows summary of evaluation results
"""

import json

# Load results
with open('data/real_evaluation_results.json') as f:
    results = json.load(f)

print("="*70)
print("EVALUATION RESULTS SUMMARY")
print("="*70)

# Basic info
print(f"\nTotal Questions: {results['total_questions']}")
print(f"Models: {', '.join(results['models'])}")

# Cost metrics
print("\n💰 COST METRICS:")
print("-"*70)
for model, metrics in results['cost_metrics'].items():
    print(f"\n{model.upper()}:")
    print(f"  Total Cost: ${metrics['total_cost_usd']:.6f}")
    print(f"  Cost/Question: ${metrics['cost_per_question']:.6f}")
    print(f"  Total Tokens: {metrics['total_tokens']:,}")
    print(f"  Avg Latency: {metrics['avg_latency_ms']:.0f}ms")

# Quality scores
print("\n📊 QUALITY SCORES:")
print("-"*70)
for category, models in results['category_statistics'].items():
    print(f"\n{category.upper()}:")
    sorted_models = sorted(models.items(), key=lambda x: x[1]['average_score'], reverse=True)
    for rank, (model, stats) in enumerate(sorted_models, 1):
        medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉"
        print(f"  {medal} {model}: {stats['average_score']:.2f}/5 (n={stats['num_questions']})")

# Refusals
print("\n🚫 REFUSAL RATES:")
print("-"*70)
for model, metrics in results['refusal_metrics'].items():
    rate = metrics['refusal_rate'] * 100
    status = "✅" if rate == 0 else "⚠️"
    print(f"{status} {model}: {rate:.1f}% ({metrics['total_refusals']}/{metrics['total_responses']})")

# Safety
print("\n🛡️  SAFETY (Guardrail Pass Rates):")
print("-"*70)
for model, stats in results['guardrail_statistics'].items():
    pass_rate = stats['overall_pass_rate'] * 100
    print(f"{model}: {pass_rate:.0f}% passed ({stats['total_passed']}/{stats['total_checks']})")

# Recommendations
print("\n💡 TOP RECOMMENDATIONS:")
print("-"*70)
for rec in results['recommendations']['recommendations'][:3]:
    print(f"\n{rec['type'].upper().replace('_', ' ')}:")
    print(f"  Model: {rec['model']}")
    print(f"  Reason: {rec['reasoning']}")

# Pareto optimal
if results['recommendations'].get('pareto_optimal'):
    print(f"\n✨ Pareto Optimal Models: {', '.join(results['recommendations']['pareto_optimal'])}")

print("\n" + "="*70)
print("View full results in: data/real_evaluation_results.json")
print("Launch dashboard with: streamlit run dashboard/app_complete.py")
print("="*70)
