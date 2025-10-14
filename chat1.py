import os
import streamlit as st
import pandas as pd
import numpy as np
from openai import OpenAI   # ✅ new client import

# -------------------------------
# CONFIG
# -------------------------------
st.set_page_config(page_title="C-Suite Marketing Insights", layout="wide")
st.title("📊 C-Suite Marketing, CRM & Financial Insights Assistant")

# -------------------------------
# API KEY (secure handling)
# -------------------------------
api_key = os.getenv("OPENAI_API_KEY")
if not api_key and "OPENAI_API_KEY" in st.secrets:
    api_key = st.secrets["OPENAI_API_KEY"]

if not api_key:
    st.error("❌ No API key found. Please set OPENAI_API_KEY as env var or in Streamlit secrets.")
else:
    client = OpenAI(api_key=api_key)

# -------------------------------
# SYSTEM PROMPT (C-Suite framing)
# -------------------------------
system_prompt = """
You are an AI insights assistant for C‑suite executives in marketing, CRM, and finance.
Your role is to analyze enterprise‑scale performance data and answer in clear, strategic,
executive‑ready language.

Always:
- Focus on financial impact, risks, and opportunities.
- Highlight trends, seasonal patterns, and anomalies.
- Provide concise, actionable recommendations for Marketing/Media, Creative, and Finance teams.
- Use metrics like Revenue, ROAS, CAC, CLV, Churn, and CRM Engagement.
- Write in a professional, boardroom‑ready tone.
"""

# -------------------------------
# EXECUTIVE QUESTIONS (UI)
# -------------------------------
SUGGESTIONS = {
    "💰 Total Revenue": "What was our total revenue last year? Break it down by month and key drivers.",
    "📈 Trends": "What trends stood out across media spend, CRM engagement, and conversions? Any seasonal patterns?",
    "💸 CAC & CLV": "How did our CAC and CLV evolve over the year? What does that mean for profitability?",
    "🎯 Next Quarter Focus": "Where should we focus next quarter? What are the biggest risks and opportunities?",
    "🧠 Recommendations": "Give me strategic recommendations for Marketing, CRM, and Finance teams based on last year’s performance."
}

selected_suggestion = st.selectbox("💬 Questions", options=[""] + list(SUGGESTIONS.values()))
user_question = st.text_input("Or type your own question:")

if selected_suggestion:
    query = selected_suggestion
elif user_question:
    query = user_question
else:
    query = None

# -------------------------------
# SAMPLE DATA GENERATION
# -------------------------------
@st.cache_data
def generate_enterprise_data():
    np.random.seed(42)
    months = pd.date_range(start="2024-10-01", periods=12, freq="MS").strftime("%b-%Y")

    campaigns = [
        "CC_Acq_YPro_Branded+Competitor_AlwaysOn",
        "CC_Acq_YPro_GenericLowFee+Rewards_Burst",
        "CC_Acq_YPro_GenericRewards_Sustain",
        "CC_Acq_YPro_Seasonal_PreHoliday_Burst",
        "PL_Acq_Students_VideoAwareness_AlwaysOn",
        "PL_Acq_Students_Reach+Engagement_Burst",
        "PL_Acq_Students_CreativeTest_Sustain",
        "PL_Acq_Students_Retargeting_Conversion",
        "MTG_Acq_Homeowners_Retargeting_AlwaysOn",
        "MTG_Acq_Homeowners_SequentialMessaging",
        "MTG_Acq_Homeowners_Awareness_Sustain",
        "MTG_Acq_Homeowners_CreativeRefresh_Burst"
    ]

    audiences = [
        "Young Professionals","Young Professionals","Young Professionals","Young Professionals",
        "Students","Students","Students","Students",
        "Homeowners","Homeowners","Homeowners","Homeowners"
    ]

    channels = ["Paid Search","Social","Display","Email","Video"]

    data = {
        "Month": months,
        "Audience Segment": audiences,
        "Campaign Name": campaigns,
        "Channel": np.random.choice(channels, size=12),
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

# -------------------------------
# AI INSIGHTS (OpenAI) with streaming
# -------------------------------
if query and api_key:
    with st.spinner("Analyzing with AI..."):
        stream = client.chat.completions.create(
            model="gpt-4o-mini",   # ✅ new client style
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
            if chunk.choices[0].delta.content:
                full_text += chunk.choices[0].delta.content
                placeholder.markdown(full_text)
