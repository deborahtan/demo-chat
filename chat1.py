import os
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from groq import Groq
from datetime import datetime

# Import theme styling AFTER st.set_page_config()
from style import load_theme

# -------------------------------
# CONFIG
# -------------------------------
st.set_page_config(
    page_title="Dentsu Intelligence Assistant",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load theme
load_theme()

# -------------------------------
# INITIALIZE SESSION STATE
# -------------------------------
if "chat_history" not in st.session_state:
    system_prompt = """
You are the Dentsu Intelligence Assistant — a senior strategist delivering enterprise-level marketing intelligence to C-suite stakeholders across Media, Marketing, CRM, Loyalty, and Finance.

Your role is to synthesize performance across all channels, formats, funnel layers, and audience segments — not just individual campaigns — and deliver quantified, executive-ready insights that reflect fiscal year context and strategic impact.

**Executive Overview**
- Summarize performance across the latest fiscal month or week (e.g., FY Month 4, Week 17).
- Quantify key shifts in ROAS, CPA, CTR, spend, and revenue.
- Highlight top-performing funnel layers, formats, and publishers.
- Frame commentary in terms of business impact, efficiency, and momentum.

**Insight**
- Segment by:
  - Funnel Layer: Awareness, Consideration, Conversion
  - Format: Video, Static, Carousel, Interactive, Radio
  - Strategy: Retargeting, Brand Lift, Product Launch, Offer Promotion
  - Publisher: Meta, YouTube, NZ Herald, NZME Radio, etc.
  - Audience Segment (Demographic): e.g., Millennials, Boomers, Parents with Kids
  - Audience Segment (Behavioral): e.g., High Intent Shoppers, Cart Abandoners, Loyalty Members
- Always compare like-for-like when evaluating performance.
- Use schema fields to explain performance drivers.
- Reference fiscal trends (MoM, WoW, FY-to-date) and NZ-specific media norms.
- Always include at least one visualisation to support your insight.

**Strategic Recommendation**
- Provide 2–4 actionable tactics with quantified impact.
- Recommend optimisations across: Channel mix, Creative format, Audience targeting, Budget allocation.
- Prioritise changes that improve CPA, ROAS, or conversion volume.

Be concise, visual, and data-driven. Always speak to overarching performance, not isolated campaigns.
"""
    st.session_state.chat_history = [{"role": "system", "content": system_prompt}]

if "show_data" not in st.session_state:
    st.session_state.show_data = False

if "question_history" not in st.session_state:
    st.session_state.question_history = {"today": [], "yesterday": []}

# -------------------------------
# GROQ SETUP
# -------------------------------
api_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")
if not api_key:
    st.error("❌ Missing GROQ_API_KEY. Add it to your environment or Streamlit secrets.")
    st.stop()

client = Groq(api_key=api_key)

# -------------------------------
# SAMPLE DATA
# -------------------------------
@st.cache_data(ttl=3600)
def generate_data():
    fy_year = 2025
    weeks = list(range(1, 53)) * 20

    publishers = [
        "Meta", "YouTube", "TikTok", "Search", "Stuff", "NZ Herald", "NZME Radio",
        "TVNZ OnDemand", "MetService", "Neighbourly", "Spotify", "We Are Frank",
        "GrabOne", "Go Media", "LUMO", "LinkedIn", "Quantcast", "The Trade Desk",
        "MediaWorks Radio"
    ]
    strategies = ["Retargeting", "Brand Lift", "Product Launch", "Offer Promotion"]
    funnel_layers = ["Awareness", "Consideration", "Conversion"]
    formats = ["Video", "Static", "Carousel", "Interactive", "Radio"]
    creative_messaging = ["Value-led", "Urgency-led", "Emotional", "Informational"]
    demo_segments = ["Millennials", "Boomers", "Parents with Kids"]
    behav_segments = ["High Intent Shoppers", "Cart Abandoners", "Loyalty Members"]

    rows = []
    for i in range(len(weeks)):
        week = weeks[i]
        funnel = funnel_layers[i % 3]
        format = formats[i % 5]
        strategy = strategies[i % 4]
        publisher = publishers[i % len(publishers)]
        creative = creative_messaging[i % 4]
        demo = demo_segments[i % 3]
        behav = behav_segments[i % 3]

        base_spend = {
            "Awareness": 100_000,
            "Consideration": 250_000,
            "Conversion": 500_000
        }[funnel]

        seasonal_multiplier = 1.25 if week >= 40 else 1.0
        spend = base_spend * seasonal_multiplier

        ctr_lookup = {
            "Video": 2.8,
            "Carousel": 3.2,
            "Static": 1.2,
            "Interactive": 2.5,
            "Radio": 0.6
        }
        ctr = ctr_lookup[format]

        cpa_lookup = {
            "High Intent Shoppers": 35,
            "Cart Abandoners": 28,
            "Loyalty Members": 22
        }
        cpa = cpa_lookup[behav]

        roas_base = {
            "Awareness": 2.0,
            "Consideration": 3.5,
            "Conversion": 5.0
        }[funnel]
        roas = max(1.2, roas_base - (spend / 1_000_000))

        cpm_adjust = {
            "Video": 6,
            "Carousel": 5,
            "Static": 4,
            "Interactive": 6,
            "Radio": 3
        }
        impressions = int(spend / cpm_adjust[format] * 1000)
        clicks = int(impressions * (ctr / 100))
        revenue = spend * roas

        if format == "Radio" and publisher in ["NZME Radio", "MediaWorks Radio"]:
            tarps = round(min(100, 30 + (week % 20)), 1)
            reach = round(tarps / 1.5, 1)
            frequency = round(tarps / reach, 1)
            spot_count = int(spend / 500)
            station = ["ZM", "The Edge", "Newstalk ZB", "Hauraki", "Coast"][i % 5]
        else:
            tarps = None
            reach = None
            frequency = None
            spot_count = None
            station = None

        rows.append({
            "FY Year": fy_year,
            "Week": week,
            "Publisher": publisher,
            "Strategy": strategy,
            "Funnel Layer": funnel,
            "Format": format,
            "Creative Messaging": creative,
            "Audience Segment (Demographic)": demo,
            "Audience Segment (Behavioral)": behav,
            "Spend ($)": spend,
            "ROAS": roas,
            "CTR (%)": ctr,
            "CPA ($)": cpa,
            "Impressions": impressions,
            "Clicks": clicks,
            "Revenue ($)": revenue,
            "TARPs": tarps,
            "Reach (%)": reach,
            "Frequency": frequency,
            "Spot Count": spot_count,
            "Station": station
        })

    return pd.DataFrame(rows)

df = generate_data()

# ===================== MAIN LAYOUT =====================
left_col, right_col = st.columns([1, 2.5], gap="large")

# ===================== LEFT SIDEBAR =====================
with left_col:
    st.markdown("""
    <div style="margin-bottom: 2rem;">
        <img src="https://www.dentsu.com/assets/images/main-logo-alt.png" width="120" style="margin-bottom: 24px;">
        <h2 style="margin: 0; font-size: 1.4rem;">Dentsu Intelligence</h2>
        <p style="color: #6b7280; font-size: 0.9rem; margin-top: 8px;">Marketing Performance Analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Today's Questions
    st.markdown('<p class="sidebar-title">Today\'s Questions</p>', unsafe_allow_html=True)
    if st.session_state.question_history["today"]:
        for q in st.session_state.question_history["today"]:
            st.markdown(f"""
            <div class="question-item">
                <div class="question-time">{q['time']}</div>
                <div class="question-text">{q['text']}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown('<p style="color: #6b7280; font-size: 0.9rem;">No questions yet today</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Yesterday's Questions
    st.markdown('<p class="sidebar-title">Yesterday\'s Questions</p>', unsafe_allow_html=True)
    if st.session_state.question_history["yesterday"]:
        for q in st.session_state.question_history["yesterday"]:
            st.markdown(f"""
            <div class="question-item">
                <div class="question-time">{q['time']}</div>
                <div class="question-text">{q['text']}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown('<p style="color: #6b7280; font-size: 0.9rem;">No questions from yesterday</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🧹 Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.question_history = {"today": [], "yesterday": []}
            st.rerun()
    with col2:
        if st.button("📊 Data", use_container_width=True):
            st.session_state.show_data = not st.session_state.show_data

# ===================== RIGHT MAIN CONTENT =====================
with right_col:
    st.markdown("""
    <div style="margin-bottom: 2rem;">
        <h1 style="margin-bottom: 0.5rem; font-size: 2.2rem;">Dentsu Intelligence</h1>
        <p style="color: #9ca3af; font-size: 1.1rem; margin: 0;">Enterprise-Level Marketing Performance Analysis</p>
    </div>
    """, unsafe_allow_html=True)

    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Spend (FY)</div>
            <div class="metric-value">${df['Spend ($)'].sum()/1e6:.1f}M</div>
            <div class="metric-change">↑ 12% vs LY</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Avg ROAS</div>
            <div class="metric-value">{df['ROAS'].mean():.2f}x</div>
            <div class="metric-change">↑ 0.3x MoM</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Revenue</div>
            <div class="metric-value">${df['Revenue ($)'].sum()/1e6:.1f}M</div>
            <div class="metric-change">↑ 18% vs LY</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Avg CPA</div>
            <div class="metric-value">${df['CPA ($)'].mean():.0f}</div>
            <div class="metric-change negative">↑ 3% vs LY</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Data preview
    if st.session_state.show_data:
        with st.expander("📋 View Dataset", expanded=True):
            st.dataframe(df.head(20), use_container_width=True)
            st.info(f"Dataset contains {len(df)} records across {df['Week'].nunique()} weeks")

    st.markdown("---")

    # Predefined questions
    st.markdown('<h3 style="margin-bottom: 12px;">Quick Questions</h3>', unsafe_allow_html=True)
    predefined_questions = [
        ("📊", "What was the top-performing publisher last week?"),
        ("💰", "How is ROAS trending month-over-month?"),
        ("🎯", "Which audience segment has the lowest CPA?"),
        ("📈", "What format performed best in the conversion layer?"),
    ]
    
    for emoji, question in predefined_questions:
        if st.button(f"{emoji} {question}", use_container_width=True, key=question):
            user_input = question
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            
            # Add to question history
            current_time = datetime.now().strftime("%H:%M")
            st.session_state.question_history["today"].append({"time": current_time, "text": user_input})
            
            st.rerun()

    st.markdown("---")
    
    st.markdown('<h3 style="margin-bottom: 12px;">💬 Chat</h3>', unsafe_allow_html=True)

    # Chat display
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat_history:
            if msg["role"] == "assistant":
                with st.chat_message("assistant", avatar="🤖"):
                    st.markdown(msg["content"])
            elif msg["role"] == "user":
                with st.chat_message("user", avatar="👤"):
                    st.markdown(msg["content"])

    # Chat input
    user_input = st.chat_input("Ask about performance, ROI, recommendations...", key="chat_input")

    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # Add to question history
        current_time = datetime.now().strftime("%H:%M")
        st.session_state.question_history["today"].append({"time": current_time, "text": user_input})
        
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_input)

        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("🔍 Analyzing performance metrics..."):
                try:
                    response = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=st.session_state.chat_history
                    )
                    output = response.choices[0].message.content
                    st.markdown(output)
                    st.session_state.chat_history.append({"role": "assistant", "content": output})
                except Exception as e:
                    st.error(f"⚠️ Error: {str(e)}")

# Footer
st.markdown("""
<div class="disclaimer" style="margin-top: 48px;">
⚠️ <strong>Legal Disclaimer</strong> — The insights and visualizations generated by this tool are for informational purposes only and should not be considered financial, legal, or business advice.
</div>
""", unsafe_allow_html=True)
