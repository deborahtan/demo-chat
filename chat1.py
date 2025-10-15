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
    page_title="Strategic Intelligence Assistant",
    page_icon="https://img.icons8.com/ios11/16/000000/dashboard-gauge.png",
    layout="wide"
)

st.markdown("""
    <style>
        body { background-color: #000000; color: #fffefe; }
        h1, h2, h3, h4, h5, h6 { color: #fffefe; font-weight: 600; border-bottom: none !important; }
        section.main > div { padding-top: 1rem; padding-bottom: 1rem; }
        .answer-card {
            background-color: #2e2e2e; border-radius: 12px; padding: 20px; color: #fffefe;
        }
        .stTable { color: #fffefe; }
        [data-testid="stSidebar"] {
            min-width: 350px;
            max-width: 420px;
        }
    </style>
""", unsafe_allow_html=True)

st.image("https://upload.wikimedia.org/wikipedia/commons/e/e5/Dentsu-logo_black.svg", width=160)
st.title("📊 Strategic Intelligence Assistant")

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
You are an AI Insights Assistant for C‑suite executives in Marketing, Media, Creative, CRM, Finance, and Loyalty/Product.
Your role is to analyze enterprise‑scale performance data and deliver clear, strategic, executive‑ready insights and interactive visualizations.

Core responsibilities:
- Structure every response as Insight → Action → Recommendation → Next Steps.
- Always factor in audience types (Millennials, Gen X, Boomers), publisher strategies (NZ Herald, Stuff, TVNZ, MediaWorks, NZME Radio, Trade Me), and overarching portfolio trade‑offs.
- Use the full funnel dataset: Impressions, Clicks, Conversions, Spend, Revenue, ROAS, ROI, CAC, CLV.
- Highlight trends, seasonal patterns, anomalies, and diminishing returns curves.
- When asked about diminishing returns, generate and plot a Streamlit‑ready Altair chart of Spend vs ROAS by Channel.
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
if "recent_questions" not in st.session_state:
    st.session_state.recent_questions = []

with st.sidebar:
    st.header("Executive Q&A")

    st.markdown(
        """
        **Instructions**  
        - Select one of the predefined strategic questions from the dropdown.  
        - Or type your own custom question in the text box below.  
        - The assistant will generate structured insights (Insight → Action → Recommendation → Next Steps) and relevant charts.  
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
with st.container():
    st.subheader("Detailed Answer")
    if question_to_answer and client:
        with st.spinner("Generating structured answer..."):
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Provide a structured answer with headings and bullet points (Insight, Action, Recommendation, Next Steps) for: {question_to_answer}, using the NZ dataset."}
                ]
            )
            detailed = response.choices[0].message.content

        # Split the AI response into sections
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

        # Render each section as an expander
        with st.expander("🔍 Insight", expanded=True):
            st.markdown(sections["Insight"], unsafe_allow_html=True)

            # Add relevant chart under Insight
            if "diminishing returns" in question_to_answer.lower():
                channels = ["Search","Social","CTV","Display"]
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
                    tooltip=["Channel","Spend ($)","ROAS"]
                ).properties(title="Diminishing Returns: Spend vs ROAS by Channel")
                st.altair_chart(chart, use_container_width=True)
                st.caption("Each channel shows a flattening ROAS curve as spend increases, highlighting saturation points.")

            elif "publisher" in question_to_answer.lower():
                pub_chart = alt.Chart(df).mark_bar().encode(
                    x="Publisher", y="Conversions", color="Audience",
                    tooltip=["Publisher","Audience","Conversions","ROAS","CAC ($)"]
                ).properties(title="Publisher Performance by Audience Segment")
                st.altair_chart(pub_chart, use_container_width=True)
                st.caption("Publishers over‑ or under‑index by audience segment; e.g. NZ Herald with Millennials vs Stuff with Gen X.")

            elif "churn" in question_to_answer.lower():
                churn_df = df.groupby("Month")["Conversions"].sum().reset_index()
                churn_df["Churn (%)"] = np.random.uniform(2, 8, size=len(churn_df))
                churn_chart = alt.Chart(churn_df).mark_line(point=True).encode(
                    x="Month", y="Churn (%)", tooltip=["Month","Churn (%)"]
                ).properties(title="Monthly Churn Trend")
                st.altair_chart(churn_chart, use_container_width=True)
                st.caption("Churn spikes in July and November, linked to CRM fatigue and macroeconomic slowdown.")

            elif "roi and cpa" in question_to_answer.lower():
                formats = pd.DataFrame({
                    "Format": ["Video","Display","Social","CTV"],
                    "ROI": [3.2, 2.1, 2.8, 3.5],
                    "CPA": [55, 40, 50, 45]
                })
                chart = alt.Chart(formats).mark_bar().encode(
                    x="Format", y="ROI", tooltip=["Format","ROI","CPA"]
                ).properties(title="ROI by Format")
                st.altair_chart(chart, use_container_width=True)
                st.caption("Video delivers highest ROI but higher CPA; Display is more efficient but lower ROI.")

            elif "click-to-conversion" in question_to_answer.lower():
                channels = pd.DataFrame({
                    "Channel": ["Search","Social","CTV","Display"],
                    "CVR (%)": [5.2, 3.8, 4.5, 2.9]
                })
                chart = alt.Chart(channels).mark_bar().encode(
                    x="Channel", y="CVR (%)", tooltip=["Channel","CVR (%)"]
                ).properties(title="Click-to-Conversion Rate by Channel")
                st.altair_chart(chart, use_container_width=True)
                st.caption("Search drives the strongest conversion efficiency, followed by CTV.")

        with st.expander("⚡ Action", expanded=False):
            st.markdown(sections["Action"], unsafe_allow_html=True)

        with st.expander("🎯 Recommendation", expanded=False):
            st.markdown(sections["Recommendation"], unsafe_allow_html=True)

        with st.expander("📝 Next Steps", expanded=False):
            st.markdown(sections["Next Steps"], unsafe_allow_html=True)

# -------------------------------
# REFERENCE DICTIONARY (Expandable)
# -------------------------------
with st.expander("📖 Dimensions & Metrics Dictionary", expanded=False):
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
