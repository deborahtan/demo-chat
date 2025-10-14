import os
import streamlit as st
import pandas as pd
import numpy as np
from openai import OpenAI

# -------------------------------
# CONFIG & BRANDING
# -------------------------------
st.set_page_config(page_title="Strategic Intelligence Assistant", page_icon="🧠", layout="wide")

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
        html, body, [class*="css"]  {
            font-family: 'Inter', sans-serif;
            background-color: #000000;
            color: #F8F8F2;
        }
        h1, h2, h3, label { color: #FFFFFF; }
        .metric-card {
            background-color: #121417;
            border: 1px solid #2A2F36;
            border-radius: 10px;
            padding: 16px;
            margin: 6px 0;
            text-align: center;
        }
        .metric-label { color: #A6B1BB; font-weight: 600; font-size: 13px; letter-spacing: 0.2px; }
        .metric-value { color: #FFFFFF; font-size: 20px; font-weight: 700; }
        .section-title {
            border-bottom: 1px solid #2A2F36;
            padding-bottom: 6px;
            margin-top: 18px;
        }
        .answer-card {
            background-color: #0E1114;
            border: 1px solid #2A2F36;
            border-radius: 10px;
            padding: 16px;
        }
    </style>
""", unsafe_allow_html=True)

# Use the dentsu black logo
st.image("https://upload.wikimedia.org/wikipedia/commons/e/e5/Dentsu-logo_black.svg", width=160)
st.title("Strategic Intelligence Assistant")

# -------------------------------
# API KEY
# -------------------------------
api_key = os.getenv("OPENAI_API_KEY")
if not api_key and "OPENAI_API_KEY" in st.secrets:
    api_key = st.secrets["OPENAI_API_KEY"]

client = None
if api_key:
    client = OpenAI(api_key=api_key)
else:
    st.error("No API key found. Please set OPENAI_API_KEY as env var or in Streamlit secrets.")

# -------------------------------
# SYSTEM PROMPT
# -------------------------------
system_prompt = """
You are an AI insights assistant for C‑suite executives in marketing, CRM, and finance.
Your role is to analyze enterprise‑scale performance data and answer in clear, strategic,
executive‑ready language.

Always:
- Focus on financial impact, risks, and opportunities.
- Highlight trends, seasonal patterns, and anomalies.
- Provide concise, actionable recommendations for Marketing/Media, Creative, and Finance teams.
- Use metrics like Revenue, ROAS, CAC, CLV, Churn, CRM Engagement, CPC, CPA, and Conversion Rate.
- Identify top-performing creative messaging, targeting strategies, channels, publishers, and formats.
- Recommend optimizations based on what worked and what underperformed.
- Analyze diminishing returns by channel and spend curve.
- Compare publisher performance by audience segment.
- Evaluate online vs. offline CLV and user journey paths.
- Recommend optimal channel mixes for different investment levels (e.g., $100M, $200M, $300M).
- Identify months with highest churn and explore internal/external drivers.
- Research external market or economic factors that may explain churn or performance shifts.
- Determine which formats generate the highest CPC, ROI, and CPA.
- Highlight channels with the highest click-to-conversion rates.
- Recommend what to scale, pause, or optimize for efficiency.
- Write in a professional, boardroom‑ready tone.
"""

# -------------------------------
# EXECUTIVE QUESTIONS (left)
# -------------------------------
QUESTIONS = [
    "Show diminishing returns by channel and spend curve. Include publisher-level insights.",
    "Which publishers performed best by audience segment?",
    "Compare online and offline CLV. What do user journey paths suggest?",
    "What mix of channels would you recommend for $100M, $200M, and $300M investment levels?",
    "Which months had the most churn? What were the internal and external factors?",
    "Research external market or economic factors that may explain churn or performance shifts.",
    "Which format generated the highest ROI and CPA?",
    "Which channels had the highest click-to-conversion rate?",
    "What should we scale, pause, or optimize for efficiency?"
]

# Wider left column so text doesn’t cut off
left, right = st.columns([1.6, 2.4])

with left:
    st.subheader("Executive questions")
    selected = st.selectbox("Select a question", options=QUESTIONS, index=0)

# -------------------------------
# SAMPLE DATA
# -------------------------------
@st.cache_data
def generate_data():
    np.random.seed(42)
    months = pd.date_range(start="2024-01-01", periods=12, freq="MS").strftime("%b-%Y")
    df = pd.DataFrame({
        "Month": months,
        "Revenue ($)": np.random.randint(200_000_000, 1_000_000_000, size=12),
        "Media Spend ($)": np.random.randint(10_000_000, 50_000_000, size=12),
        "CLV ($)": np.round(np.random.uniform(500, 2000, size=12), 2),
    })
    df["ROAS"] = df["Revenue ($)"] / df["Media Spend ($)"]
    return df

df = generate_data()

# -------------------------------
# TOP RIGHT: SUMMARY + VISUALS
# -------------------------------
with right:
    st.subheader("Executive summary")
    summary = {
        "Total Revenue": f"${df['Revenue ($)'].sum():,.0f}",
        "Total Spend": f"${df['Media Spend ($)'].sum():,.0f}",
        "Average ROAS": round(df["ROAS"].mean(), 2),
        "Average CLV": f"${df['CLV ($)'].mean():,.2f}",
        "Best Month (Revenue)": df.loc[df["Revenue ($)"].idxmax(), "Month"],
    }
    cols = st.columns(len(summary))
    for col, (k, v) in zip(cols, summary.items()):
        with col:
            st.markdown(
                f"<div class='metric-card'><div class='metric-label'>{k}</div><div class='metric-value'>{v}</div></div>",
                unsafe_allow_html=True
            )

    st.subheader("Monthly revenue & CLV")
    st.line_chart(df.set_index("Month")[["Revenue ($)", "CLV ($)"]])

# -------------------------------
# EXECUTIVE ANSWER (bottom, full width)
# -------------------------------
st.divider()
st.subheader("Executive answer")

if selected and client:
    with st.spinner("Generating executive insight..."):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": selected}
            ]
        )
        answer = response.choices[0].message.content

    # Prettify: split into bullet points and render in two columns
    bullets = [f"- {line.strip()}" for line in answer.split("\n") if line.strip()]
    if not bullets:
        bullets = [f"- {line.strip()}" for line in answer.split(". ") if line.strip()]

    st.markdown("<div class='answer-card'>", unsafe_allow_html=True)
    col_a, col_b = st.columns(2)
    half = max(1, len(bullets) // 2)
    with col_a:
        st.markdown("\n".join(bullets[:half]))
    with col_b:
        st.markdown("\n".join(bullets[half:]))
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------
# EXPANDABLE: Dimensions & metrics dictionary
# -------------------------------
st.divider()
with st.expander("Dimensions & metrics dictionary"):
    dims_metrics = {
        "Dimensions": [
            "Month", 
            "Campaign Name", 
            "Audience Segment", 
            "Channel",
            "Publisher", 
            "Format", 
            "Targeting Strategy", 
            "Creative Messaging"
        ],
        "Core metrics": [
            "Revenue ($)", 
            "Media Spend ($)", 
            "ROAS",
            "CLV ($)"
        ],
        "Additional enterprise metrics (not visualized here)": [
            "CAC ($)", 
            "Churn (%)", 
            "CRM Emails Sent", 
            "CRM Open Rate (%)",
            "Leads Generated", 
            "Conversions", 
            "Conversion Rate (%)",
            "CRM Engagements"
        ],
        "Definitions": {
            "Creative Messaging": "The specific advertising message, theme, or concept shown to an audience. Examples include value‑driven offers, urgency messaging, lifestyle positioning, or brand storytelling. In analytics, creatives are evaluated by performance metrics such as ROAS, CTR, or conversion rate to determine which messages resonate most effectively."
        },
                "Notes": [
            "ROAS = Revenue / Media Spend",
            "Monthly CLV shown for trend illustration; production views use cohort CLV",
            "Extend dictionary to match your GA4/GMP/CRM schema"
        ]
    }

    # Display dictionary nicely
    st.json(dims_metrics)
