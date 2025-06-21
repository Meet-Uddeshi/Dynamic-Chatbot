# Step => 1 Import required libraries
from flask import Flask, render_template, request, jsonify
import google.generativeai as gen_ai
import datetime
import json
import os
import time
from collections import defaultdict
import re
import speech_recognition as sr

# Step => 2 Define configuration settings and initialize analytics tracker
GEMINI_API_KEY = "YOUR_API_KEY"
GEMINI_MODEL = "gemini-1.5-flash"
CONVERSATION_LOG = "chat_history.json"
ANALYTICS_LOG = "chat_analytics.json"
analytics_tracker = {
    "interaction_count": 0,
    "sentiment_distribution": defaultdict(int),
    "response_timings": [],
    "error_count": 0
}

# Step => 3 Define intent recognition logic (Rule-based)
def recognize_intent(user_input):
    if any(x in user_input.lower() for x in ["weather", "temperature"]):
        return "weather_info"
    if "joke" in user_input.lower():
        return "tell_joke"
    if any(x in user_input.lower() for x in ["help", "support"]):
        return "support_request"
    return "general_query"

# Step => 4 Define named entity extraction logic (using basic regex)
def extract_named_entities(text):
    entities = re.findall(r"[A-Z][a-z]+", text)
    return list(set(entities))

# Step => 5 Define sentiment detection logic (keyword-based)
def detect_sentiment(text):
    positive = ["thank", "great", "awesome", "love"]
    negative = ["bad", "hate", "angry", "frustrated"]
    text = text.lower()
    if any(p in text for p in positive):
        return "positive"
    elif any(n in text for n in negative):
        return "negative"
    return "neutral"

# Step => 6 Initialize AI chatbot session
def initialize_ai_chat_session():
    try:
        gen_ai.configure(api_key=GEMINI_API_KEY)
        ai_config = """
        You are a smart AI assistant. Follow these principles:
        - Understand and remember context.
        - Identify intents and extract entities.
        - Adjust tone based on sentiment.
        - Provide short and accurate responses.
        """
        ai_model = gen_ai.GenerativeModel(GEMINI_MODEL, system_instruction=ai_config)
        return ai_model.start_chat(history=[])
    except Exception as e:
        log_system_error("INITIALIZATION", str(e))
        return None

# Step => 7 Create global chat session object
chat_session = initialize_ai_chat_session()

# Step => 8 Generate AI response from user query
def generate_ai_response(user_query):
    start_time = time.time()
    try:
        sentiment = detect_sentiment(user_query)
        intent = recognize_intent(user_query)
        entities = extract_named_entities(user_query)
        prompt = f"""
        User Intent: {intent}
        Sentiment: {sentiment}
        Named Entities: {', '.join(entities)}
        Query: {user_query}
        """
        ai_response = chat_session.send_message(prompt)
        response_text = ai_response.text
        processing_time = time.time() - start_time
        update_analytics("response_timing", processing_time)
        update_analytics("sentiment", sentiment)
        analytics_tracker["interaction_count"] += 1
        return response_text
    except Exception as e:
        update_analytics("error")
        return f"Sorry, an error occurred: {str(e)}"

# Step => 9 Log chat interaction to JSON file
def log_chat_interaction(user_input, ai_response):
    log_entry = {
        "timestamp": str(datetime.datetime.now()),
        "user_query": user_input,
        "ai_response": ai_response
    }
    if not os.path.exists(CONVERSATION_LOG):
        with open(CONVERSATION_LOG, "w") as f:
            json.dump([log_entry], f)
    else:
        with open(CONVERSATION_LOG, "r+") as f:
            data = json.load(f)
            data.append(log_entry)
            f.seek(0)
            json.dump(data, f)

# Step => 10 Update analytics metrics
def update_analytics(metric, value=None):
    if metric == "response_timing":
        analytics_tracker["response_timings"].append(value)
    elif metric == "sentiment":
        analytics_tracker["sentiment_distribution"][value] += 1
    elif metric == "error":
        analytics_tracker["error_count"] += 1

# Step => 11 Save analytics to file
def save_analytics_data():
    analytics_tracker["last_updated"] = str(datetime.datetime.now())
    with open(ANALYTICS_LOG, "w") as f:
        json.dump(analytics_tracker, f, default=list)

# Step => 12 Log system errors to file
def log_system_error(context, details):
    error_entry = {
        "timestamp": str(datetime.datetime.now()),
        "context": context,
        "details": details
    }
    with open("system_errors.json", "a") as f:
        f.write(json.dumps(error_entry) + "\n")

# Step => 13 Setup Flask app and define routes
app = Flask(__name__)
@app.route("/")
def index():
    return render_template("index.html")
@app.route("/get_response", methods=["POST"])
def get_response():
    user_message = request.json.get("message")
    ai_response = generate_ai_response(user_message)
    log_chat_interaction(user_message, ai_response)
    return jsonify({"response": ai_response})
@app.route("/analytics")
def analytics_dashboard():
    if os.path.exists(ANALYTICS_LOG):
        with open(ANALYTICS_LOG) as f:
            data = json.load(f)
        return render_template("analytics.html", data=data)
    return "Analytics not found"

# Step => 14 Start the Flask application
if __name__ == "__main__":
    if os.path.exists(ANALYTICS_LOG):
        try:
            with open(ANALYTICS_LOG) as f:
                previous_data = json.load(f)
                analytics_tracker.update(previous_data)
                if "sentiment_distribution" in previous_data:
                    analytics_tracker["sentiment_distribution"] = defaultdict(int, previous_data["sentiment_distribution"])
        except:
            pass
    app.run(debug=True)

