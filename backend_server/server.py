import os
import joblib
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import google.generativeai as genai

# 1. Setup Environment
load_dotenv() # This loads the .env file with your API key
app = Flask(__name__)

# 2. Configuration
# This matches the file created by your training script
MODEL_FILE = 'advanced_spam_filter.pkl'
API_KEY = os.getenv("GEMINI_API_KEY")

# Global variable to hold the model
model = None

def load_model():
    """Loads the single pipeline file (Vectorizer + Classifier combined)."""
    global model
    
    if not os.path.exists(MODEL_FILE):
        print(f"CRITICAL ERROR: Could not find {MODEL_FILE}")
        print("Please run 'trainmodels.py' first.")
        return False

    try:
        # We only need to load one file now!
        model = joblib.load(MODEL_FILE)
        print(f">>> Successfully loaded {MODEL_FILE}")
        return True
    except Exception as e:
        print(f"Error loading model: {e}")
        return False

# 3. Gemini (Backup Brain) Logic
if API_KEY:
    genai.configure(api_key=API_KEY)
else:
    print("WARNING: No GEMINI_API_KEY found in .env file!")

def check_with_gemini(message):
    try:
        gemini_model = genai.GenerativeModel('gemini-pro')
        response = gemini_model.generate_content(
            f"Analyze this SMS: '{message}'. Reply ONLY with 'spam' or 'ham'."
        )
        clean_response = response.text.strip().lower()
        # Remove any extra punctuation just in case
        return clean_response.replace(".", "")
    except Exception as e:
        print(f"Gemini Error: {e}")
        return "ham" # Default to safe if API fails

# 4. The Server Route
@app.route('/predict', methods=['POST'])
def predict():
    # Ensure model is loaded
    if model is None:
        return jsonify({"error": "Model not loaded"}), 500

    data = request.json
    sms_text = data.get('message', '')

    print(f"Received: {sms_text}")

    try:
        # The pipeline handles vectorization automatically!
        # predict_proba returns [[prob_ham, prob_spam]]
        probabilities = model.predict_proba([sms_text])[0]
        spam_score = probabilities[1] # The second number is the "Spam %"

        print(f"Local Model Confidence: {spam_score:.2f}")

        # DECISION LOGIC:
        # > 80% confident it's spam? -> SPAM
        # < 20% confident (very sure it's safe)? -> SAFE
        # In between? -> Ask Gemini
        
        verdict = "safe"
        source = "Local Model"

        if spam_score > 0.8:
            verdict = "spam"
        elif spam_score < 0.2:
            verdict = "safe"
        else:
            print("Model is unsure... Asking Gemini.")
            verdict = check_with_gemini(sms_text)
            source = "Gemini AI"

        return jsonify({
            "result": verdict, 
            "source": source,
            "confidence": float(spam_score)
        })

    except Exception as e:
        print(f"Prediction Error: {e}")
        return jsonify({"error": str(e)}), 500

# 5. Start the Server
if __name__ == '__main__':
    # Load model immediately on startup
    if load_model():
        app.run(host='0.0.0.0', port=5000)
