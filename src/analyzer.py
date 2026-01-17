"""
Cost-Quality Analyzer
Analyzes evaluated responses to find the "Money Shot" - best ROI models
"""

import pandas as pd
import json
from typing import Dict, Any, List
from src.utils import load_json, save_json
from src.config import MODELS, CATEGORIES


class CostQualityAnalyzer:
    """Analyzes cost vs quality tradeoffs across models."""
    
    def __init__(self):
        """Initialize the analyzer."""
        self.df = None
        self.insights = {}
    
    def load_evaluated_responses(self, filepath: str) -> pd.DataFrame:
        """
        Load and flatten evaluated responses into a DataFrame.
        
        Args:
            filepath: Path to evaluated_responses.json
        
        Returns:
            Pandas DataFrame with flattened data
        """
        print(f"📂 Loading evaluated responses from {filepath}...")
        data = load_json(filepath)
        
        if not data:
            raise ValueError("No evaluated responses found")
        
        # Flatten the nested structure
        rows = []
        
        for entry in data:
            prompt = entry.get("prompt", "")
            category = entry.get("category", "unknown")
            
            for model_name, eval_data in entry.get("evaluations", {}).items():
                scores = eval_data.get("scores", {})
                
                row = {
                    "prompt": prompt,
                    "category": category,
                    "model": model_name,
                    "cost": eval_data.get("cost", 0.0),
                    "latency_ms": eval_data.get("latency_ms", 0),
                    "tokens_input": eval_data.get("tokens_input", 0),
                    "tokens_output": eval_data.get("tokens_output", 0),
                    "refused": eval_data.get("refused", False),
                    "error": eval_data.get("error"),
                    "accuracy": scores.get("accuracy", 0),
                    "helpfulness": scores.get("helpfulness", 0),
                    "clarity": scores.get("clarity", 0),
                    "safety": scores.get("safety", 0),
                    "total_score": scores.get("total", 0)
                }
                
                rows.append(row)
        
        df = pd.DataFrame(rows)
        print(f"✅ Loaded {len(df)} evaluations")
        print(f"   {df['prompt'].nunique()} prompts × {df['model'].nunique()} models")
        
        return df
    
    def calculate_overall_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate overall statistics per model.
        
        Args:
            df: DataFrame with evaluation data
        
        Returns:
            Dictionary with per-model statistics
        """
        print("\n📊 Calculating overall statistics...")
        
        stats = {}
        
        for model in df['model'].unique():
            model_df = df[df['model'] == model]
            
            # Filter out failed/refused responses for quality metrics
            successful = model_df[~model_df['refused'] & model_df['error'].isna()]
            
            stats[model] = {
                "total_prompts": len(model_df),
                "successful_prompts": len(successful),
                "refused_prompts": model_df['refused'].sum(),
                "total_cost": model_df['cost'].sum(),
                "mean_cost": model_df['cost'].mean(),
                "mean_latency_ms": model_df['latency_ms'].mean(),
                "mean_accuracy": successful['accuracy'].mean() if len(successful) > 0 else 0,
                "mean_helpfulness": successful['helpfulness'].mean() if len(successful) > 0 else 0,
                "mean_clarity": successful['clarity'].mean() if len(successful) > 0 else 0,
                "mean_safety": successful['safety'].mean() if len(successful) > 0 else 0,
                "mean_total_score": successful['total_score'].mean() if len(successful) > 0 else 0,
                "quality_cost_ratio": (successful['total_score'].mean() / model_df['cost'].mean()) if model_df['cost'].mean() > 0 else 0
            }
        
        return stats
    
    def calculate_category_winners(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Find the best model for each category.
        
        Args:
            df: DataFrame with evaluation data
        
        Returns:
            Dictionary with category-specific winners
        """
        print("\n🏆 Finding category winners...")
        
        category_winners = {}
        
        for category in df['category'].unique():
            cat_df = df[df['category'] == category]
            
            # Group by model
            grouped = cat_df.groupby('model').agg({
                'total_score': 'mean',
                'cost': 'mean',
                'latency_ms': 'mean'
            }).reset_index()
            
            # Calculate quality/cost ratio
            grouped['quality_cost_ratio'] = grouped['total_score'] / grouped['cost']
            grouped['quality_cost_ratio'] = grouped['quality_cost_ratio'].replace([float('inf'), -float('inf')], 0)
            
            # Find winners
            best_quality = grouped.loc[grouped['total_score'].idxmax()]
            best_value = grouped.loc[grouped['quality_cost_ratio'].idxmax()]
            lowest_cost = grouped.loc[grouped['cost'].idxmin()]
            fastest = grouped.loc[grouped['latency_ms'].idxmin()]
            
            category_winners[category] = {
                "best_quality": {
                    "model": best_quality['model'],
                    "score": float(best_quality['total_score']),
                    "cost": float(best_quality['cost'])
                },
                "best_value": {
                    "model": best_value['model'],
                    "score": float(best_value['total_score']),
                    "cost": float(best_value['cost']),
                    "quality_cost_ratio": float(best_value['quality_cost_ratio'])
                },
                "lowest_cost": {
                    "model": lowest_cost['model'],
                    "score": float(lowest_cost['total_score']),
                    "cost": float(lowest_cost['cost'])
                },
                "fastest": {
                    "model": fastest['model'],
                    "latency_ms": float(fastest['latency_ms']),
                    "cost": float(fastest['cost'])
                }
            }
        
        return category_winners
    
    def generate_recommendations(self, overall_stats: Dict, category_winners: Dict) -> List[str]:
        """
        Generate actionable recommendations.
        
        Args:
            overall_stats: Overall statistics per model
            category_winners: Category-specific winners
        
        Returns:
            List of recommendation strings
        """
        print("\n💡 Generating recommendations...")
        
        recommendations = []
        
        # Find most expensive and best value overall
        sorted_by_cost = sorted(overall_stats.items(), key=lambda x: x[1]['mean_cost'], reverse=True)
        sorted_by_value = sorted(overall_stats.items(), key=lambda x: x[1]['quality_cost_ratio'], reverse=True)
        
        most_expensive = sorted_by_cost[0]
        best_value = sorted_by_value[0]
        
        # Overall recommendation
        if most_expensive[0] != best_value[0]:
            cost_savings = ((most_expensive[1]['mean_cost'] - best_value[1]['mean_cost']) / most_expensive[1]['mean_cost']) * 100
            quality_retention = (best_value[1]['mean_total_score'] / most_expensive[1]['mean_total_score']) * 100 if most_expensive[1]['mean_total_score'] > 0 else 0
            
            recommendations.append(
                f"💰 OVERALL: Switch from {most_expensive[0]} to {best_value[0]} to save {cost_savings:.1f}% "
                f"while retaining {quality_retention:.1f}% quality"
            )
        
        # Category-specific recommendations
        for category, winners in category_winners.items():
            best_quality_model = winners['best_quality']['model']
            best_value_model = winners['best_value']['model']
            
            if best_quality_model != best_value_model:
                quality_diff = winners['best_quality']['score'] - winners['best_value']['score']
                cost_savings = ((winners['best_quality']['cost'] - winners['best_value']['cost']) / winners['best_quality']['cost']) * 100 if winners['best_quality']['cost'] > 0 else 0
                
                recommendations.append(
                    f"📊 {category.upper()}: {best_value_model} offers {cost_savings:.1f}% cost savings "
                    f"vs {best_quality_model} (quality diff: {quality_diff:.1f}/40)"
                )
        
        # Speed recommendations
        fastest_overall = min(overall_stats.items(), key=lambda x: x[1]['mean_latency_ms'])
        recommendations.append(
            f"⚡ SPEED: {fastest_overall[0]} is fastest at {fastest_overall[1]['mean_latency_ms']:.0f}ms average"
        )
        
        return recommendations
    
    def generate_insights(self, filepath: str) -> Dict[str, Any]:
        """
        Generate complete analysis insights.
        
        Args:
            filepath: Path to evaluated_responses.json
        
        Returns:
            Dictionary with all insights
        """
        print("\n" + "=" * 70)
        print("COST-QUALITY ANALYZER")
        print("=" * 70)
        
        # Load and flatten data
        self.df = self.load_evaluated_responses(filepath)
        
        # Calculate statistics
        overall_stats = self.calculate_overall_stats(self.df)
        category_winners = self.calculate_category_winners(self.df)
        recommendations = self.generate_recommendations(overall_stats, category_winners)
        
        # Compile insights
        insights = {
            "overall_stats": overall_stats,
            "category_winners": category_winners,
            "recommendations": recommendations,
            "summary": {
                "total_prompts": self.df['prompt'].nunique(),
                "total_models": self.df['model'].nunique(),
                "total_evaluations": len(self.df),
                "total_cost": float(self.df['cost'].sum()),
                "categories_analyzed": list(self.df['category'].unique())
            }
        }
        
        self.insights = insights
        
        # Print summary
        print("\n" + "=" * 70)
        print("ANALYSIS COMPLETE")
        print("=" * 70)
        self._print_summary(insights)
        
        return insights
    
    def _print_summary(self, insights: Dict):
        """Print analysis summary."""
        summary = insights['summary']
        
        print(f"\n📊 Summary:")
        print(f"  - Total prompts: {summary['total_prompts']}")
        print(f"  - Total models: {summary['total_models']}")
        print(f"  - Total evaluations: {summary['total_evaluations']}")
        print(f"  - Total cost: ${summary['total_cost']:.4f}")
        print(f"  - Categories: {', '.join(summary['categories_analyzed'])}")
        
        print(f"\n💡 Recommendations:")
        for rec in insights['recommendations']:
            print(f"  {rec}")
        
        print(f"\n🏆 Top Models:")
        overall = insights['overall_stats']
        
        # Best quality
        best_quality = max(overall.items(), key=lambda x: x[1]['mean_total_score'])
        print(f"  Best Quality: {best_quality[0]} ({best_quality[1]['mean_total_score']:.1f}/40)")
        
        # Best value
        best_value = max(overall.items(), key=lambda x: x[1]['quality_cost_ratio'])
        print(f"  Best Value: {best_value[0]} (ratio: {best_value[1]['quality_cost_ratio']:.0f})")
        
        # Lowest cost
        lowest_cost = min(overall.items(), key=lambda x: x[1]['mean_cost'])
        print(f"  Lowest Cost: {lowest_cost[0]} (${lowest_cost[1]['mean_cost']:.6f}/prompt)")
    
    def analyze_debate_results(self, file_path: str = "data/debate_results.json") -> Dict[str, Any]:
        """
        Analyze debate tournament results to find winner and rankings.
        
        Args:
            file_path: Path to debate_results.json
        
        Returns:
            Dictionary with tournament analysis
        """
        print("\n" + "=" * 70)
        print("DEBATE TOURNAMENT ANALYSIS")
        print("=" * 70)
        
        # Load debate results
        debate_data = load_json(file_path)
        
        if not debate_data or 'debates' not in debate_data:
            print("❌ No debate results found")
            return {}
        
        debates = debate_data['debates']
        models = debate_data.get('models', [])
        
        print(f"\n📊 Analyzing {len(debates)} debate rounds")
        print(f"Models: {', '.join(models)}")
        
        # Calculate win rate
        win_counts = {}
        for debate in debates:
            winner = debate.get('winner')
            if winner:
                win_counts[winner] = win_counts.get(winner, 0) + 1
        
        # Calculate consensus scores
        consensus_scores = {}
        score_counts = {}
        
        for debate in debates:
            for model, result in debate.get('results', {}).items():
                avg_score = result.get('avg_score', 0)
                if model not in consensus_scores:
                    consensus_scores[model] = 0
                    score_counts[model] = 0
                consensus_scores[model] += avg_score
                score_counts[model] += 1
        
        # Calculate averages
        for model in consensus_scores:
            if score_counts[model] > 0:
                consensus_scores[model] = round(consensus_scores[model] / score_counts[model], 2)
        
        # Create ranking
        rankings = []
        for model in models:
            rankings.append({
                'model': model,
                'wins': win_counts.get(model, 0),
                'win_rate': round((win_counts.get(model, 0) / len(debates)) * 100, 1) if debates else 0,
                'consensus_score': consensus_scores.get(model, 0.0),
                'total_debates': score_counts.get(model, 0)
            })
        
        rankings.sort(key=lambda x: (x['wins'], x['consensus_score']), reverse=True)
        
        # Find disagreements
        disagreements = []
        for debate in debates:
            scores = [result['avg_score'] for result in debate.get('results', {}).values()]
            if len(scores) >= 2:
                score_range = max(scores) - min(scores)
                if score_range >= 3.0:
                    disagreements.append({
                        'round': debate.get('round'),
                        'prompt': debate.get('prompt')[:60] + '...',
                        'score_range': round(score_range, 2),
                        'winner': debate.get('winner'),
                        'winner_score': debate.get('winner_score')
                    })
        
        analysis = {
            'tournament_date': debate_data.get('tournament_date'),
            'total_rounds': len(debates),
            'winner': rankings[0] if rankings else None,
            'ranking': rankings,
            'disagreements': disagreements[:10],
            'consensus_scores': consensus_scores
        }
        
        print(f"\n🏆 Tournament Winner: {analysis['winner']['model']}")
        print(f"   Wins: {analysis['winner']['wins']}/{len(debates)} ({analysis['winner']['win_rate']}%)")
        print(f"   Consensus Score: {analysis['winner']['consensus_score']}/10")
        
        print(f"\n📊 Full Rankings:")
        for rank, entry in enumerate(rankings, 1):
            print(f"   {rank}. {entry['model']}: {entry['wins']} wins, {entry['consensus_score']}/10 avg")
        
        return analysis
    
    def export_insights(self, output_file: str):
        """
        Export insights to JSON file.
        
        Args:
            output_file: Path to save analysis.json
        """
        if not self.insights:
            raise ValueError("No insights generated. Run generate_insights() first.")
        
        print(f"\n💾 Exporting insights to {output_file}...")
        save_json(output_file, self.insights)
        print("✅ Export complete")


def main():
    """Main execution for analysis."""
    analyzer = CostQualityAnalyzer()
    
    # Generate insights
    insights = analyzer.generate_insights("data/evaluated_responses.json")
    
    # Export to JSON
    analyzer.export_insights("data/analysis.json")
    
    print("\n✅ Analysis complete! Results saved to data/analysis.json")


if __name__ == "__main__":
    main()
