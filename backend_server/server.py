from flask import Flask, request, jsonify
import joblib
import pandas as pd
import os

app = Flask(__name__)

# --- CONFIGURATION ---
# These names MUST match the files created by your trainmodels.py
MODEL_FILE = 'spam_model.pkl'
VECTORIZER_FILE = 'vectorizer.pkl'

# Global variables to hold our model
model = None
vectorizer = None

def load_model():
    """Loads the model and vectorizer from disk."""
    global model, vectorizer
    
    # Check if files exist first
    if not os.path.exists(MODEL_FILE) or not os.path.exists(VECTORIZER_FILE):
        print(f"CRITICAL ERROR: Could not find {MODEL_FILE} or {VECTORIZER_FILE}.")
        print("Please run 'trainmodels.py' first to generate these files.")
        return False

    try:
        model = joblib.load(MODEL_FILE)
        vectorizer = joblib.load(VECTORIZER_FILE)
        print(">>> Model and Vectorizer loaded successfully!")
        return True
    except Exception as e:
        print(f"Error loading files: {e}")
        return False

# Load model immediately when script starts
if not load_model():
    print("WARNING: Server started without model. Predictions will fail.")

def clean_text(text):
    """
    Basic text cleaning. 
    IMPORTANT: This must match the cleaning logic used in trainmodels.py exactly.
    """
    if not isinstance(text, str):
        return ""
    return text.lower() # Add more cleaning steps here if your trainer did them

@app.route('/', methods=['GET'])
def home():
    return "Spam Filter Server is Running! Use /predict endpoint."

@app.route('/predict', methods=['POST'])
def predict():
    global model, vectorizer
    
    if not model or not vectorizer:
        return jsonify({'error': 'Model not loaded. Check server console.'}), 500

    try:
        # 1. Get the JSON data sent from Android
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': 'No message provided'}), 400
            
        sms_text = data['message']
        print(f"Received message: {sms_text}")

        # 2. Preprocess the text
        cleaned_text = clean_text(sms_text)
        
        # 3. Convert text to numbers (Vectorize)
        # transform expects a list/iterable, so we wrap text in []
        text_vector = vectorizer.transform([cleaned_text])
        
        # 4. Predict
        # prediction comes back as an array, e.g., ['spam']
        prediction_label = model.predict(text_vector)[0]
        
        # Get probability (confidence) if supported
        # proba = model.predict_proba(text_vector).max()
        
        result = {
            'result': prediction_label, # 'spam' or 'ham'
            'original_message': sms_text
        }
        
        print(f"Prediction: {prediction_label}")
        return jsonify(result)

    except Exception as e:
        print(f"Prediction Error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # host='0.0.0.0' makes the server accessible to other devices (like the Emulator)
    # port=5000 is the standard Flask port
    app.run(host='0.0.0.0', port=5000, debug=True)