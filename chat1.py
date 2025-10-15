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
    st.error("🚫 GROQ_API_KEY not found. Please set it in your environment or Streamlit secrets.")
    st.stop()

client = Groq(api_key=api_key)

# -------------------------------
# SYSTEM PROMPT
# -------------------------------
system_prompt = """
You are an AI Insights Assistant for C‑suite executives across Marketing, Media, Creative, CRM, Finance, and Loyalty/Product. Your mandate is to analyze enterprise‑scale performance data and deliver clear, strategic, executive‑ready insights supported by interactive visualizations.

Your responses must follow this structure:
- **Insight** 🧠: A precise, data-driven finding segmented by funnel layer (Awareness/Consideration/Conversion). Include top-performing placements, performance deltas vs. benchmarks, messaging approaches, and engagement patterns. Reference specific metrics: CPCV, Completion Rate, CPM, Viewability, CPC, CTR, CPA, ROAS, transactions, revenue.
- **Recommendation** 📈: A strategic decision with rationale, financial impact, and risk/benefit trade-offs. Specific, operationalized format recommendations and optimization tactics:
  • Channel & placement allocation decisions (e.g., "increase YouTube from 25% to 40% of video budget; decrease TikTok from 30% to 15%")
  • "Increase allocation to YouTube Skippable Mid-roll (Consideration layer): achieved 8.2% CTR vs. 3.1% benchmark. Test product-focused creative variant with 15-second hook."
  • "Pause Display Network placements with <2% viewability. Redirect 40% budget to programmatic video (ROAS $4.21) and allocate 20% to search retargeting (CPA $23)."
  • Creative testing framework and success metrics
  • "Test 3-format creative rotation (Video vs. Carousel vs. Static) on Meta Conversion layer. Current Video driving $3.87 ROAS; rotate non-performing formats weekly."
  • Audience targeting refinements with expected ROI lift
  • Competitive positioning and market insights

- When analyzing paid search, include performance breakdowns by category, product, and message. Reference real examples such as:
  • "Kitchen Appliances generated $19.9K revenue from 78 purchases — recommend increasing budget allocation."
  • "Promotional ad extensions for De'Longhi and Simon Lewis drove 312K impressions — continue testing product-level relevance."
  • "CTR uplift of 13% and CPC drop led to 8% more clicks at steady budget — maintain current investment level."

- When evaluating creative performance, highlight standout variants and their contribution to revenue and efficiency:
  • "The 'Earn' creative drove 73% of total revenue with CTR of 2.46% and ROAS of $5.07 — scale across Advantage+."
  • "High Touch 1PD audiences delivered 152 remarketing transactions with ROAS of $14.14 and CPA of $19.99 — well below $100 benchmark."

- When referencing platform performance, include channel-level insights and strategic implications:
  • "Meta continues to outperform benchmarks across visibility and conversion — recommend continued investment and refreshed catalogue rollout."
  • "Search ROAS at 8.86 with $353K revenue — maintain budget and monitor TAPM vs EAPM allocation."

Always include:
- **Performance by Funnel Layer**: Break down all metrics (impressions, clicks, conversions, spend, ROAS, CPA, CPCV, Completion Rate, CPM, Viewability, CTR, CPC) by Awareness → Consideration → Conversion.
- **Top Performing Placements**: Name 3-5 placements with strongest performance on CPC, CTR, ROAS metrics. Quantify performance delta vs. average.
- **Underperforming Placements**: Identify placements with viewability <50%, CPCV >$2.50, completion rates <25%, or ROAS <$1.50. Recommend pause/optimize/test.
- **Format Analysis**: Compare Video, Carousel, Static Image, Interactive by CTR, CPA, ROAS, Completion Rate. Identify winner and rollout plan.
- **Charts** to reflect the question asked. Include relevant timeframes in all charts. Explain all key datapoints with summaries.
- **Summarized tables**: Group data by Funnel Layer, Placement, Format to make insights digestible.
- A dedicated **Evidence & Reasoning** 📊 section explaining how insights were derived, assumptions made, and confidence levels.
- **Engagement Diagnostics**: Message resonance, creative fatigue signals, audience saturation indicators. Reference NPS, sentiment, or engagement lift where applicable.
- **Optimization Recommendations**: Specific format recommendations, creative testing approaches, messaging variants to test, channels to invest/divest in.
- **Competitive Context**: Market trends, economic factors, seasonal shifts influencing performance changes, check for competitors recent activity too.

Core responsibilities:
- Structure every response: Insight → Recommendation → Next Steps.
- Ensure each element is specific, evidence‑based, and actionable:
  • Insight = Precise findings segmented by funnel layer with quantified metrics
  • Recommendation = Strategic decisions with financial impact and trade-offs
  • Next Steps = Clear owners, timelines, measurable outcomes
 
- Always account for:
  • Funnel layers: Awareness, Consideration, Conversion
  • Global platforms: Meta, TikTok, YouTube, Google Search/Display, LinkedIn, Snapchat
  • Local publishers: NZ Herald, Stuff, TVNZ, MediaWorks, NZME Radio, Trade Me
  • Format performance: Video, Carousel, Static Image, Interactive
  • Metrics: CPCV, Completion Rate, CPM, Viewability, CPC, CTR, CPA, ROAS
  • Portfolio trade-offs and opportunity costs

- Leverage the full-funnel dataset: Funnel Layer, Format, Placement, Impressions, Clicks, Conversions, Spend, Revenue, CPCV, Completion Rate, CPM, Viewability, CPC, CTR, CPA, ROAS, ROI.
- Identify and explain: trends, seasonal patterns, anomalies, diminishing returns curves, format winners, placement efficiency.
- For Diminishing Returns analysis: Identify the inflection point where ROAS begins declining by spend level. Quantify the saturation curve and recommend optimal spend threshold for each channel.
- When analyzing format performance, compare A/B results and recommend scaling winners while testing new creative variants on underperforming formats.
- Provide actionable recommendations: budget reallocations by funnel layer, creative testing frameworks, format rotation strategies, audience targeting refinements.
- Deliver all outputs in professional, concise, boardroom-ready language supporting decision-making.

Your goal: transform complex performance data into specific insights, valid actions, and strategically grounded recommendations that drive executive confidence and measurable results.
"""

# -------------------------------
# SAMPLE DATA WITH REAL DIMINISHING RETURNS
# -------------------------------
@st.cache_data
def generate_data():
    np.random.seed(42)
    
    # Generate months from Oct 2024 to Sep 2025
    months = pd.date_range(end="2025-09-30", periods=12, freq="MS")
    
    # Realistic data structures
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

    rows = []
    
    for m in months:
        for pub in publishers:
            for layer in funnel_layers:
                for fmt in formats:
                    placement = np.random.choice(placements[pub])
                    
                    # Base metrics with realistic ranges
                    impressions = np.random.randint(100_000, 2_000_000)
                    
                    # CTR varies by layer: Awareness lower, Conversion higher
                    if layer == "Awareness":
                        ctr = np.random.uniform(0.5, 2.5) / 100
                    elif layer == "Consideration":
                        ctr = np.random.uniform(2.0, 6.0) / 100
                    else:  # Conversion
                        ctr = np.random.uniform(4.0, 12.0) / 100
                    
                    clicks = int(impressions * ctr)
                    
                    # CVR varies by layer
                    if layer == "Awareness":
                        cvr = np.random.uniform(0.5, 2.0) / 100
                    elif layer == "Consideration":
                        cvr = np.random.uniform(1.5, 5.0) / 100
                    else:  # Conversion
                        cvr = np.random.uniform(5.0, 15.0) / 100
                    
                    conversions = int(clicks * cvr)
                    
                    # Spend with realistic CPC ranges
                    if pub == "Search":
                        cpc = np.random.uniform(0.80, 3.50)
                    elif pub == "LinkedIn":
                        cpc = np.random.uniform(1.20, 4.00)
                    elif pub in ["YouTube", "Programmatic Video"]:
                        cpc = np.random.uniform(0.15, 1.00)
                    else:
                        cpc = np.random.uniform(0.20, 1.50)
                    
                    spend = clicks * cpc
                    
                    # Revenue with realistic AOV
                    aov = np.random.uniform(60, 200)
                    revenue = conversions * aov
                    
                    # Calculated metrics
                    roas = revenue / spend if spend > 0 else 0
                    roi = (revenue - spend) / spend if spend > 0 else 0
                    cpa = spend / conversions if conversions > 0 else np.nan
                    
                    # Video-specific metrics
                    if fmt == "Video":
                        cpcv = np.random.uniform(0.08, 0.35)
                        completion_rate = np.random.uniform(45, 75) / 100
                    else:
                        cpcv = np.random.uniform(0.10, 0.50)
                        completion_rate = np.random.uniform(20, 50) / 100
                    
                    # CPM and Viewability
                    if pub == "Search":
                        cpm = np.random.uniform(2, 6)
                    elif pub == "YouTube":
                        cpm = np.random.uniform(3, 12)
                    elif pub in ["Meta", "TikTok"]:
                        cpm = np.random.uniform(4, 10)
                    else:
                        cpm = np.random.uniform(2, 8)
                    
                    # Viewability (critical metric)
                    if pub in ["YouTube", "Programmatic Video"]:
                        viewability = np.random.uniform(60, 85) / 100
                    elif pub in ["Meta", "TikTok"]:
                        viewability = np.random.uniform(70, 90) / 100
                    elif pub == "Google Display":
                        viewability = np.random.uniform(45, 65) / 100
                    else:
                        viewability = np.random.uniform(55, 80) / 100
                    
                    clv = np.random.uniform(500, 2000)

                    rows.append([
                        m, pub, layer, placement, fmt, impressions, clicks, conversions,
                        spend, revenue, roas, roi, cpa, cpc, ctr * 100, cpcv, 
                        completion_rate * 100, cpm, viewability * 100, clv
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
        - Your recent questions will appear below for quick re‑selection.  
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
        if st.button("🗑️ Clear History"):
            st.session_state.recent_questions = []

# -------------------------------
# CHART RENDERING WITH REAL DIMINISHING RETURNS
# -------------------------------
def render_chart_for_question(question, df):
    question = question.lower()

    try:
        if "diminishing returns" in question:
            # Create realistic diminishing returns curve by aggregating spend into buckets
            publishers_list = df["Publisher"].unique()
            
            spend_buckets = []
            for pub in publishers_list:
                pub_data = df[df["Publisher"] == pub].copy()
                pub_data_sorted = pub_data.sort_values("Spend ($)")
                
                # Create 8 spend buckets
                n_buckets = 8
                bucket_size = len(pub_data_sorted) // n_buckets
                
                for i in range(n_buckets):
                    start_idx = i * bucket_size
                    end_idx = (i + 1) * bucket_size if i < n_buckets - 1 else len(pub_data_sorted)
                    bucket = pub_data_sorted.iloc[start_idx:end_idx]
                    
                    total_spend = bucket["Spend ($)"].sum()
                    avg_roas = bucket["ROAS"].mean()
                    
                    spend_buckets.append({
                        "Publisher": pub,
                        "Spend Bucket ($M)": total_spend / 1_000_000,
                        "Avg ROAS": avg_roas,
                        "Cumulative Spend ($M)": (total_spend / 1_000_000) * (i + 1)
                    })
            
            df_diminishing = pd.DataFrame(spend_buckets)
            
            # Create line chart showing inflection point
            chart = alt.Chart(df_diminishing).mark_line(point=True, size=3).encode(
                x=alt.X("Spend Bucket ($M)", title="Spend Per Bucket ($M)"),
                y=alt.Y("Avg ROAS", title="Average ROAS"),
                color=alt.Color("Publisher", title="Publisher"),
                tooltip=["Publisher", "Spend Bucket ($M)", "Avg ROAS"]
            ).properties(
                title="Diminishing Returns Analysis: ROAS Curve by Publisher",
                width=800,
                height=400
            ).interactive()
            
            st.altair_chart(chart, use_container_width=True)
            
            # Identify inflection points
            st.markdown("### Saturation Point Analysis")
            for pub in publishers_list:
                pub_data = df_diminishing[df_diminishing["Publisher"] == pub]
                if len(pub_data) > 0:
                    # Find where ROAS drops most steeply
                    pub_data_sorted = pub_data.sort_values("Spend Bucket ($M)")
                    max_roas = pub_data_sorted["Avg ROAS"].max()
                    inflection_row = pub_data_sorted[pub_data_sorted["Avg ROAS"] < max_roas * 0.85].iloc[0:1]
                    
                    if len(inflection_row) > 0:
                        inflection_spend = inflection_row["Spend Bucket ($M)"].values[0]
                        inflection_roas = inflection_row["Avg ROAS"].values[0]
                        st.metric(f"{pub} - Saturation Point", 
                                f"${inflection_spend:.2f}M spend", 
                                f"ROAS: {inflection_roas:.2f}")
            
            st.dataframe(df_diminishing)

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
                "CPCV ($)": "mean",
                "Completion Rate (%)": "mean",
                "CPM ($)": "mean",
                "Viewability (%)": "mean"
            }).reset_index()
            
            chart = alt.Chart(funnel_summary).mark_bar().encode(
                x="Funnel Layer",
                y="ROAS",
                color=alt.Color("Funnel Layer", scale=alt.Scale(scheme="blues")),
                tooltip=[col for col in funnel_summary.columns]
            ).properties(title="Performance by Funnel Layer: ROAS Comparison")
            
            st.altair_chart(chart, use_container_width=True)
            st.dataframe(funnel_summary)

        elif "top-performing" in question or "scale" in question:
            placement_summary = df.groupby(["Publisher", "Placement", "Format"]).agg({
                "Clicks": "sum",
                "Conversions": "sum",
                "Spend ($)": "sum",
                "Revenue ($)": "sum",
                "ROAS": "mean",
                "CPA ($)": "mean",
                "CTR (%)": "mean",
                "CPC ($)": "mean",
                "CPCV ($)": "mean",
                "Completion Rate (%)": "mean",
                "Viewability (%)": "mean"
            }).reset_index().sort_values("ROAS", ascending=False)
            
            top_placements = placement_summary.head(5)
            
            st.markdown("### Top 5 Performing Placements")
            chart = alt.Chart(top_placements).mark_bar().encode(
                x=alt.X("ROAS", title="ROAS"),
                y=alt.Y("Publisher:N", sort="-x"),
                color="Format",
                tooltip=["Publisher", "Placement", "Format", "ROAS", "CPC ($)", "CTR (%)"]
            ).properties(title="Top Performing Placements by ROAS")
            
            st.altair_chart(chart, use_container_width=True)
            st.dataframe(top_placements)

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
            st.dataframe(underperforming)

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
                tooltip=[col for col in format_summary.columns]
            ).properties(title="Format Performance: ROAS by Format & Funnel Layer")
            
            st.altair_chart(chart, use_container_width=True)
            st.dataframe(format_summary)

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
            st.dataframe(publisher_summary)

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
    "Legal Disclaimer — "
    "The insights and visualizations generated by this tool are for informational purposes only "
    "and should not be considered financial, legal, or business advice."
)
