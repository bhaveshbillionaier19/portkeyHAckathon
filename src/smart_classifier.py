"""
Smart Classifier - Using user's provided classification code
Classifies prompts into categories for routing
"""

import os
import json
from dotenv import load_dotenv
from portkey_ai import Portkey
from pydantic import BaseModel, Field
from typing import Literal

# Load environment variables
load_dotenv()

# Define the allowed categories (matching user's categories)
CategoryType = Literal['science', 'math', 'code', 'logic', 'business', 'tech', 'home', 'real-time', 'unethical']

class SentenceClassification(BaseModel):
    category: CategoryType = Field(description="The single category that best describes the input sentence.")

def classify_sentence(text: str) -> str:
    """
    Classifies a given sentence into one of the predefined categories using Portkey/GPT-4o.
    Returns the category as a string.
    """
    
    # Initialize Portkey
    api_key = os.getenv("PORTKEY_API_KEY")
    if not api_key:
        raise ValueError("PORTKEY_API_KEY not found in environment variables")

    portkey = Portkey(
        api_key=api_key,
        provider="@openai" 
    )

    # Get the schema for the Pydantic model
    schema = SentenceClassification.model_json_schema()

    prompt = f"""
    Classify the following sentence into exactly one of these categories:
    ['science', 'math', 'code', 'logic', 'business', 'tech', 'home', 'real-time', 'unethical']
    
    Input Sentence: "{text}"
    
    Return the result in JSON format matching the schema.
    """

    try:
        completion = portkey.chat.completions.create(
            model="gpt-4o", 
            messages=[
                {"role": "system", "content": f"You are a strict classification system. Output JSON matching this schema: {json.dumps(schema)}"},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0  # Deterministic output
        )
        
        raw_content = completion.choices[0].message.content
        data = json.loads(raw_content)
        
        # Validate with Pydantic
        classification = SentenceClassification(**data)
        
        return classification.category

    except Exception as e:
        print(f"Error during classification: {e}")
        return "tech"  # Safe fallback category


if __name__ == "__main__":
    # Test with user input or arguments
    import sys
    
    if len(sys.argv) > 1:
        input_text = " ".join(sys.argv[1:])
        print(f"Input: {input_text}")
        result = classify_sentence(input_text)
        print(f"Category: {result}")
    else:
        # Default test loop
        print("Enter a sentence to classify (or 'q' to quit):")
        while True:
            text = input("> ")
            if text.lower() in ('q', 'quit', 'exit'):
                break
            if not text.strip():
                continue
                
            result = classify_sentence(text)
            print(f"Category: {result}")
