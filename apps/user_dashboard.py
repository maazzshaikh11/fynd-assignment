"""
User Dashboard for Customer Feedback Submission
Allows customers to submit reviews and receive AI-generated responses.
"""

import streamlit as st
import requests
import json
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Customer Feedback",
    page_icon="📝",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .main {
        max-width: 600px;
        margin: 0 auto;
    }
    .stButton button {
        width: 100%;
        height: 50px;
        font-size: 16px;
        border-radius: 10px;
    }
    .rating-stars {
        font-size: 40px;
        margin: 20px 0;
    }
    .success-message {
        padding: 20px;
        border-radius: 10px;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        margin: 20px 0;
    }
    .ai-response {
        padding: 15px;
        border-radius: 8px;
        background-color: #f8f9fa;
        border-left: 4px solid #007bff;
        margin: 15px 0;
    }
</style>
""", unsafe_allow_html=True)

if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "ai_response" not in st.session_state:
    st.session_state.ai_response = None
if "rating" not in st.session_state:
    st.session_state.rating = 5

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

def get_star_display(rating: int) -> str:
    return "⭐" * rating + "☆" * (5 - rating)

def submit_review_to_backend(rating: int, review: str) -> dict:
    try:
        payload = {
            "rating": rating,
            "review": review,
            "timestamp": datetime.now().isoformat(),
            "user_id": "anonymous"
        }

        response = requests.post(
            f"{BACKEND_URL}/api/submit-review",
            json=payload,
            timeout=10
        )

        if response.status_code == 200:
            return {
                "success": True,
                "data": response.json()
            }
        else:
            return {
                "success": False,
                "error": f"Server returned status {response.status_code}"
            }

    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "error": "Cannot connect to server. Please try again later."
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

st.markdown("# Share Your Feedback")
st.markdown("---")
st.markdown("We'd love to hear about your experience! Please share your honest review below.")

st.markdown("### How would you rate your experience?")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    if st.button("⭐", key="r1", use_container_width=True):
        st.session_state.rating = 1
with col2:
    if st.button("⭐⭐", key="r2", use_container_width=True):
        st.session_state.rating = 2
with col3:
    if st.button("⭐⭐⭐", key="r3", use_container_width=True):
        st.session_state.rating = 3
with col4:
    if st.button("⭐⭐⭐⭐", key="r4", use_container_width=True):
        st.session_state.rating = 4
with col5:
    if st.button("⭐⭐⭐⭐⭐", key="r5", use_container_width=True):
        st.session_state.rating = 5

st.markdown("**Or select rating:**")
rating_select = st.selectbox(
    "Rating",
    options=[1, 2, 3, 4, 5],
    index=st.session_state.rating - 1,
    label_visibility="collapsed"
)
st.session_state.rating = rating_select

st.markdown(
    f"<div class='rating-stars'>{get_star_display(st.session_state.rating)}</div>",
    unsafe_allow_html=True
)

st.markdown("### Tell us more about your experience")
review_text = st.text_area(
    "Your Review",
    placeholder="What did you like? What could be improved? Please be honest...",
    max_chars=500,
    height=150,
    label_visibility="collapsed"
)

chars = len(review_text) if review_text else 0
st.caption(f"{chars}/500 characters")

st.markdown("---")

col1, col2 = st.columns([3, 1])

with col1:
    if st.button("Submit Review", use_container_width=True, key="submit_btn"):
        if not review_text or len(review_text) < 10:
            st.error("Please write at least 10 characters in your review.")
        else:
            with st.spinner("Processing your feedback..."):
                result = submit_review_to_backend(
                    st.session_state.rating,
                    review_text
                )

            if result["success"]:
                st.session_state.submitted = True
                st.session_state.ai_response = result["data"]
                st.rerun()
            else:
                st.error(f"Error: {result['error']}")

with col2:
    if st.button("Clear", help="Clear form", key="clear_btn", use_container_width=True):
        st.session_state.submitted = False
        st.session_state.ai_response = None
        st.rerun()

if st.session_state.submitted and st.session_state.ai_response:
    st.markdown("---")

    st.markdown("<div class='success-message'><strong>Thank you for your feedback!</strong></div>", unsafe_allow_html=True)

    st.markdown("### Our Response")
    ai_resp = st.session_state.ai_response.get("ai_response", "Thank you for sharing your thoughts!")
    st.markdown(f"<div class='ai-response'>{ai_resp}</div>", unsafe_allow_html=True)

    with st.expander("How we'll use this feedback"):
        st.markdown("""
        - **Review Analysis**: Our AI analyzes your feedback for sentiment and key themes
        - **Action Items**: We identify specific improvements based on your comments
        - **Tracking**: We monitor trends to continuously improve our service
        - **Transparency**: Your feedback helps us stay accountable to our customers
        """)

    st.balloons()

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: gray; font-size: 12px; padding: 20px 0;">
    <p>Your feedback is valuable and completely anonymous.</p>
    <p>Last updated: """ + datetime.now().strftime("%Y-%m-%d %H:%M") + """</p>
</div>
""", unsafe_allow_html=True)
