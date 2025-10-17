import os
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from groq import Groq
from datetime import datetime, timedelta

# -------------------------------
# CONFIG
# -------------------------------
st.set_page_config(
    page_title="Dentsu Conversational Analytics",
    page_icon="https://img.icons8.com/ios11/16/000000/dashboard-gauge.png",
    layout="wide"
)

# -------------------------------
# STYLING
# -------------------------------
st.markdown("""
<style>
    .stSidebar {
        min-width: 336px;
    }
    .stSidebar .stHeading {
        color: #FAFAFA;
    }
    .stSidebar .stElementContainer {
        width: auto;
    }
    .history-section {
        margin-top: 24px;
        margin-bottom: 12px;
    }
    .history-section h4 {
        font-size: 12px;
        color: #A0A0A0;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 8px;
        margin-top: 0;
    }
    .history-item {
        padding: 8px 12px;
        margin-bottom: 6px;
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 6px;
        cursor: pointer;
        font-size: 13px;
        color: #E0E0E0;
        transition: background-color 0.2s;
        border-left: 3px solid transparent;
    }
    .history-item:hover {
        background-color: rgba(255, 255, 255, 0.1);
        border-left-color: #80D5FF;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "question_history" not in st.session_state:
    st.session_state.question_history = {}

# Helper function to get date key (YYYY-MM-DD)
def get_date_key():
    return datetime.now().strftime("%Y-%m-%d")

# Helper function to format time
def format_time(dt):
    return dt.strftime("%H:%M")

# Helper function to add question to history
def add_to_history(question):
    date_key = get_date_key()
    if date_key not in st.session_state.question_history:
        st.session_state.question_history[date_key] = []
    st.session_state.question_history[date_key].append({
        "question": question,
        "timestamp": datetime.now()
    })

# Helper function to get yesterday's date key
def get_yesterday_key():
    yesterday = datetime.now() - timedelta(days=1)
    return yesterday.strftime("%Y-%m-%d")

# Helper function to categorize questions by date
def get_history_sections():
    today_key = get_date_key()
    yesterday_key = get_yesterday_key()
    
    sections = []
    
    if today_key in st.session_state.question_history and st.session_state.question_history[today_key]:
        sections.append(("Today", today_key))
    
    if yesterday_key in st.session_state.question_history and st.session_state.question_history[yesterday_key]:
        sections.append(("Yesterday", yesterday_key))
    
    return sections

# -------------------------------
# SIDEBAR
# -------------------------------
with st.sidebar:
    st.image("https://www.dentsu.com/assets/images/main-logo-alt.png", width=160)
    if st.button("✎   Start New Chat"):
        st.session_state.chat_history = []
        st.rerun()
    
    st.header("Executive Chat")
    st.markdown("""
    **How to use**
    - Type any question about campaign performance or strategy.
    - The assistant responds with quantified, data-driven insight.
    - Conversation context is remembered.
    """)
    
    # Display question history
    history_sections = get_history_sections()
    if history_sections:
        st.markdown("---")
        st.markdown("**Recent Questions**")
        
        for section_label, date_key in history_sections:
            st.markdown(f"<div class='history-section'><h4>{section_label}</h4></div>", unsafe_allow_html=True)
            
            questions = st.session_state.question_history[date_key]
            for q_item in reversed(questions):
                question = q_item["question"]
                time_str = format_time(q_item["timestamp"])
                display_text = f"{time_str} • {question[:40]}..." if len(question) > 40 else f"{time_str} • {question}"
                
                if st.button(display_text, key=f"hist_{date_key}_{time_str}_{len(st.session_state.chat_history)}", use_container_width=True):
                    st.session_state.chat_input_value = question
                    st.rerun()

# -------------------------------
# HEADER
# -------------------------------
st.markdown("""
<div>
    <h1 style="text-align: center; font-size: 64px;>
        <span style="color: #FAFAFA; text-shadow: 0 0 4px rgba(216, 237, 255, 0.16), 0 2px 20px rgba(164, 214, 255, 0.36);">dentsu</span>
        <span style="background: radial-gradient(909.23% 218.25% at -4.5% 144.64%, #80D5FF 0%, #79AAFA 44.5%, #C4ADFF 100%); background-clip: text; -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Intelligence</span>
    </h1>
</div>
""", unsafe_allow_html=True)

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
You are the Dentsu Intelligence Assistant — a senior strategist delivering enterprise-level marketing intelligence to C-suite stakeholders across Media, Marketing, CRM, Loyalty, and Finance.

Your role is to synthesize performance across all channels, formats, funnel layers, and audience segments — not just individual campaigns — and deliver quantified, executive-ready insights that reflect fiscal year context and strategic impact.

**Executive Overview**
- Summarize performance across the latest fiscal month or week (e.g., FY Month 4, Week 17).
- Quantify key shifts in ROAS, CPA, CTR, spend, and revenue.
- Highlight top-performing funnel layers, formats, and publishers.
- Frame commentary in terms of business impact, efficiency, and momentum.

**Insight & Visualisation**
- Generate charts and graphs ONLY when directly relevant to answering the user's question.
- Never generate generic visualisations that don't serve the analysis.
- Only include visualisation if the question explicitly asks for performance comparison, trends, breakdowns, or channel/format/audience analysis.
- Recommended chart types:
  - Spend/Revenue by Publisher, Format, Funnel Layer: Bar chart or horizontal bar chart
  - ROAS, CPA, CTR trends: Line chart or area chart
  - Performance by Audience Segment: Grouped bar chart
  - Channel Mix or Attribution: Pie chart or stacked bar chart
- Always embed Altair/Vega-Lite syntax in your response when visualisation is needed. Use markdown code blocks with language `altair` for charts.
- Segment analysis by:
  - Funnel Layer: Awareness, Consideration, Conversion
  - Format: Video, Static, Carousel, Interactive, Radio
  - Strategy: Retargeting, Brand Lift, Product Launch, Offer Promotion
  - Publisher: Meta, YouTube, NZ Herald, NZME Radio, etc.
  - Audience Segment (Demographic): Millennials, Boomers, Parents with Kids
  - Audience Segment (Behavioral): High Intent Shoppers, Cart Abandoners, Loyalty Members
- Always compare like-for-like when evaluating performance.
- Use schema fields to explain performance drivers.
- Reference fiscal trends (MoM, WoW, FY-to-date) and NZ-specific media norms.

**Strategic Recommendation**
- Provide 2–4 actionable tactics with quantified impact (e.g., "Shift 12% of spend from Static to Video to improve ROAS by +0.8").
- Recommend optimisations across:
  - Channel mix based on their respective objectives
  - Creative format and testing approaches
  - Audience targeting (demographic, behavioral, or data combinations)
  - Budget allocation
- Avoid simplistic budget cuts; assess whether performance is driven by creative, audience, or channel.
- Prioritise changes that improve CPA, ROAS, or conversion volume.
- Reference platform learning, seasonal trends, and scalability potential.

**Examples**
- FY Month 4: Meta contributed 38% of total conversions with ROAS 4.1 and CPA $32. Remarketing drove +22% MoM uplift.
- FY Week 17: Consideration layer delivered 57% of conversions and 52% of revenue. Carousel formats outperformed Static by +1.3 ROAS.
- Strategic: Raise frequency on Loyalty Members from 8x to 12x to lift conversion volume by +18%.
- Audience: Boomers in Awareness layer via Radio (NZME) delivered strong reach (320 TARPs) but low conversion. Recommend shifting 15% to Consideration layer with Static formats.
- Format: Carousel in Conversion layer with High Intent Shoppers delivered ROAS 4.8 vs Static at 3.2. Recommend scaling Carousel with new creative variants.

Be concise, visual (only when relevant), and data-driven. Always speak to overarching performance, not isolated campaigns. Use the full schema to reason and recommend.
"""

# Initialize chat history with system prompt
if "groq_messages" not in st.session_state:
    st.session_state.groq_messages = [{"role": "system", "content": system_prompt}]

# -------------------------------
# SAMPLE DATA
# -------------------------------
@st.cache_data(ttl=3600)
def generate_data():
    fy_year = 2025
    weeks = list(range(1, 53)) * 20  # 1040 rows

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
        fmt = formats[i % 5]
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
        ctr = ctr_lookup[fmt]

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
        impressions = int(spend / cpm_adjust[fmt] * 1000)
        clicks = int(impressions * (ctr / 100))
        revenue = spend * roas

        # Radio-specific metrics
        if fmt == "Radio" and publisher in ["NZME Radio", "MediaWorks Radio"]:
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
            "Format": fmt,
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

# Store df in session state for context window availability
if "df" not in st.session_state:
    st.session_state.df = df

# Inject data summary into system context (one-time)
if len(st.session_state.groq_messages) == 1:
    data_summary = f"""
[Dataset Context]
You have access to marketing performance data for FY 2025 with {len(df)} records.
Schema: FY Year, Week, Publisher, Strategy, Funnel Layer, Format, Creative Messaging, Audience Segment (Demographic), Audience Segment (Behavioral), Spend ($), ROAS, CTR (%), CPA ($), Impressions, Clicks, Revenue ($), TARPs (radio), Reach (%), Frequency, Spot Count, Station.
Top Publishers: {', '.join(df['Publisher'].unique()[:5])}.
Funnel Layers: Awareness, Consideration, Conversion.
Formats: Video, Static, Carousel, Interactive, Radio.
Behavioral Segments: High Intent Shoppers, Cart Abandoners, Loyalty Members.
Demographic Segments: Millennials, Boomers, Parents with Kids.

Synthesise this data to answer user questions. Always reference actual trends and segments. Generate visualisations ONLY when directly answering performance/comparison questions.
"""
    st.session_state.groq_messages.append({"role": "assistant", "content": data_summary})

# -------------------------------
# DISPLAY PREVIOUS MESSAGES
# -------------------------------
for msg in st.session_state.groq_messages:
    if msg["role"] == "assistant" and msg != st.session_state.groq_messages[1]:
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
    add_to_history(user_input)
    st.session_state.groq_messages.append({"role": "user", "content": user_input})
    
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing performance..."):
            try:
                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=st.session_state.groq_messages
                )
                output = response.choices[0].message.content
                st.markdown(output)
                st.session_state.groq_messages.append({"role": "assistant", "content": output})
            except Exception as e:
                st.error(f"Error from Groq API: {e}")

# -------------------------------
# LEGAL DISCLAIMER
# -------------------------------
st.markdown("---")
st.markdown("""
<div style="background-color: #481d00; margin-bottom: 32px; padding: 16px; font-size: 14px; border-radius: 8px;">
    <p style="margin: 0;">Legal Disclaimer — The insights and visualisations generated by this tool are for informational purposes only and should not be considered financial, legal, or business advice.</p>
</div>
""", unsafe_allow_html=True)
