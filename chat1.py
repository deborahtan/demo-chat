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
You are an AI Insights Assistant for C‑suite executives in Marketing, Media, Creative, CRM, Finance, and Loyalty/Product.
Your role is to analyze enterprise‑scale performance data and deliver clear, strategic, executive‑ready insights and interactive visualizations.

Core responsibilities:
- Structure every response as Insight → Action → Recommendation → Next Steps.
- Focus on financial impact, risks, and opportunities; quantify upside/downside where possible.
- Highlight trends, seasonal patterns, anomalies, and diminishing returns curves.
- Provide concise, actionable recommendations tailored to Marketing/Media, Creative, CRM/Loyalty, and Finance teams.
- Use key metrics: Revenue, ROAS, CAC, CLV (online/offline), Churn, CRM Engagement, AOV, CPC, CPA, Conversion Rate, Retention, and Repeat Rate.
- When asked about diminishing returns, always generate a sample dataset and a Streamlit‑ready Altair chart showing the spend vs. ROI curve, with annotations for inflection points.

Interactive visualization (Streamlit):
- Generate Streamlit‑ready charts that are boardroom‑grade and interactive (hover tooltips show relevant metrics).
- Prefer Altair or Plotly for interactivity, tooltips, and responsive design; include clear titles, axis labels, and annotations.
"""

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
    df["Churn (%)"] = np.random.uniform(2, 8, size=len(df))
    return df

df = generate_data()

# -------------------------------
# EXECUTIVE SUMMARY (3 charts)
# -------------------------------
st.header("Executive Summary")

col1, col2, col3 = st.columns(3)

with col1:
    roas_chart = alt.Chart(df).mark_line(point=True).encode(
        x="Media Spend ($)", y="ROAS",
        tooltip=["Month","Media Spend ($)","ROAS"]
    ).properties(title="ROAS vs Media Spend")
    st.altair_chart(roas_chart, use_container_width=True)

with col2:
    churn_chart = alt.Chart(df).mark_line(point=True).encode(
        x="Month", y="Churn (%)",
        tooltip=["Month","Churn (%)"]
    ).properties(title="Monthly Churn Trend")
    st.altair_chart(churn_chart, use_container_width=True)

with col3:
    corr_chart = alt.Chart(df).mark_circle(size=80).encode(
        x="Revenue ($)", y="CLV ($)",
        tooltip=["Month","Revenue ($)","CLV ($)"]
    ).properties(title="Revenue vs CLV Correlation")
    st.altair_chart(corr_chart, use_container_width=True)

# -------------------------------
# AI OVERVIEW
# -------------------------------
st.header("AI Overview")
if client:
    with st.spinner("Generating executive overview..."):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "Provide a concise executive overview of current performance."}
            ]
        )
        overview = response.choices[0].message.content
    st.markdown(f"<div class='answer-card'>{overview}</div>", unsafe_allow_html=True)

# -------------------------------
# DETAILED ANSWER
# -------------------------------
st.header("Detailed Answer")
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

if selected and client:
    with st.spinner("Generating detailed structured answer..."):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Provide a detailed structured answer (Insight → Action → Recommendation → Next Steps) for: {selected}"}
            ]
        )
        detailed = response.choices[0].message.content
    st.markdown(f"<div class='answer-card'>{detailed}</div>", unsafe_allow_html=True)

    # Add relevant chart
    if "diminishing returns" in selected.lower():
        chart = alt.Chart(df).mark_line(point=True).encode(
            x="Media Spend ($)", y="ROAS",
            tooltip=["Month","Media Spend ($)","ROAS"]
        ).properties(title="Diminishing Returns: Spend vs ROAS")
        st.altair_chart(chart, use_container_width=True)

    elif "churn" in selected.lower():
        chart = alt.Chart(df).mark_line(point=True).encode(
            x="Month", y="Churn (%)",
            tooltip=["Month","Churn (%)"]
        ).properties(title="Monthly Churn Trend")
        st.altair_chart(chart, use_container_width=True)

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
st.header("Dimensions & Metrics Dictionary")
dims_metrics = {
    "Definitions": {
        "Revenue ($)": "Total income generated from sales.",
        "Media Spend ($)": "Total advertising expenditure.",
        "ROAS": "Return on Ad Spend = Revenue / Media Spend.",
        "CLV ($)": "Customer Lifetime Value — projected net revenue from a customer over their relationship.",
        "CAC ($)": "Customer Acquisition Cost — marketing spend divided by new customers acquired.",
        "Churn (%)": "Percentage of customers lost over a given period.",
        "CRM Engagement": "Interactions with CRM campaigns (opens, clicks, conversions).",
        "AOV ($)": "Average Order Value — total revenue divided by number of orders.",
        "Retention Rate (%)": "Percentage of customers retained over a given period.",
        "Repeat Purchase Rate (%)": "Percentage of customers making repeat purchases."
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
