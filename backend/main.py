"""
Feedback System Backend API
FastAPI application for handling customer review submissions and admin analytics.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json
import os
from datetime import datetime
from dotenv import load_dotenv
import logging
from openai import OpenAI

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
DATA_FILE = "submissions.json"

openai_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

# Data Models
class ReviewSubmission(BaseModel):
    rating: int
    review: str
    timestamp: str
    user_id: Optional[str] = "anonymous"

class AIResponse(BaseModel):
    id: str
    rating: int
    review: str
    ai_response: str
    ai_summary: str
    recommended_actions: str
    timestamp: str

# FastAPI Application
app = FastAPI(
    title="Feedback System API",
    description="Backend for user feedback and admin dashboard",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_submissions() -> List[dict]:
    """Load all submissions from persistent storage."""
    if not os.path.exists(DATA_FILE):
        return []
    
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading submissions: {e}")
        return []

def save_submissions(submissions: List[dict]):
    """Save submissions to persistent storage."""
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(submissions, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving submissions: {e}")

def generate_id() -> str:
    """Generate unique submission identifier."""
    import uuid
    return f"sub_{uuid.uuid4().hex[:8]}"

def generate_ai_response(review: str, rating: int) -> str:
    """Generate customer-facing response using LLM."""
    prompt = f"""A customer left this {rating}-star review:
"{review}"

Respond warmly and professionally in 50-80 words, acknowledging their feedback and addressing their main concerns.

Response:"""
    
    try:
        response = openai_client.chat.completions.create(
            model="google/gemini-2.0-flash-exp:free",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        return "Thank you for your feedback! We appreciate your input."

def generate_ai_summary(review: str) -> str:
    """Generate concise summary of review for admin dashboard."""
    prompt = f"""Summarize this review in one concise sentence (max 15 words):
"{review}"

Summary:"""
    
    try:
        response = openai_client.chat.completions.create(
            model="google/gemini-2.0-flash-exp:free",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        return review[:50] + "..."

def generate_recommended_actions(review: str, rating: int) -> str:
    """Generate actionable recommendations for business based on review."""
    prompt = f"""For a {rating}-star review mentioning:
"{review}"

What should the business do? Provide 1-2 specific, actionable recommendations.

Actions:"""
    
    try:
        response = openai_client.chat.completions.create(
            model="google/gemini-2.0-flash-exp:free",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error generating actions: {e}")
        return "Review and investigate customer feedback" if rating < 3 else "Maintain current service level"

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/submit-review")
async def submit_review(submission: ReviewSubmission):
    """
    Process new review submission with AI-generated responses.
    
    Args:
        submission: Review data including rating and text
        
    Returns:
        Complete submission record with AI-generated content
    """
    try:
        if not submission.review or len(submission.review) < 5:
            raise HTTPException(status_code=400, detail="Review must be at least 5 characters")
        
        if not 1 <= submission.rating <= 5:
            raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
        
        logger.info(f"Generating AI responses for review: {submission.review[:50]}...")
        
        ai_response = generate_ai_response(submission.review, submission.rating)
        ai_summary = generate_ai_summary(submission.review)
        recommended_actions = generate_recommended_actions(submission.review, submission.rating)
        
        submission_id = generate_id()
        submission_record = {
            "id": submission_id,
            "rating": submission.rating,
            "review": submission.review,
            "ai_response": ai_response,
            "ai_summary": ai_summary,
            "recommended_actions": recommended_actions,
            "timestamp": submission.timestamp,
            "user_id": submission.user_id
        }
        
        submissions = load_submissions()
        submissions.append(submission_record)
        save_submissions(submissions)
        
        logger.info(f"Submission saved: {submission_id}")
        
        return submission_record
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing submission: {e}")
        raise HTTPException(status_code=500, detail="Error processing submission")

@app.get("/api/submissions")
async def get_submissions(rating: Optional[int] = None, limit: Optional[int] = None):
    """
    Retrieve submissions with optional filtering.
    
    Query Parameters:
        rating: Filter by specific rating (1-5)
        limit: Maximum number of results to return
    """
    try:
        submissions = load_submissions()
        
        if rating:
            if not 1 <= rating <= 5:
                raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
            submissions = [s for s in submissions if s['rating'] == rating]
        
        submissions.sort(key=lambda x: x['timestamp'], reverse=True)
        
        if limit:
            submissions = submissions[:limit]
        
        return submissions
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving submissions: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving submissions")

@app.get("/api/submissions/{submission_id}")
async def get_submission(submission_id: str):
    """Retrieve specific submission by ID."""
    try:
        submissions = load_submissions()
        submission = next((s for s in submissions if s['id'] == submission_id), None)
        
        if not submission:
            raise HTTPException(status_code=404, detail="Submission not found")
        
        return submission
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving submission: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving submission")

@app.get("/api/analytics")
async def get_analytics():
    """Calculate aggregate analytics from all submissions."""
    try:
        submissions = load_submissions()
        
        if not submissions:
            return {
                "total_submissions": 0,
                "avg_rating": 0,
                "rating_distribution": {}
            }
        
        ratings = [s['rating'] for s in submissions]
        
        return {
            "total_submissions": len(submissions),
            "avg_rating": round(sum(ratings) / len(ratings), 2),
            "rating_distribution": {
                "5_stars": ratings.count(5),
                "4_stars": ratings.count(4),
                "3_stars": ratings.count(3),
                "2_stars": ratings.count(2),
                "1_star": ratings.count(1)
            }
        }
    
    except Exception as e:
        logger.error(f"Error calculating analytics: {e}")
        raise HTTPException(status_code=500, detail="Error calculating analytics")

@app.delete("/api/submissions/{submission_id}")
async def delete_submission(submission_id: str):
    """Delete specific submission by ID."""
    try:
        submissions = load_submissions()
        submissions = [s for s in submissions if s['id'] != submission_id]
        save_submissions(submissions)
        
        return {"status": "deleted", "id": submission_id}
    
    except Exception as e:
        logger.error(f"Error deleting submission: {e}")
        raise HTTPException(status_code=500, detail="Error deleting submission")

@app.get("/")
async def root():
    """Root endpoint with API documentation."""
    return {
        "name": "Feedback System API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "submit_review": "POST /api/submit-review",
            "get_submissions": "GET /api/submissions",
            "get_submission": "GET /api/submissions/{submission_id}",
            "get_analytics": "GET /api/analytics",
            "delete_submission": "DELETE /api/submissions/{submission_id}"
        }
    }
