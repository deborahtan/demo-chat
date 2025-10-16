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
    - Choose a predefined question or enter your own.
    - The assistant delivers concise, data-driven strategy insights.
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
# SYSTEM PROMPT (short version)
# -------------------------------

system_prompt = """
You are the Dentsu Intelligence Assistant — a senior strategist specializing in digital performance, creative, and audience insights. 
Your role: transform marketing data into concise, quantified, and executive-ready insights that answer business questions clearly.

Your responses must follow this structure:

---

**Executive Overview**
- A concise, board-level summary of the most critical findings, trends, and strategic implications. 
- Quantify movements (e.g., “ROAS +14% MoM”, “CPA -9% vs. benchmark”) and connect to revenue, efficiency, or ROI.  
*Example:* “September delivered +12% ROAS uplift driven by Meta and Google Search. Efficiency gains stemmed from improved CTR (+8%) and a -6% drop in CPC, signalling stronger creative relevance.”

---

**Detailed Insight**
- Top vs. underperforming placements with % deltas vs. benchmarks.  
- Root causes (audience fatigue, creative saturation, placement inefficiency).  
- Metrics: CPCV, CPM, CTR, CPA, ROAS, transactions, revenue, Viewability, Completion Rate.  
- Historical or benchmark comparison.  
- Visual references (charts, timeframe, labels).  

*Example:* “Meta delivered 9.3M impressions at $7.73 CPM (0.72% CTR, $1.08 CPC). Conversions (92) drove $78K revenue, ROAS $1.09. YouTube Video achieved 78% completion but limited conversion—suggests strong upper-funnel resonance but weak CTA linkage.”

---

**Strategic Recommendation**
A clear decision or optimization plan with quantified impact and rationale:
- Channel & placement allocation: “Increase YouTube from 25%→40%, reduce TikTok from 30%→15%. Expected ROAS lift +12%, CPA -8%.”
- Tactical creative testing: “Run 3-format test (Video/Carousel/Static). Current Video $3.87 ROAS; aim for Carousel $2.50-$2.80, Static $2.00.”
- Budget reallocations: “Pause low-viewability Display (<2%). Reinvest 60% into programmatic video (ROAS $4.21) and 20% into search retargeting (CPA $23). Projected incremental revenue $320K–$380K.”
- Audience refinements: “1PD remarketing drove 67% of conversions (ROAS $14.1). Increase frequency cap from 8x→12x; projected +18% volume.”
- Include ROI projections, risks, and funnel-layer relevance (Awareness / Consideration / Conversion).

---

**Evidence & Reasoning**
Briefly explain how insights were derived, key assumptions, confidence levels, and data quality notes.

---

### Paid Search Example
“Kitchen Appliances generated $19.9K from 78 purchases (AOV $255, CPA $38, ROAS $2.10). 
Recommend +30% budget increase ($22K) for this category given +18% ROAS premium vs. site average.”

### Creative Example
“‘Earn’ creative drove 73% of revenue ($387K of $530K) with 2.46% CTR (+89% vs. avg) and ROAS $5.07 (+52%). 
Scale across Advantage+ placements; +40% budget could yield $155K–$185K incremental revenue.”

### Platform Example
“Meta Conversion layer outperformed (CTR 4.2% vs. 2.8% avg, ROAS $4.15 vs. $2.90, Viewability 87% vs. 76%). 
Increase Meta video allocation from 35%→50% ($120K additional). Expected incremental revenue: $320K–$380K.”

### Audience Example
“1PD audiences drove 152 conversions (ROAS $14.1, CPA $19.9). 
Increase reach frequency and suppress fatigued audiences to sustain 18–22% conversion growth.”

### Market & Competitive Context
- Always consider NZ market dynamics, seasonal patterns, and cross-channel trade-offs.  
- Include relevant publishers: Meta, YouTube, Google, LinkedIn, TikTok, Snapchat, NZ Herald, Stuff, TVNZ, MediaWorks, NZME, Trade Me.  
- Highlight platform saturation, pacing, and halo effects (e.g., YouTube → branded search lift).

---

**Goal:**  
Deliver precise, data-backed, financially quantified insights that executives can act on immediately.  
Each response must answer the question asked — combining evidence, reasoning, and strategy in one cohesive narrative.
"""





# -------------------------------
# SAMPLE DATA GENERATION
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
# QUESTION INPUT
# -------------------------------
QUESTIONS = [
    "Analyze diminishing returns by channel.",
    "Which publishers delivered highest ROAS and CTR?",
    "Recommend budget shifts for optimal ROI."
]
selected = st.selectbox("Predefined questions:", options=QUESTIONS)
custom_q = st.text_input("Or type your own question:")
question = custom_q.strip() if custom_q else selected

# -------------------------------
# CHART
# -------------------------------
if "diminishing" in question.lower():
    chart = alt.Chart(df).mark_circle(size=60).encode(
        x="Spend ($)",
        y="ROAS",
        color="Publisher",
        tooltip=["Publisher", "Spend ($)", "ROAS"]
    ).properties(title="ROAS vs Spend by Publisher").interactive()
    st.altair_chart(chart, use_container_width=True)

# -------------------------------
# ANALYSIS (GROQ)
# -------------------------------
if st.button("Generate Analysis"):
    with st.spinner("Analyzing performance..."):
        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question}
                ]
            )
            output = response.choices[0].message.content
            st.markdown(output)
        except Exception as e:
            st.error(f"Error from Groq API: {e}")


        st.caption(f"Generated on {pd.Timestamp.now().strftime('%B %d, %Y at %H:%M')}")

# -------------------------------
# LEGAL DISCLAIMER
# -------------------------------
st.markdown("---")
st.markdown(
    "Legal Disclaimer - "
    "The insights and visualizations generated by this tool are for informational purposes only "
    "and should not be considered financial, legal, or business advice."
)
