"""
Enhanced Debate Arena with Portkey Models
Supports both direct API models and Portkey models for debates
"""

import json
import os
from typing import Dict, Any, List
from src.models import ModelClient
from src.portkey_models import PortkeyModelClient
from src.config import MODELS, PORTKEY_MODELS
from dotenv import load_dotenv

load_dotenv()


class EnhancedDebateArena:
    """
    Debate arena supporting both direct API models and Portkey models.
    """
    
    def __init__(self, use_portkey: bool = False):
        """
        Initialize debate arena with optional Portkey models.
        
        Args:
            use_portkey: If True, includes Portkey models in debates
        """
        self.model_clients = {}
        self.debate_count = 0
        self.portkey_api_key = os.getenv("PORTKEY_API_KEY", "")
        
        # Initialize standard models
        for model_name in MODELS.keys():
            try:
                self.model_clients[model_name] = ModelClient(model_name)
                print(f"✅ Initialized {model_name}")
            except Exception as e:
                print(f"⚠️  Failed to initialize {model_name}: {e}")
        
        # Initialize Portkey models if requested
        if use_portkey:
            if not self.portkey_api_key:
                print("⚠️  PORTKEY_API_KEY not found. Skipping Portkey models.")
                print("   Add PORTKEY_API_KEY to .env to enable Grok, Claude 4.5, GPT Realtime")
            else:
                for model_name, config in PORTKEY_MODELS.items():
                    try:
                        self.model_clients[model_name] = PortkeyModelClient(
                            config["model_id"],
                            self.portkey_api_key
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
                'critique': review_data.get('critique', 'No critique provided'),
                'error': False
            }
        
        except json.JSONDecodeError:
            return {
                'judge': judge_model,
                'score': 5.0,
                'critique': f"Parse error",
                'error': True
            }
        except Exception as e:
            return {
                'judge': judge_model,
                'score': None,
                'critique': str(e),
                'error': True
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get arena statistics."""
        return {
            'total_debates': self.debate_count,
            'models_available': list(self.model_clients.keys()),
            'total_models': len(self.model_clients),
            'portkey_enabled': bool(self.portkey_api_key)
        }


# Demo
if __name__ == "__main__":
    print("=" * 70)
    print("ENHANCED DEBATE ARENA - WITH PORTKEY MODELS")
    print("=" * 70)
    
    # Initialize with Portkey models
    arena = EnhancedDebateArena(use_portkey=True)
    
    print(f"\n📊 Arena Stats:")
    stats = arena.get_stats()
    print(f"Total models available: {stats['total_models']}")
    print(f"Portkey enabled: {stats['portkey_enabled']}")
    print(f"Models: {', '.join(stats['models_available'])}")
