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
- **Insight**: A precise, data-driven finding segmented by funnel layer (Awareness/Consideration/Conversion). Include top-performing placements, performance deltas vs. benchmarks, messaging approaches, and engagement patterns. Reference specific metrics: CPCV, Completion Rate, CPM, Viewability, CPC, CTR, CPA, ROAS, transactions, revenue.
- **Recommendation**: A strategic decision with rationale, financial impact, and risk/benefit trade-offs. Specific, operationalized format recommendations and optimization tactics:
  • Channel & placement allocation decisions (e.g., "increase YouTube from 25% to 40% of video budget; decrease TikTok from 30% to 15%")
  • "Increase allocation to YouTube Skippable Mid-roll (Consideration layer): achieved 8.2% CTR vs. 3.1% benchmark. Test product-focused creative variant with 15-second hook."
  • "Pause Display Network placements with <2% viewability. Redirect 40% budget to programmatic video (ROAS $4.21) and allocate 20% to search retargeting (CPA $23)."
  • Creative testing framework and success metrics
  • "Test 3-format creative rotation (Video vs. Carousel vs. Static) on Meta Conversion layer. Current Video driving $3.87 ROAS; rotate non-performing formats weekly."
  • Audience targeting refinements with expected ROI lift
  • Competitive positioning and market insights

Always include:
- **Performance by Funnel Layer**: Break down all metrics (impressions, clicks, conversions, spend, ROAS, CPA, CPCV, Completion Rate, CPM, Viewability, CTR, CPC) by Awareness → Consideration → Conversion.
- **Top Performing Placements**: Name 3-5 placements with strongest performance on CPC, CTR, ROAS metrics. Quantify performance delta vs. average.
- **Underperforming Placements**: Identify placements with viewability <50%, CPCV >$2.50, completion rates <25%, or ROAS <$1.50. Recommend pause/optimize/test.
- **Format Analysis**: Compare Video, Carousel, Static Image, Interactive by CTR, CPA, ROAS, Completion Rate. Identify winner and rollout plan.
- **Charts** to reflect the question asked. Include relevant timeframes in all charts. Explain all key datapoints with summaries.
- **Summarized tables**: Group data by Funnel Layer, Placement, Format to make insights digestible.
- A dedicated **Evidence & Reasoning** section explaining how insights were derived, assumptions made, and confidence levels.
- **Engagement Diagnostics**: Message resonance, creative fatigue signals, audience saturation indicators.
- **Optimization Recommendations**: Specific format recommendations, creative testing approaches, messaging variants to test, channels to invest/divest in.

Core responsibilities:
- Structure every response: Insight → Recommendation → Next Steps.
- Ensure each element is specific, evidence-based, and actionable.
- For Diminishing Returns analysis: Identify the inflection point where ROAS begins declining by spend level. Quantify the saturation curve and recommend optimal spend threshold for each channel.
- Deliver all outputs in professional, concise, boardroom-ready language supporting decision-making.

Your goal: transform complex performance data into specific insights, valid actions, and strategically grounded recommendations that drive executive confidence and measurable results.
"""

# -------------------------------
# SAMPLE DATA WITH REAL DIMINISHING RETURNS
# -------------------------------
@st.cache_data
def generate_data():
    """
    Generate realistic media campaign data with real diminishing returns curves.
    Uses power law decay: ROAS = base_roas / (1 + (spend/saturation_point)^decay_factor)
    This mimics real media performance where audience overlap and frequency saturation reduce returns.
    """
    np.random.seed(42)
    
    months = pd.date_range(end="2025-09-30", periods=12, freq="MS")
    
    publishers = ["YouTube", "Meta", "TikTok", "Google Display", "Programmatic Video", "Search", "LinkedIn"]
    funnel_layers = ["Awareness", "Consideration", "Conversion"]
    formats = ["Video", "Carousel", "Static Image", "Interactive"]
    placements = {
        "YouTube": ["Skippable Pre-roll", "Skippable Mid-roll", "Non-skippable", "In-stream Masthead"],
        "Meta": ["Feed", "Reels", "Stories", "Audience Network"],
        "TikTok": ["For You Page", "Branded Content", "Top Tier"],
        "Google Display": ["Top Banner", "Sidebar", "Interstitial", "Native"],
        "Programmatic Video": ["Header Bidding", "Open Exchange", "Private Marketplace"],
        "Search": ["Brand Keywords", "Generic Keywords", "Long-tail"],
        "LinkedIn": ["Sponsored Content", "Sponsored InMail", "Text Ads"]
    }

    # Define diminishing returns curves per publisher (realistic media decay)
    publisher_params = {
        "YouTube": {"base_roas": 5.5, "saturation_point": 500000, "decay": 0.8},
        "Meta": {"base_roas": 4.2, "saturation_point": 400000, "decay": 0.9},
        "TikTok": {"base_roas": 3.8, "saturation_point": 300000, "decay": 1.1},
        "Google Display": {"base_roas": 2.1, "saturation_point": 250000, "decay": 1.2},
        "Programmatic Video": {"base_roas": 4.8, "saturation_point": 550000, "decay": 0.75},
        "Search": {"base_roas": 6.2, "saturation_point": 600000, "decay": 0.6},
        "LinkedIn": {"base_roas": 3.5, "saturation_point": 200000, "decay": 1.3}
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
                                   "Programmatic Video": 1.0, "Search": 2.5, "LinkedIn": 0.6}
                    elif layer == "Consideration":
                        ctr_base = {"YouTube": 4.0, "Meta": 3.5, "TikTok": 5.5, "Google Display": 2.0, 
                                   "Programmatic Video": 3.2, "Search": 8.0, "LinkedIn": 2.5}
                    else:  # Conversion
                        ctr_base = {"YouTube": 8.0, "Meta": 7.0, "TikTok": 9.0, "Google Display": 3.5, 
                                   "Programmatic Video": 6.5, "Search": 12.0, "LinkedIn": 5.0}
                    
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
                        "LinkedIn": (1.5, 4.0),
                        "YouTube": (0.25, 1.0),
                        "Programmatic Video": (0.20, 0.85),
                        "Meta": (0.30, 1.2),
                        "TikTok": (0.25, 1.0),
                        "Google Display": (0.20, 0.80)
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
                    roas = max(roas * np.random.uniform(0.85, 1.15), 0.5)  # Add realistic variance
                    
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
                        "LinkedIn": (8, 18)
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
                        "LinkedIn": (70, 88)
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
        - The assistant will generate structured insights with funnel-layer analysis and relevant charts.  
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
                width=900,
                height=450
            ).interactive()
            
            st.altair_chart(chart, use_container_width=True)
            
            st.markdown("### Saturation Point Analysis")
            st.markdown("Each publisher shows where spending more yields declining returns due to audience overlap and frequency saturation:")
            
            for pub in publishers_list:
                pub_data = df_diminishing[df_diminishing["Publisher"] == pub]
                if len(pub_data) > 3:
                    peak_roas = pub_data["ROAS"].max()
                    peak_bucket = pub_data[pub_data["ROAS"] == peak_roas]["Bucket"].values[0]
                    
                    # Find where ROAS drops to 80% of peak
                    threshold = pub_data[pub_data["ROAS"] < peak_roas * 0.80]
                    if len(threshold) > 0:
                        saturation_bucket = threshold["Bucket"].values[0]
                        saturation_spend = threshold["Spend Level"].values[0]
                        saturation_roas = threshold["ROAS"].values[0]
                        
                        col1, col2, col3 = st.columns(3)
                        col1.metric(f"{pub}", "Peak ROAS", f"${peak_roas:.2f}", f"at Bucket {int(peak_bucket)}")
                        col2.metric(f"{pub}", "Saturation Point", f"${saturation_roas:.2f}", f"at {saturation_spend}")
                        col3.metric(f"{pub}", "ROI Decline", f"{((peak_roas - saturation_roas)/peak_roas * 100):.1f}%", "from peak to saturation")
            
            st.dataframe(df_diminishing, use_container_width=True)

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
            
            chart = alt.Chart(funnel_summary).mark_bar().encode(
                x="Funnel Layer",
                y="ROAS",
                color=alt.Color("Funnel Layer", scale=alt.Scale(scheme="blues")),
                tooltip=["Funnel Layer", "ROAS", "CPA ($)", "CTR (%)", "Conversions"]
            ).properties(title="Performance by Funnel Layer: ROAS Comparison")
            
            st.altair_chart(chart, use_container_width=True)
            st.dataframe(funnel_summary, use_container_width=True)

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
            
            st.markdown("### Top 5 Performing Placements")
            chart = alt.Chart(top_placements).mark_bar().encode(
                x=alt.X("ROAS", title="ROAS"),
                y=alt.Y("Publisher:N", sort="-x"),
                color="Format",
                tooltip=["Publisher", "Placement", "Format", "ROAS", "CPA ($)", "CTR (%)"]
            ).properties(title="Top Performing Placements by ROAS")
            
            st.altair_chart(chart, use_container_width=True)
            st.dataframe(top_placements, use_container_width=True)

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
            
            st.markdown("### Underperforming Placements (Pause/Optimize Candidates)")
            if len(underperforming) > 0:
                st.dataframe(underperforming, use_container_width=True)
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
            ).properties(title="Format Performance: ROAS by Format & Funnel Layer")
            
            st.altair_chart(chart, use_container_width=True)
            st.dataframe(format_summary, use_container_width=True)

        elif "ctr" in question or "cpc" in question:
            publisher_summary = df.groupby("Publisher").agg({
                "CTR (%)": "mean",
                "CPC ($)": "mean",
                "Conversions": "sum",
                "Revenue ($)": "sum",
                "ROAS": "mean"
            }).reset_index().sort_values("CTR (%)", ascending=False)
            
            chart = alt.Chart(publisher_summary).mark_bar().encode(
                x="CTR (%)",
                y=alt.Y("Publisher", sort="-x"),
                color="CPC ($)",
                tooltip=["Publisher", "CTR (%)", "CPC ($)", "ROAS"]
            ).properties(title="CTR vs CPC by Publisher")
            
            st.altair_chart(chart, use_container_width=True)
            st.dataframe(publisher_summary, use_container_width=True)

    except Exception as e:
        st.warning(f"Error rendering chart: {str(e)}")


# -------------------------------
# Render Structured Answer
# -------------------------------
with st.container():
    st.subheader("Detailed Answer")
    if question_to_answer and client:
        with st.spinner("Generating structured answer..."):
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Provide a structured answer (Insight, Recommendation, Next Steps) for: {question_to_answer}. Include funnel layer breakdowns, specific format recommendations, optimization tactics, and channel strategy. Quantify all recommendations with expected ROI lift or CPA reduction."}
                ]
            )
            detailed = response.choices[0].message.content

        # Parse response into sections
        sections = {"Insight": "", "Recommendation": "", "Next Steps": ""}
        current = None
        for line in detailed.splitlines():
            if any(h in line for h in sections.keys()):
                for h in sections.keys():
                    if h in line:
                        current = h
                        break
            elif current:
                sections[current] += line + "\n"

        # Fallback if parsing fails
        if not any(sections.values()):
            st.warning("Could not parse structured sections. Here's the full output:")
            st.markdown(detailed)

        # Render each section
        with st.expander("Insight", expanded=True):
            st.markdown(sections["Insight"], unsafe_allow_html=True)
            render_chart_for_question(question_to_answer, df)

        with st.expander("Recommendation", expanded=False):
            st.markdown(sections["Recommendation"], unsafe_allow_html=True)

        with st.expander("Next Steps", expanded=False):
            st.markdown(sections["Next Steps"], unsafe_allow_html=True)

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
