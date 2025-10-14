import os
import streamlit as st
import pandas as pd
import numpy as np
from openai import OpenAI

# -------------------------------
# CONFIG & BRANDING
# -------------------------------
st.set_page_config(page_title="Black Detsu | Strategic Insights", page_icon="🧠", layout="wide")

st.markdown("""
    <style>
        .main {background-color: #0B0C10;}
        h1, h2, h3, .stTextInput label, .stSelectbox label { color: #F8F8F2; }
        .stMetric label { color: #66FCF1; }
        .stMetric { background-color: #1F2833; border-radius: 8px; padding: 10px; }
        .stDataFrame { background-color: #1F2833; }
        .css-1d391kg { color: #C5C6C7; }
        .block-container { padding-top: 2rem; }
    </style>
""", unsafe_allow_html=True)

st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Black_circle.svg/768px-Black_circle.svg.png", width=60)
st.title("🧠 Black Detsu Strategic Intelligence Assistant")

# -------------------------------
# API KEY
# -------------------------------
api_key = os.getenv("OPENAI_API_KEY")
if not api_key and "OPENAI_API_KEY" in st.secrets:
    api_key = st.secrets["OPENAI_API_KEY"]

if not api_key:
    st.error("❌ No API key found. Please set OPENAI_API_KEY as env var or in Streamlit secrets.")
else:
    client = OpenAI(api_key=api_key)

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
# EXECUTIVE QUESTIONS
# -------------------------------
st.sidebar.header("🧭 Insight Controls")
persona = st.sidebar.radio("Insight Style", ["Boardroom", "Creative", "Financial"])

SUGGESTIONS = {
    "📉 Diminishing Returns": "Show diminishing returns by channel and spend curve. Include publisher-level insights.",
    "🧑‍🤝‍🧑 Publisher by Audience": "Which publishers performed best by audience segment?",
    "🔁 Online vs Offline CLV": "Compare online and offline CLV. What do user journey paths and app usage suggest?",
    "💡 Channel Mix by Investment": "What mix of channels would you recommend for $100M, $200M, and $300M investment levels?",
    "📆 Churn Timing": "Which months had the most churn? What were the internal and external factors?",
    "🌐 External Factors": "Research external market or economic factors that may explain churn or performance shifts.",
    "🎥 Format Efficiency": "Which format generated the highest CPC, ROI, and CPA?",
    "🚀 Conversion Efficiency": "Which channels had the highest click-to-conversion rate?",
    "⚖️ Efficiency Strategy": "What should we scale, pause, or optimize based on efficiency?"
}

selected_suggestion = st.selectbox("💬 Executive Questions", options=[""] + list(SUGGESTIONS.values()))
user_question = st.text_input("Or type your own question:")
query = selected_suggestion or user_question or None

# -------------------------------
# SAMPLE DATA GENERATION
# -------------------------------
@st.cache_data
def generate_enterprise_data():
    np.random.seed(42)
    months = pd.date_range(start="2024-01-01", periods=12, freq="MS").strftime("%b-%Y")

    campaigns = [
        "CC Acquisition Q1", "CC Retargeting Q2", "CA Onboarding Q1", "CA Growth Q2",
        "Mortgage LeadGen Q1", "Mortgage Seasonality Q2", "Loans Promo Q1", "Loans Burst Q2",
        "BB Awareness Q1", "BB LeadGen Q2", "CRM Re-engage Q1", "CRM Loyalty Q2"
    ]
    audiences = [
        "Students", "Young Professionals", "Families", "Homeowners",
        "Small Business", "High Net Worth", "Loyal Customers", "Churn Risk",
        "Prospects", "App Users", "Web Users", "In-branch"
    ]
    channels = ["Paid Search", "Social", "Display", "Email", "Video"]
    creatives = ["Low Fee + Rewards", "Holiday Urgency", "Student Empowerment", "Homeowner Stability", "Creative Refresh"]
    strategies = ["Retargeting", "Lookalike", "Sequential Messaging", "Always On", "Burst"]
    publishers = ["Google", "Meta", "YouTube", "TikTok", "LinkedIn"]
    formats = ["Video", "Carousel", "Search Ad", "Email", "Display Banner"]

    data = {
        "Month": months,
        "Audience Segment": audiences,
        "Campaign Name": campaigns,
        "Channel": np.random.choice(channels, size=12),
        "Creative Messaging": np.random.choice(creatives, size=12),
        "Targeting Strategy": np.random.choice(strategies, size=12),
        "Publisher": np.random.choice(publishers, size=12),
        "Format": np.random.choice(formats, size=12),
        "Media Spend ($)": np.random.randint(10_000_000, 50_000_000, size=12),
        "CRM Emails Sent": np.random.randint(5_000_000, 20_000_000, size=12),
        "CRM Open Rate (%)": np.round(np.random.uniform(15, 35, size=12), 2),
        "Leads Generated": np.random.randint(500_000, 2_000_000, size=12),
        "Conversions": np.random.randint(150_000, 800_000, size=12),
        "Revenue ($)": np.random.randint(200_000_000, 1_000_000_000, size=12),
        "Customer Churn (%)": np.round(np.random.uniform(1.5, 6.5, size=12), 2),
        "CAC ($)": np.round(np.random.uniform(40, 120, size=12), 2),
        "CLV ($)": np.round(np.random.uniform(500, 2000, size=12), 2),
    }

    df = pd.DataFrame(data)
    df["Conversion Rate (%)"] = (df["Conversions"] / df["Leads Generated"]) * 100
    df["ROAS"] = df["Revenue ($)"] / df["Media Spend ($)"]
    df["CRM Engagements"] = df["CRM Emails Sent"] * (df["CRM Open Rate (%)"] / 100)
    return df

df = generate_enterprise_data()

# -------------------------------
# EXECUTIVE SUMMARY
# -------------------------------
summary = {
    "Total Revenue": f"${df['Revenue ($)'].sum():,.0f}",
    "Total Spend": f"${df['Media Spend ($)'].sum():,.0f}",
    "Average ROAS": round(df["ROAS"].mean(), 2),
    "Average CAC": f"${df['CAC ($)'].mean():,.2f}",
    "Average CLV": f"${df['CLV ($)'].mean():,.2f}",
    "Best Month (ROAS)": df.loc[df["ROAS"].idxmax(), "Month"],
    "Worst Month (Churn)": df.loc[df["Customer Churn (%)"].idxmax(), "Month"],
    "CRM Engagement Peak": df.loc[df["CRM Engagements"].idxmax(), "Month"],
}

# -------------------------------
# DISPLAY
# -------------------------------
st.subheader("📈 Monthly Performance")
st.dataframe(df, use_container_width=True)

st.subheader("📌 Executive Summary")
cols = st.columns(len(summary))
for col, (k, v) in zip(cols, summary.items()):
    col.metric(label=k, value=v)

st.subheader("📊 Visual Trends")
st.line_chart(df.set_index("Month")[["Revenue ($)", "Media Spend ($)"]])
st.bar_chart(df.set_index("Month")[["Conversion Rate (%)", "Customer Churn (%)"]])

st.subheader("🎨 Top Performing Creatives by ROAS")
top_creatives = df.groupby("Creative Messaging")["ROAS"].mean().sort_values(ascending=False).head(5)
st.bar_chart(top_creatives)

st.subheader("🎯 Targeting Strategy Effectiveness")
strategy_conv = df.groupby("Targeting Strategy")["Conversion Rate (%)"].mean()
st.bar_chart(strategy_conv)

st.subheader("📡 Channel Revenue Performance")
channel_rev = df.groupby("Channel")["Revenue ($)"].sum().sort_values(ascending=False)
st.bar_chart(channel_rev)

st.subheader("📰 Publisher Performance by Audience Segment")
publisher_audience = df.groupby(["Publisher", "Audience Segment"])["Revenue ($)"].sum().unstack().fillna(0)
st.bar_chart(publisher_audience)

st.subheader("🎥 Format Efficiency (ROAS)")
format_roas = df.groupby("Format")["ROAS"].mean().sort_values(ascending=False)
st.bar_chart(format_roas)

st.subheader("🚀 Click-to-Conversion Rate by Channel")
click_conv = df.groupby("Channel")[["Leads Generated", "Conversions"]].sum()
click_conv["Click-to-Conversion (%)"] = (click_conv["Conversions"] / click_conv["Leads Generated"]) * 100
st.bar_chart(click_conv["Click-to-Conversion (%)"])

# -------------------------------
# AI INSIGHTS
# -------------------------------
if query and api_key:
    with st.spinner("Analyzing with AI..."):
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            stream=True,
        )

        st.subheader("🤖 AI Executive Insight")
        placeholder = st.empty()
        full_text = ""

        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                full_text += chunk.choices[0].delta.content
                placeholder.markdown(full_text)
