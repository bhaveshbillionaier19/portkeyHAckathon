"""
Add Performance Analysis to Existing Results
Enhances evaluation results with accuracy, precision, FPR and shift recommendations
"""

import json
from src.performance_analyzer import ModelPerformanceAnalyzer

# Load existing results
print("Loading evaluation results...")
with open('data/real_evaluation_results.json') as f:
    results = json.load(f)

# Run performance analysis
print("Analyzing performance metrics...")
analyzer = ModelPerformanceAnalyzer(results)
performance_report = analyzer.generate_detailed_report()

# Add to results
results['performance_analysis'] = performance_report

# Save enhanced results
print("Saving enhanced results...")
with open('data/real_evaluation_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print("\n" + "="*70)
print("PERFORMANCE ANALYSIS COMPLETE")
print("="*70)

# Display summary
print("\n📊 PERFORMANCE METRICS:")
for model, metrics in performance_report['performance_metrics'].items():
    print(f"\n{model.upper()}:")
    print(f"  Accuracy:  {metrics['accuracy']:.2%}")
    print(f"  Precision: {metrics['precision']:.2%}")
    print(f"  FPR:       {metrics['fpr']:.2%}")

print("\n💡 SHIFT RECOMMENDATIONS:")
for rec in performance_report['shift_recommendations']:
    if rec['type'] == 'overall_recommendation':
        print(f"\n🏆 BEST OVERALL: {rec['model']}")
        print(f"   {rec['reason']}")
    elif rec['type'] == 'category_shift':
        print(f"\n📂 {rec['category'].upper()}:")
        print(f"   {rec['reason']}")

print("\n✅ Results enhanced with performance analysis!")
print("   View in dashboard: streamlit run dashboard/app_complete.py")
