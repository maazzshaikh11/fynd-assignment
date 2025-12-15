# Task 1: Yelp Review Rating Prediction - Starter Code
# Save as: task1_rating_prediction.py

import pandas as pd
import json
import time
from datetime import datetime
from typing import Dict, List, Tuple
import os
from dotenv import load_dotenv

load_dotenv()

# ============================================================================
# CONFIGURATION
# ============================================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # Get from https://ai.google.dev/
SAMPLE_SIZE = 200
EVALUATION_SPLIT = 0.8

# ============================================================================
# LLM SETUP
# ============================================================================

def setup_gemini():
    """Initialize Gemini API"""
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)
    return genai.GenerativeModel('gemini-2.0-flash')  # Changed this line



model = setup_gemini()

# ============================================================================
# PROMPTING APPROACHES
# ============================================================================

PROMPT_APPROACH_1 = """You are a restaurant review sentiment classifier. Your task is to read a review and predict the star rating (1-5).

Review: "{review}"

Respond ONLY with valid JSON in this exact format:
{{"predicted_stars": <number 1-5>, "explanation": "<brief reason>"}}"""

PROMPT_APPROACH_2 = """You are an expert review analyst. Analyze this review by examining these key aspects:
1. Food Quality (taste, presentation, portions)
2. Service Quality (speed, friendliness, attentiveness)
3. Ambiance/Cleanliness (environment, hygiene, comfort)
4. Value for Money (price vs quality)
5. Overall Experience

Review: "{review}"

For each aspect, identify positive/negative mentions. Then synthesize into an overall 1-5 star rating based on the balance of factors.

Respond ONLY with valid JSON:
{{"predicted_stars": <number 1-5>, "explanation": "<brief reason>"}}"""

PROMPT_APPROACH_3 = """You are an expert review classifier trained on thousands of restaurant reviews. Use these examples as reference:

EXAMPLE 1 (5 stars):
Review: "Amazing food, great service, will come back!"

EXAMPLE 2 (3 stars):
Review: "Food was okay but service was slow."

EXAMPLE 3 (1 star):
Review: "Worst experience ever. Rude staff, cold food."

Now classify this review:
Review: "{review}"

Respond ONLY with valid JSON:
{{"predicted_stars": <number 1-5>, "explanation": "<brief reason>"}}"""

# ============================================================================
# DATA LOADING
# ============================================================================

def load_yelp_dataset(csv_path: str, sample_size: int = 200) -> pd.DataFrame:
    """
    Load Yelp reviews dataset
    Download from: https://www.kaggle.com/datasets/omkarsabnis/yelp-reviews-dataset
    """
    df = pd.read_csv(csv_path)
    
    # Assume columns are 'review_text' and 'rating' (adjust as needed)
    df = df[['text', 'stars']].dropna()
    df = df.rename(columns={'text': 'review_text', 'stars': 'rating'})

    
    # Sample for efficiency
    df = df.sample(n=min(sample_size, len(df)), random_state=42)
    
    return df.reset_index(drop=True)

# ============================================================================
# LLM INFERENCE
# ============================================================================

def call_llm(prompt: str, max_retries: int = 3) -> Dict:
    """
    Call Gemini API with error handling and retry logic
    """
    for attempt in range(max_retries):
        try:
            # Remove temperature parameter - not supported in this version
            response = model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Try to parse JSON
            try:
                result = json.loads(response_text)
                return {"success": True, "data": result, "raw": response_text}
            except json.JSONDecodeError:
                # Try to extract JSON from response
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                    return {"success": True, "data": result, "raw": response_text}
                else:
                    return {"success": False, "error": "Invalid JSON", "raw": response_text}
                    
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                return {"success": False, "error": str(e), "raw": None}
    
    return {"success": False, "error": "Max retries exceeded", "raw": None}


# ============================================================================
# EVALUATION
# ============================================================================

def evaluate_approach(df: pd.DataFrame, approach_name: str, prompt_template: str) -> Dict:
    """
    Evaluate a single prompting approach
    """
    results = []
    execution_times = []
    
    for idx, row in df.iterrows():
        prompt = prompt_template.format(review=row['review_text'])
        
        start_time = time.time()
        response = call_llm(prompt)
        execution_time = time.time() - start_time
        execution_times.append(execution_time)
        
        if response["success"]:
            predicted = response["data"].get("predicted_stars")
            explanation = response["data"].get("explanation", "")
            is_valid_json = True
        else:
            predicted = None
            explanation = response.get("error", "")
            is_valid_json = False
        
        results.append({
            "actual": int(row['rating']),
            "predicted": predicted,
            "explanation": explanation,
            "valid_json": is_valid_json,
            "execution_time": execution_time
        })
    
    # Calculate metrics
    valid_results = [r for r in results if r["valid_json"]]
    correct = sum(1 for r in valid_results if r["actual"] == r["predicted"])
    
    accuracy = (correct / len(valid_results) * 100) if valid_results else 0
    json_validity = (len(valid_results) / len(results) * 100)
    avg_execution_time = sum(execution_times) / len(execution_times)
    
    # Consistency: standard deviation of differences
    differences = [abs(r["actual"] - r["predicted"]) for r in valid_results if r["predicted"]]
    consistency = sum(d == 0 for d in differences) / len(differences) * 100 if differences else 0
    
    return {
        "approach": approach_name,
        "accuracy": round(accuracy, 2),
        "json_validity": round(json_validity, 2),
        "consistency": round(consistency, 2),
        "avg_time_ms": round(avg_execution_time * 1000, 2),
        "total_samples": len(results),
        "valid_samples": len(valid_results),
        "detailed_results": results
    }

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Run evaluation of all three approaches"""
    
    print("=" * 70)
    print("YELP REVIEW RATING PREDICTION - PROMPTING APPROACHES EVALUATION")
    print("=" * 70)
    
    # Load data
    print("\n[1] Loading Yelp Reviews Dataset...")
    df = load_yelp_dataset("yelp_reviews_sample.csv", sample_size=SAMPLE_SIZE)
    print(f"    Loaded {len(df)} reviews")
    print(f"    Sample review: {df.iloc[0]['review_text'][:100]}...")
    
    # Evaluate all approaches
    print("\n[2] Evaluating Prompting Approaches...")
    
    approaches = [
        ("Approach 1: Direct Prompting", PROMPT_APPROACH_1),
        ("Approach 2: Chain-of-Thought", PROMPT_APPROACH_2),
        ("Approach 3: Few-Shot Prompting", PROMPT_APPROACH_3),
    ]
    
    evaluation_results = []
    
    for approach_name, prompt_template in approaches:
        print(f"\n    Evaluating {approach_name}...")
        result = evaluate_approach(df, approach_name, prompt_template)
        evaluation_results.append(result)
        print(f"    ✓ Accuracy: {result['accuracy']}%")
        print(f"    ✓ JSON Validity: {result['json_validity']}%")
        print(f"    ✓ Consistency: {result['consistency']}%")
    
    # Create comparison table
    print("\n[3] Comparison Table")
    print("-" * 70)
    print(f"{'Approach':<30} {'Accuracy':<12} {'JSON Valid':<12} {'Consistency':<12} {'Avg Time'}")
    print("-" * 70)
    
    for result in evaluation_results:
        print(f"{result['approach']:<30} {result['accuracy']:<12}% {result['json_validity']:<12}% {result['consistency']:<12}% {result['avg_time_ms']}ms")
    
    # Save results
    print("\n[4] Saving Results...")
    
    with open("evaluation_results.json", "w") as f:
        json.dump(evaluation_results, f, indent=2, default=str)
    
    print(f"    ✓ Results saved to evaluation_results.json")
    
    # Find best approach
    best = max(evaluation_results, key=lambda x: x["accuracy"])
    print(f"\n[5] Best Approach: {best['approach']} (Accuracy: {best['accuracy']}%)")
    
    print("\n" + "=" * 70)
    print("Evaluation complete! Check evaluation_results.json for details.")
    print("=" * 70)

if __name__ == "__main__":
    main()
