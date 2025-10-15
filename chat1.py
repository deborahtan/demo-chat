import os
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from groq import Groq  # ✅ Groq SDK

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
system_prompt = """[same as before — no changes needed]"""

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
    st.markdown("""
        **Instructions**  
        - Select one of the predefined strategic questions from the dropdown.  
        - Or type your own custom question in the text box below.  
        - The assistant will generate structured insights (Insight → Action → Recommendation → Next Steps) and relevant charts.  
        - Your recent questions will appear below for quick re‑selection.  
    """)

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
# GROQ RESPONSE GENERATION
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

        except Exception as e:
            st.error(f"Error generating response: {e}")
