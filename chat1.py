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
    st.header("Executive Chat")
    st.markdown("""
    **How to use**
    - Type any question about campaign performance or strategy.
    - The assistant responds with quantified, data-driven insight.
    - Conversation context is remembered.
    """)
    if st.button("🧹 Clear Conversation"):
        st.session_state.chat_history = []
        st.experimental_rerun()

# -------------------------------
# GROQ SETUP
# -------------------------------
api_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")
if not api_key:
    st.error("Missing GROQ_API_KEY. Add it to your environment or Streamlit secrets.")
    st.stop()

client = Groq(api_key=api_key)

# -------------------------------
# SYSTEM PROMPT (your version)
# -------------------------------
system_prompt = """
You are the Dentsu Intelligence Assistant — a senior strategist turning marketing data into concise, quantified, executive-ready insight.

**Executive Overview**
- 2–4 sentences. Quantify performance (e.g., ROAS +14% MoM, CPA -9% vs. benchmark). Focus on revenue and efficiency impact.

**Insight**
- Include metrics (CPCV, CPM, CTR, CPA, ROAS, etc.), top performers, and underperformers.
- Explain key drivers, trends, and audience/creative learnings.
- Use NZ-relevant context when applicable.

**Strategic Recommendation**
- 2–4 actionable tactics with quantified impact and ROI or CPA/ROAS deltas.
- Cover channel shifts, creative tests, or audience optimizations.

**Examples**
- Meta: 9.3M impressions, $7.73 CPM, 0.72% CTR, $1.08 CPC → $78K revenue, ROAS $1.09.
- Audience: 1PD remarketing drove 67% of conversions (ROAS $14.1). Raise frequency 8x→12x (+18% volume expected).

Be concise, data-driven, and provide clear next steps.
"""

# -------------------------------
# CHAT MEMORY
# -------------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [{"role": "system", "content": system_prompt}]

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
# DISPLAY PREVIOUS MESSAGES
# -------------------------------
for msg in st.session_state.chat_history:
    if msg["role"] == "assistant":
        with st.chat_message("assistant"):
            st.markdown(msg["content"])
    elif msg["role"] == "user":
        with st.chat_message("user"):
            st.markdown(msg["content"])

# -------------------------------
# CHAT INPUT
# -------------------------------
user_input = st.chat_input("Ask about performance, ROI, or recommendations...")

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing performance..."):
            try:
                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=st.session_state.chat_history
                )
                output = response.choices[0].message.content
                st.markdown(output)
                st.session_state.chat_history.append({"role": "assistant", "content": output})
            except Exception as e:
                st.error(f"Error from Groq API: {e}")

# -------------------------------
# LEGAL DISCLAIMER
# -------------------------------
st.markdown("---")
st.markdown(
    "Legal Disclaimer — The insights and visualizations generated by this tool are for informational purposes only "
    "and should not be considered financial, legal, or business advice."
)
