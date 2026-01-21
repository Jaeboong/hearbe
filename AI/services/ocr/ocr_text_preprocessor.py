"""
OCR Text Preprocessing Module

This module provides functions to clean and filter OCR results before
sending them to LLM for summarization. It removes noise, low-confidence
results, and meaningless characters.
"""

import re
from typing import Dict, List, Tuple


def _is_meaningful_text(text: str) -> bool:
    """
    Check if text contains meaningful Korean or English content.
    
    Args:
        text: Text to check
        
    Returns:
        True if text is meaningful, False otherwise
    """
    # Must contain at least one Korean syllable or English word
    has_korean = bool(re.search(r'[가-힣]', text))
    has_english_word = bool(re.search(r'[a-zA-Z]{2,}', text))
    
    # Filter out texts with too many special characters or numbers only
    alphanumeric_ratio = len(re.findall(r'[가-힣a-zA-Z0-9]', text)) / max(len(text), 1)
    
    return (has_korean or has_english_word) and alphanumeric_ratio > 0.5


def preprocess_ocr_texts(
    texts: List[str],
    scores: List[float],
    min_score: float = 0.7,
    min_length: int = 2,
    verbose: bool = True
) -> Tuple[List[str], Dict]:
    """
    Preprocess OCR texts by filtering noise and low-confidence results.
    
    Args:
        texts: List of OCR recognized texts
        scores: List of confidence scores (0-1)
        min_score: Minimum confidence score threshold (default: 0.7)
        min_length: Minimum text length to keep (default: 2)
        verbose: Print preprocessing statistics (default: True)
        
    Returns:
        Tuple of (cleaned_texts, statistics_dict)
    """
    if len(texts) != len(scores):
        raise ValueError(f"texts and scores must have same length: {len(texts)} vs {len(scores)}")
    
    cleaned = []
    filtered_examples = {
        "by_score": [],
        "by_length": [],
        "by_pattern": []
    }
    
    stats = {
        "original_count": len(texts),
        "filtered_by_score": 0,
        "filtered_by_length": 0,
        "filtered_by_pattern": 0,
        "duplicates_removed": 0,
        "final_count": 0
    }
    
    for text, score in zip(texts, scores):
        original_text = text
        text = text.strip()
        
        # Filter by confidence score
        if score < min_score:
            stats["filtered_by_score"] += 1
            if len(filtered_examples["by_score"]) < 3:
                filtered_examples["by_score"].append(f'"{text}" (score: {score:.2f})')
            continue
            
        # Filter by length
        if len(text) < min_length:
            stats["filtered_by_length"] += 1
            if len(filtered_examples["by_length"]) < 3:
                filtered_examples["by_length"].append(f'"{text}" (length: {len(text)})')
            continue
            
        # Filter by pattern (must contain Korean or meaningful English)
        if not _is_meaningful_text(text):
            stats["filtered_by_pattern"] += 1
            if len(filtered_examples["by_pattern"]) < 3:
                filtered_examples["by_pattern"].append(f'"{text}"')
            continue
            
        cleaned.append(text)
    
    # Remove duplicates while preserving order
    original_cleaned_count = len(cleaned)
    cleaned = list(dict.fromkeys(cleaned))
    stats["duplicates_removed"] = original_cleaned_count - len(cleaned)
    stats["final_count"] = len(cleaned)
    
    if verbose:
        print("\n=== OCR Text Preprocessing Statistics ===")
        print(f"Original texts: {stats['original_count']}")
        print(f"Filtered by score (< {min_score}): {stats['filtered_by_score']}")
        if filtered_examples["by_score"]:
            print(f"  Examples: {', '.join(filtered_examples['by_score'])}")
        print(f"Filtered by length (< {min_length}): {stats['filtered_by_length']}")
        if filtered_examples["by_length"]:
            print(f"  Examples: {', '.join(filtered_examples['by_length'])}")
        print(f"Filtered by pattern: {stats['filtered_by_pattern']}")
        if filtered_examples["by_pattern"]:
            print(f"  Examples: {', '.join(filtered_examples['by_pattern'])}")
        print(f"Duplicates removed: {stats['duplicates_removed']}")
        print(f"Final cleaned texts: {stats['final_count']}")
        print(f"Reduction: {stats['original_count'] - stats['final_count']} texts ({(1 - stats['final_count']/max(stats['original_count'], 1))*100:.1f}%)")
        print("=" * 40 + "\n")
    
    return cleaned, stats


def load_and_preprocess_ocr_json(
    json_data: Dict,
    min_score: float = 0.7,
    min_length: int = 2,
    verbose: bool = True
) -> Tuple[List[str], Dict]:
    """
    Load OCR results from JSON and preprocess them.
    
    Args:
        json_data: OCR result JSON dictionary
        min_score: Minimum confidence score threshold
        min_length: Minimum text length to keep
        verbose: Print preprocessing statistics
        
    Returns:
        Tuple of (cleaned_texts, preprocessing_stats)
    """
    texts = json_data.get("rec_texts", [])
    scores = json_data.get("rec_scores", [])
    
    if not texts:
        raise ValueError("No 'rec_texts' found in JSON data")
    
    # If no scores provided, assume all texts have high confidence (1.0)
    if not scores:
        if verbose:
            print("Note: No 'rec_scores' found. Assuming all texts have score 1.0")
        scores = [1.0] * len(texts)
    
    return preprocess_ocr_texts(texts, scores, min_score, min_length, verbose)


if __name__ == "__main__":
    # Example usage
    import json
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python text_preprocessor.py <ocr_json_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    cleaned_texts, stats = load_and_preprocess_ocr_json(data, verbose=True)
    
    print("\nCleaned texts:")
    for i, text in enumerate(cleaned_texts, 1):
        print(f"{i}. {text}")
