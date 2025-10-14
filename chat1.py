import os
import streamlit as st
import pandas as pd
import numpy as np
from openai import OpenAI

# -------------------------------
# CONFIG & BRANDING
# -------------------------------
st.set_page_config(
    page_title="Strategic Intelligence Assistant",
    page_icon="https://img.icons8.com/ios11/16/000000/dashboard-gauge.png",  # professional favicon
    layout="wide"
)

# Custom theme using your palette
st.markdown("""
    <style>
        body {
            background-color: #000000;
            color: #fffefe;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #fffefe;
            font-weight: 600;
            border-bottom: none !important;
        }
        section.main > div {
            padding-top: 1rem;
            padding-bottom: 1rem;
        }
        .metric-card {
            background-color: #2e2e2e;
            border: 1px solid #7e7e7e;
            border-radius: 12px;
            padding: 18px;
            margin: 8px 0;
            text-align: center;
        }
        .metric-label {
            color: #b6b6b6;
            font-weight: 600;
            font-size: 13px;
            letter-spacing: 0.3px;
        }
        .metric-value {
            color: #cc1e27;
            font-size: 22px;
            font-weight: 700;
        }
        .answer-card {
            background-color: #0e4136;
            border: 1px solid #15395c;
            border-radius: 12px;
            padding: 20px;
            color: #f1efec;
        }
        .point-card {
            background-color: #2e2e2e;
            border-radius: 8px;
            padding: 10px 14px;
            margin: 6px 0;
            color: #f1efec;
            font-size: 15px;
            line-height: 1.4;
        }
        .point-card.internal {
            border-left: 4px solid #cc1e27;
        }
        .point-card.external {
            border-left: 4px solid #15395c;
        }
        .stButton>button {
            background-color: #cc1e27;
            color: #fffefe;
            border-radius: 6px;
            border: none;
            padding: 8px 16px;
            font-weight: 600;
        }
        .stButton>button:hover {
            background-color: #f1a4a5;
            color: #000000;
        }
        a.disclaimer {
            color: #f1a4a5;
            text-decoration: underline;
            font-size: 13px;
        }
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
- Identify top-performing creative messaging, targeting strategies, channels, publishers, formats, and audience segments.
- Recommend optimizations based on what worked and what underperformed; include risk/impact and effort levels.
- Analyze diminishing returns by channel and spend curve; flag thresholds where marginal ROI declines.
- Compare publisher performance by audience segment; include reach, frequency, and quality (post‑click) metrics.
- Evaluate online vs. offline CLV, attribution, and user journey paths; recommend journey‑level interventions.
- Recommend optimal channel mixes for different investment levels ($100M, $200M, $300M), with marginal ROI and risk scenarios.
- Identify months with highest churn; separate internal vs. external drivers; estimate revenue impact.
- Research and contextualize external market/economic factors; distinguish controllable vs. uncontrollable.
- Determine formats with highest ROI and CPA; balance efficiency vs. scale and creative fatigue risk.
- Highlight channels with highest click‑to‑conversion and CLV; avoid over‑indexing on low‑quality volume.
- Recommend what to scale, pause, or optimize for efficiency; include forecasted impact on EBITDA.

Interactive visualization (Streamlit):
- Generate Streamlit‑ready charts that are boardroom‑grade and interactive (hover tooltips show relevant metrics).
- Prefer Altair or Plotly for interactivity, tooltips, and responsive design; include clear titles, axis labels, and annotations.
- Provide code snippets ready to paste into a Streamlit app (st.altair_chart / st.plotly_chart); ensure hover tooltips expose metric values.

Evidence and reasoning:
- Draw from internal dataset (provided tables/fields) and enrich with external research/context (industry benchmarks, macroeconomic trends).
- Reference experiential knowledge across Media buying, Creative testing, CRM/Lifecycle, Loyalty programs, Product assortment, and Pricing/Promo.
- Clearly separate data‑driven findings vs. judgment calls; flag assumptions and confidence levels.

Follow‑up readiness:
- Anticipate C‑suite follow‑up questions (e.g., “What’s the ROI if we reallocate 10% from Meta to CTV?”).
- Provide scenario‑based insights and sensitivity analysis (best/base/worst).
- Offer next‑step instrumentation (tracking, experiments, governance) to operationalize recommendations.

Tone & delivery:
- Write in professional, boardroom‑ready language.
- Be concise, avoid jargon, and prioritize clarity and decision‑readiness.

Output structure per question:
1) Insight: What the data and context say (with numbers).
2) Action: Concrete moves teams can take now.
3) Recommendation: Strategic decision and rationale (financial impact, risks).
4) Next Steps: Implementation, owners, timeline, measurement (KPIs, guardrails).

When providing charts, include:
- Chart title, labeled axes, currency/units, and tooltip fields (e.g., Spend, Revenue, ROAS, CAC, CPA, CVR, CLV).
- Visual aids (benchmarks lines, thresholds, annotations for inflection points and anomalies).
- Accessibility defaults (high contrast color palette, legible fonts).
"""


# -------------------------------
# EXECUTIVE QUESTIONS
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
# SUMMARY + VISUALS
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
# EXECUTIVE ANSWER
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

    bullets = [line.strip("- ").strip() for line in answer.split("\n") if line.strip()]
    if not bullets:
        bullets = [line.strip("- ").strip() for line in answer.split(". ") if line.strip()]

    st.markdown("<div class='answer-card'>", unsafe_allow_html=True)
    for text in bullets:
        if "internal" in text.lower():
            st.markdown(f"<div class='point-card internal'>✅ {text}</div>", unsafe_allow_html=True)
        elif "external" in text.lower():
            st.markdown(f"<div class='point-card external'>🌍 {text}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='point-card'>{text}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Simple keyword frequency chart
    keywords = pd.Series(" ".join(answer.split()).split()).value_counts().head(10)
    st.subheader("AI-generated keyword frequency")
    st.bar_chart(keywords)

# -------------------------------
# EXPANDABLE: Dimensions & metrics dictionary
# -------------------------------
st.divider()
with st.expander("Dimensions & metrics dictionary"):
    dims_metrics = {
        "Dimensions": [
            "Month", "Campaign Name", "Audience Segment", "Channel",
            "Publisher", "Format", "Targeting Strategy", "Creative Messaging"
        ],
        "Core metrics": [
            "Revenue ($)", "Media Spend ($)", "ROAS", "CLV ($)"
        ],
        "Additional enterprise metrics": [
            "CAC ($)", "Churn (%)", "CRM Emails Sent", "CRM Open Rate (%)",
            "Leads Generated", "Conversions", "Conversion Rate (%)", "CRM Engagements",
            "Retention Rate (%)", "Repeat Purchase Rate (%)", "AOV ($)"
        ],
        "Definitions": {
            "Creative Messaging": "The specific advertising message, theme, or concept shown to an audience. Examples include value‑driven offers, urgency messaging, lifestyle positioning, or brand storytelling.",
            "CAC ($)": "Customer Acquisition Cost — total marketing spend divided by new customers acquired.",
            "CLV ($)": "Customer Lifetime Value — projected net revenue from a customer over their relationship with the company.",
            "ROAS": "Return on Ad Spend — Revenue divided by Media Spend.",
            "Churn (%)": "Percentage of customers lost over a given period.",
            "AOV ($)": "Average Order Value — total revenue divided by number of orders."
        },
        "Notes": [
            "ROAS = Revenue / Media Spend",
            "Monthly CLV shown for trend illustration; production views use cohort CLV",
            "Extend dictionary to match your GA4/GMP/CRM schema",
            "Include both online and offline CLV where possible",
            "Ensure consistency of metric definitions across Finance, Marketing, and CRM teams"
        ]
    }

    # Display dictionary nicely
    st.json(dims_metrics)
