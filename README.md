# 📊 Dentsu Intelligence Assistant

This assistant transforms complex performance data into strategic, executive-ready insights using Groq’s AI capabilities and interactive visualizations.

---

## 🚀 Overview

The Dentsu Intelligence Assistant delivers:
- Insights segmented by funnel stage (Awareness → Consideration → Conversion)
- Strategic recommendations for media mix, creative optimization, audience targeting, and budget allocation
- Interactive charts and tables that directly answer business-critical questions
- Custom styling and branding aligned with Dentsu’s visual identity

---

## 🧠 Core Capabilities

- **AI-Powered Analysis**: Uses Groq’s LLM to generate structured insights and recommendations based on performance data.
- **Strategic Framework**: All responses follow a rigorous structure:
  - Executive Overview
  - Detailed Insight
  - Strategic Recommendation
- **Visual Intelligence**: Charts and tables built with Altair and Pandas to support decision-making.
- **Custom Styling**: Dark-themed UI with Inter font, branded sidebar, and responsive layout.

---

## 📋 Key Questions Answered

The assistant is trained to respond to high-impact strategic queries, including:

- What are the diminishing returns by channel and spend curve?
- Which publishers perform best by audience segment?
- How should we allocate $100M, $200M, or $300M across funnel layers?
- Which formats deliver the highest ROI and lowest CPA?
- Which channels and publishers have the strongest click-to-conversion rates?
- What months show the highest churn, and what are the internal vs. external drivers?
- What should we scale, pause, or optimize for maximum efficiency?
- What creative testing strategies should we deploy?

---

## 🛠️ Tech Stack

| Component     | Purpose                                                                 | Documentation |
|--------------|-------------------------------------------------------------------------|----------------|
| **Streamlit** | Web app framework for Python                                            | [Streamlit Docs](https://docs.streamlit.io/) |
| **Pandas**    | Data manipulation and analysis                                          | [Pandas Docs](https://pandas.pydata.org/docs/) |
| **NumPy**     | Numerical computing and array operations                                | [NumPy Docs](https://numpy.org/doc/) |
| **Altair**    | Declarative statistical visualization                                   | [Altair Docs](https://altair-viz.github.io/) |
| **Groq SDK**  | Interface to Groq’s LLMs for strategic insights                         | [Groq SDK](https://github.com/groq/groq-python) |
| **Groq Cloud**| API key management and usage dashboard                                  | [Groq Console](https://console.groq.com/) |
| **Google Fonts (Inter)** | Typography styling for clean, modern UI                     | [Inter Font](https://fonts.google.com/specimen/Inter) |
| **Dentsu Branding** | Sidebar logo and brand identity                                  | [Dentsu Global](https://www.dentsu.com/) |

---

## 🔐 Setup & Configuration

### 1. Environment Variables

Ensure your Groq API key is available via environment or Streamlit secrets:

```bash
export GROQ_API_KEY=your_api_key_here
