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
            background-color: #1F2833;
            border-radius: 8px;
            padding: 15px;
            margin: 5px;
            text-align: center;
        }
        .metric-label { color: #66FCF1; font-weight: 600; }
        .metric-value { color: #FFFFFF; font-size: 20px; font-weight: 700; }
    </style>
""", unsafe_allow_html=True)

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
    st.error("❌ No API key found. Please set OPENAI_API_KEY as env var or in Streamlit secrets.")

# -------------------------------
# SYSTEM PROMPT
# -------------------------------
system_prompt = """
You are an AI insights assistant for C‑suite executives in marketing, CRM, and finance.
Your role is to analyze enterprise‑scale performance data and answer in clear, strategic,
executive‑ready language.
"""

# -------------------------------
# EXECUTIVE QUESTIONS
# -------------------------------
QUESTIONS = [
    "Show diminishing returns by channel and spend curve.",
    "Which publishers performed best by audience segment?",
    "Compare online and offline CLV. What do user journey paths suggest?",
    "What mix of channels would you recommend for $100M, $200M, $300M?",
    "Which months had the most churn? What were the drivers?",
    "Research external market or economic factors that may explain churn.",
    "Which format generated the highest ROI and CPA?",
    "Which channels had the highest click-to-conversion rate?",
    "What should we scale, pause, or optimize for efficiency?"
]

left, right = st.columns([1,3])

with left:
    st.subheader("Executive Questions")
    selected = st.selectbox("Select a question", options=QUESTIONS)

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
# EXECUTIVE SUMMARY + INSIGHTS
# -------------------------------
with right:
    st.subheader("Executive Summary")
    summary = {
        "Total Revenue": f"${df['Revenue ($)'].sum():,.0f}",
        "Total Spend": f"${df['Media Spend ($)'].sum():,.0f}",
        "Average ROAS": round(df["ROAS"].mean(), 2),
        "Average CLV": f"${df['CLV ($)'].mean():,.2f}",
        "Best Month (Revenue)": df.loc[df["Revenue ($)"].idxmax(), "Month"],
    }
    cols = st.columns(len(summary))
    for col, (k,v) in zip(cols, summary.items()):
        with col:
            st.markdown(f"<div class='metric-card'><div class='metric-label'>{k}</div><div class='metric-value'>{v}</div></div>", unsafe_allow_html=True)

    # AI INSIGHT
    if selected and client:
        with st.spinner("Analyzing with AI..."):
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": selected}
                ]
            )
            answer = response.choices[0].message.content

        st.subheader("Executive Answer")
        # Format answer into bullet points, two columns
        bullets = [f"- {line.strip()}" for line in answer.split(". ") if line.strip()]
        col1, col2 = st.columns(2)
        half = len(bullets)//2
        with col1:
            st.markdown("\n".join(bullets[:half]))
        with col2:
            st.markdown("\n".join(bullets[half:]))

    # -------------------------------
    # VISUALS
    # -------------------------------
    st.subheader("Monthly Revenue & CLV")
    st.line_chart(df.set_index("Month")[["Revenue ($)", "CLV ($)"]])
