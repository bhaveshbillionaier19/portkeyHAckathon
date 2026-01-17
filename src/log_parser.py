"""
Log File Parser with Category Detection
Parses .log files containing Q&A pairs with category markers
"""

import re
import json
from typing import List, Dict, Any
from pathlib import Path


class LogParser:
    """
    Parser for .log files containing model responses with category headers.
    
    Expected format in .log files:
    - Category headers: # SCIENCE QUESTIONS, # MATH QUESTIONS, etc.
    - Question: followed by answer
    """
    
    def __init__(self):
        self.qa_pairs = []
        # Map various category names to standard ones
        self.category_map = {
            'science': 'knowledge',
            'scien': 'knowledge',
            'math': 'math',
            'mathematic': 'math',
            'cod': 'code',
            'coding': 'code',
            'program': 'code',
            'logic': 'analysis',
            'puzzle': 'analysis',
            'reasoning': 'analysis',
            'business': 'business',
            'career': 'business',
            'creative': 'creative',
            'creativ': 'creative'
        }
    
    def parse_log_file(self, file_path: str, model_name: str) -> List[Dict[str, Any]]:
        """
        Parse a single .log file with category detection.
        
        Args:
            file_path: Path to .log file
            model_name: Name of the model (gemini, claude, gpt)
        
        Returns:
            List of Q&A pairs with metadata and categories
        """
        print(f"📂 Parsing {file_path} for {model_name}...")
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Parse with category detection
        qa_pairs = self._parse_with_categories(content, model_name)
        
        print(f"✅ Found {len(qa_pairs)} Q&A pairs from {model_name}")
        return qa_pairs
    
    def _parse_with_categories(self, content: str, model_name: str) -> List[Dict[str, Any]]:
        """Parse content detecting category headers and Q&A pairs."""
        qa_pairs = []
        lines = content.split('\n')
        
        current_category = "general"
        current_question = None
        current_answer_lines = []
        question_id = 0
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Skip empty lines
            if not line:
                i += 1
                continue
            
            # Detect category headers (# CATEGORY QUESTIONS or # CATEGORY)
            if line.startswith('#') and not line.startswith('##'):
                category_text = line.lstrip('#').strip()
                # Remove "QUESTIONS" suffix
                category_text = re.sub(r'\s+QUESTIONS?$', '', category_text, flags=re.IGNORECASE)
                
                # Map to standard category
                category_lower = category_text.lower()
                matched_category = None
                
                for key, value in self.category_map.items():
                    if key in category_lower:
                        matched_category = value
                        break
                
                current_category = matched_category if matched_category else category_lower.split()[0] if category_lower else 'general'
                
                i += 1
                continue
            
            # Detect Question line
            if line.startswith(('Question:', 'Q:')):
                # Save previous Q&A if exists
                if current_question and current_answer_lines:
                    question_id += 1
                    qa_pairs.append({
                        'question_id': question_id,
                        'question': current_question,
                        'answer': '\n'.join(current_answer_lines).strip(),
                        'model': model_name,
                        'category': current_category
                    })
                    current_answer_lines = []
                
                # Extract question text
                current_question = line.split(':', 1)[1].strip() if ':' in line else line.lstrip('Question ').strip()
                i += 1
                continue
            
            # Detect Answer line
            if line.startswith(('Answer:', 'A:')):
                answer_text = line.split(':', 1)[1].strip() if ':' in line else line.lstrip('Answer ').strip()
                current_answer_lines = [answer_text] if answer_text else []
                i += 1
                continue
            
            # Accumulate answer lines (everything between Answer and next Question)
            if current_question:
                # Stop if we hit another Question or category marker
                if not (line.startswith(('Question:', 'Q:', '#'))):
                    current_answer_lines.append(line)
            
            i += 1
        
        # Save last Q&A
        if current_question and current_answer_lines:
            question_id += 1
            qa_pairs.append({
                'question_id': question_id,
                'question': current_question,
                'answer': '\n'.join(current_answer_lines).strip(),
                'model': model_name,
                'category': current_category
            })
        
        return qa_pairs
    
    def merge_model_responses(
        self,
        gemini_file: str,
        claude_file: str,
        gpt_file: str
    ) -> List[Dict[str, Any]]:
        """
        Merge responses from all three models WITH categories.
        
        Args:
            gemini_file: Path to Gemini .log file
            claude_file: Path to Claude .log file
            gpt_file: Path to GPT .log file
        
        Returns:
            List of questions with answers from all models and categories
        """
        # Parse all files
        gemini_qa = self.parse_log_file(gemini_file, 'gemini')
        claude_qa = self.parse_log_file(claude_file, 'claude')
        gpt_qa = self.parse_log_file(gpt_file, 'gpt')
        
        # Create merged structure
        merged = []
        max_questions = max(len(gemini_qa), len(claude_qa), len(gpt_qa))
        
        print(f"\n📊 Merging responses:")
        print(f"   Gemini: {len(gemini_qa)} responses")
        print(f"   Claude: {len(claude_qa)} responses")
        print(f"   GPT: {len(gpt_qa)} responses")
        
        for i in range(max_questions):
            # Get question (prefer the longest/most detailed one)
            questions = []
            categories = []
            
            if i < len(gemini_qa):
                questions.append(gemini_qa[i]['question'])
                categories.append(gemini_qa[i].get('category', 'general'))
            if i < len(claude_qa):
                questions.append(claude_qa[i]['question'])
                categories.append(claude_qa[i].get('category', 'general'))
            if i < len(gpt_qa):
                questions.append(gpt_qa[i]['question'])
                categories.append(gpt_qa[i].get('category', 'general'))
            
            question = max(questions, key=len) if questions else f"Question {i+1}"
            # Use first available category (they should all be the same)
            category = categories[0] if categories else 'general'
            
            entry = {
                'question_id': i + 1,
                'question': question,
                'category': category,  # Category from log file!
                'answers': {}
            }
            
            # Add answers from each model
            if i < len(gemini_qa):
                entry['answers']['gemini'] = gemini_qa[i]['answer']
            
            if i < len(claude_qa):
                entry['answers']['claude'] = claude_qa[i]['answer']
            
            if i < len(gpt_qa):
                entry['answers']['gpt'] = gpt_qa[i]['answer']
            
            merged.append(entry)
        
        print(f"✅ Merged {len(merged)} questions with model responses and categories")
        return merged


# Example usage and testing
if __name__ == "__main__":
    parser = LogParser()
    
    # Test with sample content
    sample_log = """
# SCIENCE QUESTIONS

Question: What is machine learning?
Answer: Machine learning is a field of AI that enables computers to learn from data.

Question: Explain neural networks
Answer: Neural networks are computing systems inspired by biological neural networks.

# MATH QUESTIONS

Question: What is 2+2?
Answer: 2+2 equals 4.
"""
    
    # Save sample
    with open('test_sample.log', 'w') as f:
        f.write(sample_log)
    
    # Parse
    qa_pairs = parser.parse_log_file('test_sample.log', 'test-model')
    
    print("\n" + "="*70)
    print("SAMPLE PARSE RESULTS")
    print("="*70)
    for qa in qa_pairs:
        print(f"\nQ{qa['question_id']} [{qa['category']}]: {qa['question'][:60]}...")
        print(f"A: {qa['answer'][:60]}...")
