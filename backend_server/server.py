import os
import csv
import joblib
import string
from flask import Flask, request, jsonify
import google.generativeai as genai

# --- CONFIGURATION ---
# PASTE YOUR KEY INSIDE THE QUOTES BELOW
GEMINI_API_KEY = "PASTE_YOUR_GOOGLE_API_KEY_HERE"

genai.configure(api_key=GEMINI_API_KEY)
model_gemini = genai.GenerativeModel('gemini-pro')

app = Flask(__name__)

# Load Local Models
if not os.path.exists('advanced_spam_filter.pkl'):
    print("Error: Model file not found. Run train_models.py first.")
    exit()

artifacts = joblib.load('advanced_spam_filter.pkl')
vectorizer = artifacts['vectorizer']
classifier = artifacts['classifier']

KNOWLEDGE_BASE_FILE = 'knowledge_base.csv'
if not os.path.exists(KNOWLEDGE_BASE_FILE):
    with open(KNOWLEDGE_BASE_FILE, 'w', newline='') as f:
        csv.writer(f).writerow(['message', 'verdict'])

def clean_text(text):
    return "".join([char for char in text if char not in string.punctuation]).lower()

def get_recent_attacks():
    attacks = []
    try:
        with open(KNOWLEDGE_BASE_FILE, 'r') as f:
            reader = list(csv.reader(f))
            if len(reader) > 1:
                attacks = [row[0] for row in reader[-3:]]
    except: pass
    return attacks

def save_to_knowledge_base(message, verdict):
    with open(KNOWLEDGE_BASE_FILE, 'a', newline='') as f:
        csv.writer(f).writerow([message, verdict])

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    raw_msg = data.get('message', '')
    cleaned_msg = clean_text(raw_msg)

    # 1. Local ML Check
    vec_msg = vectorizer.transform([cleaned_msg])
    rf_pred = classifier.predict(vec_msg)[0]
    rf_proba = classifier.predict_proba(vec_msg).max()

    # 2. Gemini AI Check
    recent_attacks = get_recent_attacks()
    prompt = f"Context: Recent attacks: {recent_attacks}. Task: Analyze SMS: '{raw_msg}'. Verdict (Safe/Suspicious/Phishing) and Reason."
    
    try:
        response = model_gemini.generate_content(prompt)
        ai_text = response.text.lower()
        ai_verdict = "phishing" if "phishing" in ai_text else ("suspicious" if "suspicious" in ai_text else "safe")
        ai_reason = response.text
    except:
        ai_verdict = "error"
        ai_reason = "AI Offline"

    # 3. Final Decision
    final_verdict = "safe"
    if ai_verdict == "phishing" or (rf_pred == "spam" and rf_proba > 0.85):
        final_verdict = "phishing"
        save_to_knowledge_base(raw_msg, final_verdict)
    elif ai_verdict == "suspicious":
        final_verdict = "suspicious"

    result = {'verdict': final_verdict, 'reasons': ai_reason}
    print(f"Analyzed: {raw_msg[:15]}... -> {result}")
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)