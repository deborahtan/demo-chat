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
    </style>
""", unsafe_allow_html=True)

# Page title
st.title("Dentsu Intelligence Assistant")
st.markdown("*Your AI-powered insights partner for executive decision-making*")

# -------------------------------
# API KEY
# -------------------------------
api_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")

if not api_key:
    st.error("GROQ_API_KEY not found. Please set it in your environment or Streamlit secrets.")
    st.stop()

client = Groq(api_key=api_key)

system_prompt = """
You are an AI Insights Assistant for C-suite executives across Marketing, Media, Creative, CRM, Finance, and Loyalty/Product. Your mandate is to analyze enterprise-scale performance data and deliver clear, strategic, executive-ready insights supported by interactive visualizations.

Your responses must follow this structure:

- Executive Overview:
  A concise, high-level summary of the most critical findings and strategic implications. Highlight key trends, performance shifts, and business impact across funnel layers. Include quantified impact on revenue, efficiency, and ROI. This section must be boardroom-ready and suitable for presentation without additional context.

- Detailed Insight:
  A segmented, data-driven analysis by funnel layer (Awareness / Consideration / Conversion). Include:
    • Top-performing placements with performance deltas vs. benchmarks
    • Underperforming placements with root cause analysis
    • Messaging and creative performance patterns
    • Audience engagement trends and saturation signals
    • Format-channel conversion dynamics
    • Specific metrics: CPCV, Completion Rate, CPM, Viewability, CPC, CTR, CPA, ROAS, transactions, revenue
    • Comparative benchmarks and historical trends
    • Charts that directly answer the executive question with clear labeling, timeframe relevance, and annotated insights

- Strategic Recommendation:
  A strategic decision with rationale, financial impact, and risk/benefit trade-offs. Specific, operationalized format recommendations and optimization tactics:
    • Channel & placement allocation decisions with percentage shifts and expected impact (e.g., "increase YouTube from 25% to 40% of video budget; decrease TikTok from 30% to 15%. Expected ROAS lift: +12%, CPA reduction: -8%")
    • Specific tactical actions: "Increase allocation to YouTube Skippable Mid-roll (Consideration layer): achieved 8.2% CTR vs. 3.1% benchmark. Test product-focused creative variant with 15-second hook. Expected CTR improvement: 10-12%, estimated additional revenue: $45K-$65K per month"
    • Budget reallocation rationale: "Pause Display Network placements with <2% viewability. Redirect 40% budget ($180K) to programmatic video (ROAS $4.21) and allocate 20% ($90K) to search retargeting (CPA $23). Projected incremental revenue: $320K-$380K"
    • Creative testing frameworks with detailed success metrics and rollout timelines
    • "Test 3-format creative rotation (Video vs. Carousel vs. Static) on Meta Conversion layer. Current Video driving $3.87 ROAS; rotate non-performing formats weekly. Expected performance: Video maintains $3.87, Carousel targets $2.50-$2.80, Static targets $1.80-$2.20"
    • Audience targeting refinements with quantified ROI lift expectations
    • Competitive positioning and market context including seasonal trends and economic factors
    • Consider funnel layer (Awareness, Consideration, Conversion)

Always include:
- **Performance by Funnel Layer**: Comprehensive breakdown of all metrics (impressions, clicks, conversions, spend, ROAS, CPA, CPCV, Completion Rate, CPM, Viewability, CTR, CPC) by Awareness → Consideration → Conversion with trend analysis and comparative insights
- **Top Performing Placements**: Name 3-5 placements with strongest performance, quantify performance delta vs. average (e.g., "ROAS 42% above average"), include spend contribution and revenue impact
- **Underperforming Placements**: Identify placements with viewability <50%, CPCV >$2.50, completion rates <25%, or ROAS <$1.50. Detail specific reasons for underperformance and recommend pause/optimize/test with expected outcomes
- **Format Analysis**: Detailed comparison of Video, Carousel, Static Image, Interactive by CTR, CPA, ROAS, Completion Rate. Identify winner with rollout plan and expected uplift percentages
- **Charts**: Reflect the question asked with relevant timeframes. Include multiple data points and explain key findings with quantified insights
- **Summarized Tables**: Group data by Funnel Layer, Placement, Format. Make insights digestible with index to top performers
- **Evidence & Reasoning**: Dedicated section explaining how insights were derived, what assumptions were made, confidence levels, and data quality indicators
- **Engagement Diagnostics**: Message resonance, creative fatigue signals, audience saturation indicators with specific metrics and recommendations
- **Optimization Recommendations**: Specific format recommendations, creative testing approaches, messaging variants with success thresholds, channels to invest/divest with ROI projections
- **Competitive Context**: Market trends, economic factors, seasonal shifts influencing performance, competitive activity where relevant for NZ market

Paid Search Analysis:
When analyzing paid search, include detailed performance breakdowns by category, product, and message with concrete examples:
- Revenue, CPA, ROAS, impressions, CTR, spend, order value
- "Kitchen Appliances category generated $19.9K revenue from 78 purchases (avg order value $255) with CPA of $38 and ROAS of $2.10. Recommend increasing budget allocation by 30% ($22K) based on 18% ROAS premium vs. category average"
- Tactical recommendations based on performance premiums
- Extension and message-level insights with financial impact

Creative Performance Evaluation:
When evaluating creative performance, highlight standout variants with detailed contribution analysis:
- "The 'Earn' creative drove 73% of total revenue ($387K of $530K) with CTR of 2.46% (+89% vs. average) and ROAS of $5.07 (+52% vs. average). Scale across Advantage+ placements. Estimated incremental revenue at 40% budget increase: $155K-$185K"
- Contribution to revenue, CTR, ROAS vs. average
- Audience impact and placement efficiency
- Scaling recommendations with budget impact and projected revenue

Platform-Level Insights:
When referencing platform performance, include channel-level insights with strategic implications:
- Meta, YouTube, Google Search/Display, LinkedIn, TikTok, Snapchat, NZ Herald, Stuff, TVNZ, MediaWorks, NZME Radio, Trade Me
- "Meta continues to outperform benchmarks: Conversion layer showing 4.2% CTR vs. 2.8% average, ROAS of $4.15 vs. $2.90 average, Viewability at 87% vs. 76% average. Recommend increasing video budget allocation from 35% to 50% ($120K additional). Expected incremental revenue: $320K-$380K"
- "Promotional ad extensions drove 312K impressions with 2.8% CTR vs. 1.9% baseline, contributing $156K revenue — continue testing product-level relevance"
- "CTR uplift of 13% and CPC drop of 6% led to 8% more clicks at steady budget — maintain current investment level"
- Viewability, CTR, ROAS, CPM benchmarks
- Budget allocation recommendations with financial projections

Audience Strategy:
- Segment by audience type (1PD, 3PD, contextual, behavioral, lookalike, retargeting)
- "1PD audiences delivered 152 remarketing transactions (67% of total conversions) with ROAS of $14.14 and CPA of $19.99, well below $100 benchmark. Increase frequency capping from 8x to 12x daily. Expected volume increase: 18-22%, ROAS maintenance: $13.50-$14.50"
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
                    
                    impressions = np.random.randint(100_000, 2_000_000)
                    
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
                    else:
                        ctr_base = {"YouTube": 8.0, "Meta": 7.0, "TikTok": 9.0, "Google Display": 3.5, 
                                   "Programmatic Video": 6.5, "Search": 12.0, "NZ Herald": 5.5, "Stuff": 4.8,
                                   "TVNZ": 9.5, "MediaWorks": 6.5, "NZME Radio": 3.0, "Trade Me": 11.0,
                                   "We Are Frank": 7.5, "Taboola": 8.5}
                    
                    ctr = (ctr_base.get(pub, 2.0) / 100) * np.random.uniform(0.8, 1.2)
                    clicks = int(impressions * ctr)
                    
                    if layer == "Awareness":
                        cvr = np.random.uniform(0.5, 1.5) / 100
                    elif layer == "Consideration":
                        cvr = np.random.uniform(1.5, 4.0) / 100 * (1.2 if fmt == "Video" else 0.9)
                    else:
                        cvr = np.random.uniform(5.0, 12.0) / 100 * (1.3 if fmt == "Video" else 0.85)
                    
                    conversions = int(clicks * cvr)
                    
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
                    
                    params = publisher_params.get(pub, {"base_roas": 3.0, "saturation_point": 400000, "decay": 0.9})
                    base_roas = params["base_roas"]
                    saturation_pt = params["saturation_point"]
                    decay_factor = params["decay"]
                    
                    roas = base_roas / (1 + (spend / saturation_pt) ** decay_factor)
                    roas = max(roas * np.random.uniform(0.85, 1.15), 0.5)
                    
                    revenue = spend * roas
                    roi = (revenue - spend) / spend if spend > 0 else 0
                    cpa = spend / conversions if conversions > 0 else np.nan
                    
                    if fmt == "Video":
                        cpcv = np.random.uniform(0.12, 0.45)
                        completion_rate = np.random.uniform(55, 78)
                    else:
                        cpcv = np.random.uniform(0.15, 0.55)
                        completion_rate = np.random.uniform(25, 45)
                    
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

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

if "suggested_question" not in st.session_state:
    st.session_state.suggested_question = None

# Helper function to render charts
def render_chart_for_question(question, df):
    question = question.lower()

    try:
        if "diminishing returns" in question:
            publishers_list = df["Publisher"].unique()
            
            spend_buckets = []
            for pub in publishers_list:
                pub_data = df[df["Publisher"] == pub].copy()
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
            
            st.altair_chart(chart, use_container_width=True)

        elif "funnel" in question or "layer" in question:
            funnel_summary = df.groupby("Funnel Layer").agg({
                "Impressions": "sum",
                "Clicks": "sum",
                "Conversions": "sum",
                "Spend ($)": "sum",
                "Revenue ($)": "sum",
                "ROAS": "mean",
                "CPA ($)": "mean",
                "CTR (%)": "mean"
            }).reset_index()
            
            chart = alt.Chart(funnel_summary).mark_bar(color="#0066cc").encode(
                x="Funnel Layer",
                y="ROAS",
                tooltip=["Funnel Layer", "ROAS", "CPA ($)", "CTR (%)"]
            ).properties(title="Performance by Funnel Layer", width=600, height=400)
            
            st.altair_chart(chart, use_container_width=True)

        elif "top" in question or "scale" in question or "perform" in question:
            placement_summary = df.groupby(["Publisher", "Placement"]).agg({
                "Conversions": "sum",
                "Spend ($)": "sum",
                "Revenue ($)": "sum",
                "ROAS": "mean",
                "CPA ($)": "mean"
            }).reset_index().sort_values("ROAS", ascending=False)
            
            chart = alt.Chart(placement_summary.head(5)).mark_bar(color="#00b366").encode(
                x=alt.X("ROAS", title="ROAS"),
                y=alt.Y("Publisher:N", sort="-x"),
                tooltip=["Publisher", "Placement", "ROAS", "CPA ($)"]
            ).properties(title="Top 5 Performing Placements", width=600, height=400)
            
            st.altair_chart(chart, use_container_width=True)

        elif "format" in question:
            format_summary = df.groupby(["Format", "Funnel Layer"]).agg({
                "ROAS": "mean",
                "CPA ($)": "mean",
                "CTR (%)": "mean"
            }).reset_index()
            
            chart = alt.Chart(format_summary).mark_bar().encode(
                x="Format",
                y="ROAS",
                color="Funnel Layer",
                tooltip=["Format", "Funnel Layer", "ROAS"]
            ).properties(title="Format Performance", width=600, height=400)
            
            st.altair_chart(chart, use_container_width=True)

    except Exception as e:
        st.error(f"Error rendering chart: {str(e)}")

# Display chat history
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user", avatar="👤"):
            st.markdown(msg["content"])
    else:
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(msg["content"])
            if "chart_data" in msg:
                render_chart_for_question(msg["question"], df)

# Chat input
col1, col2 = st.columns([3, 1])

with col1:
    user_input = st.chat_input("Ask me anything about your media performance...")

with col2:
    st.markdown("**Suggested Questions:**")
    
    QUESTIONS = [
        "Analyze diminishing returns by channel and spend curve.",
        "Identify top-performing publishers by audience segment.",
        "Recommend optimal channel mixes for $100M, $200M, and $300M investment levels.",
        "Determine which formats delivered the highest ROI and CPA.",
        "Evaluate channels & publishers with the strongest click-to-conversion rates.",
        "Highlight months with the highest churn and distinguish internal vs. external drivers.",
        "Advise what to scale, pause, or optimize for maximum efficiency.",
        "Provide creative testing recommendations with specific format and messaging approaches."
    ]
    
    for question in QUESTIONS:
        if st.button(question, use_container_width=True):
            user_input = question
            st.session_state.suggested_question = question
            st.rerun()

if user_input:
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)
    
    # Generate response
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Analyzing data..."):
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": system_prompt},
                    *[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages if "chart_data" not in m]
                ]
            )
            
            detailed = response.choices[0].message.content
            st.markdown(detailed)
            
            # Add assistant response to history
            st.session_state.messages.append({
                "role": "assistant", 
                "content": detailed,
                "question": user_input,
                "chart_data": True
            })
            
            # Render chart
            render_chart_for_question(user_input, df)

# Legal disclaimer at bottom
st.markdown("---")
st.caption("Legal Disclaimer - The insights and visualizations generated by this tool are for informational purposes only and should not be considered financial, legal, or business advice.")
