    dims_metrics = {
        "Dimensions": [
            "Month", 
            "Campaign Name", 
            "Audience Segment", 
            "Channel",
            "Publisher", 
            "Format", 
            "Targeting Strategy", 
            "Creative Messaging"
        ],
        "Core metrics": [
            "Revenue ($)", 
            "Media Spend ($)", 
            "ROAS",
            "CLV ($)"
        ],
        "Additional enterprise metrics (not visualized here)": [
            "CAC ($)", 
            "Churn (%)", 
            "CRM Emails Sent", 
            "CRM Open Rate (%)",
            "Leads Generated", 
            "Conversions", 
            "Conversion Rate (%)",
            "CRM Engagements"
        ],
        "Definitions": {
            "Creative Messaging": "The specific advertising message, theme, or concept shown to an audience. Examples include value‑driven offers, urgency messaging, lifestyle positioning, or brand storytelling. In analytics, creatives are evaluated by performance metrics such as ROAS, CTR, or conversion rate to determine which messages resonate most effectively."
        },
        "Notes": [
            "ROAS = Revenue / Media Spend",
            "Monthly CLV shown for trend illustration; production views use cohort CLV",
            "Extend dictionary to match your GA4/GMP/CRM schema"
        ],
    }
        ],
        "Notes": [
            "ROAS = Revenue / Media Spend",
            "Monthly CLV shown for trend illustration; production views use cohort CLV",
            "Extend dictionary to match your GA4/GMP/CRM schema"
        ]
    }

    # Render dictionary in columns for scannability
    dcol1, dcol2 = st.columns(2)
    with dcol1:
        st.markdown("**Dimensions**")
        st.markdown("\n".join([f"- {x}" for x in dims_metrics["Dimensions"]]))
        st.markdown("**Core metrics**")
        st.markdown("\n".join([f"- {x}" for x in dims_metrics["Core metrics"]]))
    with dcol2:
        st.markdown("**Additional enterprise metrics**")
        st.markdown("\n".join([f"- {x}" for x in dims_metrics["Additional enterprise metrics (not visualized here)"]]))
        st.markdown("**Definitions**")
        for k, v in dims_metrics["Definitions"].items():
            st.markdown(f"- **{k}**: {v}")
        st.markdown("**Notes**")
        st.markdown("\n".join([f"- {x}" for x in dims_metrics["Notes"]]))
