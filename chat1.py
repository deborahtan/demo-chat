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

# Custom theme
st.markdown("""
    <style>
        body { background-color: #000000; color: #fffefe; }
        h1, h2, h3, h4, h5, h6 { color: #fffefe; font-weight: 600; border-bottom: none !important; }
        section.main > div { padding-top: 1rem; padding-bottom: 1rem; }
        .metric-card {
            background-color: #2e2e2e; border-radius: 12px; padding: 18px; margin: 8px 0; text-align: center;
        }
        .metric-label { color: #b6b6b6; font-weight: 600; font-size: 13px; }
        .metric-value { font-size: 22px; font-weight: 700; }
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
system_prompt = """<-- your long detailed system_prompt from above goes here -->"""

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
# EXECUTIVE SUMMARY
# -------------------------------
st.header("Executive Summary")

def trend_arrow(current, previous, higher_is_better=True):
    if current > previous:
        return "▲", "green" if higher_is_better else "red"
    elif current < previous:
        return "▼", "red" if higher_is_better else "green"
    else:
        return "→", "white"

summary = {
    "Total Revenue": df["Revenue ($)"].sum(),
    "Total Spend": df["Media Spend ($)"].sum(),
    "Average ROAS": df["ROAS"].mean(),
    "Average CLV": df["CLV ($)"].mean(),
}

cols = st.columns(len(summary))
for i, (k, v) in enumerate(summary.items()):
    prev = df.iloc[-2][df.columns[i+1]] if len(df) > 1 and i < len(df.columns)-1 else v
    arrow, color = trend_arrow(v, prev, higher_is_better=True)
    with cols[i]:
        st.markdown(
            f"<div class='metric-card'><div class='metric-label'>{k}</div>"
            f"<div class='metric-value' style='color:{color}'>{v:,.2f} {arrow}</div></div>",
            unsafe_allow_html=True
        )

# Top-level graphs
roas_chart = alt.Chart(df).mark_line(point=True).encode(
    x="Media Spend ($)", y="ROAS", tooltip=["Month","Media Spend ($)","ROAS"]
).properties(title="ROAS vs Media Spend")
st.altair_chart(roas_chart, use_container_width=True)

churn_chart = alt.Chart(df).mark_line(point=True).encode(
    x="Month", y="Churn (%)", tooltip=["Month","Churn (%)"]
).properties(title="Monthly Churn Trend")
st.altair_chart(churn_chart, use_container_width=True)

channels = pd.DataFrame({
    "Channel": ["Search","Social","CTV","Display"],
    "Spend": [40,30,20,10]
})
pie = alt.Chart(channels).mark_arc().encode(
    theta="Spend", color="Channel", tooltip=["Channel","Spend"]
).properties(title="Channel Mix (Spend Share)")
st.altair_chart(pie, use_container_width=True)

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

# -------------------------------
# REFERENCE DICTIONARY
# -------------------------------
st.header("Dimensions & Metrics Dictionary")
dims_metrics = {
    "Definitions": {
        "Revenue ($)": "Total income generated from sales.",
        "Media Spend ($)": "Total advertising expenditure.",
        "ROAS": "Return on Ad Spend = Revenue / Media Spend.",
        "CLV ($)": "Customer Lifetime Value.",
        "CAC ($)": "Customer Acquisition Cost.",
        "Churn (%)": "Percentage of customers lost.",
        "CRM Engagement": "Interactions with CRM campaigns.",
        "AOV ($)": "Average Order Value.",
        "Retention Rate (%)": "Percentage of customers retained.",
        "Repeat Purchase Rate (%)": "Percentage of customers making repeat purchases."
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
    "The insights and visualizations generated by this tool are for informational purposes only and "
    "should not be considered financial, legal, or business advice."
)
