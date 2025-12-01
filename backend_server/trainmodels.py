import pandas as pd
import string
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier, IsolationForest

# 1. Load Data
try:
    df = pd.read_csv('SMSSpamCollection', sep='\t', names=['label', 'message'], header=None)
except FileNotFoundError:
    print("Error: 'SMSSpamCollection' file not found. Please download it from UCI repository.")
    exit()

def clean_text(text):
    text = "".join([char for char in text if char not in string.punctuation])
    return text.lower()

df['clean_message'] = df['message'].apply(clean_text)

# 2. Vectorization (TF-IDF)
vectorizer = TfidfVectorizer(stop_words='english', max_features=3000)
X = vectorizer.fit_transform(df['clean_message'])
y = df['label']

# 3. Train Main Classifier: Random Forest
print("Training Random Forest...")
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(X, y)

# 4. Train Anomaly Detector: Isolation Forest
print("Training Anomaly Detector...")
# --- FIX APPLIED HERE: Added .values to prevent crash ---
mask = (y == 'ham').values
ham_data = X[mask]

anomaly_model = IsolationForest(contamination=0.1, random_state=42)
anomaly_model.fit(ham_data)

# 5. Save Everything
artifacts = {
    'vectorizer': vectorizer,
    'classifier': rf_model,
    'anomaly_detector': anomaly_model
}
joblib.dump(artifacts, 'advanced_spam_filter.pkl')
print("Success: 'advanced_spam_filter.pkl' created.")