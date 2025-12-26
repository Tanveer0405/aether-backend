from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os
import sys

app = Flask(__name__)
CORS(app)

# 1. SETUP API KEY
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    print("CRITICAL ERROR: GOOGLE_API_KEY is missing from Environment Variables!")
else:
    genai.configure(api_key=GOOGLE_API_KEY)

# 2. SMART MODEL SELECTION (The Fix)
# We ask Google what is available instead of guessing
active_model = None

try:
    print("--- CHECKING AVAILABLE MODELS ---")
    available_models = []
    
    # List all models that support 'generateContent' (chat)
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            available_models.append(m.name)
    
    print(f"MODELS FOUND: {available_models}")

    # Logic to pick the best one automatically
    # We prefer Flash, then Pro, then anything else that works.
    if 'models/gemini-1.5-flash' in available_models:
        model_name = 'gemini-1.5-flash'
    elif 'models/gemini-pro' in available_models:
        model_name = 'gemini-pro'
    elif available_models:
        model_name = available_models[0] # Pick the first available one
    else:
        raise Exception("No chat models found for this API key.")

    print(f"--- SELECTED MODEL: {model_name} ---")
    active_model = genai.GenerativeModel(model_name)

except Exception as e:
    print(f"--- MODEL SELECTION ERROR: {e} ---")

# 3. CHAT ROUTE
@app.route('/chat', methods=['POST'])
def chat():
    if not active_model:
        return jsonify({"reply": "System Failure: No AI Model selected. Check Logs."}), 500

    data = request.json
    user_message = data.get('message')
    
    system_instruction = "You are AETHER, an AI assistant for a space command dashboard. Keep answers brief, technical, and sci-fi."
    full_prompt = f"{system_instruction}\n\nUser: {user_message}\nAETHER:"

    try:
        response = active_model.generate_content(full_prompt)
        return jsonify({"reply": response.text})
    except Exception as e:
        print(f"GENERATION ERROR: {e}")
        return jsonify({"reply": "Error: Signal Lost. Check Mission Logs."}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)