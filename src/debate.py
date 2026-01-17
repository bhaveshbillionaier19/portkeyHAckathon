"""
Debate Arena
Peer-review system where models judge each other's responses
"""

import json
from typing import Dict, Any, List
from src.models import ModelClient
from src.config import MODELS


class DebateArena:
    """
    Conducts peer reviews where models critique each other's answers.
    """
    
    def __init__(self):
        """Initialize the debate arena."""
        self.model_clients = {}
        self.debate_count = 0
        
        # Initialize clients for all models
        for model_name in MODELS.keys():
            try:
                self.model_clients[model_name] = ModelClient(model_name)
                print(f"✅ Initialized {model_name} for debate")
            except Exception as e:
                print(f"⚠️  Failed to initialize {model_name}: {e}")
    
    def conduct_peer_review(self, prompt: str, answers: Dict[str, str]) -> Dict[str, Any]:
        """
        Conduct peer review where each model judges others' answers.
        
        Args:
            prompt: The original user prompt
            answers: Dict mapping model_name -> answer_text
        
        Returns:
            Dictionary with review results for each model
            Format: {
                'model_name': {
                    'answer': str,
                    'avg_score': float,
                    'reviews': [{'judge': str, 'score': float, 'critique': str}]
                }
            }
        """
        results = {}
        
        print(f"\n⚔️ Starting debate for prompt: {prompt[:60]}...")
        print(f"Participants: {', '.join(answers.keys())}")
        
        # For each candidate model
        for candidate_model, candidate_answer in answers.items():
            print(f"\n📊 Evaluating {candidate_model}...")
            
            reviews = []
            scores = []
            
            # Get reviews from all other models (judges)
            for judge_model in answers.keys():
                if judge_model == candidate_model:
                    continue  # Models don't judge themselves
                
                try:
                    review = self._get_peer_review(
                        prompt=prompt,
                        candidate_answer=candidate_answer,
                        candidate_model=candidate_model,
                        judge_model=judge_model
                    )
                    
                    if review and review['score'] is not None:
                        reviews.append(review)
                        scores.append(review['score'])
                        print(f"  ✅ {judge_model}: {review['score']}/10")
                    else:
                        print(f"  ⚠️  {judge_model}: Review failed")
                
                except Exception as e:
                    print(f"  ❌ {judge_model}: Error - {e}")
            
            # Calculate average score
            avg_score = sum(scores) / len(scores) if scores else 0.0
            
            results[candidate_model] = {
                'answer': candidate_answer,
                'avg_score': round(avg_score, 2),
                'reviews': reviews,
                'total_reviews': len(reviews)
            }
            
            print(f"  📈 Average score: {avg_score:.2f}/10")
        
        self.debate_count += 1
        return results
    
    def _get_peer_review(
        self,
        prompt: str,
        candidate_answer: str,
        candidate_model: str,
        judge_model: str
    ) -> Dict[str, Any]:
        """
        Get a peer review from a judge model.
        
        Args:
            prompt: Original user prompt
            candidate_answer: The answer to review
            candidate_model: Name of the model being judged
            judge_model: Name of the judge model
        
        Returns:
            Dict with judge, score, and critique
        """
        judge_client = self.model_clients[judge_model]
        
        # Construct debate prompt
        debate_prompt = f"""You are a strict technical reviewer evaluating AI model responses.

ORIGINAL USER PROMPT:
{prompt}

CANDIDATE MODEL: {candidate_model}
CANDIDATE ANSWER:
{candidate_answer}

YOUR TASK:
Critique this answer thoroughly for:
1. **Correctness**: Is the answer factually accurate and relevant?
2. **Safety**: Are there any security, ethical, or safety concerns?
3. **Conciseness**: Is it appropriately detailed without being verbose?
4. **Quality**: Overall response quality

Then rate it on a 0-10 scale where:
- 0-3: Poor (incorrect, unsafe, or unhelpful)
- 4-6: Acceptable (mostly correct but with issues)
- 7-8: Good (correct and helpful)
- 9-10: Excellent (perfect response)

OUTPUT FORMAT (JSON only, no markdown):
{{"score": 8.5, "critique": "Brief explanation of your rating"}}

Provide your review:"""

        try:
            response_text, metadata = judge_client.generate(
                prompt=debate_prompt,
                max_tokens=300,
                temperature=0.3  # Lower temp for consistent judging
            )
            
            if not response_text or metadata.get('error'):
                return {
                    'judge': judge_model,
                    'score': None,
                    'critique': f"Error: {metadata.get('error', 'No response')}",
                    'error': True
                }
            
            # Parse JSON response
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            review_data = json.loads(response_text)
            
            # Validate score
            score = float(review_data.get('score', 0))
            score = max(0, min(10, score))  # Clamp to 0-10
            
            return {
                'judge': judge_model,
                'score': score,
                'critique': review_data.get('critique', 'No critique provided'),
                'error': False
            }
        
        except json.JSONDecodeError as e:
            print(f"    ⚠️ JSON parse error from {judge_model}: {e}")
            return {
                'judge': judge_model,
                'score': 5.0,  # Default middle score
                'critique': f"Parse error: {str(e)[:100]}",
                'error': True
            }
        except Exception as e:
            print(f"    ⚠️ Error from {judge_model}: {e}")
            return {
                'judge': judge_model,
                'score': None,
                'critique': str(e),
                'error': True
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get debate arena statistics."""
        return {
            'total_debates': self.debate_count,
            'models_available': list(self.model_clients.keys()),
            'total_models': len(self.model_clients)
        }


# Demo function
def demo_debate():
    """Demo of the debate arena."""
    arena = DebateArena()
    
    # Sample prompt and answers
    test_prompt = "Write a Python function to check if a number is prime"
    
    test_answers = {
        'gpt-4o': """def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True""",
        
        'gpt-4o-mini': """def is_prime(n):
    if n <= 1:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(n**0.5) + 1, 2):
        if n % i == 0:
            return False
    return True""",
        
        'claude-sonnet-4': """def is_prime(n):
    \"\"\"Check if a number is prime.\"\"\"
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(n**0.5) + 1, 2):
        if n % i == 0:
            return False
    return True"""
    }
    
    print("=" * 70)
    print("DEBATE ARENA DEMO")
    print("=" * 70)
    
    results = arena.conduct_peer_review(test_prompt, test_answers)
    
    print("\n" + "=" * 70)
    print("DEBATE RESULTS")
    print("=" * 70)
    
    # Sort by average score
    sorted_results = sorted(results.items(), key=lambda x: x[1]['avg_score'], reverse=True)
    
    for rank, (model, data) in enumerate(sorted_results, 1):
        print(f"\n🏆 Rank {rank}: {model}")
        print(f"   Average Score: {data['avg_score']}/10")
        print(f"   Reviews received: {data['total_reviews']}")
        print(f"\n   Peer Reviews:")
        for review in data['reviews']:
            print(f"     - {review['judge']}: {review['score']}/10")
            print(f"       \"{review['critique'][:80]}...\"")


if __name__ == "__main__":
    demo_debate()
