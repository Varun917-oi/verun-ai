from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
from datetime import datetime
import requests
import re

# ===================== CREATE APP =====================

app = Flask(__name__)
CORS(app)

# ===================== CONFIG =====================

OPENROUTER_API_KEY = "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"
WEATHER_API_KEY = "da3e71068f4f9798679f383c26b66567"
CITY = "Farrukhabad"

client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

# ===================== MEMORY =====================

conversation_history = [
    {"role": "system", "content": "You are Verun AI. Be intelligent, clear and concise."}
]

MAX_MESSAGES = 12

# ===================== UTILITIES =====================

def trim_memory():
    if len(conversation_history) > MAX_MESSAGES:
        conversation_history[:] = (
            conversation_history[:1] +
            conversation_history[-MAX_MESSAGES:]
        )

def is_math_expression(text):
    return re.fullmatch(r"[0-9+\-*/(). ]+", text.strip()) is not None

def get_date():
    return datetime.now().strftime("Today is %A, %d %B %Y.")

def get_time():
    return datetime.now().strftime("Current time is %I:%M %p.")

def get_weather():
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url)
        data = response.json()

        if data.get("cod") != 200:
            return "Unable to fetch weather data."

        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"]
        humidity = data["main"]["humidity"]

        return f"The current temperature in {CITY} is {temp}°C with {desc}. Humidity is {humidity}%."

    except:
        return "Weather service unavailable."

# ===================== ROUTES =====================

@app.route("/")
def home():
    return "Verun AI Backend Running"

@app.route("/chat", methods=["POST"])
def chat():

    user_input = request.json["message"]
    lower_input = user_input.lower().strip()

    # MATH
    if is_math_expression(user_input):
        try:
            result = eval(user_input)
            return jsonify({"response": str(result)})
        except:
            pass

    # DATE
    if "date" in lower_input:
        return jsonify({"response": get_date()})

    # TIME
    if "time" in lower_input:
        return jsonify({"response": get_time()})

    # WEATHER
    if "weather" in lower_input:
        return jsonify({"response": get_weather()})

    # AI CHAT
    conversation_history.append(
        {"role": "user", "content": user_input}
    )

    trim_memory()

    try:
        response = client.chat.completions.create(
            model="meta-llama/llama-3.1-8b-instruct",
            messages=conversation_history
        )

        reply = response.choices[0].message.content

        conversation_history.append(
            {"role": "assistant", "content": reply}
        )

    except Exception as e:
        reply = f"API Error: {str(e)}"

    return jsonify({"response": reply})

# ===================== RUN =====================

if __name__ == "__main__":
    app.run(debug=False)