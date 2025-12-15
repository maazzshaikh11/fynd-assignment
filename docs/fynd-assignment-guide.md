# Fynd AI Intern Take-Home Assessment - Complete Implementation Guide

## Overview
**Deadline**: Monday, December 15, 2025 EOD (approximately 43 hours from now)
**Submission**: Google Form with GitHub repo, report PDF, and deployed dashboard URLs

---

## Task 1: Rating Prediction via Prompting

### Setup & Data Preparation
```python
# Install dependencies
pip install kaggle pandas numpy requests openai python-dotenv

# Download Yelp Reviews Dataset
# 1. Download from: https://www.kaggle.com/datasets/omkarsabnis/yelp-reviews-dataset
# 2. Load and sample 200 rows for evaluation
```

### Three Prompting Approaches

#### Approach 1: Basic Direct Prompting
**Prompt Template:**
```
You are a restaurant review sentiment classifier. Classify the following review into 1-5 stars.

Review: "{review}"

Return JSON:
{"predicted_stars": <1-5>, "explanation": "<reasoning>"}
```

**Design Rationale**: Simplest baseline to establish ground truth accuracy.

---

#### Approach 2: Chain-of-Thought (CoT) with Aspect Analysis
**Prompt Template:**
```
Analyze the review by examining these aspects:
1. Food Quality
2. Service Quality
3. Ambiance/Cleanliness
4. Value for Money
5. Overall Experience

Review: "{review}"

For each aspect, note positive/negative mentions (0-3 scale).
Then synthesize into an overall 1-5 star rating.

Return JSON:
{"predicted_stars": <1-5>, "explanation": "<brief reasoning>"}
```

**Design Rationale**: Structured reasoning helps LLM break down complex sentiments and improves consistency.

---

#### Approach 3: Few-Shot Prompting with Examples
**Prompt Template:**
```
You are an expert review classifier. Use these examples as reference:

EXAMPLE 1:
Review: "Amazing food, great service, will come back!"
Rating: 5 stars

EXAMPLE 2:
Review: "Food was okay but service was slow."
Rating: 3 stars

EXAMPLE 3:
Review: "Worst experience ever. Rude staff, cold food."
Rating: 1 star

Now classify this review:
Review: "{review}"

Return JSON:
{"predicted_stars": <1-5>, "explanation": "<reasoning>"}
```

**Design Rationale**: Few-shot examples anchor the model to specific rating thresholds and improve accuracy through pattern matching.

---

### Evaluation Metrics

Create a comparison table with:
- **Accuracy**: (Correct Predictions / Total) × 100
- **JSON Validity Rate**: % of responses that are valid JSON
- **Consistency Score**: Variance in predictions for similar reviews
- **Response Time**: Avg milliseconds per prediction

### Expected Results Structure
```
| Approach | Accuracy | JSON Valid | Consistency | Avg Time |
|----------|----------|-----------|-------------|----------|
| Basic    | 68%      | 100%      | Medium      | 450ms    |
| CoT      | 76%      | 100%      | High        | 520ms    |
| Few-Shot | 72%      | 100%      | High        | 480ms    |
```

---

## Task 2: Two-Dashboard AI Feedback System

### Architecture Overview

```
Frontend (Streamlit/Gradio) ← → Backend (FastAPI/Flask)
                              ↓
                        Shared Data Store (JSON/CSV/SQLite)
                              ↑
                         LLM API (Gemini/OpenRouter)
```

### Recommended Tech Stack (Fastest Implementation)
- **Frontend**: Streamlit (rapid deployment, minimal setup)
- **Backend**: FastAPI (lightweight, async support)
- **Data Store**: SQLite + JSON export for portability
- **LLM**: Gemini API free tier or OpenRouter
- **Deployment**: Streamlit Cloud (free, auto-deploying from GitHub)

### A. User Dashboard (Public)

**Features:**
- Star rating selector (1-5 stars with visual indicators)
- Review text input area (100-500 char limit)
- Submit button with loading state
- AI-generated response display
- Success confirmation

**Implementation Pseudocode:**
```python
import streamlit as st
import requests
import json

st.set_page_config(page_title="User Feedback", layout="centered")

st.title("📝 Share Your Feedback")

col1, col2 = st.columns([1, 4])
with col1:
    rating = st.selectbox("Rate:", [5,4,3,2,1])
with col2:
    stars_display = "⭐" * rating

st.write(f"Your rating: {stars_display}")

review_text = st.text_area("Write your review:", max_chars=500)

if st.button("Submit Review"):
    with st.spinner("Processing..."):
        # Call backend API
        response = requests.post(
            "https://your-backend-url/api/submit-review",
            json={
                "rating": rating,
                "review": review_text,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        result = response.json()
        
        st.success("Thank you for your feedback!")
        st.write("**AI Response:**")
        st.write(result['ai_response'])
        
        # Store in local session
        st.balloons()
```

---

### B. Admin Dashboard (Internal)

**Features:**
- Live-updating table of all submissions
- Sort/filter by rating, date, sentiment
- Display AI-generated summaries
- Show recommended actions
- Basic analytics (avg rating, sentiment distribution)
- Export to CSV button

**Implementation Pseudocode:**
```python
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Admin Dashboard", layout="wide")

st.title("🔐 Admin Dashboard")

# Add authentication
if "admin_logged_in" not in st.session_state:
    password = st.text_input("Admin Password:", type="password")
    if password == "your-admin-password":
        st.session_state.admin_logged_in = True
    else:
        st.stop()

# Load data
df = load_submissions_data()

# Metrics row
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Submissions", len(df))
with col2:
    st.metric("Avg Rating", df['rating'].mean().round(1))
with col3:
    st.metric("5-Star Reviews", (df['rating'] == 5).sum())
with col4:
    st.metric("1-Star Reviews", (df['rating'] == 1).sum())

# Filters
st.subheader("Filters")
col1, col2 = st.columns(2)
with col1:
    selected_rating = st.multiselect("Filter by Rating:", [5,4,3,2,1], default=[5,4,3,2,1])
with col2:
    date_range = st.date_input("Date Range:", [datetime.now().date() - timedelta(days=7), datetime.now().date()])

# Filter dataframe
filtered_df = df[
    (df['rating'].isin(selected_rating)) &
    (df['date'] >= pd.Timestamp(date_range[0])) &
    (df['date'] <= pd.Timestamp(date_range[1]))
]

# Display table
st.subheader("All Submissions")
st.dataframe(
    filtered_df[['date', 'rating', 'review', 'ai_summary', 'recommended_actions']].sort_values('date', ascending=False),
    width="stretch"
)

# Analytics
st.subheader("Analytics")
col1, col2 = st.columns(2)

with col1:
    rating_dist = df['rating'].value_counts().sort_index()
    st.bar_chart(rating_dist)

with col2:
    sentiment_trend = df.groupby(df['date'].dt.date)['rating'].mean()
    st.line_chart(sentiment_trend)

# Export
if st.button("📥 Export to CSV"):
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name=f"submissions_{datetime.now().strftime('%Y%m%d')}.csv"
    )
```

---

### C. Shared Backend API

**Endpoints:**

1. **POST /api/submit-review**
   ```
   Request:
   {
     "rating": 4,
     "review": "Great food!",
     "timestamp": "2025-12-14T15:30:00"
   }
   
   Response:
   {
     "id": "sub_123456",
     "ai_response": "Thank you for the positive feedback...",
     "ai_summary": "Customer appreciated food quality",
     "recommended_actions": "Continue maintaining food quality standards"
   }
   ```

2. **GET /api/submissions**
   ```
   Response: List of all submissions in JSON format
   ```

---

### Deployment Strategy

#### Option 1: Streamlit Cloud (FASTEST - Recommended)

**User Dashboard:**
```bash
# Create Streamlit app
# File: apps/user_dashboard.py

# Push to GitHub
git push origin main

# Deploy on Streamlit Cloud
# 1. Go to https://streamlit.io/cloud
# 2. Connect GitHub repo
# 3. Select apps/user_dashboard.py
# 4. Get URL: https://your-username-user-dashboard.streamlit.app
```

**Admin Dashboard:**
- Same process with apps/admin_dashboard.py

---

#### Option 2: FastAPI + Vercel

**Backend (FastAPI):**
```python
# api/main.py
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import json

app = FastAPI()

@app.post("/api/submit-review")
async def submit_review(data: dict):
    # Process with LLM
    ai_response = await generate_ai_response(data['review'], data['rating'])
    
    # Store data
    store_submission(data)
    
    return ai_response

# Deploy on Vercel
# 1. Create vercel.json
# 2. Deploy: vercel deploy
```

---

### Data Storage Implementation

**Option 1: JSON File (Simplest)**
```python
import json
from datetime import datetime

def store_submission(review_data):
    try:
        with open('submissions.json', 'r') as f:
            submissions = json.load(f)
    except FileNotFoundError:
        submissions = []
    
    submission = {
        "id": generate_id(),
        "rating": review_data['rating'],
        "review": review_data['review'],
        "timestamp": review_data.get('timestamp', datetime.now().isoformat()),
        "ai_summary": review_data.get('ai_summary'),
        "ai_response": review_data.get('ai_response'),
        "recommended_actions": review_data.get('recommended_actions')
    }
    
    submissions.append(submission)
    
    with open('submissions.json', 'w') as f:
        json.dump(submissions, f, indent=2)

def load_submissions():
    with open('submissions.json', 'r') as f:
        return json.load(f)
```

**Option 2: SQLite (More Scalable)**
```python
import sqlite3

def init_db():
    conn = sqlite3.connect('submissions.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS submissions
                 (id TEXT PRIMARY KEY,
                  rating INTEGER,
                  review TEXT,
                  ai_summary TEXT,
                  ai_response TEXT,
                  recommended_actions TEXT,
                  timestamp TEXT)''')
    conn.commit()
    return conn
```

---

### LLM Prompts for Task 2

#### AI Response Prompt (User-Facing)
```
A customer left this review with a {rating}-star rating:
"{review}"

Respond warmly and professionally, acknowledging their feedback and addressing their main concerns. Keep it under 100 words.

Response:
```

#### Summarization Prompt
```
Summarize this review in one sentence:
"{review}"

Summary:
```

#### Recommended Actions Prompt
```
For a {rating}-star review mentioning: "{review}"

What should the business do? Provide 1-2 specific, actionable recommendations.

Actions:
```

---

## Implementation Timeline (43 Hours Available)

### Hour 0-6: Task 1 Setup & Prompting
- [ ] Download Yelp dataset, sample 200 rows
- [ ] Create notebook with all 3 prompting approaches
- [ ] Test each prompt on sample data
- [ ] Calculate evaluation metrics
- [ ] Create comparison table

### Hour 6-12: Task 1 Refinement & Reporting
- [ ] Fine-tune best performing prompt
- [ ] Document all findings
- [ ] Create comprehensive report
- [ ] Push to GitHub

### Hour 12-24: Task 2 Development (User Dashboard)
- [ ] Set up Streamlit project
- [ ] Build user dashboard UI
- [ ] Integrate LLM API
- [ ] Implement data storage
- [ ] Deploy to Streamlit Cloud

### Hour 24-36: Task 2 Development (Admin Dashboard)
- [ ] Build admin dashboard UI
- [ ] Add filtering and analytics
- [ ] Connect to shared data source
- [ ] Deploy to Streamlit Cloud

### Hour 36-43: Testing & Final Submission
- [ ] End-to-end testing (both dashboards)
- [ ] Verify data flow between dashboards
- [ ] Create final report PDF
- [ ] Prepare GitHub repository
- [ ] Submit via Google Form

---

## Key Implementation Tips

1. **For Task 1:**
   - Use Gemini API free tier (1,500 RPM limit)
   - Cache results locally to avoid redundant API calls
   - Use `json.loads()` with error handling for invalid JSON responses

2. **For Task 2:**
   - Start with Streamlit for fastest deployment
   - Use Streamlit's `@st.cache_data` for performance
   - Store data both in JSON and in-memory for speed
   - Use `st.rerun()` to refresh admin dashboard

3. **General:**
   - Create `.env` file for API keys (add to `.gitignore`)
   - Add clear documentation in README.md
   - Use proper error handling and logging
   - Test deployments before final submission

---

## Submission Checklist

- [ ] GitHub repository with Task 1 notebook
- [ ] GitHub repository with Task 2 application code
- [ ] Report PDF (approach, design decisions, results)
- [ ] User Dashboard deployed and working
- [ ] Admin Dashboard deployed and working
- [ ] Both dashboards can read/write shared data
- [ ] All links working and public
- [ ] Submitted via Google Form

---

## Resources

- Yelp Dataset: https://www.kaggle.com/datasets/omkarsabnis/yelp-reviews-dataset
- Gemini API: https://ai.google.dev/
- OpenRouter: https://openrouter.ai/
- Streamlit Docs: https://docs.streamlit.io/
- FastAPI Docs: https://fastapi.tiangolo.com/

Good luck! 🚀
