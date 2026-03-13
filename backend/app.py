from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
from datetime import datetime
import requests
import asyncio
import edge_tts
import tempfile
import os
import threading
import re
from dotenv import load_dotenv

# ===================== LOAD ENV =====================

load_dotenv()

# ===================== CREATE APP =====================

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# ===================== CONFIG =====================

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
CITY = os.getenv("CITY", "Farrukhabad")

client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

# ===================== MEMORY =====================

conversation_history = [
    {"role": "system", "content": "You are Verun AI. Be intelligent, clear and concise."}
]

MAX_MESSAGES = 12

# ===================== EDGE TTS =====================

VOICE = "en-IN-PrabhatNeural"

def speak(text):
    threading.Thread(
        target=lambda: asyncio.run(edge_speak(text)),
        daemon=True
    ).start()

async def edge_speak(text):
    communicate = edge_tts.Communicate(text, VOICE)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
        temp_path = tmp.name

    await communicate.save(temp_path)

    # playsound removed (servers cannot play audio)
    # file will simply be generated and removed

    try:
        pass
    finally:
        os.remove(temp_path)

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
    data = request.get_json()
    user_input = data.get("message", "")

    lower_input = user_input.lower().strip()

    # MATH
    if is_math_expression(user_input):
        try:
            result = eval(user_input)
            reply = str(result)
            speak(reply)
            return jsonify({"response": reply})
        except:
            pass

    # DATE
    if "date" in lower_input:
        reply = get_date()
        speak(reply)
        return jsonify({"response": reply})

    # TIME
    if "time" in lower_input:
        reply = get_time()
        speak(reply)
        return jsonify({"response": reply})

    # WEATHER
    if "weather" in lower_input:
        reply = get_weather()
        speak(reply)
        return jsonify({"response": reply})

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

    speak(reply)
    return jsonify({"response": reply})

# ===================== RUN =====================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
