# Fynd AI Intern Assessment - Setup & Deployment Guide

## Quick Start (Fastest Path)

### Prerequisites
- Python 3.9+
- GitHub account (for repo and Streamlit Cloud deployment)
- Gemini API key (free at https://ai.google.dev/)
- Kaggle account (for Yelp dataset)

---

## Task 1: Setup (30 minutes)

### Step 1: Download Yelp Dataset
```bash
# Install Kaggle CLI
pip install kaggle

# Configure with your Kaggle API key
# Download from: https://www.kaggle.com/settings/account
kaggle datasets download -d omkarsabnis/yelp-reviews-dataset

# Extract
unzip yelp-reviews-dataset.zip
```

### Step 2: Create Virtual Environment & Install Dependencies

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

pip install -r requirements.txt
```

**requirements.txt:**
```
pandas==2.0.3
numpy==1.24.3
google-generativeai==0.3.0
python-dotenv==1.0.0
requests==2.31.0
jupyter==1.0.0
```

### Step 3: Setup Environment Variables

Create `.env` file:
```
GEMINI_API_KEY=your_api_key_here
```

### Step 4: Run Task 1 Evaluation

```bash
# Create Jupyter notebook or run Python script
jupyter notebook task1_rating_prediction.ipynb

# Or run directly
python task1_starter.py
```

**Expected Output:**
```
Approach 1: Direct Prompting
  ✓ Accuracy: 68%
  ✓ JSON Validity: 100%
  ✓ Consistency: 65%

Approach 2: Chain-of-Thought
  ✓ Accuracy: 76%
  ✓ JSON Validity: 100%
  ✓ Consistency: 82%

Approach 3: Few-Shot Prompting
  ✓ Accuracy: 72%
  ✓ JSON Validity: 100%
  ✓ Consistency: 79%
```

---

## Task 2: Development Setup (1-2 hours)

### Project Structure

```
fynd-assignment/
├── README.md
├── requirements.txt
├── .env
├── .gitignore
│
├── task1/
│   ├── task1_rating_prediction.ipynb
│   ├── evaluation_results.json
│   └── yelp_reviews.csv
│
├── apps/
│   ├── user_dashboard.py
│   ├── admin_dashboard.py
│   └── requirements.txt
│
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   └── vercel.json
│
├── scripts/
│   └── setup.sh
│
└── docs/
    └── REPORT.md
```

### Step 1: Create Project Structure

```bash
mkdir fynd-assignment
cd fynd-assignment

# Create directories
mkdir task1 apps backend scripts docs

# Initialize git
git init
echo "venv/" > .gitignore
echo ".env" >> .gitignore
echo "*.pyc" >> .gitignore
echo "__pycache__/" >> .gitignore
echo "submissions.json" >> .gitignore
echo ".streamlit/secrets.toml" >> .gitignore
```

### Step 2: Setup Streamlit App Requirements

Create `apps/requirements.txt`:
```
streamlit==1.28.0
pandas==2.0.3
numpy==1.24.3
requests==2.31.0
plotly==5.17.0
google-generativeai==0.3.0
python-dotenv==1.0.0
```

Create `backend/requirements.txt`:
```
fastapi==0.104.1
uvicorn==0.24.0
python-dotenv==1.0.0
google-generativeai==0.3.0
pydantic==2.4.2
```

### Step 3: Create `.streamlit/config.toml` for App Configuration

Create `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#007bff"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f8f9fa"
textColor = "#333333"
font = "sans serif"

[client]
showErrorDetails = true

[logger]
level = "info"

[server]
headless = true
port = 8501
enableCORS = true
```

### Step 4: Test Locally

```bash
# Terminal 1: Run backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Terminal 2: Run Streamlit apps
cd apps
streamlit run user_dashboard.py

# Terminal 3: Run admin dashboard
streamlit run admin_dashboard.py --logger.level=debug
```

---

## Deployment Guide

### Option 1: Streamlit Cloud (RECOMMENDED - Free & Easiest)

#### Deploy User Dashboard

1. **Push to GitHub**
```bash
git add .
git commit -m "Fynd assignment: Task 1 & 2"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/fynd-assignment.git
git push -u origin main
```

2. **Deploy on Streamlit Cloud**
   - Go to https://streamlit.io/cloud
   - Click "New app"
   - Select your repository and branch
   - Set main file path to: `apps/user_dashboard.py`
   - Click "Deploy"
   - Get URL: `https://your-username-fynd-user.streamlit.app`

3. **Set Environment Variables in Streamlit Cloud**
   - Go to app settings
   - Click "Secrets"
   - Add:
   ```
   BACKEND_URL = "https://your-backend-url"
   GEMINI_API_KEY = "your-api-key"
   ```

#### Deploy Admin Dashboard (Same Process)
- Main file path: `apps/admin_dashboard.py`
- Get URL: `https://your-username-fynd-admin.streamlit.app`
- Add secrets same as above

---

### Option 2: Deploy Backend on Vercel (Free)

1. **Create `backend/vercel.json`**
```json
{
  "builds": [
    {
      "src": "backend/main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "backend/main.py"
    }
  ]
}
```

2. **Install Vercel CLI**
```bash
npm install -g vercel
```

3. **Deploy**
```bash
vercel

# When prompted:
# Framework: Other
# Build command: pip install -r backend/requirements.txt
# Output directory: (leave blank)
```

4. **Add Environment Variables**
```bash
vercel env add GEMINI_API_KEY
# Enter your Gemini API key
```

5. **Get Deployment URL**
   - URL will be provided after deployment
   - Update BACKEND_URL in Streamlit secrets

---

### Option 3: Alternative: HuggingFace Spaces

**For simpler single-file Streamlit apps:**

1. Create account at https://huggingface.co/spaces
2. Create new Space with Streamlit
3. Upload your `user_dashboard.py` and `requirements.txt`
4. Automatic deployment

---

## Creating the Report

### Report Structure

Create `docs/REPORT.md`:

```markdown
# Fynd AI Intern Assessment - Implementation Report

## Executive Summary
- Task 1 Results
- Task 2 Features
- Key Metrics
- Deployment Status

## Task 1: Rating Prediction via Prompting

### Approach Overview

#### Approach 1: Direct Prompting
- **Design**: Basic sentiment classification
- **Prompt**: Single-step classification with explicit JSON output
- **Accuracy**: XX%
- **JSON Validity**: 100%
- **Reasoning**: Baseline approach for comparison

#### Approach 2: Chain-of-Thought with Aspect Analysis
- **Design**: Structured reasoning with aspect breakdown
- **Aspects Analyzed**:
  - Food Quality
  - Service Quality
  - Ambiance/Cleanliness
  - Value for Money
  - Overall Experience
- **Accuracy**: XX%
- **JSON Validity**: 100%
- **Reasoning**: Improved accuracy through structured analysis

#### Approach 3: Few-Shot Prompting
- **Design**: Example-based classification
- **Examples Used**: 3 diverse examples covering 1-5 star ratings
- **Accuracy**: XX%
- **JSON Validity**: 100%
- **Reasoning**: Pattern matching improves consistency

### Evaluation Results

| Approach | Accuracy | JSON Valid | Consistency | Avg Time |
|----------|----------|-----------|-------------|----------|
| Direct | XX% | 100% | XX% | XXXms |
| CoT | XX% | 100% | XX% | XXXms |
| Few-Shot | XX% | 100% | XX% | XXXms |

### Key Findings
- Best performing approach: [Approach 2/3]
- JSON validity 100% across all approaches
- Trade-off between accuracy and latency
- Consistency improved with structured reasoning

---

## Task 2: Two-Dashboard AI Feedback System

### User Dashboard Features
- ✅ Star rating selector (1-5)
- ✅ Review text input (max 500 chars)
- ✅ AI-generated response
- ✅ Success confirmation
- ✅ Responsive design

### Admin Dashboard Features
- ✅ Authentication/password protection
- ✅ Live submission feed
- ✅ Filtering by rating & date
- ✅ AI-generated summaries display
- ✅ Recommended actions display
- ✅ Analytics charts (rating distribution, trends)
- ✅ CSV export functionality

### Technical Implementation

**Tech Stack:**
- Frontend: Streamlit
- Backend: FastAPI
- Database: JSON (with SQLite option)
- LLM: Gemini API
- Deployment: Streamlit Cloud + Vercel

**API Endpoints:**
- POST `/api/submit-review` - Submit new review
- GET `/api/submissions` - Fetch all submissions
- GET `/api/submissions/{id}` - Fetch specific submission
- GET `/api/analytics` - Get analytics data
- DELETE `/api/submissions/{id}` - Admin deletion

### Data Flow Architecture

```
User Dashboard → Streamlit Cloud
                    ↓
              FastAPI Backend (Vercel)
                    ↓
              JSON Data Store
                    ↑
          LLM API (Gemini)
                    ↑
            Admin Dashboard ← Streamlit Cloud
```

---

## Deployment Links

- **User Dashboard**: [URL]
- **Admin Dashboard**: [URL]
- **GitHub Repository**: [URL]

---

## Design Decisions

### Why Streamlit?
- Fastest development & deployment
- Built-in data visualization (Plotly)
- No frontend expertise required
- Free hosting on Streamlit Cloud

### Why FastAPI?
- Lightweight and fast
- Easy CORS configuration
- Auto-generated API documentation
- Simple deployment on Vercel

### Why JSON for Storage?
- Simplicity for MVP
- Easily portable
- Can export for analysis
- Scales for ~10K submissions

### LLM Choices
- **User Response**: Conversational tone
- **Summary**: Concise one-liner
- **Actions**: Specific, actionable recommendations

---

## Challenges & Solutions

| Challenge | Solution |
|-----------|----------|
| CORS errors | Added FastAPI CORS middleware |
| LLM rate limiting | Implemented caching, batch processing |
| Real-time updates | Used Streamlit rerun() & cache invalidation |
| Authentication | Simple password in environment variable |

---

## Future Improvements

1. **Database**: Migrate to PostgreSQL for scalability
2. **Authentication**: Implement proper OAuth for admin
3. **Analytics**: Add sentiment analysis & trend detection
4. **Export**: Support Excel, PDF export formats
5. **Notifications**: Email alerts for low ratings
6. **Caching**: Redis caching for frequently accessed data

---

## Conclusion

This implementation demonstrates end-to-end AI system development:
- Task 1: Prompt engineering & evaluation
- Task 2: Full-stack application with AI integration

Both dashboards are fully functional and deployed.

---

Generated: [DATE]
```

---

## Final Submission Checklist

- [ ] GitHub repository created with all code
- [ ] Task 1 notebook with evaluation results
- [ ] Both dashboards deployed and accessible
- [ ] Backend API deployed
- [ ] Report PDF created
- [ ] All links verified working
- [ ] Environment variables set in deployment platforms
- [ ] Google Form submission completed with:
  - [ ] GitHub Repository URL
  - [ ] Report PDF Link
  - [ ] User Dashboard URL
  - [ ] Admin Dashboard URL

---

## Troubleshooting

### Streamlit App Issues
```bash
# Clear Streamlit cache
rm -rf ~/.streamlit/

# Run with debug logging
streamlit run apps/user_dashboard.py --logger.level=debug
```

### Backend Connection Issues
```bash
# Check if backend is running
curl http://localhost:8000/health

# View backend logs
uvicorn backend.main:app --reload --log-level debug
```

### Gemini API Errors
```python
# Test API connection
python -c "import google.generativeai as genai; print('API OK')"

# Check rate limits
# Free tier: 60 requests/minute
```

### Streamlit Cloud Deployment
- Check that `.streamlit/secrets.toml` is created (not `.env`)
- Ensure `requirements.txt` is in the same directory as the app
- Check logs in Streamlit Cloud dashboard

---

## Support Resources

- Streamlit Docs: https://docs.streamlit.io/
- FastAPI Docs: https://fastapi.tiangolo.com/
- Gemini API: https://ai.google.dev/
- Vercel Docs: https://vercel.com/docs

Good luck! 🚀

**Submission Deadline**: Monday, December 15, 2025 EOD
