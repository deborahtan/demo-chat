import os
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from groq import Groq

# -------------------------------
# CONFIG
# -------------------------------
st.set_page_config(
    page_title="Dentsu Intelligence Assistant",
    page_icon="https://img.icons8.com/ios11/16/000000/dashboard-gauge.png",
    layout="wide"
)

# -------------------------------
# STYLING
# -------------------------------
st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #000;
    color: #fff;
}
h1,h2,h3,h4,h5,h6 {font-weight:600;color:#fff;}
[data-testid="stSidebar"] {
    background-color:#000;
    color:#fff;
}
[data-testid="stSidebar"] button {
    background-color:#fff !important;
    color:#000 !important;
    border-radius:6px;
    font-weight:600;
}
.answer-card {
    background-color:#2e2e2e;
    border-radius:12px;
    padding:20px;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# SIDEBAR
# -------------------------------
with st.sidebar:
    st.image("https://www.dentsu.com/assets/images/main-logo-alt.png", width=160)
    st.header("Executive Q&A")
    st.markdown("""
    **Instructions**
    - Ask performance questions or choose a predefined one.
    - The assistant will remember your conversation for context.
    """)

# -------------------------------
# GROQ SETUP
# -------------------------------
api_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")
if not api_key:
    st.error("Missing GROQ_API_KEY. Add it to your environment or Streamlit secrets.")
    st.stop()

client = Groq(api_key=api_key)

# -------------------------------
# SYSTEM PROMPT
# -------------------------------
system_prompt = """
You are the Dentsu Intelligence Assistant — a senior strategist turning marketing data into concise, quantified, executive-ready insight. Answer the user’s question directly and follow this structure.

--- 
Executive Overview
- 2–4 sentences, board-ready. Quantify key movements (e.g., “ROAS +14% MoM”, “CPA -9% vs. benchmark”) and state business impact.

Insight
- Key metrics: CPCV, CPM, CTR, CPC, CPA, ROAS, conversions, revenue, Viewability, Completion Rate.
- Highlight top and underperformers vs. benchmarks and historical trends.
- Include charts/tables that directly answer the question (timeframe, labels, 3–5 data points).
- Diagnostics: creative resonance, fatigue, audience saturation, and recommended metric thresholds.

Strategic Recommendation
- 2–4 actionable tactics with quantified impact, costs, and risks (channel allocation %, creative tests, budget moves, audience actions).
- Show expected ROI or CPA/ROAS deltas and funnel-layer relevance (Awareness / Consideration / Conversion).

Evidence & Reasoning
- Briefly state data sources, assumptions, confidence level, and any data quality caveats.

Examples (short)
- Paid Search: “Kitchen Appliances: $19.9K revenue, 78 purchases (AOV $255), CPA $38, ROAS $2.10. Recommend +30% budget ($22K).”
- Creative: “‘Earn’ creative: 73% revenue ($387K), CTR 2.46% (+89%), ROAS $5.07 (+52%). Scale +40% → est. $155K–$185K incremental.”
- Platform: “Meta conv. layer: CTR 4.2% vs 2.8% avg, ROAS $4.15 vs $2.90. Increase video allocation 35%→50% ($120K); expected revenue +$320K–$380K.”
- Audience: “1PD remarketing: 152 convs, ROAS $14.1, CPA $19.9. Increase frequency cap 8x→12x; projected +18–22% volume.”

NZ Context
- Consider NZ publishers and market seasonality (Meta, YouTube, Google, LinkedIn, TikTok, Snapchat, NZ Herald, Stuff, TVNZ, MediaWorks, NZME, Trade Me).

Be concise, numeric, and deliver clear next steps the exec can act on.
"""

# -------------------------------
# SAMPLE DATA
# -------------------------------
@st.cache_data(ttl=3600)
def generate_data():
    np.random.seed(42)
    publishers = ["YouTube", "Meta", "TikTok", "Search"]
    df = pd.DataFrame({
        "Publisher": np.random.choice(publishers, 500),
        "Spend ($)": np.random.uniform(1e3, 2e5, 500),
        "ROAS": np.random.uniform(1.2, 6.0, 500),
        "CTR (%)": np.random.uniform(0.5, 3.5, 500),
        "CPA ($)": np.random.uniform(10, 60, 500)
    })
    df["Revenue ($)"] = df["Spend ($)"] * df["ROAS"]
    return df

df = generate_data()

# -------------------------------
# SESSION STATE (for chat memory)
# -------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": system_prompt}
    ]

# -------------------------------
# PREDEFINED QUESTIONS
# -------------------------------
QUESTIONS = [
    "Analyze diminishing returns by channel.",
    "Which publishers delivered the most ROAS and CTR?",
    "Recommend budget shifts for optimal ROI."
]
st.write("### 💬 Chat with Dentsu Intelligence Assistant")
selected = st.selectbox("Quick question templates:", options=QUESTIONS)
custom_q = st.text_input("Or type your own question:")
question = custom_q.strip() if custom_q else selected

# -------------------------------
# DISPLAY CHAT HISTORY
# -------------------------------
for msg in st.session_state.messages[1:]:
    if msg["role"] == "user":
        st.markdown(f"**🧑 You:** {msg['content']}")
    elif msg["role"] == "assistant":
        st.markdown(f"<div class='answer-card'>{msg['content']}</div>", unsafe_allow_html=True)

# -------------------------------
# CHART DISPLAY (optional)
# -------------------------------
if "diminishing" in question.lower():
    chart = alt.Chart(df).mark_circle(size=60).encode(
        x="Spend ($)", y="ROAS", color="Publisher",
        tooltip=["Publisher", "Spend ($)", "ROAS"]
    ).properties(title="ROAS vs Spend by Publisher").interactive()
    st.altair_chart(chart, use_container_width=True)

# -------------------------------
# SEND MESSAGE
# -------------------------------
if st.button("Send Question"):
    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.spinner("Analyzing..."):
            try:
                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=st.session_state.messages
                )
                output = response.choices[0].message.content
                st.session_state.messages.append({"role": "assistant", "content": output})
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Error from Groq API: {e}")

# -------------------------------
# TIMESTAMP & DISCLAIMER
# -------------------------------
st.caption(f"Generated on {pd.Timestamp.now().strftime('%B %d, %Y at %H:%M')}")
st.markdown("---")
st.caption(
    "Insights are for strategic reference only and should not be considered financial or legal advice."
)
