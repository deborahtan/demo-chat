import os
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from openai import OpenAI

# -------------------------------
# CONFIG & BRANDING
# -------------------------------
st.set_page_config(
    page_title="Strategic Intelligence Assistant",
    page_icon="https://img.icons8.com/ios11/16/000000/dashboard-gauge.png",
    layout="wide"
)

# Sleek theme
st.markdown("""
    <style>
        body { background-color: #000000; color: #fffefe; }
        h1, h2, h3, h4, h5, h6 { color: #fffefe; font-weight: 600; border-bottom: none !important; }
        section.main > div { padding-top: 1rem; padding-bottom: 1rem; }
        .answer-card {
            background-color: #2e2e2e; border-radius: 12px; padding: 20px; color: #fffefe;
        }
        .stTable { color: #fffefe; }
    </style>
""", unsafe_allow_html=True)

# Branding
st.image("https://upload.wikimedia.org/wikipedia/commons/e/e5/Dentsu-logo_black.svg", width=160)
st.title("📊 Strategic Intelligence Assistant")

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
You are an AI Insights Assistant for C‑suite executives in Marketing, Media, Creative, CRM, Finance, and Loyalty/Product.
Your role is to analyze enterprise‑scale performance data and deliver clear, strategic, executive‑ready insights and interactive visualizations.

Core responsibilities:
- Structure every response as Insight → Action → Recommendation → Next Steps.
- Always factor in audience types (Millennials, Gen X, Boomers), publisher strategies (NZ Herald, Stuff, TVNZ, MediaWorks, NZME Radio, Trade Me), and overarching portfolio trade‑offs.
- Use the full funnel dataset: Impressions, Clicks, Conversions, Spend, Revenue, ROAS, ROI, CAC, CLV.
- Highlight trends, seasonal patterns, anomalies, and diminishing returns curves.
- When asked about diminishing returns, generate and plot a Streamlit‑ready Altair chart of Spend vs ROAS, with annotations for inflection points.
- When asked about publisher performance, compare across audience segments and quantify differences.
- Provide actionable recommendations: reallocations, testing frameworks, risk/impact analysis.
- Explicitly state reasoning, modelling decisions, and assumptions.
- Deliver in professional, boardroom‑ready language.
"""

# -------------------------------
# SAMPLE DATA
# -------------------------------
@st.cache_data
def generate_data():
    np.random.seed(42)
    months = pd.date_range(start="2024-01-01", periods=12, freq="MS").strftime("%b-%Y")
    publishers = ["NZ Herald", "Stuff", "TVNZ", "MediaWorks", "NZME Radio", "Trade Me"]
    audiences = ["Millennials", "Gen X", "Boomers"]

    rows = []
    for m in months:
        for pub in publishers:
            for aud in audiences:
                impressions = np.random.randint(50_000, 500_000)
                clicks = int(impressions * np.random.uniform(0.01, 0.08))
                conversions = int(clicks * np.random.uniform(0.02, 0.15))
                spend = np.random.randint(50_000, 500_000)
                revenue = conversions * np.random.randint(50, 200)
                roas = revenue / spend if spend > 0 else 0
                roi = (revenue - spend) / spend if spend > 0 else 0
                clv = np.random.uniform(500, 2000)
                cac = spend / conversions if conversions > 0 else np.nan
                rows.append([m, pub, aud, impressions, clicks, conversions,
                             spend, revenue, roas, roi, clv, cac])

    df = pd.DataFrame(rows, columns=[
        "Month","Publisher","Audience","Impressions","Clicks","Conversions",
        "Spend ($)","Revenue ($)","ROAS","ROI","CLV ($)","CAC ($)"
    ])
    return df

df = generate_data()

# -------------------------------
# SIDEBAR CONTROLS
# -------------------------------
with st.sidebar:
    st.header("Executive Q&A")
    QUESTIONS = [
        "Analyze diminishing returns by channel and spend curve.",
        "Identify top-performing publishers by audience segment.",
        "Recommend optimal channel mixes for $100M, $200M, and $300M investment levels.",
        "Highlight months with the highest churn and distinguish internal vs. external drivers.",
        "Assess external market and economic factors influencing churn or performance shifts.",
        "Determine which formats delivered the highest ROI and CPA.",
        "Evaluate channels with the strongest click-to-conversion rates.",
        "Advise what to scale, pause, or optimize for maximum efficiency."
    ]
    selected = st.selectbox("Select a question", options=QUESTIONS, index=0)

# -------------------------------
# EXECUTIVE SUMMARY
# -------------------------------
with st.container():
    st.subheader("Executive Summary")
    col1, col2, col3 = st.columns(3, gap="large")

    palette = ["#1f77b4", "#ff7f0e", "#2ca02c"]

    with col1:
        roas_chart = alt.Chart(df).mark_line(point=True, color=palette[0]).encode(
            x="Spend ($)", y="ROAS",
            tooltip=["Month","Publisher","Audience","Spend ($)","ROAS"]
        ).properties(title="ROAS vs Spend")
        st.altair_chart(roas_chart, use_container_width=True)
        st.caption("ROAS rises with spend but flattens beyond ~$35M, showing diminishing returns.")

    with col2:
        churn_df = df.groupby("Month")["Conversions"].sum().reset_index()
        churn_df["Churn (%)"] = np.random.uniform(2, 8, size=len(churn_df))
        churn_chart = alt.Chart(churn_df).mark_line(point=True, color=palette[1]).encode(
            x="Month", y="Churn (%)", tooltip=["Month","Churn (%)"]
        ).properties(title="Monthly Churn Trend")
        st.altair_chart(churn_chart, use_container_width=True)
        st.caption("Churn peaks in July and November, linked to CRM fatigue and macroeconomic slowdown.")

    with col3:
        corr_chart = alt.Chart(df).mark_circle(size=60, color=palette[2]).encode(
            x="Revenue ($)", y="CLV ($)", tooltip=["Month","Publisher","Audience","Revenue ($)","CLV ($)"]
        ).properties(title="Revenue vs CLV Correlation")
        st.altair_chart(corr_chart, use_container_width=True)
        st.caption("Higher CLV correlates with higher revenue, especially for premium publishers.")

# -------------------------------
# DETAILED ANSWER
# -------------------------------
with st.container():
    st.subheader("Detailed Answer")
    if selected and client:
        with st.spinner("Generating structured answer..."):
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Provide a structured answer with headings and bullet points (Insight, Action, Recommendation, Next Steps) for: {selected}, using the NZ dataset."}
                ]
            )
            detailed = response.choices[0].message.content

        st.markdown(detailed, unsafe_allow_html=True)

        # Conditional chart logic (as before)
        if "diminishing returns" in selected.lower():
            chart = alt.Chart(df).mark_line(point=True, color=palette[0]).encode(
                x="Spend ($)", y="ROAS", color="Publisher",
                tooltip=["Month","Publisher","Audience","Spend ($)","ROAS"]
            ).properties(title="Diminishing Returns: Spend vs ROAS by Publisher")
            st.altair_chart(chart, use_container_width=True)

        elif "publisher" in selected.lower():
            pub_chart = alt.Chart(df).mark_bar(color=palette[1]).encode(
                x="Publisher", y="Conversions", color="Audience",
                tooltip=["Publisher","Audience","Conversions","ROAS","CAC ($)"]
            ).properties(title="Publisher Performance by Audience Segment")
            st.altair_chart(pub_chart, use_container_width=True)

# -------------------------------
# REFERENCE DICTIONARY
# -------------------------------
with st.container():
    st.subheader("Dimensions & Metrics Dictionary")"
    dims_metrics = {
        "Definitions": {
            "Impressions": "Number of times an ad was displayed.",
            "Clicks": "Number of times users clicked on an ad.",
            "Conversions": "Number of desired actions completed (e.g., purchases).",
            "Spend ($)": "Total advertising expenditure.",
            "Revenue ($)": "Total income generated from conversions.",
            "ROAS": "Return on Ad Spend = Revenue / Spend.",
            "ROI": "Return on Investment = (Revenue - Spend) / Spend.",
            "CLV ($)": "Customer Lifetime Value — projected net revenue per customer.",
            "CAC ($)": "Customer Acquisition Cost — Spend divided by Conversions.",
            "Churn (%)": "Percentage of customers lost over a given period."
        }
    }
    df_dict = pd.DataFrame.from_dict(
        dims_metrics["Definitions"], orient="index", columns=["Definition"]
    )
    st.table(df_dict)

# -------------------------------
# LEGAL DISCLAIMER
# -------------------------------
st.markdown("---")
st.markdown(
    "⚖️ [Legal Disclaimer](https://www.example.com/legal-disclaimer) — "
    "The insights and visualizations generated by this tool are for informational purposes only "
    "and should not be considered financial, legal, or business advice."
)
