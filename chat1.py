import os
import difflib
from datetime import datetime

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from groq import Groq

# ============================================================================
# CONFIG & BRANDING
# ============================================================================

st.set_page_config(
    page_title="Dentsu Intelligence Assistant",
    page_icon="https://img.icons8.com/ios11/16/000000/dashboard-gauge.png",
    layout="wide"
)

# Color palette for charts
PALETTE = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]

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
    st.image(
        "https://www.dentsu.com/assets/images/main-logo-alt.png",
        width=160
    )

# Page title
st.title("Dentsu Intelligence Assistant")

# ============================================================================
# API KEY SETUP
# ============================================================================

api_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")

if not api_key:
    st.error("🚫 GROQ_API_KEY not found. Please set it in your environment or Streamlit secrets.")
    st.stop()

client = Groq(api_key=api_key)

# ============================================================================
# SYSTEM PROMPT
# ============================================================================

system_prompt = """
You are an AI Insights Assistant for C‑suite executives across Marketing, Media, Creative, CRM, Finance, and Loyalty/Product. Your mandate is to analyze enterprise‑scale performance data and deliver clear, strategic, executive‑ready insights supported by interactive visualizations.

Your responses must follow this structure:
- **Insight** 🧠: A precise, data-driven finding (trend, anomaly, comparison, or opportunity). Include timeframe and relevant metrics.
- **Action** 🎯: A specific, clickable operational step. Format each Action as a hyperlink that auto-populates a follow-up prompt and triggers a new insight using that prompt.
- **Recommendation** 📈: A strategic decision with rationale, financial impact, and trade-offs. Include workings, calculations, and modeling logic. Use best-practice functions from data science and statistics where applicable.
- **Next Steps** 🛠️: Clear owners, timelines, and measurable outcomes.

Always include:
- **Charts** to reflect the question that was asked. Use 2025 data only. Embed charts directly in the output. Include relevant timeframes and hover summaries for all key datapoints. Never describe charts — show them.
- **Summarized tables**: Group data by relevant dimensions (e.g. Publisher, Audience, Month, Format) to make insights digestible. Avoid raw line-by-line tables unless explicitly requested.
- A dedicated **Evidence & Reasoning** 📊 section that explains how the insight was derived, what assumptions were made, what modeling was used, and what confidence level applies.
- **Creative, targeting, messaging, and strategy data** where applicable — especially when analyzing campaign performance.
- **Internal and external factors** (e.g. market trends, economic shifts, competitor moves) based on recent research. Reference these when explaining performance changes or churn.
- **CX diagnostics**: When analyzing churn, include Net Promoter Score (NPS) and Customer Satisfaction (CSAT) metrics for the top 3 churn months to identify internal experience drivers.
- **Specific recommendations**: Be precise. If budget should be reallocated, explain where and why. If action is needed, define what, who, and how — not just vague monitoring advice.

Core responsibilities:
- Structure every response in the framework: Insight → Action → Recommendation → Next Steps.
- Ensure each element is specific, evidence‑based, and valid:
  • Insight = A precise finding from the data (with metrics, trends, anomalies, or quantified comparisons).  
  • Action = A concrete operational step that teams can take immediately, formatted as a clickable link that triggers a follow-up insight.  
  • Recommendation = A strategic decision with rationale, financial impact, and risk/benefit trade‑offs. Include workings and modeling.  
  • Next Steps = Clear owners, timelines, and measurement criteria.

- Always account for:
  • Audience cohorts (Millennials, Gen X, Boomers)  
  • Global platforms: Meta, TikTok, YouTube, Google Search/Display, LinkedIn, Snapchat  
  • Local publishers: NZ Herald, Stuff, TVNZ, MediaWorks, NZME Radio, Trade Me  
  • Performance/content partners: We Are Frank, Taboola, and other relevant publishers  
  • Portfolio‑level trade‑offs and opportunity costs  
  • Strategic & tactical thinking

- Leverage the full‑funnel dataset: Creative, Targeting, Strategy, Impressions, Clicks, Conversions, Spend, Revenue, ROAS, ROI, CAC, CLV.
- Identify and explain: trends, seasonal patterns, anomalies, and diminishing returns curves.
- When analyzing diminishing returns, generate a chart of Spend vs. ROAS by Channel or Month, with hover tooltips for Spend, Revenue, ROAS, and CAC. Highlight inflection points where ROAS declines.
- When evaluating publisher or platform performance, compare across audience segments, quantify differences, and visualize conversion totals with data labels and % share by audience.
- For Creative insights, frame findings through A/B testing results and key performance trends:
  • Identify winning vs. underperforming variants  
  • Highlight message, format, and visual elements that drive higher CTR, CVR, or CLV  
  • Recommend next creative tests and scaling strategies

- Provide actionable recommendations including: budget reallocations, testing frameworks, risk/impact assessments, and scenario planning.
- Explicitly state reasoning, modelling choices, and assumptions; flag confidence levels where appropriate.
- Anticipate likely C‑suite follow‑up questions (ROI sensitivity, scalability, risk exposure, competitive benchmarks) and prepare concise, data‑driven responses.
- Deliver all outputs in professional, concise, boardroom‑ready language that supports decision‑making.
"""

# ============================================================================
# DATA GENERATION
# ============================================================================

@st.cache_data
def generate_data():
    """Generate sample performance dataset for Oct 2024 - Sep 2025."""
    np.random.seed(42)
    
    months = pd.date_range(end="2025-09-30", periods=12, freq="MS")
    publishers = ["NZ Herald", "Stuff", "TVNZ", "MediaWorks", "NZME Radio", "Trade Me"]
    audiences = ["Millennials", "Gen X", "Boomers"]
    creatives = ["Video", "Carousel", "Static Image", "Interactive"]
    targeting_strategies = ["Behavioral", "Contextual", "Demographic", "Lookalike"]
    messaging_themes = ["Value-driven", "Urgency", "Emotional Appeal", "Product Benefits"]
    strategic_objectives = ["Acquisition", "Retention", "Upsell", "Reactivation"]

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

                rows.append([
                    m, pub, aud, impressions, clicks, conversions,
                    spend, revenue, roas, roi, clv, cac,
                    np.random.choice(creatives),
                    np.random.choice(targeting_strategies),
                    np.random.choice(messaging_themes),
                    np.random.choice(strategic_objectives)
                ])

    df = pd.DataFrame(rows, columns=[
        "Month", "Publisher", "Audience", "Impressions", "Clicks", "Conversions",
        "Spend ($)", "Revenue ($)", "ROAS", "ROI", "CLV ($)", "CAC ($)",
        "Creative Format", "Targeting Strategy", "Messaging Theme", "Strategic Objective"
    ])

    df["Month"] = pd.to_datetime(df["Month"])
    return df


df = generate_data()

# ============================================================================
# SIDEBAR CONTROLS
# ============================================================================

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

if "recent_questions" not in st.session_state:
    st.session_state.recent_questions = []

with st.sidebar:
    st.header("Executive Q&A")

    st.markdown("""
        **Instructions**  
        - Select one of the predefined strategic questions from the dropdown.  
        - Or type your own custom question in the text box below.  
        - Click ➡️ **Generate Answer** to receive structured insights and charts.  
        - Your recent questions will appear below for quick re‑selection.  
    """)

    selected = st.selectbox("Select a predefined question:", options=QUESTIONS, index=0)
    custom_question = st.text_area("Or type your own question:")

    question_to_answer = custom_question.strip() if custom_question.strip() else selected

    generate_triggered = st.button("➡️ Generate Answer")

    if generate_triggered and question_to_answer and question_to_answer not in st.session_state.recent_questions:
        st.session_state.recent_questions.insert(0, question_to_answer)
        st.session_state.recent_questions = st.session_state.recent_questions[:5]

    if st.session_state.recent_questions:
        st.markdown("**Recent Questions**")
        for q in st.session_state.recent_questions:
            if st.button(q, key=f"recent_{q}"):
                question_to_answer = q

        if st.button("🗑️ Clear History"):
            st.session_state.recent_questions = []

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def autocomplete_suggestions(input_text, questions, recent, top_n=5):
    """Generate autocomplete suggestions from recent and predefined questions."""
    input_text = (input_text or "").strip()
    pool = list(dict.fromkeys(recent + questions))
    
    if not input_text:
        return pool[:top_n]
    
    matches = difflib.get_close_matches(input_text, pool, n=top_n, cutoff=0.2)
    substring = [q for q in pool if input_text.lower() in q.lower() and q not in matches]
    
    return matches + substring[:max(0, top_n - len(matches))]


def detect_inflection_point(spend, roas):
    """Detect saturation point on spend vs ROAS curve using numerical derivatives."""
    d1 = np.gradient(roas, spend)
    d2 = np.gradient(d1, spend)
    idx = np.argmin(d2)
    
    if d2[idx] < 0:
        return float(spend[idx]), float(roas[idx]), float(d1[idx]), float(d2[idx])
    
    return None


@st.cache_data(show_spinner=False)
def cached_llm_response(question_text, sys_prompt, client_params):
    """Fetch and cache LLM response (placeholder for demonstration)."""
    return {
        "text": f"""
Insight:
A placeholder answer for: {question_text}

Action:
Example action to take immediately

Recommendation:
Example strategic recommendation

Next Steps:
Example next steps with owners and timelines
"""
    }

# ============================================================================
# CHART RENDERING
# ============================================================================

def render_chart_for_question(question, data):
    """Generate visualizations based on question type."""
    q = question.lower()

    # Diminishing returns analysis
    if "diminishing returns" in q:
        channels = ["Search", "Social", "CTV", "Display"]
        spend = np.linspace(1e6, 50e6, 50)
        curves = {
            "Search": 5 - 4e-7 * spend + 2e10 / (spend + 1),
            "Social": 4 - 5e-7 * spend + 1.2e10 / (spend + 1),
            "CTV": 6 - 3.5e-7 * spend + 3e10 / (spend + 1),
            "Display": 3 - 4.5e-7 * spend + 0.8e10 / (spend + 1)
        }

        rows = []
        inflections = []
        
        for ch in channels:
            roas = curves[ch]
            for s, r in zip(spend, roas):
                rows.append({"Channel": ch, "Spend ($)": s, "ROAS": r})
            
            inf = detect_inflection_point(spend, roas)
            if inf:
                inflections.append({"Channel": ch, "Spend ($)": inf[0], "ROAS": inf[1]})

        df_channels = pd.DataFrame(rows)

        base = alt.Chart(df_channels).mark_line().encode(
            x=alt.X("Spend ($):Q", title="Spend ($)", axis=alt.Axis(format="$~s")),
            y=alt.Y("ROAS:Q", title="Return on Ad Spend"),
            color=alt.Color("Channel:N", scale=alt.Scale(range=PALETTE)),
            tooltip=[
                alt.Tooltip("Channel:N"),
                alt.Tooltip("Spend ($):Q", format="$,.0f"),
                alt.Tooltip("ROAS:Q", format=".2f")
            ]
        ).properties(title="Spend vs ROAS by Channel — Inflection Points Highlighted", height=420)

        points = alt.Chart(pd.DataFrame(inflections)).mark_point(
            filled=True, size=80, shape="triangle"
        ).encode(
            x="Spend ($):Q",
            y="ROAS:Q",
            color=alt.Color("Channel:N", scale=alt.Scale(range=PALETTE)),
            tooltip=[
                alt.Tooltip("Channel:N"),
                alt.Tooltip("Spend ($):Q", format="$,.0f"),
                alt.Tooltip("ROAS:Q", format=".2f")
            ]
        )

        text = alt.Chart(pd.DataFrame(inflections)).mark_text(
            align="left", dx=7, dy=-7, fontWeight="bold"
        ).encode(
            x="Spend ($):Q",
            y="ROAS:Q",
            text=alt.Text("Channel:N"),
            color=alt.value("#000000")
        )

        st.altair_chart((base + points + text).interactive(), use_container_width=True)
        st.markdown("Each channel's ROAS flattens as incremental spend increases. Marked triangles indicate estimated saturation/inflection points.")
        return

    # Publisher performance
    if "publisher" in q:
        summary = data.groupby(["Publisher", "Audience"], as_index=False).agg({"Conversions": "sum"})
        total_audience = summary.groupby("Audience", as_index=False).agg({"Conversions": "sum"}).rename(columns={"Conversions": "AudienceTotal"})
        summary = summary.merge(total_audience, on="Audience")
        summary["% Share"] = (summary["Conversions"] / summary["AudienceTotal"]) * 100
        summary["Label"] = summary.apply(lambda r: f"{int(r['Conversions']):,} ({r['% Share']:.1f}%)", axis=1)

        chart = alt.Chart(summary).mark_bar().encode(
            x=alt.X("Publisher:N", sort=alt.EncodingSortField(field="Conversions", op="sum", order="descending")),
            y=alt.Y("Conversions:Q"),
            color=alt.Color("Audience:N", scale=alt.Scale(range=PALETTE)),
            tooltip=[
                alt.Tooltip("Publisher:N"),
                alt.Tooltip("Audience:N"),
                alt.Tooltip("Conversions:Q", format=",.0f"),
                alt.Tooltip("% Share:Q", format=".1f")
            ]
        ).properties(title="Publisher Conversion Volume by Audience Segment", height=420)

        labels = alt.Chart(summary).mark_text(dy=-8, fontWeight="bold", fontSize=11).encode(
            x=alt.X("Publisher:N", sort=alt.EncodingSortField(field="Conversions", op="sum", order="descending")),
            y=alt.Y("Conversions:Q"),
            detail="Audience:N",
            text=alt.Text("Label:N"),
            color=alt.value("#000000")
        )

        st.altair_chart((chart + labels).interactive(), use_container_width=True)
        st.markdown("Bars show absolute conversion volume; labels show per-audience totals and percent share within each audience.")
        return

    # CTR and CVR analysis
    if "click-through" in q or "ctr" in q or "conversion" in q or "cvr" in q:
        channels = ["Meta", "YouTube", "Trade Me", "Google"]
        summary = []
        
        for ch in channels:
            subset = data[data["Publisher"].str.contains(ch, case=False, na=False)] if any(data["Publisher"].str.contains(ch, case=False, na=False)) else data.sample(20)
            impressions = subset["Impressions"].sum()
            clicks = subset["Clicks"].sum()
            conversions = subset["Conversions"].sum()
            ctr = (clicks / impressions) * 100 if impressions > 0 else 0
            cvr = (conversions / clicks) * 100 if clicks > 0 else 0
            
            summary.append({
                "Channel": ch,
                "Impressions": impressions,
                "Clicks": clicks,
                "Conversions": conversions,
                "CTR (%)": ctr,
                "CVR (%)": cvr
            })

        summary_df = pd.DataFrame(summary)

        chart_ctr = alt.Chart(summary_df).mark_bar().encode(
            x=alt.X("Channel:N", sort=channels),
            y=alt.Y("CTR (%):Q", title="CTR (%)"),
            color=alt.Color("Channel:N", scale=alt.Scale(range=PALETTE)),
            tooltip=[
                alt.Tooltip("Channel:N"),
                alt.Tooltip("CTR (%):Q", format=".2f"),
                alt.Tooltip("Impressions:Q", format=",.0f")
            ]
        ).properties(title="Click-through Rates by Channel", height=300)

        chart_cvr = alt.Chart(summary_df).mark_bar().encode(
            x=alt.X("Channel:N", sort=channels),
            y=alt.Y("CVR (%):Q", title="CVR (%)"),
            color=alt.Color("Channel:N", scale=alt.Scale(range=PALETTE)),
            tooltip=[
                alt.Tooltip("Channel:N"),
                alt.Tooltip("CVR (%):Q", format=".2f"),
                alt.Tooltip("Conversions:Q", format=",.0f")
            ]
        ).properties(title="Conversion Rates by Channel", height=300)

        st.altair_chart(chart_ctr, use_container_width=True)
        st.altair_chart(chart_cvr, use_container_width=True)
        st.markdown("CTR and CVR are shown side-by-side to inform trade-offs between reach and conversion efficiency.")
        return

    # Creative format analysis
    if "creative" in q or "format" in q:
        summary = data.groupby("Creative Format", as_index=False).agg({
            "Clicks": "sum",
            "Conversions": "sum",
            "Spend ($)": "sum"
        })
        total_impressions = data["Impressions"].sum()
        summary["CTR (%)"] = (summary["Clicks"] / total_impressions) * 100
        summary["CVR (%)"] = summary["Conversions"] / summary["Clicks"].replace({0: np.nan}) * 100
        summary["ROI"] = (summary["Conversions"] * data["CLV ($)"].mean() - summary["Spend ($)"]) / summary["Spend ($)"]

        chart = alt.Chart(summary).mark_bar().encode(
            x=alt.X("Creative Format:N"),
            y=alt.Y("ROI:Q"),
            color=alt.Color("Creative Format:N", scale=alt.Scale(range=PALETTE)),
            tooltip=[
                "Creative Format",
                alt.Tooltip("CTR (%):Q", format=".2f"),
                alt.Tooltip("CVR (%):Q", format=".2f"),
                alt.Tooltip("ROI:Q", format=".2f")
            ]
        ).properties(title="Creative Format Performance (ROI)", height=420)

        st.altair_chart(chart, use_container_width=True)
        st.markdown("- Example: Carousel with urgency messaging produced 3.2x higher CVR vs static images.")
        st.markdown("- Example: Short-form video with product benefits messaging produced highest ROAS and CLV uplift.")
        return

    st.markdown("No visual template matched this question. Please choose a question from the autocomplete or refine your query.")

# ============================================================================
# MAIN CONTENT RENDERING
# ============================================================================

input_text = st.text_input("Enter question or choose from suggestions", value="", key="question_input")
suggests = autocomplete_suggestions(input_text, QUESTIONS, st.session_state.recent_questions, top_n=5)

for s in suggests:
    if st.button(s, key=f"sugg_{s}"):
        st.session_state.question_input = s
        input_text = s

if st.button("➡️ Generate Answer"):
    question_to_answer = st.session_state.get("question_input", "").strip() or QUESTIONS[0]
    
    if question_to_answer not in st.session_state.recent_questions:
        st.session_state.recent_questions.insert(0, question_to_answer)
        st.session_state.recent_questions = st.session_state.recent_questions[:10]

    client_params = {"model": "llama-3.1-8b-instant"}
    llm_out = cached_llm_response(question_to_answer, system_prompt, client_params)
    detailed = llm_out["text"]

    sections = {"Insight": "", "Action": "", "Recommendation": "", "Next Steps": ""}
    cur = None
    
    for line in detailed.splitlines():
        line_stripped = line.strip()
        if line_stripped.startswith("Insight"):
            cur = "Insight"
            continue
        if line_stripped.startswith("Action"):
            cur = "Action"
            continue
        if line_stripped.startswith("Recommendation"):
            cur = "Recommendation"
            continue
        if line_stripped.startswith("Next Steps"):
            cur = "Next Steps"
            continue
        if cur:
            sections[cur] += line + "\n"

    st.markdown("### Insight")
    st.markdown(sections["Insight"])
    render_chart_for_question(question_to_answer, df)

    st.markdown("### Action")
    st.markdown(sections["Action"])
    if sections["Action"].strip() and st.button("Use action as follow-up prompt"):
        st.session_state.question_input = sections["Action"].strip()
        st.rerun()

    st.markdown("### Recommendation")
    st.markdown(sections["Recommendation"])
    st.markdown("**Modeling & Calculations Used:**")
    st.markdown("- ROI = (Revenue - Spend) / Spend")
    st.markdown("- CAC = Spend / Conversions")
    st.markdown("- CLV used is historical cohort average; specify cohort window to change CLV estimates")

    st.markdown("### Next Steps")
    st.markdown(sections["Next Steps"])
    st.caption(f"Generated on {datetime.now().strftime('%B %d, %Y at %H:%M')}")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown(
    "⚖️ [Legal Disclaimer](https://www.example.com/legal-disclaimer) — "
    "The insights and visualizations generated by this tool are for informational purposes only "
    "and should not be considered financial, legal, or business advice."
)
