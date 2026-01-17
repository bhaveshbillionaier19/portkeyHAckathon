"""
Weekly Debate Tournament Runner
Runs model peer-review tournament on demand or scheduled
"""

import json
import random
from datetime import datetime
from src.debate import DebateArena
from src.models import ModelClient
from src.config import MODELS
from src.utils import load_prompts, save_json, ensure_data_dir


def run_weekly_tournament(num_prompts: int = 20, output_file: str = "data/debate_results.json"):
    """
    Run a tournament where models answer prompts and peer-review each other.
    
    Args:
        num_prompts: Number of prompts to use in tournament
        output_file: Where to save results
    """
    print("=" * 70)
    print("🏆 WEEKLY MODEL TOURNAMENT")
    print("=" * 70)
    
    # Load prompts
    print(f"\n📂 Loading prompts...")
    all_prompts = load_prompts()
    
    if not all_prompts:
        print("❌ No prompts found. Please generate prompts first.")
        print("Run: python src/generate_data.py")
        return
    
    # Select random prompts
    num_prompts = min(num_prompts, len(all_prompts))
    selected_prompts = random.sample(all_prompts, num_prompts)
    
    print(f"✅ Selected {num_prompts} random prompts for tournament")
    
    # Initialize arena and model clients
    arena = DebateArena()
    model_clients = {}
    
    for model_name in MODELS.keys():
        try:
            model_clients[model_name] = ModelClient(model_name)
        except Exception as e:
            print(f"⚠️ Could not initialize {model_name}: {e}")
    
    print(f"✅ Initialized {len(model_clients)} models for tournament")
    
    # Tournament results
    tournament_results = {
        "tournament_date": datetime.now().isoformat(),
        "num_prompts": num_prompts,
        "models": list(model_clients.keys()),
        "debates": []
    }
    
    # Run tournament
    print(f"\n🎮 Starting tournament with {num_prompts} rounds...")
    
    for round_num, prompt_data in enumerate(selected_prompts, 1):
        prompt = prompt_data.get('prompt', '')
        category = prompt_data.get('category', 'unknown')
        
        print(f"\n{'='*70}")
        print(f"ROUND {round_num}/{num_prompts}")
        print(f"Category: {category}")
        print(f"Prompt: {prompt[:60]}...")
        print(f"{'='*70}")
        
        # Step 1: Generate answers from all models
        print(f"\n📝 Generating answers from all models...")
        answers = {}
        
        for model_name, client in model_clients.items():
            try:
                response_text, metadata = client.generate(prompt, max_tokens=500)
                
                if response_text and not metadata.get('error'):
                    answers[model_name] = response_text
                    cost = client.calculate_cost(
                        metadata.get('tokens_input', 0),
                        metadata.get('tokens_output', 0)
                    )
                    print(f"  ✅ {model_name}: Generated (${cost:.6f})")
                else:
                    print(f"  ❌ {model_name}: Failed - {metadata.get('error')}")
            
            except Exception as e:
                print(f"  ❌ {model_name}: Error - {e}")
        
        # Step 2: Conduct peer review
        if len(answers) >= 2:  # Need at least 2 models to debate
            print(f"\n⚔️ Starting peer review...")
            debate_results = arena.conduct_peer_review(prompt, answers)
            
            # Find winner of this round
            winner = max(debate_results.items(), key=lambda x: x[1]['avg_score'])
            winner_name = winner[0]
            winner_score = winner[1]['avg_score']
            
            print(f"\n🏆 Round {round_num} Winner: {winner_name} ({winner_score}/10)")
            
            # Step 3: Store results
            round_result = {
                "round": round_num,
                "prompt": prompt,
                "category": category,
                "winner": winner_name,
                "winner_score": winner_score,
                "results": debate_results
            }
            
            tournament_results["debates"].append(round_result)
        else:
            print(f"\n⚠️ Not enough models responded ({len(answers)}), skipping round")
    
    # Save results
    ensure_data_dir()
    save_json(output_file, tournament_results)
    
    print(f"\n{'='*70}")
    print("TOURNAMENT COMPLETE")
    print(f"{'='*70}")
    print(f"Results saved to: {output_file}")
    print(f"Total rounds completed: {len(tournament_results['debates'])}")
    
    # Quick summary
    if tournament_results['debates']:
        winner_counts = {}
        for debate in tournament_results['debates']:
            winner = debate['winner']
            winner_counts[winner] = winner_counts.get(winner, 0) + 1
        
        print(f"\n🏆 Tournament Summary:")
        sorted_winners = sorted(winner_counts.items(), key=lambda x: x[1], reverse=True)
        for rank, (model, wins) in enumerate(sorted_winners, 1):
            print(f"  {rank}. {model}: {wins} wins")


def quick_tournament(num_prompts: int = 5):
    """Run a quick 5-round tournament for testing."""
    print("🚀 Running quick tournament (5 rounds)...\n")
    run_weekly_tournament(num_prompts=num_prompts, output_file="data/quick_debate_results.json")


if __name__ == "__main__":
    # Run full tournament
    run_weekly_tournament(num_prompts=20)
