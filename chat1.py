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
    st.error("GROQ_API_KEY not found. Please set it in your environment or Streamlit secrets.")
    st.stop()

client = Groq(api_key=api_key)

# -------------------------------
# SYSTEM PROMPT
# -------------------------------
system_prompt = """
You are an AI Insights Assistant for C-suite executives across Marketing, Media, Creative, CRM, Finance, and Loyalty/Product. Your mandate is to analyze enterprise-scale performance data and deliver clear, strategic, executive-ready insights supported by interactive visualizations.

Your responses must follow this structure:
- Insight: A precise, data-driven finding segmented by funnel layer (Awareness / Consideration / Conversion). Include top-performing placements, performance deltas vs. benchmarks, messaging approaches, and engagement patterns. Reference specific metrics: CPCV, Completion Rate, CPM, Viewability, CPC, CTR, CPA, ROAS, transactions, revenue. Provide detailed analysis with multiple data points and quantified findings.

- Recommendation: A strategic decision with rationale, financial impact, and risk/benefit trade-offs. Specific, operationalized format recommendations and optimization tactics:
  • Channel & placement allocation decisions with percentage shifts and expected impact
  • Tactical actions with performance benchmarks and financial projections
  • Budget reallocation rationale with ROI uplift estimates
  • Creative testing frameworks with success metrics and rollout timelines
  • Format rotation strategies with expected performance ranges
  • Audience targeting refinements with quantified ROI lift expectations
  • Competitive positioning and market context including seasonal trends and economic factors
  • Always consider funnel layer (Awareness, Consideration, Conversion)

Always include:
- Performance by Funnel Layer: Breakdown of all metrics (impressions, clicks, conversions, spend, ROAS, CPA, CPCV, Completion Rate, CPM, Viewability, CTR, CPC) by Awareness → Consideration → Conversion with trend analysis and comparative insights
- Top Performing Placements: Name 3–5 placements with strongest performance, quantify performance delta vs. average, include spend contribution and revenue impact
- Underperforming Placements: Identify placements with viewability <50%, CPCV >$2.50, completion rates <25%, or ROAS <$1.50. Detail reasons for underperformance and recommend pause/optimize/test actions
- Format Analysis: Compare Video, Carousel, Static Image, Interactive by CTR, CPA, ROAS, Completion Rate. Identify winner with rollout plan and expected uplift percentages. Include commentary on format-channel fit and conversion type suitability
- Charts: Must directly answer the executive question asked. Include relevant timeframes, multiple data points, and clearly explain key findings with quantified insights
- Summarized Tables: Group data by Funnel Layer, Placement, Format. Make insights digestible with index to top performers
- Evidence & Reasoning: Explain how insights were derived, what assumptions were made, confidence levels, and data quality indicators
- Engagement Diagnostics: Message resonance, creative fatigue signals, audience saturation indicators with specific metrics and recommendations
- Optimization Recommendations: Specific format recommendations, creative testing approaches, messaging variants with success thresholds, channels to invest/divest with ROI projections
- Competitive Context: Market trends, economic factors, seasonal shifts influencing performance, competitive activity relevant to NZ market

Strategic Intelligence Additions:

Audience Strategy:
- Segment by audience type (1PD, 3PD, contextual, behavioral, lookalike, retargeting)
- Recommend layering strategies and frequency caps to reduce CPA and improve ROAS
- Identify overexposed audiences and recommend rotation/suppression

Creative Diagnostics:
- Highlight top-performing creative variants with contribution analysis
- Flag fatigue indicators and recommend refresh cadence
- Recommend modular testing of headlines, CTAs, visuals with projected uplift

Portfolio Optimization:
- Recommend trade-offs across channels, formats, funnel layers with quantified opportunity cost
- Identify saturation points and recommend pacing strategies (flighting, dayparting, frequency)
- Quantify halo effects (e.g., YouTube → branded search lift)

Competitive Intelligence:
- Benchmark against category averages and competitor activity
- Reference macroeconomic indicators and seasonal shifts
- Recommend proactive positioning strategies

Paid Search Deep Dive:
Include detailed breakdowns by category, product, and message:
- Revenue, CPA, ROAS, impressions, CTR, spend, order value
- Tactical recommendations based on performance premiums
- Extension and message-level insights with financial impact

Creative Performance Deep Dive:
Highlight standout variants:
- Contribution to revenue, CTR, ROAS vs. average
- Audience impact and placement efficiency
- Scaling recommendations with budget impact and projected revenue

Platform-Level Insights:
Include channel-level strategic implications:
- Meta, YouTube, Google Search/Display, LinkedIn, TikTok, Snapchat
- Viewability, CTR, ROAS, CPM benchmarks
- Budget allocation recommendations with financial projections

NZ Market Context:
Always account for:
- Funnel layers (Awareness, Consideration, Conversion)
- Local NZ platforms and publishers (Meta, YouTube, Google, LinkedIn, TikTok, Snapchat, NZ Herald, Stuff, TVNZ, MediaWorks, NZME Radio, Trade Me)
- Format performance (Video, Carousel, Static, Interactive)
- Metrics (CPCV, Completion Rate, CPM, Viewability, CPC, CTR, CPA, ROAS)
- Portfolio trade-offs and opportunity costs

Goal:
Transform complex performance data into specific, quantified insights, valid strategic actions, and rigorously grounded recommendations that drive executive confidence and measurable results with clear ROI projections.
"""


# -------------------------------
# SAMPLE DATA WITH REAL DIMINISHING RETURNS
# -------------------------------
@st.cache_data
def generate_data():
    """
    Generate realistic media campaign data with real diminishing returns curves.
    Uses power law decay: ROAS = base_roas / (1 + (spend/saturation_point)^decay_factor)
    """
    np.random.seed(42)
    
    months = pd.date_range(end="2025-09-30", periods=12, freq="MS")
    
    publishers = ["YouTube", "Meta", "TikTok", "Google Display", "Programmatic Video", "Search", 
                  "NZ Herald", "Stuff", "TVNZ", "MediaWorks", "NZME Radio", "Trade Me", "We Are Frank", "Taboola"]
    funnel_layers = ["Awareness", "Consideration", "Conversion"]
    formats = ["Video", "Carousel", "Static Image", "Interactive"]
    placements = {
        "YouTube": ["Skippable Pre-roll", "Skippable Mid-roll", "Non-skippable", "In-stream Masthead"],
        "Meta": ["Feed", "Reels", "Stories", "Audience Network"],
        "TikTok": ["For You Page", "Branded Content", "Top Tier"],
        "Google Display": ["Top Banner", "Sidebar", "Interstitial", "Native"],
        "Programmatic Video": ["Header Bidding", "Open Exchange", "Private Marketplace"],
        "Search": ["Brand Keywords", "Generic Keywords", "Long-tail"],
        "NZ Herald": ["Homepage", "Article Embed", "Sidebar", "Native"],
        "Stuff": ["Homepage", "News Feed", "Sponsored", "Content Recommendation"],
        "TVNZ": ["Pre-roll", "Mid-roll", "Post-roll", "Bumper"],
        "MediaWorks": ["Pre-roll Video", "Display", "Native", "Sponsorship"],
        "NZME Radio": ["Audio Ad", "Podcast", "Streaming", "Display"],
        "Trade Me": ["Sponsored Results", "Homepage", "Category Pages", "Email"],
        "We Are Frank": ["Native Content", "Sponsored Articles", "Video", "Sponsored Feeds"],
        "Taboola": ["Content Recommendations", "Native Ads", "Video Ads", "Display"]
    }

    # Define diminishing returns curves per publisher (realistic media decay)
    publisher_params = {
        "YouTube": {"base_roas": 5.5, "saturation_point": 500000, "decay": 0.8},
        "Meta": {"base_roas": 4.2, "saturation_point": 400000, "decay": 0.9},
        "TikTok": {"base_roas": 3.8, "saturation_point": 300000, "decay": 1.1},
        "Google Display": {"base_roas": 2.1, "saturation_point": 250000, "decay": 1.2},
        "Programmatic Video": {"base_roas": 4.8, "saturation_point": 550000, "decay": 0.75},
        "Search": {"base_roas": 6.2, "saturation_point": 600000, "decay": 0.6},
        "NZ Herald": {"base_roas": 2.8, "saturation_point": 180000, "decay": 1.4},
        "Stuff": {"base_roas": 2.5, "saturation_point": 160000, "decay": 1.5},
        "TVNZ": {"base_roas": 3.9, "saturation_point": 350000, "decay": 1.0},
        "MediaWorks": {"base_roas": 2.9, "saturation_point": 200000, "decay": 1.3},
        "NZME Radio": {"base_roas": 1.8, "saturation_point": 120000, "decay": 1.6},
        "Trade Me": {"base_roas": 4.5, "saturation_point": 450000, "decay": 0.85},
        "We Are Frank": {"base_roas": 3.2, "saturation_point": 220000, "decay": 1.2},
        "Taboola": {"base_roas": 2.4, "saturation_point": 140000, "decay": 1.4}
    }

    rows = []
    
    for m in months:
        for pub in publishers:
            for layer in funnel_layers:
                for fmt in formats:
                    placement = np.random.choice(placements[pub])
                    
                    # Generate cumulative spend across the period
                    impressions = np.random.randint(100_000, 2_000_000)
                    
                    # CTR varies by layer and publisher
                    if layer == "Awareness":
                        ctr_base = {"YouTube": 1.5, "Meta": 1.2, "TikTok": 2.0, "Google Display": 0.8, 
                                   "Programmatic Video": 1.0, "Search": 2.5, "NZ Herald": 0.6, "Stuff": 0.5,
                                   "TVNZ": 1.8, "MediaWorks": 1.0, "NZME Radio": 0.3, "Trade Me": 1.2,
                                   "We Are Frank": 1.5, "Taboola": 2.2}
                    elif layer == "Consideration":
                        ctr_base = {"YouTube": 4.0, "Meta": 3.5, "TikTok": 5.5, "Google Display": 2.0, 
                                   "Programmatic Video": 3.2, "Search": 8.0, "NZ Herald": 2.5, "Stuff": 2.2,
                                   "TVNZ": 5.0, "MediaWorks": 3.5, "NZME Radio": 1.5, "Trade Me": 6.5,
                                   "We Are Frank": 4.0, "Taboola": 5.8}
                    else:  # Conversion
                        ctr_base = {"YouTube": 8.0, "Meta": 7.0, "TikTok": 9.0, "Google Display": 3.5, 
                                   "Programmatic Video": 6.5, "Search": 12.0, "NZ Herald": 5.5, "Stuff": 4.8,
                                   "TVNZ": 9.5, "MediaWorks": 6.5, "NZME Radio": 3.0, "Trade Me": 11.0,
                                   "We Are Frank": 7.5, "Taboola": 8.5}
                    
                    ctr = (ctr_base.get(pub, 2.0) / 100) * np.random.uniform(0.8, 1.2)
                    clicks = int(impressions * ctr)
                    
                    # CVR varies by layer and format
                    if layer == "Awareness":
                        cvr = np.random.uniform(0.5, 1.5) / 100
                    elif layer == "Consideration":
                        cvr = np.random.uniform(1.5, 4.0) / 100 * (1.2 if fmt == "Video" else 0.9)
                    else:  # Conversion
                        cvr = np.random.uniform(5.0, 12.0) / 100 * (1.3 if fmt == "Video" else 0.85)
                    
                    conversions = int(clicks * cvr)
                    
                    # CPC by publisher (realistic market rates)
                    cpc_ranges = {
                        "Search": (1.2, 3.5),
                        "Trade Me": (1.0, 2.8),
                        "YouTube": (0.25, 1.0),
                        "Programmatic Video": (0.20, 0.85),
                        "Meta": (0.30, 1.2),
                        "TikTok": (0.25, 1.0),
                        "Google Display": (0.20, 0.80),
                        "TVNZ": (0.40, 1.5),
                        "NZ Herald": (0.35, 1.2),
                        "Stuff": (0.30, 1.0),
                        "MediaWorks": (0.25, 0.95),
                        "NZME Radio": (0.15, 0.60),
                        "We Are Frank": (0.20, 0.80),
                        "Taboola": (0.25, 0.90)
                    }
                    cpc_min, cpc_max = cpc_ranges.get(pub, (0.25, 1.0))
                    cpc = np.random.uniform(cpc_min, cpc_max)
                    spend = clicks * cpc
                    
                    # Apply diminishing returns curve based on spend level
                    params = publisher_params.get(pub, {"base_roas": 3.0, "saturation_point": 400000, "decay": 0.9})
                    base_roas = params["base_roas"]
                    saturation_pt = params["saturation_point"]
                    decay_factor = params["decay"]
                    
                    # Power law: ROAS declines as spend increases
                    roas = base_roas / (1 + (spend / saturation_pt) ** decay_factor)
                    roas = max(roas * np.random.uniform(0.85, 1.15), 0.5)
                    
                    revenue = spend * roas
                    roi = (revenue - spend) / spend if spend > 0 else 0
                    cpa = spend / conversions if conversions > 0 else np.nan
                    
                    # Video-specific metrics with realistic ranges
                    if fmt == "Video":
                        cpcv = np.random.uniform(0.12, 0.45)
                        completion_rate = np.random.uniform(55, 78)
                    else:
                        cpcv = np.random.uniform(0.15, 0.55)
                        completion_rate = np.random.uniform(25, 45)
                    
                    # CPM by publisher
                    cpm_ranges = {
                        "Search": (3, 7),
                        "YouTube": (5, 15),
                        "Meta": (6, 12),
                        "TikTok": (6, 11),
                        "Google Display": (2, 6),
                        "Programmatic Video": (4, 10),
                        "Trade Me": (4, 9),
                        "TVNZ": (8, 18),
                        "NZ Herald": (5, 12),
                        "Stuff": (4, 10),
                        "MediaWorks": (5, 11),
                        "NZME Radio": (2, 6),
                        "We Are Frank": (3, 8),
                        "Taboola": (2, 6)
                    }
                    cpm_min, cpm_max = cpm_ranges.get(pub, (3, 8))
                    cpm = np.random.uniform(cpm_min, cpm_max)
                    
                    # Viewability with realistic ranges per publisher
                    viewability_ranges = {
                        "YouTube": (65, 85),
                        "Programmatic Video": (60, 80),
                        "Meta": (75, 90),
                        "TikTok": (80, 92),
                        "Google Display": (45, 65),
                        "Search": (80, 95),
                        "Trade Me": (70, 85),
                        "TVNZ": (75, 88),
                        "NZ Herald": (55, 75),
                        "Stuff": (50, 70),
                        "MediaWorks": (60, 80),
                        "NZME Radio": (65, 85),
                        "We Are Frank": (62, 82),
                        "Taboola": (45, 65)
                    }
                    view_min, view_max = viewability_ranges.get(pub, (60, 80))
                    viewability = np.random.uniform(view_min, view_max)
                    
                    clv = np.random.uniform(600, 2000)

                    rows.append([
                        m, pub, layer, placement, fmt, impressions, clicks, conversions,
                        spend, revenue, roas, roi, cpa, cpc, ctr * 100, cpcv, 
                        completion_rate, cpm, viewability, clv
                    ])

    df = pd.DataFrame(rows, columns=[
        "Month", "Publisher", "Funnel Layer", "Placement", "Format", 
        "Impressions", "Clicks", "Conversions",
        "Spend ($)", "Revenue ($)", "ROAS", "ROI", "CPA ($)", "CPC ($)", "CTR (%)", 
        "CPCV ($)", "Completion Rate (%)", "CPM ($)", "Viewability (%)", "CLV ($)"
    ])

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
        - The assistant will generate comprehensive, data-driven insights with detailed analysis.  
        - Your recent questions will appear below for quick re-selection.  
        """
    )

    QUESTIONS = [
        "Analyze diminishing returns by publisher and identify exact saturation point where ROAS declines.",
        "Evaluate performance by funnel layer (Awareness, Consideration, Conversion) and recommend budget allocation.",
        "Identify top-performing placements and formats. What should we scale and what should we pause?",
        "Assess underperforming placements. Which have viewability issues or high CPCV?",
        "Recommend format strategy: Video vs. Carousel vs. Static. Which drives best ROAS and lowest CPA?",
        "Analyze CTR and CPC by publisher. Where are we getting strongest engagement efficiency?",
        "Provide creative testing recommendations with specific format and messaging approaches.",
        "What is the optimal budget allocation across awareness, consideration, and conversion layers?"
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
        if st.button("Clear History"):
            st.session_state.recent_questions = []

# -------------------------------
# CHART RENDERING WITH REAL DIMINISHING RETURNS
# -------------------------------
def render_chart_for_question(question, df):
    question = question.lower()

    try:
        if "diminishing returns" in question:
            # Group data by spend increments to show saturation curve
            publishers_list = df["Publisher"].unique()
            
            spend_buckets = []
            for pub in publishers_list:
                pub_data = df[df["Publisher"] == pub].copy()
                
                # Sort by spend and create percentile-based buckets
                pub_data_sorted = pub_data.sort_values("Spend ($)").reset_index(drop=True)
                n_buckets = 10
                
                for i in range(n_buckets):
                    start_idx = int(len(pub_data_sorted) * i / n_buckets)
                    end_idx = int(len(pub_data_sorted) * (i + 1) / n_buckets)
                    bucket = pub_data_sorted.iloc[start_idx:end_idx]
                    
                    if len(bucket) > 0:
                        total_spend = bucket["Spend ($)"].sum()
                        avg_roas = bucket["ROAS"].mean()
                        avg_impressions = bucket["Impressions"].mean()
                        
                        spend_buckets.append({
                            "Publisher": pub,
                            "Spend Level": f"${total_spend/1_000_000:.2f}M",
                            "Spend ($)": total_spend,
                            "ROAS": avg_roas,
                            "Impressions (avg)": avg_impressions,
                            "Bucket": i + 1
                        })
            
            df_diminishing = pd.DataFrame(spend_buckets)
            
            # Create line chart showing real diminishing returns
            chart = alt.Chart(df_diminishing).mark_line(point=True, size=3).encode(
                x=alt.X("Bucket:Q", title="Spend Bucket (Low to High)"),
                y=alt.Y("ROAS:Q", title="Average ROAS"),
                color=alt.Color("Publisher", title="Publisher"),
                tooltip=["Publisher", "Spend Level", "ROAS", "Impressions (avg)"]
            ).properties(
                title="Diminishing Returns Analysis: ROAS Degradation by Spend Level",
                width=600,
                height=400
            ).interactive()
            
            col1, col2 = st.columns([2, 1])
            with col1:
                st.altair_chart(chart, use_container_width=True)
            
            with col2:
                st.markdown("### Saturation Points")
                st.markdown("*Peak ROAS vs. saturation threshold:*")
                
                for pub in publishers_list:
                    pub_data = df_diminishing[df_diminishing["Publisher"] == pub]
                    if len(pub_data) > 3:
                        peak_roas = pub_data["ROAS"].max()
                        peak_bucket = pub_data[pub_data["ROAS"] == peak_roas]["Bucket"].values[0]
                        
                        # Find where ROAS drops to 80% of peak
                        threshold = pub_data[pub_data["ROAS"] < peak_roas * 0.80]
                        if len(threshold) > 0:
                            sat_bucket = int(threshold["Bucket"].values[0])
                            sat_spend = threshold["Spend Level"].values[0]
                            sat_roas = threshold["ROAS"].values[0]
                            decline = ((peak_roas - sat_roas) / peak_roas) * 100
                            
                            st.metric(
                                label=f"{pub}",
                                value=f"${sat_roas:.2f}",
                                delta=f"{decline:.1f}% decline"
                            )
            
            st.dataframe(df_diminishing, use_container_width=False, width=700)

        elif "funnel layer" in question:
            funnel_summary = df.groupby("Funnel Layer").agg({
                "Impressions": "sum",
                "Clicks": "sum",
                "Conversions": "sum",
                "Spend ($)": "sum",
                "Revenue ($)": "sum",
                "ROAS": "mean",
                "CPA ($)": "mean",
                "CTR (%)": "mean",
                "Viewability (%)": "mean"
            }).reset_index()
            
            chart = alt.Chart(funnel_summary).mark_bar(color="#0066cc").encode(
                x="Funnel Layer",
                y="ROAS",
                tooltip=["Funnel Layer", "ROAS", "CPA ($)", "CTR (%)", "Conversions"]
            ).properties(
                title="Performance by Funnel Layer: ROAS",
                width=600,
                height=400
            )
            
            col1, col2 = st.columns([2, 1])
            with col1:
                st.altair_chart(chart, use_container_width=True)
            
            with col2:
                st.markdown("### Funnel Metrics")
                for _, row in funnel_summary.iterrows():
                    st.metric(
                        label=row["Funnel Layer"],
                        value=f"${row['ROAS']:.2f}",
                        delta=f"CPA: ${row['CPA ($)']:.2f}"
                    )
            
            st.dataframe(funnel_summary, use_container_width=False, width=700)

        elif "top-performing" in question or "scale" in question:
            placement_summary = df.groupby(["Publisher", "Placement", "Format"]).agg({
                "Clicks": "sum",
                "Conversions": "sum",
                "Spend ($)": "sum",
                "Revenue ($)": "sum",
                "ROAS": "mean",
                "CPA ($)": "mean",
                "CTR (%)": "mean",
                "Viewability (%)": "mean"
            }).reset_index().sort_values("ROAS", ascending=False)
            
            top_placements = placement_summary.head(5)
            
            chart = alt.Chart(top_placements).mark_bar(color="#00b366").encode(
                x=alt.X("ROAS", title="ROAS"),
                y=alt.Y("Publisher:N", sort="-x"),
                tooltip=["Publisher", "Placement", "Format", "ROAS", "CPA ($)"]
            ).properties(
                title="Top 5 Performing Placements by ROAS",
                width=600,
                height=400
            )
            
            col1, col2 = st.columns([2, 1])
            with col1:
                st.altair_chart(chart, use_container_width=True)
            
            with col2:
                st.markdown("### Top Performers")
                for i, (_, row) in enumerate(top_placements.iterrows(), 1):
                    st.metric(
                        label=f"#{i} {row['Publisher']} - {row['Format']}",
                        value=f"${row['ROAS']:.2f}",
                        delta=f"Spend: ${row['Spend ($)']/1000:.0f}K"
                    )
            
            st.dataframe(top_placements, use_container_width=False, width=700)

        elif "underperforming" in question:
            underperforming = df[
                (df["Viewability (%)"] < 50) | 
                (df["CPCV ($)"] > 2.50) | 
                (df["Completion Rate (%)"] < 25) |
                (df["ROAS"] < 1.50)
            ].groupby(["Publisher", "Placement"]).agg({
                "Spend ($)": "sum",
                "ROAS": "mean",
                "Viewability (%)": "mean",
                "CPCV ($)": "mean",
                "Completion Rate (%)": "mean"
            }).reset_index().sort_values("ROAS")
            
            if len(underperforming) > 0:
                chart = alt.Chart(underperforming).mark_bar(color="#ff6b6b").encode(
                    x="ROAS",
                    y=alt.Y("Publisher:N", sort="x"),
                    tooltip=["Publisher", "Placement", "ROAS", "Viewability (%)", "CPCV ($)"]
                ).properties(
                    title="Underperforming Placements",
                    width=600,
                    height=400
                )
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.altair_chart(chart, use_container_width=True)
                
                with col2:
                    st.markdown("### Issues Detected")
                    for i, (_, row) in enumerate(underperforming.head(3).iterrows(), 1):
                        st.metric(
                            label=f"{row['Publisher']}",
                            value=f"${row['ROAS']:.2f}",
                            delta=f"View: {row['Viewability (%)']:.0f}%"
                        )
                
                st.dataframe(underperforming, use_container_width=False, width=700)
            else:
                st.info("No significantly underperforming placements detected.")

        elif "format" in question:
            format_summary = df.groupby(["Format", "Funnel Layer"]).agg({
                "Conversions": "sum",
                "Spend ($)": "sum",
                "Revenue ($)": "sum",
                "ROAS": "mean",
                "CPA ($)": "mean",
                "CTR (%)": "mean",
                "Completion Rate (%)": "mean"
            }).reset_index()
            
            chart = alt.Chart(format_summary).mark_bar().encode(
                x="Format",
                y="ROAS",
                color="Funnel Layer",
                tooltip=["Format", "Funnel Layer", "ROAS", "CPA ($)", "CTR (%)"]
            ).properties(
                title="Format Performance by Funnel Layer",
                width=600,
                height=400
            )
            
            col1, col2 = st.columns([2, 1])
            with col1:
                st.altair_chart(chart, use_container_width=True)
            
            with col2:
                st.markdown("### Format Rankings")
                format_avg = format_summary.groupby("Format").agg({"ROAS": "mean"}).sort_values("ROAS", ascending=False)
                for i, (fmt, roas) in enumerate(format_avg.iterrows(), 1):
                    st.metric(
                        label=f"#{i} {fmt}",
                        value=f"${roas['ROAS']:.2f}",
                        delta="Avg ROAS"
                    )
            
            st.dataframe(format_summary, use_container_width=False, width=700)

        elif "ctr" in question or "cpc" in question:
            publisher_summary = df.groupby("Publisher").agg({
                "CTR (%)": "mean",
                "CPC ($)": "mean",
                "Conversions": "sum",
                "Revenue ($)": "sum",
                "ROAS": "mean"
            }).reset_index().sort_values("CTR (%)", ascending=False)
            
            chart = alt.Chart(publisher_summary).mark_bar(color="#6b5bff").encode(
                x="CTR (%)",
                y=alt.Y("Publisher", sort="-x"),
                tooltip=["Publisher", "CTR (%)", "CPC ($)", "ROAS"]
            ).properties(
                title="CTR vs CPC by Publisher",
                width=600,
                height=400
            )
            
            col1, col2 = st.columns([2, 1])
            with col1:
                st.altair_chart(chart, use_container_width=True)
            
            with col2:
                st.markdown("### Engagement Leaders")
                for i, (_, row) in enumerate(publisher_summary.head(3).iterrows(), 1):
                    st.metric(
                        label=f"#{i} {row['Publisher']}",
                        value=f"{row['CTR (%)']:.2f}%",
                        delta=f"CPC: ${row['CPC ($)']:.2f}"
                    )
            
            st.dataframe(publisher_summary, use_container_width=False, width=700)

    except Exception as e:
        st.error(f"Error rendering chart: {str(e)}")


# -------------------------------
# Render Structured Answer
# -------------------------------
with st.container():
    st.subheader("Detailed Analysis")
    if question_to_answer and client:
        with st.spinner("Generating comprehensive analysis..."):
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Provide detailed structured answer for: {question_to_answer}. Generate comprehensive sections with specific data points, quantified recommendations, financial impact projections, and strategic rationale. Minimum 1500 characters per section. Include Insight (performance analysis with 5+ data points), Recommendation (3-5 specific tactical actions with ROI impact), and Next Steps (owners, timelines, success metrics)."}
                ]
            )
            detailed = response.choices[0].message.content

        # Parse response into sections
        sections = {"Insight": "", "Recommendation": "", "Next Steps": ""}
        current = None
        current_section = ""
        
        for line in detailed.splitlines():
            # Check if line contains a section header
            if "Insight" in line and "Insight" not in current_section:
                if current:
                    sections[current] = current_section.strip()
                current = "Insight"
                current_section = ""
            elif "Recommendation" in line and "Recommendation" not in current_section:
                if current:
                    sections[current] = current_section.strip()
                current = "Recommendation"
                current_section = ""
            elif "Next Steps" in line and "Next Steps" not in current_section:
                if current:
                    sections[current] = current_section.strip()
                current = "Next Steps"
                current_section = ""
            elif current:
                current_section += line + "\n"
        
        # Catch final section
        if current:
            sections[current] = current_section.strip()

        # Render sections
        with st.expander("Insight - Performance Analysis", expanded=True):
            if sections["Insight"]:
                st.markdown(sections["Insight"])
                st.divider()
                render_chart_for_question(question_to_answer, df)
            else:
                st.write("Generating insight analysis...")

        with st.expander("Recommendation - Strategic Actions", expanded=False):
            if sections["Recommendation"]:
                st.markdown(sections["Recommendation"])
            else:
                st.write("Generating recommendations...")

        with st.expander("Next Steps - Execution Plan", expanded=False):
            if sections["Next Steps"]:
                st.markdown(sections["Next Steps"])
            else:
                st.write("Generating next steps...")

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
