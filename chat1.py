import os
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from groq import Groq

# -------------------------------
# CONFIG & BRANDING
# -------------------------------
st.set_page_config(page_title="Strategic Intelligence Assistant", page_icon="📊", layout="wide")

st.markdown("""
    <style>
        body { background-color: #000000; color: #fffefe; }
        h1, h2, h3, h4, h5, h6 { color: #fffefe; font-weight: 600; }
        .stTable { color: #fffefe; }
        [data-testid="stSidebar"] { min-width: 350px; max-width: 420px; }
        .answer-card {
            background-color: #ffffff;
            border-radius: 12px;
            padding: 20px;
            color: #000000;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
            font-size: 16px;
            line-height: 1.6;
        }
    </style>
""", unsafe_allow_html=True)

st.image("https://upload.wikimedia.org/wikipedia/commons/e/e5/Dentsu-logo_black.svg", width=160)
st.title("📊 Strategic Intelligence Assistant")

# -------------------------------
# API KEY & CLIENT
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
You are a Strategic Intelligence Assistant for C-suite executives across Marketing, Media, CRM, Finance, Loyalty, and Product.

Your role is to analyze enterprise-scale performance data and deliver structured, boardroom-ready insights using the NZ dataset provided.

Your response must always follow this structure:
- Insight: What’s happening and why.
- Action: What should be done immediately.
- Recommendation: Strategic advice for medium-term planning.
- Next Steps: Tactical follow-ups or governance suggestions.

You must:
- Use full funnel metrics: Impressions, Clicks, Conversions, Spend, Revenue, ROAS, ROI, CAC, CLV.
- Reference audience segments (Millennials, Gen X, Boomers) and publishers (NZ Herald, Stuff, TVNZ, MediaWorks, NZME Radio, Trade Me).
- Highlight patterns such as seasonal shifts, anomalies, and diminishing returns.

When asked about diminishing returns:
- Model ROAS as a curve that rises initially, flattens, and then declines — with a clear inflection point.
- Example: Display and Audio channels often show early saturation; CTV and Search sustain growth longer.

When asked about channel mix:
- Recommend allocations based on marginal ROAS and saturation thresholds.
- Example: CTV maintains higher ROAS at scale; Display delivers early efficiency but plateaus quickly; Search performs well across budget tiers.

When asked about churn:
- Distinguish internal vs. external drivers and visualize monthly trends.
- Example internal drivers: CRM fatigue, loyalty drop-off, poor onboarding.
- Example external drivers: economic uncertainty, seasonal demand shifts, competitive switching.

When asked about publisher performance:
- Compare across audience segments and quantify differences.
- Highlight which publishers over- or under-index with Millennials, Gen X, and Boomers.

When asked about formats or conversion rates:
- Rank by ROI, CPA, and CVR.
- Example: Video formats often deliver highest ROI but higher CPA; Display is more efficient but lower ROI.

Your tone must be:
- Executive-ready, confident, and concise.
- Free of filler or generic advice.
- Always grounded in the NZ dataset and performance metrics.
"""

# -------------------------------
# SIDEBAR CONTROLS
# -------------------------------
if "recent_questions" not in st.session_state:
    st.session_state.recent_questions = []

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
# SAMPLE DATA FOR CHARTS
# -------------------------------
def generate_roas_data():
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    channels = ["Display", "CTV", "Search"]
    data = []
    for i, month in enumerate(months):
        data.append({"Month": month, "Channel": "Display", "ROAS": max(2.1 - i * 0.1, 0.5)})
        data.append({"Month": month, "Channel": "CTV", "ROAS": max(3.4 - i * 0.1, 1.0)})
        data.append({"Month": month, "Channel": "Search", "ROAS": max(3.9 - i * 0.1, 1.5)})
    return pd.DataFrame(data)

# -------------------------------
# GROQ RESPONSE + CHARTS
# -------------------------------
if question_to_answer and client:
    with st.spinner("Generating strategic insights..."):
        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question_to_answer}
                ]
            )
            response_text = response.choices[0].message.content

            sections = {
                "Insight": "",
                "Action": "",
                "Recommendation": "",
                "Next Steps": "",
                "Evidence": ""
            }

            current = None
            for line in response_text.splitlines():
                line = line.strip()
                if any(line.lower().startswith(h.lower()) for h in sections.keys()):
                    for h in sections.keys():
                        if line.lower().startswith(h.lower()):
                            current = h
                            break
                elif current:
                    sections[current] += line + "\n"

            for key, icon in {
                "Insight": "🧠",
                "Action": "⚡",
                "Recommendation": "📌",
                "Next Steps": "🛠️",
                "Evidence": "🧪"
            }.items():
                if sections[key].strip():
                    with st.expander(f"{icon} {key}", expanded=(key == "Insight")):
                        st.markdown(f'<div class="answer-card">{sections[key].strip()}</div>', unsafe_allow_html=True)

            # ROAS Chart
            st.markdown("### 📈 ROAS Trends by Channel")
            df_roas = generate_roas_data()
            chart = alt.Chart(df_roas).mark_line(point=True).encode(
                x="Month",
                y="ROAS",
                color="Channel",
                tooltip=["Month", "Channel", "ROAS"]
            ).properties(height=400)
            st.altair_chart(chart, use_container_width=True)

        except Exception as e:
            st.error(f"Error generating response: {e}")
