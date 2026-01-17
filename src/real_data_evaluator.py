"""
Real Data Evaluator
Evaluates .log file data using peer review (models judge each other)
Outputs scores out of 5 with category-wise averages
"""

import json
from typing import Dict, Any, List
from src.log_parser import LogParser
from src.debate import DebateArena
from src.categorizer import PromptCategorizer
from src.utils import save_json, ensure_data_dir


class RealDataEvaluator:
    """
    Evaluates real log file data using peer review.
    Models judge each other's answers on a 0-5 scale.
    """
    
    def __init__(self):
        """Initialize evaluator."""
        self.parser = LogParser()
        self.arena = DebateArena()
        self.categorizer = PromptCategorizer()
    
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
        print("REAL DATA EVALUATION - FROM LOG FILES")
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
        
        # Step 2: Categorize questions
        print("\n🏷️  Step 2: Categorizing questions...")
        questions = [item['question'] for item in merged_data]
        categories = self.categorizer.categorize_batch(questions)
        
        for i, category in enumerate(categories):
            merged_data[i]['category'] = category
        
        # Step 3: Run peer reviews
        print("\n⚔️ Step 3: Conducting peer reviews...")
        evaluation_results = []
        
        total_questions = len(merged_data)
        
        for i, item in enumerate(merged_data, 1):
            print(f"\n[{i}/{total_questions}] Evaluating Q{item['question_id']}")
            print(f"Category: {item['category']}")
            print(f"Question: {item['question'][:60]}...")
            
            # Conduct peer review for this question
            review_results = self.arena.conduct_peer_review(
                prompt=item['question'],
                answers=item['answers']
            )
            
            # Convert scores to 0-5 scale instead of 0-10
            for model, result in review_results.items():
                result['avg_score_5'] = round(result['avg_score'] / 2, 2)  # Convert 0-10 to 0-5
                
                # Also convert individual review scores
                for review in result['reviews']:
                    review['score_5'] = round(review['score'] / 2, 2)
            
            evaluation_results.append({
                'question_id': item['question_id'],
                'question': item['question'],
                'category': item['category'],
                'peer_reviews': review_results
            })
            
            # Show quick summary
            print("\n  Scores (out of 5):")
            for model, result in review_results.items():
                print(f"    {model}: {result['avg_score_5']}/5")
        
        # Step 4: Calculate category-wise averages
        print("\n📊 Step 4: Calculating category averages...")
        category_stats = self._calculate_category_averages(evaluation_results)
        
        # Step 5: Save results
        ensure_data_dir()
        
        final_results = {
            'total_questions': len(evaluation_results),
            'models': list(merged_data[0]['answers'].keys()) if merged_data else [],
            'evaluations': evaluation_results,
            'category_statistics': category_stats
        }
        
        save_json(output_file, final_results)
        
        print("\n" + "=" * 70)
        print("EVALUATION COMPLETE")
        print("=" * 70)
        print(f"\nResults saved to: {output_file}")
        
        # Print summary
        self._print_summary(category_stats)
        
        return final_results
    
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
    
    def _print_summary(self, category_stats: Dict[str, Any]):
        """Print summary statistics."""
        print("\n📊 Category-wise Average Scores (out of 5):")
        print("=" * 70)
        
        for category, model_stats in sorted(category_stats.items()):
            print(f"\n🏷️  {category.upper()}")
            print("-" * 70)
            
            # Sort models by average score
            sorted_models = sorted(
                model_stats.items(),
                key=lambda x: x[1]['average_score'],
                reverse=True
            )
            
            for rank, (model, stats) in enumerate(sorted_models, 1):
                medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else "  "
                print(f"  {medal} {model:15} → {stats['average_score']:.2f}/5  "
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
        
        # Calculate overall averages
        overall_avg = {
            model: round(sum(scores) / len(scores), 2)
            for model, scores in overall_scores.items()
        }
        
        sorted_overall = sorted(overall_avg.items(), key=lambda x: x[1], reverse=True)
        
        for rank, (model, avg_score) in enumerate(sorted_overall, 1):
            medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else "  "
            print(f"{medal} {rank}. {model:15} → {avg_score:.2f}/5 average across all categories")


def main():
    """
    Main execution.
    
    USAGE:
    ------
    Replace these paths with your actual .log file paths:
    """
    import sys
    
    print("=" * 70)
    print("REAL DATA EVALUATOR")
    print("=" * 70)
    print("\nThis script evaluates your .log files with real Q&A data.")
    print("\nPlease configure the file paths in this script or pass them as arguments.")
    
    # Example file paths - UPDATE THESE
    gemini_log = "path/to/gemini_answers.log"
    claude_log = "path/to/claude_answers.log"
    gpt_log = "path/to/gpt_answers.log"
    
    # Check if paths provided as arguments
    if len(sys.argv) > 3:
        gemini_log = sys.argv[1]
        claude_log = sys.argv[2]
        gpt_log = sys.argv[3]
        sample_size = int(sys.argv[4]) if len(sys.argv) > 4 else None
    else:
        print("\n⚠️  No file paths provided!")
        print("\nUSAGE:")
        print("  python src/real_data_evaluator.py <gemini.log> <claude.log> <gpt.log> [sample_size]")
        print("\nExample:")
        print("  python src/real_data_evaluator.py data/gemini.log data/claude.log data/gpt.log 50")
        return
    
    # Run evaluation
    evaluator = RealDataEvaluator()
    
    evaluator.evaluate_log_files(
        gemini_log=gemini_log,
        claude_log=claude_log,
        gpt_log=gpt_log,
        sample_size=sample_size if 'sample_size' in locals() else None
    )


if __name__ == "__main__":
    main()
