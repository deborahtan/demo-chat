

# -------------------------------
# ADVANCED STYLING
# -------------------------------
st.markdown("""
<style>
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%);
    color: #e8eef5;
}

[data-testid="stMainBlockContainer"] {
    background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%);
    padding-top: 2rem;
}

h1, h2, h3, h4, h5, h6 {
    font-weight: 700;
    color: #ffffff;
    letter-spacing: -0.5px;
}

h1 { font-size: 2.5rem; margin-bottom: 0.5rem; }
h2 { font-size: 1.8rem; margin-bottom: 1rem; }
h3 { font-size: 1.3rem; margin-bottom: 0.75rem; }

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f1428 0%, #1a1f3a 100%);
    border-right: 1px solid rgba(255, 255, 255, 0.1);
}

[data-testid="stSidebar"] button {
    background: linear-gradient(135deg, #00d4ff 0%, #0099ff 100%);
    color: #000 !important;
    border-radius: 8px;
    font-weight: 600;
    border: none;
    padding: 10px 16px;
    transition: all 0.3s ease;
}

[data-testid="stSidebar"] button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(0, 212, 255, 0.3);
}

.metric-card {
    background: linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(0, 153, 255, 0.05) 100%);
    border: 1px solid rgba(0, 212, 255, 0.3);
    border-radius: 12px;
    padding: 20px;
    backdrop-filter: blur(10px);
    transition: all 0.3s ease;
}

.metric-card:hover {
    border-color: rgba(0, 212, 255, 0.6);
    background: linear-gradient(135deg, rgba(0, 212, 255, 0.15) 0%, rgba(0, 153, 255, 0.1) 100%);
    box-shadow: 0 8px 24px rgba(0, 212, 255, 0.2);
}

.metric-label {
    font-size: 0.85rem;
    color: #9ca3af;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 8px;
}

.metric-value {
    font-size: 2rem;
    font-weight: 700;
    color: #00d4ff;
    margin-bottom: 4px;
}

.metric-change {
    font-size: 0.9rem;
    color: #10b981;
    font-weight: 600;
}

.metric-change.negative {
    color: #ef4444;
}

.answer-card {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    padding: 24px;
    backdrop-filter: blur(10px);
    margin: 16px 0;
}

.chart-container {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.02) 0%, rgba(255, 255, 255, 0.01) 100%);
    border: 1px solid rgba(0, 212, 255, 0.2);
    border-radius: 12px;
    padding: 16px;
    margin: 20px 0;
}

[data-testid="stChatMessage"] {
    background: transparent !important;
}

[data-testid="stChatMessageContent"] {
    background: transparent !important;
}

.user-message {
    background: linear-gradient(135deg, rgba(0, 212, 255, 0.15) 0%, rgba(0, 153, 255, 0.05) 100%);
    border: 1px solid rgba(0, 212, 255, 0.3);
    border-radius: 12px;
    padding: 16px;
    margin: 8px 0;
}

.assistant-message {
    background: transparent;
}

[data-testid="stChatInput"] {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%);
    border: 1px solid rgba(0, 212, 255, 0.3) !important;
    border-radius: 12px;
    backdrop-filter: blur(10px);
}

input[type="text"] {
    background: transparent !important;
    color: #e8eef5 !important;
    font-size: 1rem;
}

input[type="text"]::placeholder {
    color: rgba(232, 238, 245, 0.4) !important;
}

.sidebar-section {
    margin-bottom: 2rem;
}

.sidebar-title {
    font-size: 0.75rem;
    color: #6b7280;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    margin-bottom: 12px;
    margin-top: 16px;
}

.insight-section {
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(16, 185, 129, 0.05) 100%);
    border-left: 4px solid #10b981;
    padding: 16px;
    border-radius: 8px;
    margin: 16px 0;
}

.recommendation-section {
    background: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(139, 92, 246, 0.05) 100%);
    border-left: 4px solid #8b5cf6;
    padding: 16px;
    border-radius: 8px;
    margin: 16px 0;
}

hr {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0, 212, 255, 0.3), transparent);
    margin: 24px 0;
}

.top-bar {
    background: linear-gradient(90deg, rgba(0, 212, 255, 0.1) 0%, rgba(0, 153, 255, 0.05) 100%);
    border-bottom: 1px solid rgba(0, 212, 255, 0.2);
    padding: 16px 24px;
    border-radius: 12px;
    margin-bottom: 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.disclaimer {
    font-size: 0.85rem;
    color: #9ca3af;
    padding: 16px;
    background: rgba(0, 0, 0, 0.2);
    border-radius: 8px;
    border-left: 3px solid #f59e0b;
    margin-top: 32px;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# SIDEBAR
# -------------------------------
with st.sidebar:
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.image("https://www.dentsu.com/assets/images/main-logo-alt.png", width=140)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<h3 style="margin-top: 0; margin-bottom: 12px;">Executive Chat</h3>', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size: 0.9rem; color: #9ca3af; line-height: 1.6;">
    📊 Ask questions about campaign performance, ROI, and strategic recommendations<br><br>
    💡 The assistant delivers data-driven insights across all channels and metrics<br><br>
    📈 Conversation context is preserved for deeper analysis
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🧹 Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
    with col2:
        if st.button("📊 Data", use_container_width=True):
            st.session_state.show_data = True
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<p class="sidebar-title">Quick Info</p>', unsafe_allow_html=True)
    st.markdown(f"**Session Time:** {datetime.now().strftime('%H:%M')}")
    st.markdown(f"**FY Year:** 2025")
    st.markdown('</div>', unsafe_allow_html=True)
