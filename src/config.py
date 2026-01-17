"""
Configuration - PORTKEY ONLY
All models accessed via Portkey unified API
"""

import os
from dotenv import load_dotenv

load_dotenv()

# API Key
PORTKEY_API_KEY = os.getenv("PORTKEY_API_KEY", "")

# Portkey Models - ONLY WORKING MODELS (tested and verified)
MODELS = {
    "gpt-4o": {
        "provider": "portkey",
        "model_id": "@openai/gpt-4o",
        "input_cost": 0.0025,
        "output_cost": 0.01,
        "display_name": "GPT-4o"
    },
    "gpt-4o-mini": {
        "provider": "portkey",
        "model_id": "@openai/gpt-4o-mini",
        "input_cost": 0.00015,
        "output_cost": 0.0006,
        "display_name": "GPT-4o Mini"
    },
    "claude-sonnet-4": {
        "provider": "portkey",
        "model_id": "@anthropic/claude-sonnet-4-20250514",
        "input_cost": 0.003,
        "output_cost": 0.015,
        "display_name": "Claude Sonnet 4"
    },
    "claude-haiku": {
        "provider": "portkey",
        "model_id": "@anthropic/claude-3-haiku-20240307",
        "input_cost": 0.00025,
        "output_cost": 0.00125,
        "display_name": "Claude 3 Haiku"
    },
    "claude-sonnet-4-5": {
        "provider": "portkey",
        "model_id": "@anthropic/claude-sonnet-4-5-20250929",
        "input_cost": 0.003,
        "output_cost": 0.015,
        "display_name": "Claude Sonnet 4.5"
    }
    
    # REMOVED - Not accessible with your Portkey configuration:
    # "gemini-flash" - Google API key not configured in Portkey
    # "grok-vision" - Model doesn't exist or xAI key not configured
    # "llama-3-3-70b" - Groq API key not configured in Portkey
}

# Categories for question classification
CATEGORIES = ["code", "math", "creative", "analysis", "knowledge", "business"]

# Judge model for evaluation
JUDGE_MODEL = "claude-sonnet-4"

# Data file paths
import os
DATA_DIR = "data"
PROMPTS_FILE = os.path.join(DATA_DIR, "prompts.json")
RESPONSES_FILE = os.path.join(DATA_DIR, "responses.json")
ANALYSIS_FILE = os.path.join(DATA_DIR, "analysis.json")
