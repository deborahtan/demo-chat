import os
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import anthropic  # ✅ Replaces OpenAI

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
        [data-testid="stSidebar"] {
            min-width: 350px;
            max-width: 420px;
        }
    </style>
""", unsafe_allow_html=True)

# Branding
st.image("https://upload.wikimedia.org/wikipedia/commons/e/e5/Dentsu-logo_black.svg", width=160)
st.title("📊 Strategic Intelligence Assistant")

# -------------------------------
# API KEY
# -------------------------------
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key and "ANTHROPIC_API_KEY" in st.secrets:
    api_key = st.secrets["ANTHROPIC_API_KEY"]

client = None
if api_key:
    client = anthropic.Anthropic(api_key=api_key)
else:
    st.error("No API key found. Please set ANTHROPIC_API_KEY as env var or in Streamlit secrets.")

# -------------------------------
# SYSTEM PROMPT
# -------------------------------
system_prompt = """
You are an AI Insights Assistant for C‑suite executives across Marketing, Media, Creative, CRM, and Loyalty/Product.
Your mandate is to analyze enterprise‑scale performance data and deliver clear, strategic, executive‑ready insights supported by interactive visualizations.

Core responsibilities:
- Structure every response in the framework: **Insight → Action → Recommendation → Next Steps**.
- Ensure each element is **specific, evidence‑based, and valid**:
  • Insight = A precise finding from the data (with metrics, trends, anomalies, or quantified comparisons).  
  • Action = A concrete operational step that teams can take immediately.  
  • Recommendation = A strategic decision with rationale, financial impact, and risk/benefit trade‑offs.  
  • Next Steps = Clear owners, timelines, and measurement criteria.  

- Always account for:
  • Audience cohorts (Millennials, Gen X, Boomers)  
  • Global platforms: Meta, TikTok, YouTube, Google Search/Display, LinkedIn, Snapchat  
  • Local publishers: NZ Herald, Stuff, TVNZ, MediaWorks, NZME Radio, Trade Me  
  • Performance/content partners: We Are Frank, Taboola, and other relevant publishers  
  • Portfolio‑level trade‑offs and opportunity costs  

- Leverage the full‑funnel dataset: Impressions, Clicks, Conversions, Spend, Revenue, ROAS, ROI, CAC, CLV.
- Identify and explain: trends, seasonal patterns, anomalies, and diminishing returns curves.
- When analyzing diminishing returns, generate a Streamlit‑ready Altair chart of **Spend vs. ROAS by Channel**, with hover tooltips for Spend, Revenue, ROAS, and CAC.
- When evaluating publisher or platform performance, compare across audience segments, quantify differences, and highlight impact.
- For **Creative insights**, frame findings through **A/B testing results and key performance trends**:
  • Identify winning vs. underperforming variants.  
  • Highlight message, format, and visual elements that drive higher CTR, CVR, or CLV.  
  • Recommend next creative tests and scaling strategies.  

- Provide actionable recommendations including: budget reallocations, testing frameworks, risk/impact assessments, and scenario planning.
- Explicitly state reasoning, modelling choices, and assumptions; flag confidence levels where appropriate.
- Anticipate likely C‑suite follow‑up questions (ROI sensitivity, scalability, risk exposure, competitive benchmarks) and prepare concise, data‑driven responses.
- Deliver all outputs in professional, concise, boardroom‑ready language that supports decision‑making.

Your goal: transform complex performance data into **specific insights, valid actions, and strategically grounded recommendations** that drive executive confidence and measurable results.
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
# CLAUDE RESPONSE GENERATION
# -------------------------------
if question_to_answer and client:
    with st.spinner("Generating strategic insights..."):
        try:
            response = client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                temperature=0.7,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": question_to_answer}
                ]
            )

            response_text = response.content

            st.markdown("### Executive Insight")
            st.markdown(f'<div class="answer-card">{response_text}</div>', unsafe_allow_html=True)

            if "Spend vs. ROAS by Channel" in response_text:
                st.markdown("### 📈 Spend vs. ROAS by Channel")
                chart_data = df.groupby("Publisher").agg({
                    "Spend ($)": "sum",
                    "Revenue ($)": "sum",
                    "ROAS": "mean",
                    "CAC ($)": "mean"
                }).reset_index()

                chart = alt.Chart(chart_data).mark_circle(size=100).encode(
                    x=alt.X("Spend ($)", scale=alt.Scale(zero=False)),
                    y=alt.Y("ROAS", scale=alt.Scale(zero=False)),
                    color="Publisher",
                    tooltip=["Publisher", "Spend ($)", "Revenue ($)", "ROAS", "CAC ($)"]
                ).properties(height=400)

                st.altair_chart(chart, use_container_width=True)

        except anthropic.RateLimitError:
            st.error("⚠️ Claude's rate limit has been reached. Please wait a few minutes and try again.")
        except Exception as e:
            st.error(f"Error generating response: {e}")
