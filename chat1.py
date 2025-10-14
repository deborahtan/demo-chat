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
- When asked about diminishing returns, generate and plot a Streamlit‑ready Altair chart of Spend vs ROAS, with annotations for inflection points. Explain the modelling choice (e.g., logarithmic fit) and why it reflects saturation.
- When asked about publisher performance, compare across audience segments and quantify differences (e.g., “NZ Herald delivers 35% higher conversion for Millennials vs Stuff, which over‑indexes with Gen X”).
- Provide actionable recommendations: reallocations, testing frameworks, risk/impact analysis.
- Explicitly state reasoning, modelling decisions, and assumptions (e.g., why a certain publisher is favoured, how CAC is calculated, what external NZ market factors are considered).
- Anticipate follow‑up questions (e.g., “What if we shift 10% from TVNZ to Trade Me?”) and outline scenario‑based impacts.
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
                revenue = conversions * np.random.randint(50, 200)  # avg order value
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
    st.header("Controls")
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
    selected = st.selectbox("Executive Question", options=QUESTIONS, index=0)
    selected_audience = st.multiselect("Audience", ["Millennials","Gen X","Boomers"], default=["Millennials","Gen X","Boomers"])
    selected_publishers = st.multiselect("Publishers", ["NZ Herald","Stuff","TVNZ","MediaWorks","NZME Radio","Trade Me"], default=["NZ Herald","Stuff","TVNZ"])

# -------------------------------
# EXECUTIVE SUMMARY
# -------------------------------
with st.container():
    st.subheader("Executive Summary")
    col1, col2, col3 = st.columns(3, gap="large")

    with col1:
        roas_chart = alt.Chart(df).mark_line(point=True).encode(
            x="Spend ($)", y="ROAS", tooltip=["Month","Publisher","Audience","Spend ($)","ROAS"]
        ).properties(title="ROAS vs Spend")
        st.altair_chart(roas_chart, use_container_width=True)

    with col2:
        churn_df = df.groupby("Month")["Conversions"].sum().reset_index()
        churn_df["Churn (%)"] = np.random.uniform(2, 8, size=len(churn_df))
        churn_chart = alt.Chart(churn_df).mark_line(point=True).encode(
            x="Month", y="Churn (%)", tooltip=["Month","Churn (%)"]
        ).properties(title="Monthly Churn Trend")
        st.altair_chart(churn_chart, use_container_width=True)

    with col3:
        corr_chart = alt.Chart(df).mark_circle(size=60).encode(
            x="Revenue ($)", y="CLV ($)", color="Publisher", tooltip=["Month","Publisher","Audience","Revenue ($)","CLV ($)"]
        ).properties(title="Revenue vs CLV Correlation")
        st.altair_chart(corr_chart, use_container_width=True)

# -------------------------------
# AI OVERVIEW
# -------------------------------
with st.container():
    st.subheader("AI Overview")
    if client:
        with st.spinner("Generating executive overview..."):
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": "Provide a concise executive overview of current performance in the New Zealand market."}
                ]
            )
            overview = response.choices[0].message.content
        st.markdown(f"<div class='answer-card'>{overview}</div>", unsafe_allow_html=True)

# -------------------------------
# DETAILED ANSWER
# -------------------------------
with st.container():
    st.subheader("Detailed Answer")
    if selected and client:
        with st.spinner("Generating detailed structured answer..."):
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Provide a detailed structured answer (Insight → Action → Recommendation → Next Steps) for: {selected}, using the New Zealand dataset with publishers and audiences, and explicitly include reasoning, modelling decisions, and assumptions."}
                ]
            )
            detailed = response.choices[0].message.content
        st.markdown(f"<div class='answer-card'>{detailed}</div>", unsafe_allow_html=True)

        # Conditional charts depending on the question
        if "diminishing returns" in selected.lower():
            chart = alt.Chart(df).mark_line(point=True).encode(
                x="Spend ($)", y="ROAS",
                color="Publisher",
                tooltip=["Month","Publisher","Audience","Spend ($)","ROAS"]
            ).properties(title="Diminishing Returns: Spend vs ROAS by Publisher")
            st.altair_chart(chart, use_container_width=True)

        elif "publisher" in selected.lower():
            pub_chart = alt.Chart(df).mark_bar().encode(
                x="Publisher", y="Conversions", color="Audience",
                tooltip=["Publisher","Audience","Conversions","ROAS","CAC ($)"]
            ).properties(title="Publisher Performance by Audience Segment")
            st.altair_chart(pub_chart, use_container_width=True)

        elif "churn" in selected.lower():
            churn_df = df.groupby("Month")["Conversions"].sum().reset_index()
            churn_df["Churn (%)"] = np.random.uniform(2, 8, size=len(churn_df))
            churn_chart = alt.Chart(churn_df).mark_line(point=True).encode(
                x="Month", y="Churn (%)", tooltip=["Month","Churn (%)"]
            ).properties(title="Monthly Churn Trend")
            st.altair_chart(churn_chart, use_container_width=True)

        elif "roi and cpa" in selected.lower():
            formats = pd.DataFrame({
                "Format": ["Video","Display","Social","CTV"],
                "ROI": [3.2, 2.1, 2.8, 3.5],
                "CPA": [55, 40, 50, 45]
            })
            chart = alt.Chart(formats).mark_bar().encode(
                x="Format", y="ROI", tooltip=["Format","ROI","CPA"]
            ).properties(title="ROI by Format")
            st.altair_chart(chart, use_container_width=True)

        elif "click-to-conversion" in selected.lower():
            channels = pd.DataFrame({
                "Channel": ["Search","Social","CTV","Display"],
                "CVR (%)": [5.2, 3.8, 4.5, 2.9]
            })
            chart = alt.Chart(channels).mark_bar().encode(
                x="Channel", y="CVR (%)", tooltip=["Channel","CVR (%)"]
            ).properties(title="Click-to-Conversion Rate by Channel")
            st.altair_chart(chart, use_container_width=True)

# -------------------------------
# REFERENCE DICTIONARY
# -------------------------------
with st.container():
    st.subheader("Dimensions & Metrics Dictionary")
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
    df_dict = pd.DataFrame.from_dict(dims_metrics["Definitions"], orient="index", columns=["Definition"])
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
