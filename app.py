# Step => 1 Import required libraries
import streamlit as st
import speech_recognition as sr
import time
import os
import json
import matplotlib.pyplot as plt
import seaborn as sns
from chatbot import (
    generate_ai_response,
    log_chat_interaction,
    save_analytics_data,
)

# Step => 2 Configure Streamlit UI
st.set_page_config(page_title="Dynamic AI Chatbot", layout="centered", initial_sidebar_state="collapsed")

# Step => 3 Inject custom futuristic CSS
st.markdown("""
    <style>
    body {
        background-color: #0d1117;
        color: white;
    }
    .stApp {
        background: linear-gradient(to right, #0f2027, #203a43, #2c5364);
        color: white;
        font-family: 'Segoe UI', sans-serif;
    }
    .stTextInput>div>div>input {
        background-color: rgba(255, 255, 255, 0.1);
        color: white;
    }
    .stButton>button {
        background: #1f6feb;
        color: white;
        border-radius: 12px;
        border: none;
        padding: 0.5rem 1rem;
    }
    .metric-container {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 15px;
    }
    .stDownloadButton>button {
        background: #238636;
        color: white;
        border-radius: 12px;
        border: none;
        padding: 0.4rem 0.8rem;
        margin-top: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Step => 4 App Title
st.title("🤖 Dynamic AI Chatbot")

# Step => 5 Tabs for UI
tab1, tab2, tab3 = st.tabs(["💬 Chat", "📊 Analytics", "⚙️ System Logs"])
with tab1:
    st.subheader("💡 Talk with Dynamic AI Chatbot")
    col1, col2 = st.columns([1, 4])
    with col1:
        speak_pressed = st.button("Speak")
    with col2:
        user_input = st.text_input("Type your message here...")
    if speak_pressed:
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            st.info("Listening...")
            try:
                audio = recognizer.listen(source, timeout=5)
                text = recognizer.recognize_google(audio)
                st.success(f"You = {text}")
                user_input = text
            except Exception:
                st.error("❌ Could not process your voice input.")
    if user_input:
        with st.spinner("🤖 Thinking..."):
            response = generate_ai_response(user_input)
            log_chat_interaction(user_input, response)
            save_analytics_data()
            st.markdown("### 🤖 Chatbot Response")
            st.markdown(f"> {response}")
    if os.path.exists("chat_history.json"):
        with open("chat_history.json") as f:
            history_data = json.load(f)
        st.download_button(
            label="⬇️ Download Chat History",
            data=json.dumps(history_data, indent=4),
            file_name="chat_history.json",
            mime="application/json"
        )
with tab2:
    st.subheader("📊 Chat Analytics Dashboard")
    if os.path.exists("chat_analytics.json"):
        with open("chat_analytics.json") as f:
            analytics = json.load(f)
        st.expander("📄 Raw JSON").json(analytics)
        st.subheader("📈 Graphical Insights")
        with st.container():
            col1, col2 = st.columns(2)
            col1.metric("💬 Total Interactions", analytics.get("interaction_count", 0))
            col2.metric("⚠️ Errors Encountered", analytics.get("error_count", 0))
        sentiments = analytics.get("sentiment_distribution", {})
        if sentiments:
            fig, ax = plt.subplots()
            sns.barplot(x=list(sentiments.keys()), y=list(sentiments.values()), ax=ax, palette="coolwarm")
            ax.set_title("Sentiment Distribution")
            ax.set_ylabel("Count")
            ax.set_xlabel("Sentiment")
            st.pyplot(fig)
        response_timings = analytics.get("response_timings", [])
        if response_timings:
            fig2, ax2 = plt.subplots()
            sns.histplot(response_timings, kde=True, bins=10, ax=ax2, color="cyan")
            ax2.set_title("Response Time Distribution (seconds)")
            st.pyplot(fig2)
        st.caption(f"📅 Last updated: {analytics.get('last_updated', 'N/A')}")
        st.download_button(
            label="⬇️ Download Analytics JSON",
            data=json.dumps(analytics, indent=4),
            file_name="chat_analytics.json",
            mime="application/json"
        )
    else:
        st.warning("🚫 No analytics data found.")
with tab3:
    st.subheader("🧾 System Error Logs")
    if os.path.exists("system_errors.json"):
        with open("system_errors.json") as f:
            logs = f.readlines()
        if logs:
            for log in logs[-10:]:
                st.code(log.strip())
            st.download_button(
                label="⬇️ Download System Logs",
                data="".join(logs),
                file_name="system_errors.json",
                mime="text/plain"
            )
        else:
            st.info("✅ No system errors recorded.")
    else:
        st.info("ℹ️ No system_errors.json file found.")
