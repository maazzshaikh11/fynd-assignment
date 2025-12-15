import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
st.set_page_config(
    page_title="Admin Dashboard",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

def check_admin_password():
    """Authenticate admin user before allowing dashboard access."""
    if "admin_authenticated" not in st.session_state:
        st.session_state.admin_authenticated = False
    
    if not st.session_state.admin_authenticated:
        st.title("Admin Dashboard")
        st.warning("Please enter admin password to continue")
        
        password = st.text_input("Admin Password:", type="password")
        
        if st.button("Login"):
            if password == ADMIN_PASSWORD:
                st.session_state.admin_authenticated = True
                st.success("Authenticated successfully")
                st.rerun()
            else:
                st.error("Incorrect password")
        
        st.stop()

check_admin_password()

@st.cache_data(ttl=30)
def fetch_submissions():
    """Retrieve all submissions from backend API."""
    try:
        response = requests.get(f"{BACKEND_URL}/api/submissions", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                return pd.DataFrame(data)
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Failed to fetch submissions: {str(e)}")
    
    return pd.DataFrame()

def export_to_csv(df):
    """Convert dataframe to CSV format for download."""
    return df.to_csv(index=False).encode('utf-8')

# Main Dashboard UI
st.title("Admin Dashboard")
st.markdown("Live feedback monitoring and analytics")
st.markdown("---")

col1, col2 = st.columns([10, 2])
with col2:
    if st.button("Refresh", key="refresh_btn"):
        st.cache_data.clear()
        st.rerun()

# Load and process data
df = fetch_submissions()

if df.empty:
    st.warning("No submissions yet. Check back soon!")
    st.stop()

# Data preprocessing
if 'timestamp' in df.columns and df['timestamp'].dtype == 'object':
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df['date'] = df['timestamp'].dt.date
    df['hour'] = df['timestamp'].dt.hour
else:
    df['date'] = pd.Timestamp.now().date()

# Key Metrics Section
st.subheader("Key Metrics")

metric_col1, metric_col2, metric_col3, metric_col4, metric_col5 = st.columns(5)

with metric_col1:
    st.metric("Total Submissions", len(df))

with metric_col2:
    avg_rating = df['rating'].mean()
    st.metric("Avg Rating", f"{avg_rating:.1f}⭐", delta=None)

with metric_col3:
    five_star_count = (df['rating'] == 5).sum()
    st.metric("5-Star Reviews", five_star_count)

with metric_col4:
    three_star_count = (df['rating'] == 3).sum()
    st.metric("3-Star Reviews", three_star_count)

with metric_col5:
    one_star_count = (df['rating'] == 1).sum()
    st.metric("1-Star Reviews", one_star_count)

st.markdown("---")

# Filters Section
st.subheader("Filters")

filter_col1, filter_col2, filter_col3 = st.columns(3)

with filter_col1:
    all_ratings = sorted(df['rating'].unique(), reverse=True)
    selected_ratings = st.multiselect(
        "Filter by Rating:",
        options=all_ratings,
        default=all_ratings,
        key="rating_filter"
    )
    
    if not selected_ratings:
        selected_ratings = all_ratings

with filter_col2:
    date_range = st.date_input(
        "Date Range:",
        value=(
            df['date'].min() if len(df) > 0 else datetime.now().date(),
            datetime.now().date()
        ),
        key="date_range"
    )

with filter_col3:
    search_keyword = st.text_input(
        "Search Reviews:",
        placeholder="Enter keyword...",
        key="search_box"
    )

# Apply filters
if selected_ratings:
    filtered_df = df[df['rating'].isin(selected_ratings)].copy()
else:
    filtered_df = df.copy()

if len(date_range) == 2:
    filtered_df = filtered_df[
        (filtered_df['date'] >= date_range[0]) &
        (filtered_df['date'] <= date_range[1])
    ]

if search_keyword:
    filtered_df = filtered_df[
        filtered_df['review'].str.contains(search_keyword, case=False, na=False)
    ]

st.markdown(f"**Showing {len(filtered_df)} of {len(df)} submissions**")
st.markdown("---")

# Submissions Table
st.subheader("All Submissions")

if len(filtered_df) > 0:
    display_df = filtered_df[[
        'timestamp', 'rating', 'review', 'ai_summary', 'recommended_actions'
    ]].copy().sort_values('timestamp', ascending=False)
    
    display_df = display_df.rename(columns={
        'timestamp': 'Time',
        'rating': 'Rating',
        'review': 'Review',
        'ai_summary': 'AI Summary',
        'recommended_actions': 'Actions'
    })
    
    st.dataframe(
        display_df,
        width="stretch",
        height=500,
        column_config={
            "Time": st.column_config.DatetimeColumn(format="YYYY-MM-DD HH:mm"),
            "Rating": st.column_config.NumberColumn(format="%d ⭐"),
            "Review": st.column_config.TextColumn(width="medium"),
            "AI Summary": st.column_config.TextColumn(width="medium"),
            "Actions": st.column_config.TextColumn(width="medium"),
        }
    )
else:
    st.info("No submissions match your filters.")

st.markdown("---")

# Analytics Charts
st.subheader("Analytics")

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.markdown("**Rating Distribution**")
    if len(filtered_df) > 0:
        rating_counts = filtered_df['rating'].value_counts().sort_index()
        fig_rating = px.bar(
            x=rating_counts.index,
            y=rating_counts.values,
            labels={'x': 'Rating', 'y': 'Count'},
            color=rating_counts.index,
            color_continuous_scale='RdYlGn'
        )
        st.plotly_chart(fig_rating, config={'displayModeBar': True})
    else:
        st.info("No data to display for selected filters.")

with chart_col2:
    st.markdown("**Rating Trend Over Time**")
    if len(filtered_df) > 0 and 'date' in filtered_df.columns:
        daily_avg = filtered_df.groupby('date')['rating'].mean()
        fig_trend = px.line(
            x=daily_avg.index,
            y=daily_avg.values,
            labels={'x': 'Date', 'y': 'Avg Rating'},
            markers=True
        )
        st.plotly_chart(fig_trend, config={'displayModeBar': True})
    else:
        st.info("No data to display for selected filters.")

# Sentiment Analysis
st.markdown("**Sentiment Breakdown**")

sentiment_col1, sentiment_col2, sentiment_col3 = st.columns(3)

with sentiment_col1:
    positive = (filtered_df['rating'] >= 4).sum()
    st.metric("Positive (4-5⭐)", positive, f"{positive/len(filtered_df)*100:.1f}%" if len(filtered_df) > 0 else "0%")

with sentiment_col2:
    neutral = (filtered_df['rating'] == 3).sum()
    st.metric("Neutral (3⭐)", neutral, f"{neutral/len(filtered_df)*100:.1f}%" if len(filtered_df) > 0 else "0%")

with sentiment_col3:
    negative = (filtered_df['rating'] < 3).sum()
    st.metric("Negative (1-2⭐)", negative, f"{negative/len(filtered_df)*100:.1f}%" if len(filtered_df) > 0 else "0%")

st.markdown("---")

# Export and Actions
st.subheader("Actions")

export_col1, export_col2, export_col3 = st.columns(3)

with export_col1:
    csv = export_to_csv(filtered_df)
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name=f"feedback_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

with export_col2:
    if st.button("Clear Cache & Refresh", key="clear_cache"):
        st.cache_data.clear()
        st.success("Cache cleared! Refreshing data...")
        st.rerun()

with export_col3:
    st.markdown(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Insights Section
st.markdown("---")
st.subheader("Insights & Next Steps")

col_insight1, col_insight2 = st.columns(2)

with col_insight1:
    st.markdown("**Top Issues Mentioned**")
    if 'review' in filtered_df.columns and len(filtered_df) > 0:
        keywords = []
        for review in filtered_df[filtered_df['rating'] < 3]['review'].head(5):
            keywords.extend(review.lower().split()[:5])
        
        if keywords:
            st.caption("Common words in negative reviews:")
            for keyword in list(set(keywords))[:5]:
                st.caption(f"• {keyword}")
        else:
            st.caption("No negative reviews to analyze")

with col_insight2:
    st.markdown("**Recommended Actions**")
    st.caption("Based on current feedback:")
    
    if len(filtered_df) > 0:
        negative_pct = (filtered_df['rating'] < 3).sum() / len(filtered_df) * 100
        
        if negative_pct > 30:
            st.warning("High proportion of negative reviews - Priority investigation needed")
        else:
            st.success("Overall positive sentiment - Continue current practices")

# Footer
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: gray; font-size: 11px; padding: 10px 0;">
    <p>Admin Dashboard • Last refreshed: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
    <p>Data auto-refreshes every 30 seconds. Use "Refresh" button to force immediate update.</p>
</div>
""", unsafe_allow_html=True)
