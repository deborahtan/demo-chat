import streamlit as st
import pandas as pd
import numpy as np

# -------------------------------
# CONFIG
# -------------------------------
st.set_page_config(page_title="C-Suite Marketing & CRM Insights", layout="wide")

st.title("📊 C-Suite Marketing & CRM Insights Assistant")

# -------------------------------
# SUGGESTED QUESTIONS
# -------------------------------
SUGGESTIONS = {
    ":blue[:material/insights:] What was our total revenue last year?": (
        "What was our total revenue last year? Can you break it down by month and highlight key drivers?"
    ),
    ":green[:material/trending_up:] What trends stood out across media and CRM?": (
        "What trends stood out across media spend, CRM engagement, and conversions? Any seasonal patterns?"
    ),
    ":orange[:material/compare:] How did CAC and CLV evolve?": (
        "How did our CAC and CLV evolve over the year? What does that mean for profitability?"
    ),
    ":violet[:material/priority:] Where should we focus next quarter?": (
        "Where should we focus next quarter? What are the biggest risks and opportunities?"
    ),
    ":red[:material/strategy:] Strategic recommendations for teams": (
        "Give me strategic recommendations for marketing, CRM, and finance teams based on last year's performance."
    ),
}

selected_suggestion = st.selectbox("💬 Executive Questions", options=[""] + list(SUGGESTIONS.values()))
if selected_suggestion:
    st.info(f"**{selected_suggestion}**")

# -------------------------------
# DATA GENERATION
# -------------------------------
@st.cache_data
def generate_enterprise_data():
    np.random.seed(42)
    months = pd.date_range(start="2024-10-01", periods=12, freq="MS").strftime("%b-%Y")

    data = {
        "Month": months,
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
# INSIGHT EXTRACTION
# -------------------------------
def extract_summary(df):
    return {
        "Total Revenue": f"${df['Revenue ($)'].sum():,.0f}",
        "Total Spend": f"${df['Media Spend ($)'].sum():,.0f}",
        "Average ROAS": round(df["ROAS"].mean(), 2),
        "Average CAC": f"${df['CAC ($)'].mean():,.2f}",
        "Average CLV": f"${df['CLV ($)'].mean():,.2f}",
        "Best Month (ROAS)": df.loc[df["ROAS"].idxmax(), "Month"],
        "Worst Month (Churn)": df.loc[df["Customer Churn (%)"].idxmax(), "Month"],
        "CRM Engagement Peak": df.loc[df["CRM Engagements"].idxmax(), "Month"],
    }

summary = extract_summary(df)

# -------------------------------
# STRATEGIC RECOMMENDATIONS
# -------------------------------
def generate_recommendations(df):
    recs = []
    if df["ROAS"].mean() < 10:
        recs.append("📉 ROAS is below optimal. Reallocate spend to high-performing channels.")
    if df["CAC ($)"].mean() > 100:
        recs.append("💸 CAC is elevated. Optimize acquisition and refine lead scoring.")
    if df["CLV ($)"].mean() < 1000:
        recs.append("📦 CLV is low. Explore upsell/cross-sell and loyalty strategies.")
    if df["Customer Churn (%)"].max() > 6:
        recs.append("⚠️ High churn detected. Reinforce onboarding and retention programs.")
    if df["CRM Open Rate (%)"].mean() < 20:
        recs.append("📬 CRM engagement is weak. Test new subject lines and segmentation.")
    return recs

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

st.subheader("🧠 Strategic Recommendations")
for rec in generate_recommendations(df):
    st.markdown(f"- {rec}")
