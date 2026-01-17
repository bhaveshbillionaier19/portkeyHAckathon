"""
Simplified Debate Arena - PORTKEY ONLY
Uses only Portkey models for all debates
"""

import json
import os
from typing import Dict, Any, List
from src.portkey_models import PortkeyModelClient
from src.config import MODELS, PORTKEY_API_KEY


class PortkeyDebateArena:
    """
    Debate arena using ONLY Portkey models.
    Simpler and more unified than mixed approach.
    """
    
    def __init__(self):
        """Initialize debate arena with Portkey models."""
        self.model_clients = {}
        self.debate_count = 0
        
        if not PORTKEY_API_KEY:
            raise ValueError("PORTKEY_API_KEY not found in .env file!")
        
        # Initialize all Portkey models
        for model_name, config in MODELS.items():
            try:
                self.model_clients[model_name] = PortkeyModelClient(
                    config["model_id"],
                    PORTKEY_API_KEY
                )
                print(f"✅ Initialized {config['display_name']}")
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
        """
        results = {}
        
        print(f"\n⚔️ Starting debate for prompt: {prompt[:60]}...")
        print(f"Participants: {', '.join(answers.keys())}")
        
        for candidate_model, candidate_answer in answers.items():
            print(f"\n📊 Evaluating {candidate_model}...")
            
            reviews = []
            scores = []
            
            for judge_model in answers.keys():
                if judge_model == candidate_model:
                    continue
                
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
            
            
            avg_score = sum(scores) / len(scores) if scores else 0.0
            
            # Aggregate costs and tokens from reviews
            total_cost = sum(r.get('cost_usd', 0) for r in reviews)
            total_tokens = sum(r.get('tokens', 0) for r in reviews)
            avg_latency = sum(r.get('latency_ms', 0) for r in reviews) / len(reviews) if reviews else 0
            
            results[candidate_model] = {
                'answer': candidate_answer,
                'avg_score': round(avg_score, 2),
                'avg_score_5': round(avg_score / 2, 2),  # 0-5 scale
                'reviews': reviews,
                'total_reviews': len(reviews),
                'total_cost_usd': round(total_cost, 6),
                'total_tokens': total_tokens,
                'avg_latency_ms': round(avg_latency, 2)
            }
            
            print(f"  📈 Average score: {avg_score:.2f}/10 ({results[candidate_model]['avg_score_5']}/5)")
            print(f"  💰 Evaluation cost: ${total_cost:.6f} ({total_tokens} tokens)")
        
        self.debate_count += 1
        return results
    
    def _get_peer_review(
        self,
        prompt: str,
        candidate_answer: str,
        candidate_model: str,
        judge_model: str
    ) -> Dict[str, Any]:
        """Get peer review from judge model."""
        judge_client = self.model_clients.get(judge_model)
        
        if not judge_client:
            return {
                'judge': judge_model,
                'score': None,
                'critique': f"Judge model {judge_model} not available",
                'error': True
            }
        
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
                temperature=0.3
            )
            
            if not response_text or metadata.get('error'):
                return {
                    'judge': judge_model,
                    'score': None,
                    'critique': f"Error: {metadata.get('error', 'No response')}",
                    'error': True
                }
            
            # Parse JSON
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            review_data = json.loads(response_text)
            score = float(review_data.get('score', 0))
            score = max(0, min(10, score))
            
            return {
                'judge': judge_model,
                'score': score,
                'score_5': round(score / 2, 2),  # Also include 0-5 scale
                'critique': review_data.get('critique', 'No critique provided'),
                'cost_usd': metadata.get('cost_usd', 0.0),
                'tokens': metadata.get('total_tokens', 0),
                'latency_ms': metadata.get('latency_ms', 0),
                'error': False
            }
        
        except json.JSONDecodeError:
            return {
                'judge': judge_model,
                'score': 5.0,
                'score_5': 2.5,
                'critique': f"Parse error",
                'error': True
            }
        except Exception as e:
            return {
                'judge': judge_model,
                'score': None,
                'score_5': None,
                'critique': str(e),
                'error': True
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get arena statistics."""
        return {
            'total_debates': self.debate_count,
            'models_available': list(self.model_clients.keys()),
            'total_models': len(self.model_clients)
        }


if __name__ == "__main__":
    print("=" * 70)
    print("PORTKEY DEBATE ARENA")
    print("=" * 70)
    
    arena = PortkeyDebateArena()
    
    print(f"\n📊 Arena Stats:")
    stats = arena.get_stats()
    print(f"Total models available: {stats['total_models']}")
    print(f"Models: {', '.join(stats['models_available'])}")
