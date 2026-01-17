"""
Real Data Evaluator - COMPLETE SYSTEM
Evaluates .log file data using Portkey models exclusively
Includes: Cost tracking, Refusal detection, Guardrails, Recommendations
"""

import json
from typing import Dict, Any, List
from src.log_parser import LogParser
from src.debate_clean import PortkeyDebateArena
from src.refusal_detector import RefusalDetector
from src.guardrail_checker import GuardrailChecker
from src.recommendation_engine import TradeOffAnalyzer
from src.utils import save_json, ensure_data_dir


class PortkeyRealDataEvaluator:
    """
    Evaluates real log file data using ONLY Portkey models.
    Simpler and more unified approach.
    """
    
    def __init__(self):
        """Initialize evaluator with all analysis modules."""
        self.parser = LogParser()
        self.arena = PortkeyDebateArena()
        self.refusal_detector = RefusalDetector()
        self.guardrail_checker = GuardrailChecker()
        self.trade_off_analyzer = TradeOffAnalyzer()
    
    def evaluate_log_files(
        self,
        gemini_log: str,
        claude_log: str,
        gpt_log: str,
        output_file: str = "data/real_evaluation_results.json",
        sample_size: int = None
    ):
        """
        Main evaluation pipeline for .log files.
        
        Args:
            gemini_log: Path to Gemini .log file
            claude_log: Path to Claude .log file
            gpt_log: Path to GPT .log file
            output_file: Where to save results
            sample_size: Optional limit on number of questions to evaluate
        """
        print("=" * 70)
        print("PORTKEY REAL DATA EVALUATION")
        print("=" * 70)
        
        # Step 1: Parse and merge log files
        print("\n📂 Step 1: Parsing log files...")
        merged_data = self.parser.merge_model_responses(
            gemini_log,
            claude_log,
            gpt_log
        )
        
        # Limit to sample size if specified
        if sample_size:
            merged_data = merged_data[:sample_size]
            print(f"   Limited to {sample_size} questions for evaluation")
        
        # Categories are already extracted from log file headers!
        print("\n🏷️  Step 2: Using categories from log files...")
        
        # Step 3: Run peer reviews
        print("\n⚔️ Step 3: Conducting peer reviews...")
        evaluation_results = []
        
        # Map log file model names to actual Portkey models for judging
        model_mapping = {
            'gemini': 'claude-sonnet-4',    # Use Claude to judge Gemini
            'claude': 'gpt-4o',              # Use GPT to judge Claude  
            'gpt': 'claude-haiku'             # Use Claude Haiku to judge GPT
        }
        
        total_questions = len(merged_data)
        
        for i, item in enumerate(merged_data, 1):
            print(f"\n[{i}/{total_questions}] Evaluating Q{item['question_id']}")
            print(f"Category: {item['category']}")
            print(f"Question: {item['question'][:60]}...")
            
            # Remap model names for judging
            judge_answers = {}
            for log_model_name in item['answers'].keys():
                judge_model = model_mapping.get(log_model_name, 'claude-sonnet-4')
                judge_answers[judge_model] = item['answers'][log_model_name]
            
            # Conduct peer review with remapped names
            review_results = self.arena.conduct_peer_review(
                prompt=item['question'],
                answers=judge_answers
            )
            
            # Remap results back to original names for display
            final_results = {}
            reverse_mapping = {v: k for k, v in model_mapping.items()}
            for model, result in review_results.items():
                original_name = reverse_mapping.get(model, model)
                final_results[original_name] = result
            
            # Detect refusals and run guardrail checks
            refusal_checks = {}
            guardrail_checks = {}
            for model_name, answer in item['answers'].items():
                refusal_checks[model_name] = self.refusal_detector.detect(answer)
                guardrail_checks[model_name] = self.guardrail_checker.check(answer, item['question'])
            
            evaluation_results.append({
                'question_id': item['question_id'],
                'question': item['question'],
                'category': item['category'],
                'peer_reviews': final_results,
                'refusal_checks': refusal_checks,
                'guardrail_checks': guardrail_checks
            })
            
            # Show quick summary (0-5 scale)
            print("\n  Scores (out of 5):")
            for model, result in final_results.items():
                refused = " [REFUSED]" if refusal_checks.get(model, {}).get('refused') else ""
                print(f"    {model}: {result['avg_score_5']}/5{refused}")
        
        # Step 4: Calculate all metrics
        print("\n📊 Step 4: Calculating all metrics...")
        category_stats = self._calculate_category_averages(evaluation_results)
        cost_metrics = self._calculate_cost_metrics(evaluation_results)
        refusal_metrics = self._calculate_refusal_metrics(evaluation_results)
        guardrail_stats = self._calculate_guardrail_stats(evaluation_results)
        
        # Step 5: Generate recommendations
        print("\n💡 Step 5: Generating smart recommendations...")
        recommendations = self.trade_off_analyzer.analyze(
            category_stats, cost_metrics, refusal_metrics, guardrail_stats
        )
        
        # Step 6: Save complete results
        ensure_data_dir()
        
        final_results = {
            'total_questions': len(evaluation_results),
            'models': list(merged_data[0]['answers'].keys()) if merged_data else [],
            'evaluations': evaluation_results,
            'category_statistics': category_stats,
            'cost_metrics': cost_metrics,
            'refusal_metrics': refusal_metrics,
            'guardrail_statistics': guardrail_stats,
            'recommendations': recommendations
        }
        
        save_json(output_file, final_results)
        
        print("\n" + "=" * 70)
        print("EVALUATION COMPLETE")
        print("=" * 70)
        print(f"\nResults saved to: {output_file}")
        
        # Print comprehensive summary
        self._print_summary(category_stats, cost_metrics, refusal_metrics, guardrail_stats, recommendations)
        
        return final_results
    
    def _categorize_batch(self, questions: List[str]) -> List[str]:
        """Auto-categorize questions using Portkey model."""
        # Use Claude for categorization (one of the Portkey models)
        from src.portkey_models import PortkeyModelClient
        from src.config import PORTKEY_API_KEY
        
        categorizer = PortkeyModelClient("@anthropic/claude-sonnet-4-20250514", PORTKEY_API_KEY)
        
        categories = []
        batch_size = 20
        
        for i in range(0, len(questions), batch_size):
            batch = questions[i:i+batch_size]
            
            prompt = f"""Categorize these questions into ONE of these categories: code, math, creative, analysis, knowledge, business.

Questions:
{json.dumps(batch, indent=2)}

Return ONLY a JSON array of categories in the same order. Example: ["code", "math", "creative"]

Categories:"""
            
            try:
                response, _ = categorizer.generate(prompt, max_tokens=200, temperature=0.1)
                
                if "```json" in response:
                    response = response.split("```json")[1].split("```")[0].strip()
                elif "```" in response:
                    response = response.split("```")[1].split("```")[0].strip()
                
                batch_categories = json.loads(response)
                categories.extend(batch_categories)
            except:
                # Fallback to 'knowledge' category
                categories.extend(['knowledge'] * len(batch))
        
        return categories
    
    def _calculate_category_averages(self, evaluations: List[Dict]) -> Dict[str, Any]:
        """Calculate average scores per category for each model."""
        category_scores = {}
        
        for eval_item in evaluations:
            category = eval_item['category']
            
            if category not in category_scores:
                category_scores[category] = {}
            
            for model, review_data in eval_item['peer_reviews'].items():
                if model not in category_scores[category]:
                    category_scores[category][model] = []
                
                category_scores[category][model].append(review_data['avg_score_5'])
        
        # Calculate averages
        category_stats = {}
        
        for category, model_scores in category_scores.items():
            category_stats[category] = {}
            
            for model, scores in model_scores.items():
                avg = sum(scores) / len(scores) if scores else 0
                category_stats[category][model] = {
                    'average_score': round(avg, 2),
                    'num_questions': len(scores),
                    'min_score': round(min(scores), 2) if scores else 0,
                    'max_score': round(max(scores), 2) if scores else 0
                }
        
        
        return category_stats
    
    def _calculate_cost_metrics(self, evaluation_results: List[Dict]) -> Dict[str, Any]:
        """Calculate cost and performance metrics per model."""
        model_costs = {}
        
        for result in evaluation_results:
            for model, review_data in result['peer_reviews'].items():
                if model not in model_costs:
                    model_costs[model] = {
                        'total_cost_usd': 0.0,
                        'total_tokens': 0,
                        'total_questions': 0,
                        'avg_latency_ms': []
                    }
                
                model_costs[model]['total_cost_usd'] += review_data.get('total_cost_usd', 0)
                model_costs[model]['total_tokens'] += review_data.get('total_tokens', 0)
                model_costs[model]['total_questions'] += 1
                if review_data.get('avg_latency_ms'):
                    model_costs[model]['avg_latency_ms'].append(review_data['avg_latency_ms'])
        
        # Calculate averages 
        for model in model_costs:
            latencies = model_costs[model]['avg_latency_ms']
            model_costs[model]['avg_latency_ms'] = round(sum(latencies) / len(latencies), 2) if latencies else 0
            model_costs[model]['cost_per_question'] = round(
                model_costs[model]['total_cost_usd'] / model_costs[model]['total_questions'], 6
            ) if model_costs[model]['total_questions'] > 0 else 0
            model_costs[model]['total_cost_usd'] = round(model_costs[model]['total_cost_usd'], 6)
        
        return model_costs
    
    def _calculate_refusal_metrics(self, evaluation_results: List[Dict]) -> Dict[str, Any]:
        """Calculate refusal statistics per model."""
        model_refusals = {}
        
        for result in evaluation_results:
            refusal_checks = result.get('refusal_checks', {})
            for model, refusal_data in refusal_checks.items():
                if model not in model_refusals:
                    model_refusals[model] = {
                        'total_responses': 0,
                        'total_refusals': 0,
                        'refusal_reasons': {}
                    }
                
                model_refusals[model]['total_responses'] += 1
                if refusal_data.get('refused'):
                    model_refusals[model]['total_refusals'] += 1
                    reason = refusal_data.get('reason', 'unknown')
                    model_refusals[model]['refusal_reasons'][reason] = model_refusals[model]['refusal_reasons'].get(reason, 0) + 1
        
        # Calculate refusal rates
        for model in model_refusals:
            total = model_refusals[model]['total_responses']
            refused = model_refusals[model]['total_refusals']
            model_refusals[model]['refusal_rate'] = round(refused / total, 4) if total > 0 else 0
        
        
        return model_refusals
    
    def _calculate_guardrail_stats(self, evaluation_results: List[Dict]) -> Dict[str, Any]:
        """Calculate guardrail statistics per model."""
        model_guards = {}
        
        for result in evaluation_results:
            guardrail_checks = result.get('guardrail_checks', {})
            for model, guard_data in guardrail_checks.items():
                if model not in model_guards:
                    model_guards[model] = {
                        'total_checks': 0,
                        'total_passed': 0,
                        'pii_found': 0,
                        'toxicity_flagged': 0,
                        'safety_flagged': 0
                    }
                
                model_guards[model]['total_checks'] += 1
                if guard_data.get('overall_pass'):
                    model_guards[model]['total_passed'] += 1
                if guard_data.get('pii', {}).get('found'):
                    model_guards[model]['pii_found'] += 1
                if guard_data.get('toxicity', {}).get('flagged'):
                    model_guards[model]['toxicity_flagged'] += 1
                if guard_data.get('safety', {}).get('flagged'):
                    model_guards[model]['safety_flagged'] += 1
        
        # Calculate pass rates
        for model in model_guards:
            total = model_guards[model]['total_checks']
            model_guards[model]['overall_pass_rate'] = round(
                model_guards[model]['total_passed'] / total, 3
            ) if total > 0 else 1.0
        
        return model_guards
    
    def _print_summary(self, category_stats: Dict[str, Any], cost_metrics: Dict[str, Any] = None, refusal_metrics: Dict[str, Any] = None, guardrail_stats: Dict[str, Any] = None, recommendations: Dict[str, Any] = None):
        """Print summary statistics."""
        print("\n📊 Category-wise Average Scores (out of 5):")
        print("=" * 70)
        
        for category, model_stats in sorted(category_stats.items()):
            print(f"\n🏷️  {category.upper()}")
            print("-" * 70)
            
            sorted_models = sorted(
                model_stats.items(),
                key=lambda x: x[1]['average_score'],
                reverse=True
            )
            
            for rank, (model, stats) in enumerate(sorted_models, 1):
                medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else "  "
                print(f"  {medal} {model:20} → {stats['average_score']:.2f}/5  "
                      f"(n={stats['num_questions']}, min={stats['min_score']}, max={stats['max_score']})")
        
        # Overall winner
        print("\n" + "=" * 70)
        print("🏆 OVERALL PERFORMANCE")
        print("=" * 70)
        
        overall_scores = {}
        for category, model_stats in category_stats.items():
            for model, stats in model_stats.items():
                if model not in overall_scores:
                    overall_scores[model] = []
                overall_scores[model].append(stats['average_score'])
        
        overall_avg = {
            model: round(sum(scores) / len(scores), 2)
            for model, scores in overall_scores.items()
        }
        
        sorted_overall = sorted(overall_avg.items(), key=lambda x: x[1], reverse=True)
        
        for rank, (model, avg_score) in enumerate(sorted_overall, 1):
            medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else "  "
            print(f"{medal} {rank}. {model:20} → {avg_score:.2f}/5 average across all categories")


def main():
    """Main execution."""
    import sys
    
    if len(sys.argv) < 4:
        print("=" * 70)
        print("PORTKEY REAL DATA EVALUATOR")
        print("=" * 70)
        print("\nUSAGE:")
        print("  python evaluate_portkey.py <gemini.log> <claude.log> <gpt.log> [sample_size] [output_file]")
        print("\nExample:")
        print("  python evaluate_portkey.py data/gemini.log data/claude.log data/gpt.log 50")
        print("  python evaluate_portkey.py data/gemini.log data/claude.log data/gpt.log 50 results_jan17.json")
        print("\nNote: Each run overwrites the output file. Rename previous results to preserve them!")
        return
    
    gemini_log = sys.argv[1]
    claude_log = sys.argv[2]
    gpt_log = sys.argv[3]
    sample_size = int(sys.argv[4]) if len(sys.argv) > 4 and sys.argv[4].isdigit() else None
    output_file = sys.argv[5] if len(sys.argv) > 5 else "data/real_evaluation_results.json"
    
    # Add data/ prefix if not already there
    if output_file and not output_file.startswith('data/'):
        output_file = f"data/{output_file}"
    
    evaluator = PortkeyRealDataEvaluator()
    evaluator.evaluate_log_files(gemini_log, claude_log, gpt_log, 
                                   sample_size=sample_size, 
                                   output_file=output_file)


if __name__ == "__main__":
    main()
