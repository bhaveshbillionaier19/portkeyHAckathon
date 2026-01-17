"""
Utility functions for data handling
"""

import json
import os
from typing import List, Dict, Any
from src.config import DATA_DIR, PROMPTS_FILE, RESPONSES_FILE, ANALYSIS_FILE


def ensure_data_dir():
    """Ensure data directory exists."""
    os.makedirs(DATA_DIR, exist_ok=True)


def load_json(filepath: str) -> Any:
    """
    Load JSON file.
    
    Args:
        filepath: Path to JSON file
    
    Returns:
        Parsed JSON data or None if file doesn't exist
    """
    if not os.path.exists(filepath):
        return None
    
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(filepath: str, data: Any):
    """
    Save data to JSON file.
    
    Args:
        filepath: Path to save to
        data: Data to save
    """
    ensure_data_dir()
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_prompts() -> List[Dict[str, Any]]:
    """
    Load prompts from prompts.json.
    
    Returns:
        List of prompt dictionaries
    """
    prompts = load_json(PROMPTS_FILE)
    return prompts if prompts else []


def save_prompts(prompts: List[Dict[str, Any]]):
    """
    Save prompts to prompts.json.
    
    Args:
        prompts: List of prompt dictionaries
    """
    save_json(PROMPTS_FILE, prompts)


def load_responses() -> List[Dict[str, Any]]:
    """
    Load responses from responses.json.
    
    Returns:
        List of response dictionaries
    """
    responses = load_json(RESPONSES_FILE)
    return responses if responses else []


def save_responses(responses: List[Dict[str, Any]]):
    """
    Save responses to responses.json.
    
    Args:
        responses: List of response dictionaries
    """
    save_json(RESPONSES_FILE, responses)


def load_analysis() -> Dict[str, Any]:
    """
    Load analysis from analysis.json.
    
    Returns:
        Analysis dictionary
    """
    analysis = load_json(ANALYSIS_FILE)
    return analysis if analysis else {}


def save_analysis(analysis: Dict[str, Any]):
    """
    Save analysis to analysis.json.
    
    Args:
        analysis: Analysis dictionary
    """
    save_json(ANALYSIS_FILE, analysis)


def csv_to_prompts(csv_path: str) -> List[Dict[str, Any]]:
    """
    Convert CSV file to prompts format.
    
    Args:
        csv_path: Path to CSV file
    
    Returns:
        List of prompt dictionaries
    """
    import pandas as pd
    
    df = pd.read_csv(csv_path)
    
    prompts = []
    for _, row in df.iterrows():
        prompt_dict = {
            "prompt": row.get("prompt", ""),
            "category": row.get("category", "unknown")
        }
        
        # Add optional fields if present
        if "expected_output" in df.columns:
            prompt_dict["expected_output"] = row.get("expected_output")
        
        prompts.append(prompt_dict)
    
    return prompts
