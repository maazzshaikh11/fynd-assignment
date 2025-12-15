"""
Yelp Review Rating Prediction System
Evaluates three different prompting approaches for LLM-based sentiment classification.
"""

import pandas as pd
import json
import time
from datetime import datetime
from typing import Dict, List
import os
from dotenv import load_dotenv
from openai import OpenAI
import re

load_dotenv()

# Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
SAMPLE_SIZE = 200

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

# Prompting Strategies
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

def load_yelp_dataset(csv_path: str, sample_size: int = 200) -> pd.DataFrame:
    """Load and preprocess Yelp reviews dataset."""
    df = pd.read_csv(csv_path)
    df = df[['text', 'stars']].dropna()
    df = df.rename(columns={'text': 'review_text', 'stars': 'rating'})
    df = df.sample(n=min(sample_size, len(df)), random_state=42)
    return df.reset_index(drop=True)

def call_llm(prompt: str, max_retries: int = 3) -> Dict:
    """Execute LLM API call with retry logic and error handling."""
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="google/gemini-2.0-flash-exp:free",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
            )
            
            response_text = response.choices[0].message.content.strip()
            
            try:
                result = json.loads(response_text)
                return {"success": True, "data": result, "raw": response_text}
            except json.JSONDecodeError:
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                    return {"success": True, "data": result, "raw": response_text}
                else:
                    return {"success": False, "error": "Invalid JSON", "raw": response_text}
                    
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                return {"success": False, "error": str(e), "raw": None}
    
    return {"success": False, "error": "Max retries exceeded", "raw": None}

def evaluate_approach(df: pd.DataFrame, approach_name: str, prompt_template: str) -> Dict:
    """Evaluate single prompting approach across dataset."""
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
        
        if (idx + 1) % 10 == 0:
            print(f"    Progress: {idx + 1}/{len(df)} reviews processed...")
    
    # Calculate evaluation metrics
    valid_results = [r for r in results if r["valid_json"] and r["predicted"] is not None]
    correct = sum(1 for r in valid_results if r["actual"] == r["predicted"])
    
    accuracy = (correct / len(valid_results) * 100) if valid_results else 0
    json_validity = (len(valid_results) / len(results) * 100)
    avg_execution_time = sum(execution_times) / len(execution_times)
    
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

def main():
    """Execute evaluation workflow for all prompting approaches."""
    print("=" * 70)
    print("YELP REVIEW RATING PREDICTION - PROMPTING APPROACHES EVALUATION")
    print("Using OpenRouter API")
    print("=" * 70)
    
    print("\n[1] Loading Yelp Reviews Dataset...")
    df = load_yelp_dataset("yelp_reviews_sample.csv", sample_size=SAMPLE_SIZE)
    print(f"    Loaded {len(df)} reviews")
    print(f"    Sample review: {df.iloc[0]['review_text'][:100]}...")
    
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
        print(f"    Accuracy: {result['accuracy']}%")
        print(f"    JSON Validity: {result['json_validity']}%")
        print(f"    Consistency: {result['consistency']}%")
    
    print("\n[3] Comparison Table")
    print("-" * 70)
    print(f"{'Approach':<30} {'Accuracy':<12} {'JSON Valid':<12} {'Consistency':<12} {'Avg Time'}")
    print("-" * 70)
    
    for result in evaluation_results:
        print(f"{result['approach']:<30} {result['accuracy']:<12}% {result['json_validity']:<12}% {result['consistency']:<12}% {result['avg_time_ms']}ms")
    
    print("\n[4] Saving Results...")
    with open("evaluation_results.json", "w") as f:
        json.dump(evaluation_results, f, indent=2, default=str)
    print(f"    Results saved to evaluation_results.json")
    
    best = max(evaluation_results, key=lambda x: x["accuracy"])
    print(f"\n[5] Best Approach: {best['approach']} (Accuracy: {best['accuracy']}%)")
    
    print("\n" + "=" * 70)
    print("Evaluation complete! Check evaluation_results.json for details.")
    print("=" * 70)

if __name__ == "__main__":
    main()
