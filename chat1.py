import os
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from groq import Groq 

# -------------------------------
# CONFIG & BRANDING
# -------------------------------
st.set_page_config(
    page_title="Dentsu Intelligence Assistant",
    page_icon="https://img.icons8.com/ios11/16/000000/dashboard-gauge.png",
    layout="wide"
)

# Apply global styling
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            background-color: #000000;
            color: #fffefe;
        }

        h1, h2, h3, h4, h5, h6 {
            font-weight: 600;
            color: #fffefe;
        }

        section.main > div {
            padding-top: 1rem;
            padding-bottom: 1rem;
        }

        .answer-card {
            background-color: #2e2e2e;
            border-radius: 12px;
            padding: 20px;
            color: #fffefe;
        }

        .stTable {
            color: #fffefe;
        }

        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background-color: #000000;
            color: #fffefe;
        }

        [data-testid="stSidebar"] .stMarkdown,
        [data-testid="stSidebar"] .stTextInput,
        [data-testid="stSidebar"] .stSelectbox,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] .stButton,
        [data-testid="stSidebar"] .stHeader {
            color: #fffefe !important;
            font-family: 'Inter', sans-serif;
        }

        /* Recent Questions buttons */
        [data-testid="stSidebar"] button,
        [data-testid="stSidebar"] .stButton button {
            color: #000000 !important;
            background-color: #ffffff !important;
            border-radius: 6px;
            font-weight: 600;
        }
    </style>
""", unsafe_allow_html=True)

# Sidebar logo
with st.sidebar:
    st.image("https://www.dentsu.com/assets/images/main-logo-alt.png", width=160)

# Page title
st.title("Dentsu Intelligence Assistant")

# -------------------------------
# API KEY
# -------------------------------
api_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")

if not api_key:
    st.error("🚫 GROQ_API_KEY not found. Please set it in your environment or Streamlit secrets.")
    st.stop()

client = Groq(api_key=api_key)

# -------------------------------
# SYSTEM PROMPT
# -------------------------------
system_prompt = """
You are an AI Insights Assistant for C‑suite executives across Marketing, Media, Creative, CRM, Finance, and Loyalty/Product. Your mandate is to analyze enterprise‑scale performance data and deliver clear, strategic, executive‑ready insights supported by interactive visualizations.

Your responses must follow this structure:
- **Insight** 🧠: A precise, data-driven finding (trend, anomaly, comparison, or opportunity). Include timeframe and relevant metrics.
- **Action** 🎯: A specific, clickable operational step. Make it easy to follow up with a deeper question or next move.
- **Recommendation** 📈: A strategic decision with rationale, financial impact, and trade-offs. Tailor it to relevant channels or campaigns.
- When analyzing paid search, include performance breakdowns by category, product, and message. Reference real examples such as:
  • "Kitchen Appliances generated $19.9K revenue from 78 purchases — recommend increasing budget allocation."  
  • "Promotional ad extensions for De'Longhi and Simon Lewis drove 312K impressions — continue testing product-level relevance."  
  • "CTR uplift of 13% and CPC drop led to 8% more clicks at steady budget — maintain current investment level."

- When evaluating creative performance, highlight standout variants and their contribution to revenue and efficiency:
  • "The 'Earn' creative drove 73% of total revenue with CTR of 2.46% and ROAS of $5.07 — scale across Advantage+."  
  • "High Touch 1PD audiences delivered 152 remarketing transactions with ROAS of $14.14 and CPA of $19.99 — well below $100 benchmark."

- When referencing platform performance, include channel-level insights and strategic implications:
  • "Meta continues to outperform benchmarks across visibility and conversion — recommend continued investment and refreshed catalogue rollout."  
  • "Search ROAS at 8.86 with $353K revenue — maintain budget and monitor TAPM vs EAPM allocation."
  
- **Next Steps** 🛠️: Clear owners, timelines, and measurable outcomes.

Always include:
- **Charts** to reflect the question that was asked. Use 2025 data only. Include relevant **timeframes** in all charts and insights. Explain ALL key datapoints with summaries. If asked which format performs best, visualize all format performance.
- **Summarized tables**: Group data by relevant dimensions (e.g. Publisher, Audience, Month, Format) to make insights digestible. Avoid line-by-line raw tables unless explicitly requested.
- A dedicated **Evidence & Reasoning** 📊 section that explains how the insight was derived, what assumptions were made, and what confidence level applies.
- **Creative, targeting, messaging, and strategy data** where applicable — especially when analyzing campaign performance.
- **Internal and external factors** (e.g. market trends, economic shifts, competitor moves) based on recent research. Reference these when explaining performance changes or churn.
- **CX diagnostics**: When analyzing churn, include Net Promoter Score (NPS) and Customer Satisfaction (CSAT) metrics for the top 3 churn months to identify internal experience drivers.
- **Specific recommendations**: Be precise. If budget should be reallocated, explain where and why. If action is needed, define what, who, and how — not just vague monitoring advice.
- "Advise what to scale, pause, or optimize for maximum efficiency — including platforms, formats, and creative variants (messages, visuals, calls-to-action)."

Core responsibilities:
- Structure every response in the framework: Insight → Action → Recommendation → Next Steps.
- Ensure each element is specific, evidence‑based, and valid:
  • Insight = A precise finding from the data (with metrics, trends, anomalies, or quantified comparisons).  
  • **Action** 🎯: A specific, clickable operational step. Format each Action as a hyperlink that auto-populates a follow-up prompt and triggers a new insight using that prompt. Actions must include channel-level recommendations (e.g. Sponsored Posts on Meta), targeting adjustments (e.g. LinkedIn audience filters), creative guidance (e.g. message, visual, CTA variants), and strategic rationale tied to ROI, CPA, or CLV improvements. 
  • Recommendation = A strategic decision with rationale, financial impact, and risk/benefit trade‑offs - media, creative, strategic, messaging included.  
  • Evidence & Assumptions = In own category assuming about the data, with a confidence interval
 
- Always account for:
  • Audience cohorts (Millennials, Gen X, Boomers)  
  • Global platforms: Meta, TikTok, YouTube, Google Search/Display, LinkedIn, Snapchat  
  • Local publishers: NZ Herald, Stuff, TVNZ, MediaWorks, NZME Radio, Trade Me  
  • Performance/content partners: We Are Frank, Taboola, and other relevant publishers  
  • Portfolio‑level trade‑offs and opportunity costs  
  • Strategic & tactical thinking

- Leverage the full‑funnel dataset: Creative, Targeting, Strategy, Impressions, Clicks, Conversions, Spend, Revenue, ROAS, ROI, CAC, CLV.
- Identify and explain: trends, seasonal patterns, anomalies, and diminishing returns curves.
- When analyzing diminishing returns, generate a Streamlit‑ready Altair chart of Spend vs. ROAS by Channel or Month, with hover tooltips for Spend, Revenue, ROAS, and CAC. Highlight inflection points where ROAS declines.
- When evaluating publisher or platform performance, compare across audience segments, quantify differences, and highlight impact.
- For Creative insights, frame findings through A/B testing results and key performance trends:
  • Identify winning vs. underperforming variants  
  • Highlight message, format, and visual elements that drive higher CTR, CVR, or CLV  
  • Recommend next creative tests and scaling strategies

- Provide actionable recommendations including: budget reallocations, testing frameworks, risk/impact assessments, and scenario planning.
- Explicitly state reasoning, modelling choices, and assumptions; flag confidence levels where appropriate.
- Anticipate likely C‑suite follow‑up questions (ROI sensitivity, scalability, risk exposure, competitive benchmarks) and prepare concise, data‑driven responses.
- Deliver all outputs in professional, concise, boardroom‑ready language that supports decision‑making.

- Always phrase outputs in stakeholder-facing language. Do not mention technical tools or implementation details (e.g. Streamlit, Altair, Python). Focus on business impact, strategic clarity, and executive relevance.

Your goal: transform complex performance data into specific insights, valid actions, and strategically grounded recommendations that drive executive confidence and measurable results.
"""

# -------------------------------
# SAMPLE DATA
# -------------------------------
@st.cache_data
def generate_data():
    np.random.seed(42)
    # Generate months from Oct 2024 to Sep 2025 as datetime objects
    months = pd.date_range(end="2025-09-30", periods=12, freq="MS")
    publishers = ["NZ Herald", "Stuff", "TVNZ", "MediaWorks", "NZME Radio", "Trade Me"]
    audiences = ["Millennials", "Gen X", "Boomers"]
    creatives = ["Video", "Carousel", "Static Image", "Interactive"]
    targeting_strategies = ["Behavioral", "Contextual", "Demographic", "Lookalike"]
    messaging_themes = ["Value-driven", "Urgency", "Emotional Appeal", "Product Benefits"]
    strategic_objectives = ["Acquisition", "Retention", "Upsell", "Reactivation"]

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
                creative = np.random.choice(creatives)
                targeting = np.random.choice(targeting_strategies)
                messaging = np.random.choice(messaging_themes)
                strategy = np.random.choice(strategic_objectives)

                rows.append([
                    m, pub, aud, impressions, clicks, conversions,
                    spend, revenue, roas, roi, clv, cac,
                    creative, targeting, messaging, strategy
                ])

    df = pd.DataFrame(rows, columns=[
        "Month", "Publisher", "Audience", "Impressions", "Clicks", "Conversions",
        "Spend ($)", "Revenue ($)", "ROAS", "ROI", "CLV ($)", "CAC ($)",
        "Creative Format", "Targeting Strategy", "Messaging Theme", "Strategic Objective"
    ])

    # Ensure Month is datetime for charting
    df["Month"] = pd.to_datetime(df["Month"])

    return df


df = generate_data()

# -------------------------------
# SIDEBAR CONTROLS
# -------------------------------
if "recent_questions" not in st.session_state:
    st.session_state.recent_questions = []

with st.sidebar:
    st.header("Executive Q&A")

    st.markdown(
        """
        **Instructions**  
        - Select one of the predefined strategic questions from the dropdown.  
        - Or type your own custom question in the text box below.  
        - The assistant will generate structured insights (Insight to Action/Recommendation) and relevant charts.  
        - Your recent questions will appear below for quick re‑selection.  
        """
    )

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

    selected = st.selectbox("Select a predefined question:", options=QUESTIONS, index=0)
    custom_question = st.text_area("Or type your own question:")

    question_to_answer = custom_question.strip() if custom_question.strip() else selected

    if question_to_answer and question_to_answer not in st.session_state.recent_questions:
        st.session_state.recent_questions.insert(0, question_to_answer)
        st.session_state.recent_questions = st.session_state.recent_questions[:5]

    if st.session_state.recent_questions:
        st.markdown("**Recent Questions**")
        for q in st.session_state.recent_questions:
            if st.button(q, key=f"recent_{q}"):
                question_to_answer = q
        if st.button("🗑️ Clear History"):
            st.session_state.recent_questions = []

# -------------------------------
# DETAILED ANSWER
# -------------------------------
def render_chart_for_question(question, df):
    question = question.lower()

    try:
        if "diminishing returns" in question:
            channels = ["Search", "Social", "CTV", "Display"]
            df_channels = pd.DataFrame({
                "Channel": np.repeat(channels, 10),
                "Spend ($)": np.tile(np.linspace(1e6, 50e6, 10), len(channels)),
                "ROAS": np.concatenate([
                    5 - 0.00000005*np.linspace(1e6, 50e6, 10),
                    4 - 0.00000007*np.linspace(1e6, 50e6, 10),
                    6 - 0.00000004*np.linspace(1e6, 50e6, 10),
                    3 - 0.00000006*np.linspace(1e6, 50e6, 10)
                ])
            })
            chart = alt.Chart(df_channels).mark_line(point=True).encode(
                x="Spend ($)", y="ROAS", color="Channel",
                tooltip=["Channel", "Spend ($)", "ROAS"]
            ).properties(title="Diminishing Returns: Spend vs ROAS by Channel")
            st.altair_chart(chart, use_container_width=True)
            st.caption("Each channel shows a flattening ROAS curve as spend increases, highlighting saturation points.")
            st.dataframe(df_channels)

        elif "publisher" in question:
            cols = ["Publisher", "Audience"]
            metrics = {
                "Conversions": "sum",
                "Spend ($)": "sum",
                "Revenue ($)": "sum",
                "ROAS": "mean",
                "CAC ($)": "mean"
            }
            valid_metrics = {k: v for k, v in metrics.items() if k in df.columns}
            summary = df.groupby(cols).agg(valid_metrics).reset_index()
            chart = alt.Chart(summary).mark_bar().encode(
                x="Publisher", y="Conversions", color="Audience",
                tooltip=[col for col in summary.columns if col not in cols]
            ).properties(title="Publisher Performance by Audience Segment")
            st.altair_chart(chart, use_container_width=True)
            st.caption("Audience-level performance across publishers reveals strategic strengths and gaps.")
            st.dataframe(summary)

        elif "churn" in question:
            metrics = {
                "Conversions": "sum",
                "NPS": "mean",
                "CSAT (%)": "mean",
                "Unsubscribe Rate (%)": "mean"
            }
            valid_metrics = {k: v for k, v in metrics.items() if k in df.columns}
            if "Month" in df.columns:
                churn_df = df.groupby("Month").agg(valid_metrics).reset_index()
                churn_df["Churn (%)"] = np.random.uniform(2, 8, size=len(churn_df))
                chart = alt.Chart(churn_df).mark_line(point=True).encode(
                    x="Month", y="Churn (%)",
                    tooltip=[col for col in churn_df.columns if col != "Churn (%)"]
                ).properties(title="Monthly Churn Trend with CX Diagnostics")
                st.altair_chart(chart, use_container_width=True)
                st.caption("CX metrics help diagnose internal churn drivers. Lower NPS and CSAT often correlate with higher churn.")
                st.dataframe(churn_df)
            else:
                st.warning("There was an error, please try again.")

        elif "roi and cpa" in question:
            group_col = "Creative Format"
            metrics = {
                "Spend ($)": "sum",
                "Revenue ($)": "sum",
                "ROI": "mean",
                "CAC ($)": "mean"
            }
            valid_metrics = {k: v for k, v in metrics.items() if k in df.columns}
            if group_col in df.columns:
                summary = df.groupby(group_col).agg(valid_metrics).reset_index()
                chart = alt.Chart(summary).mark_bar().encode(
                    x=group_col, y="ROI", tooltip=[col for col in summary.columns if col != group_col]
                ).properties(title="ROI by Creative Format")
                st.altair_chart(chart, use_container_width=True)
                st.caption("Compare creative efficiency across formats to guide scaling and testing.")
                st.dataframe(summary)
            else:
                st.warning("There was an error, please try again.")

        elif "click-to-conversion" in question:
            group_col = "Targeting Strategy"
            metrics = {
                "Clicks": "sum",
                "Conversions": "sum"
            }
            valid_metrics = {k: v for k, v in metrics.items() if k in df.columns}
            if group_col in df.columns and "Clicks" in df.columns and "Conversions" in df.columns:
                summary = df.groupby(group_col).agg(valid_metrics).reset_index()
                summary["CVR (%)"] = (summary["Conversions"] / summary["Clicks"]) * 100
                chart = alt.Chart(summary).mark_bar().encode(
                    x=group_col, y="CVR (%)", tooltip=[group_col, "CVR (%)"]
                ).properties(title="Click-to-Conversion Rate by Targeting Strategy")
                st.altair_chart(chart, use_container_width=True)
                st.caption("Conversion efficiency varies by targeting strategy — behavioral and lookalike often outperform.")
                st.dataframe(summary)
            else:
                st.warning("There was an error, please try again.")

        elif "organic" in question:
            metrics = {
                "Organic Traffic": "sum",
                "Organic Conversions": "sum"
            }
            valid_metrics = {k: v for k, v in metrics.items() if k in df.columns}
            if "Month" in df.columns and "Organic Traffic" in df.columns and "Organic Conversions" in df.columns:
                organic_df = df.groupby("Month").agg(valid_metrics).reset_index()
                organic_df["Conversion Rate (%)"] = (organic_df["Organic Conversions"] / organic_df["Organic Traffic"]) * 100
                chart = alt.Chart(organic_df).mark_line(point=True).encode(
                    x="Month", y="Conversion Rate (%)",
                    tooltip=["Month", "Organic Traffic", "Organic Conversions", "Conversion Rate (%)"]
                ).properties(title="Organic Conversion Rate Over Time")
                st.altair_chart(chart, use_container_width=True)
                st.caption("Organic performance trends reveal SEO and content impact.")
                st.dataframe(organic_df)
            else:
                st.warning("There was an error, please try again.")

    except Exception:
        st.warning("There was an error, please try again.")


# -------------------------------
# Render Structured Answer
# -------------------------------
with st.container():
    st.subheader("📘 Detailed Answer")
    if question_to_answer and client:
        with st.spinner("Generating structured answer..."):
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Provide a structured answer with headings and bullet points (Insight, Action, Recommendation, Next Steps) for: {question_to_answer}, using the NZ dataset."}
                ]
            )
            detailed = response.choices[0].message.content

        # Parse response into sections
        sections = {"Insight": "", "Action": "", "Recommendation": "", "Next Steps": ""}
        current = None
        for line in detailed.splitlines():
            if any(h in line for h in sections.keys()):
                for h in sections.keys():
                    if h in line:
                        current = h
                        break
            elif current:
                sections[current] += line + "\n"

        # Fallback if parsing fails
        if not any(sections.values()):
            st.warning("⚠️ Could not parse structured sections. Here's the full output:")
            st.markdown(detailed)

        # Render each section
        with st.expander("🔍 Insight", expanded=True):
            st.markdown(sections["Insight"], unsafe_allow_html=True)
            render_chart_for_question(question_to_answer, df)

        with st.expander("⚡ Action", expanded=False):
            st.markdown(sections["Action"], unsafe_allow_html=True)
            if sections["Action"].strip():
                if st.button("💬 Ask a follow-up based on this action"):
                    st.session_state.custom_question = f"Expand on this action: {sections['Action'].strip()[:100]}..."

        with st.expander("🎯 Recommendation", expanded=False):
            st.markdown(sections["Recommendation"], unsafe_allow_html=True)

        with st.expander("📝 Next Steps", expanded=False):
            st.markdown(sections["Next Steps"], unsafe_allow_html=True)

        st.caption(f"Generated on {pd.Timestamp.now().strftime('%B %d, %Y at %H:%M')}")

# -------------------------------
# LEGAL DISCLAIMER
# -------------------------------
st.markdown("---")
st.markdown(
    "⚖️ [Legal Disclaimer](https://www.example.com/legal-disclaimer) — "
    "The insights and visualizations generated by this tool are for informational purposes only "
    "and should not be considered financial, legal, or business advice."
)
