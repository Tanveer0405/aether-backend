from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os

app = Flask(__name__)
CORS(app)

# CONFIGURATION
# This tells python to get the key from Render's "Environment" tab
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

# Set up the model
model = genai.GenerativeModel('gemini-pro')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message')
    
    # Optional: Add a "System Prompt" to give the bot a personality
    system_instruction = "You are AETHER, an AI assistant for a space command dashboard. Keep answers brief, technical, and sci-fi."
    full_prompt = f"{system_instruction}\n\nUser: {user_message}\nAETHER:"

    try:
        response = model.generate_content(full_prompt)
        return jsonify({"reply": response.text})
    except Exception as e:
        # This prints the error to Render logs so you can see what went wrong
        print(f"Error: {e}") 
        return jsonify({"reply": "Error: Signal Lost. Check Mission Logs."}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)