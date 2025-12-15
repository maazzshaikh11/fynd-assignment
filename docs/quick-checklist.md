# Fynd AI Intern Assessment - Quick Reference Checklist

## Timeline Overview
- **Current Time**: Sunday, December 14, 2025, 3:17 PM IST
- **Submission Deadline**: Monday, December 15, 2025 EOD
- **Time Available**: ~43 hours
- **Recommended Pace**: Complete Task 1 (6-8 hrs) → Task 2 (10-14 hrs) → Report (2-3 hrs) → Testing & Polish (4-6 hrs)

---

## TASK 1: Rating Prediction via Prompting

### Setup Checklist (0-2 hours)
- [ ] Create GitHub repository
- [ ] Clone repository locally
- [ ] Create Python virtual environment
- [ ] Install dependencies (pandas, google-generativeai, dotenv, requests)
- [ ] Set up `.env` file with GEMINI_API_KEY
- [ ] Download Yelp Reviews dataset from Kaggle
- [ ] Sample 200 rows from dataset

### Implementation Checklist (2-6 hours)
- [ ] Create Jupyter notebook: `task1_rating_prediction.ipynb`
- [ ] Implement Approach 1: Direct Prompting
  - [ ] Write prompt template
  - [ ] Test on 5 sample reviews
  - [ ] Debug JSON parsing
- [ ] Implement Approach 2: Chain-of-Thought
  - [ ] Design aspect-based prompt
  - [ ] Test on 5 sample reviews
  - [ ] Verify JSON output
- [ ] Implement Approach 3: Few-Shot Prompting
  - [ ] Create 3 example reviews with ratings
  - [ ] Write prompt template with examples
  - [ ] Test on 5 sample reviews
- [ ] Create evaluation function
- [ ] Run evaluation on ~200 samples for each approach
  - [ ] Calculate accuracy
  - [ ] Calculate JSON validity rate
  - [ ] Calculate consistency score
  - [ ] Measure response time
- [ ] Save evaluation results to JSON
- [ ] Create comparison table/visualization

### Deliverables Checklist
- [ ] Notebook with all 3 prompting approaches clearly documented
- [ ] evaluation_results.json with metrics for each approach
- [ ] Comparison table in notebook (Approach | Accuracy | JSON Valid | Consistency | Time)
- [ ] Written explanation of why each approach was designed that way
- [ ] Analysis of which approach performs best and why

---

## TASK 2: Two-Dashboard AI Feedback System

### Backend Setup (0-2 hours)
- [ ] Create `backend/` directory
- [ ] Create `backend/main.py` with FastAPI app
- [ ] Implement data models (ReviewSubmission, AIResponse)
- [ ] Implement endpoints:
  - [ ] POST `/api/submit-review`
  - [ ] GET `/api/submissions`
  - [ ] GET `/api/submissions/{id}`
  - [ ] GET `/api/analytics`
- [ ] Add CORS middleware
- [ ] Implement JSON file storage (submissions.json)
- [ ] Create LLM functions:
  - [ ] generate_ai_response()
  - [ ] generate_ai_summary()
  - [ ] generate_recommended_actions()
- [ ] Test locally with curl/Postman
- [ ] Create `backend/requirements.txt`

**Test Commands:**
```bash
# Terminal 1
cd backend
uvicorn main:app --reload --port 8000

# Terminal 2
curl http://localhost:8000/health
# Should return: {"status": "healthy", ...}

curl -X POST http://localhost:8000/api/submit-review \
  -H "Content-Type: application/json" \
  -d '{"rating": 4, "review": "Great experience!", "timestamp": "2025-12-14T15:30:00"}'
```

### User Dashboard Setup (2-4 hours)
- [ ] Create `apps/user_dashboard.py`
- [ ] Implement UI components:
  - [ ] Page configuration
  - [ ] Title and instructions
  - [ ] Star rating selector (1-5)
  - [ ] Review text input area (max 500 chars)
  - [ ] Character counter
  - [ ] Submit button
- [ ] Add input validation:
  - [ ] Review minimum length (10 chars)
  - [ ] Rating between 1-5
- [ ] Implement backend integration:
  - [ ] POST request to `/api/submit-review`
  - [ ] Error handling
  - [ ] Loading state with spinner
- [ ] Display AI response after submission
- [ ] Add success message and confirmation
- [ ] Add styling (CSS) for better UX
- [ ] Test locally with Streamlit
- [ ] Create `apps/requirements.txt`

**Test Locally:**
```bash
cd apps
streamlit run user_dashboard.py
# Visit: http://localhost:8501
```

### Admin Dashboard Setup (2-4 hours)
- [ ] Create `apps/admin_dashboard.py`
- [ ] Implement authentication:
  - [ ] Password input field
  - [ ] Session state tracking
  - [ ] Logout functionality
- [ ] Implement data display:
  - [ ] Fetch submissions from backend
  - [ ] Display in filterable table
  - [ ] Show all relevant columns (rating, review, summary, actions)
- [ ] Implement filtering:
  - [ ] Filter by rating (1-5 stars)
  - [ ] Filter by date range
  - [ ] Search by keyword
- [ ] Implement metrics section:
  - [ ] Total submissions count
  - [ ] Average rating
  - [ ] Count of each rating level
  - [ ] Sentiment breakdown (positive/neutral/negative)
- [ ] Implement analytics visualizations:
  - [ ] Bar chart: Rating distribution
  - [ ] Line chart: Rating trend over time
- [ ] Add admin actions:
  - [ ] CSV export button
  - [ ] Refresh data button
  - [ ] Last updated timestamp
- [ ] Add insights section:
  - [ ] Top issues mentioned
  - [ ] Recommended actions based on feedback
- [ ] Add caching with @st.cache_data for performance

**Test Locally:**
```bash
cd apps
streamlit run admin_dashboard.py
# Visit: http://localhost:8501
# Default password: admin123 (changeable)
```

### Deployment Checklist (3-5 hours)

#### Local Testing
- [ ] Verify both dashboards work with backend running locally
- [ ] Test end-to-end: Submit review → See in admin dashboard
- [ ] Test data persistence (data survives app restart)
- [ ] Test error handling (backend down, invalid input, etc.)

#### Push to GitHub
- [ ] Create `.gitignore` (exclude venv, .env, submissions.json, etc.)
- [ ] Add all files to git
- [ ] Create meaningful commit message
- [ ] Push to GitHub

#### Deploy Backend (Vercel)
- [ ] Create `backend/vercel.json`
- [ ] Install Vercel CLI: `npm install -g vercel`
- [ ] Run `vercel` command from project root
- [ ] Add GEMINI_API_KEY environment variable in Vercel dashboard
- [ ] Note the deployment URL (e.g., `https://your-project.vercel.app`)
- [ ] Test backend endpoint: `curl https://your-project.vercel.app/health`

#### Deploy User Dashboard (Streamlit Cloud)
- [ ] Go to https://streamlit.io/cloud
- [ ] Sign in with GitHub
- [ ] Create new app
- [ ] Select repository and branch
- [ ] Set main file to: `apps/user_dashboard.py`
- [ ] Click "Deploy"
- [ ] Wait for deployment (2-3 minutes)
- [ ] In app settings → Secrets, add:
  ```
  BACKEND_URL = "https://your-vercel-url"
  GEMINI_API_KEY = "your-key"
  ADMIN_PASSWORD = "your-password"
  ```
- [ ] Note the deployed URL (e.g., `https://your-user-dashboard.streamlit.app`)
- [ ] Test the deployed app

#### Deploy Admin Dashboard (Streamlit Cloud)
- [ ] Create new app on Streamlit Cloud
- [ ] Set main file to: `apps/admin_dashboard.py`
- [ ] Deploy
- [ ] Add same secrets as user dashboard
- [ ] Note the deployed URL (e.g., `https://your-admin-dashboard.streamlit.app`)
- [ ] Test the deployed app
- [ ] Test login with password

#### Final Verification
- [ ] User Dashboard: Can submit review → AI response appears
- [ ] Admin Dashboard: Can login → sees submitted reviews
- [ ] Data flows between dashboards correctly
- [ ] All links in submission form are working

---

## TASK 2 DELIVERABLES

### Files Required
- [ ] `backend/main.py` - FastAPI backend
- [ ] `backend/requirements.txt` - Backend dependencies
- [ ] `backend/vercel.json` - Vercel configuration
- [ ] `apps/user_dashboard.py` - User-facing dashboard
- [ ] `apps/admin_dashboard.py` - Admin dashboard
- [ ] `apps/requirements.txt` - App dependencies
- [ ] `.streamlit/config.toml` - Streamlit configuration
- [ ] `.env` (not submitted, but tracked in .gitignore)

### Deployed URLs Required
- [ ] **User Dashboard URL**: https://...streamlit.app/
- [ ] **Admin Dashboard URL**: https://...streamlit.app/
- [ ] **Backend URL**: https://...vercel.app/

---

## REPORT & SUBMISSION

### Report Structure (1-2 hours)

Create `REPORT.md` or PDF with:

- [ ] **Executive Summary** (100 words)
  - Overview of both tasks
  - Key metrics achieved
  - Deployment status

- [ ] **Task 1 Analysis** (500-700 words)
  - Prompt design for each approach
  - Rationale for each approach
  - Evaluation metrics table
  - Key findings
  - Best approach analysis

- [ ] **Task 2 Implementation** (500-700 words)
  - Architecture diagram/description
  - Tech stack justification
  - Feature breakdown
  - API endpoints overview
  - Data flow explanation

- [ ] **Design Decisions** (300-400 words)
  - Why Streamlit?
  - Why FastAPI?
  - Why JSON storage?
  - Why Gemini API?
  - Trade-offs made

- [ ] **Challenges & Solutions** (200-300 words)
  - Problems encountered
  - How they were solved
  - Lessons learned

- [ ] **Deployment Details** (200-300 words)
  - How to access dashboards
  - Environment configuration
  - Any special setup required

- [ ] **Future Improvements** (150-200 words)
  - Database migration
  - Enhanced analytics
  - Additional features

### Submission Checklist
- [ ] Convert REPORT.md to PDF (use https://pandoc.org/ or Google Docs)
- [ ] Copy report PDF link to accessible location (Google Drive, GitHub, etc.)
- [ ] Verify all dashboard URLs are working and public
- [ ] Verify GitHub repository is public and contains all code
- [ ] Open Google Form: https://docs.google.com/forms/d/1fBJIMi82lCLE7vYvEWNkiZHE-vDD3AxbZIGJYELSTWc/edit

### Submit via Google Form:
- [ ] **GitHub Repository URL**
- [ ] **Report PDF Link**
- [ ] **User Dashboard URL**
- [ ] **Admin Dashboard URL**
- [ ] Click "Submit"

---

## Time Management Guide

### Hours 0-6 (Sunday 3 PM - 9 PM)
- **Task**: Task 1 Setup & Implementation
- **Milestones**:
  - 3:30 PM: Dataset downloaded, environment set up
  - 5:00 PM: All 3 prompting approaches implemented & tested
  - 7:00 PM: Evaluation complete on 200 samples
  - 9:00 PM: Results compiled in notebook, evaluation_results.json saved

### Hours 6-12 (Sunday 9 PM - Monday 3 AM)
- **Task**: Task 1 Report + Task 2 Backend Setup
- **Milestones**:
  - 9:30 PM: Task 1 report written
  - 11:00 PM: Task 1 complete and pushed to GitHub
  - 12:30 AM: Backend (FastAPI) implemented and tested locally
  - 3:00 AM: Backend deployed to Vercel

### Hours 12-24 (Monday 3 AM - 3 PM)
- **Task**: Task 2 Frontend (User Dashboard)
- **Milestones**:
  - 3:30 AM: User dashboard UI complete
  - 5:00 AM: Backend integration working locally
  - 7:00 AM: User dashboard deployed to Streamlit Cloud
  - 9:00 AM: Admin dashboard implemented
  - 12:00 PM: Admin dashboard deployed
  - 3:00 PM: End-to-end testing complete

### Hours 24-30 (Monday 3 PM - 9 PM)
- **Task**: Testing, Bug Fixes, Polish
- **Milestones**:
  - 3:30 PM: All deployments verified working
  - 5:00 PM: Data persistence verified
  - 7:00 PM: Report finalized and converted to PDF
  - 9:00 PM: Final checks before submission

### Hours 30-43 (Monday 9 PM - EOD)
- **Task**: Final submission
- **Milestones**:
  - 9:00 PM: All links verified working
  - 9:30 PM: Google Form filled out
  - 10:00 PM: Submission complete ✅

---

## Common Pitfalls to Avoid

1. **❌ Overly Complex Prompts for Task 1**
   - ✅ Keep prompts focused and clear
   - ✅ Test on small sample first (5 reviews)

2. **❌ Forgetting Environment Variables**
   - ✅ Always use `.env` file locally
   - ✅ Always set secrets in Streamlit Cloud and Vercel

3. **❌ CORS Errors**
   - ✅ Add CORS middleware in FastAPI
   - ✅ Set correct BACKEND_URL in Streamlit secrets

4. **❌ JSON Parsing Failures**
   - ✅ Always include error handling
   - ✅ Use regex to extract JSON from LLM responses

5. **❌ Real-time Data Not Updating**
   - ✅ Use `st.rerun()` in Streamlit
   - ✅ Use `@st.cache_data(ttl=30)` for data refresh

6. **❌ Forgetting to Push Code to GitHub**
   - ✅ Commit and push frequently
   - ✅ Verify repository is public

7. **❌ Incomplete Submission**
   - ✅ Follow the exact format required
   - ✅ Verify all 4 fields in Google Form

---

## Quick Commands Reference

### Local Development
```bash
# Create & activate venv
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run backend
uvicorn backend.main:app --reload

# Run Streamlit apps
streamlit run apps/user_dashboard.py
streamlit run apps/admin_dashboard.py

# Test API
curl http://localhost:8000/health
```

### GitHub
```bash
git add .
git commit -m "Fynd assignment submission"
git push origin main
```

### Streamlit Cloud Secrets
```
# Settings → Secrets → Copy-Paste:
BACKEND_URL = "https://your-url.vercel.app"
GEMINI_API_KEY = "your-key"
ADMIN_PASSWORD = "your-password"
```

---

## Success Criteria

### Task 1 ✅
- [x] 3+ prompting approaches implemented
- [x] Evaluated on ~200 samples
- [x] Accuracy metric calculated
- [x] JSON validity metric calculated
- [x] Consistency metric calculated
- [x] Results documented and compared
- [x] Code in GitHub notebook

### Task 2 ✅
- [x] User dashboard fully functional
- [x] Admin dashboard fully functional
- [x] Both dashboards deployed and public
- [x] Backend API working
- [x] Data persistence working
- [x] LLM integration working
- [x] All features implemented

### Submission ✅
- [x] GitHub repository public
- [x] Report PDF accessible
- [x] Both dashboard URLs working
- [x] Google Form submitted

---

## You've Got This! 🚀

Remember:
- **Start early, test often**
- **Deploy early, don't wait until last minute**
- **Use the provided starter code to save time**
- **Focus on functionality over perfection**
- **Document as you go**

**Good luck! You're going to do great at Fynd! 💪**
