from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import pandas as pd
import uvicorn
import os
import re
from urllib.parse import urlparse

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model and encoder
model_path = "model.pkl"
encoder_path = "label_encoder.pkl"

if os.path.exists(model_path) and os.path.exists(encoder_path):
    model = joblib.load(model_path)
    label_encoder = joblib.load(encoder_path)
else:
    model = None
    label_encoder = None

# -------------------------------------------------------
# Expanded whitelist of trusted domains
# -------------------------------------------------------
TRUSTED_DOMAINS = [
    # Search & Tech
    'google.com', 'google.co.in', 'google.co.uk',
    'youtube.com', 'youtu.be',
    'gmail.com', 'googlemail.com',
    'microsoft.com', 'outlook.com', 'live.com', 'hotmail.com',
    'office.com', 'microsoft365.com',
    'apple.com', 'icloud.com',
    'bing.com', 'yahoo.com', 'yahoo.co.in',
    # Social Media
    'facebook.com', 'fb.com', 'messenger.com',
    'instagram.com', 'twitter.com', 'x.com',
    'linkedin.com', 'pinterest.com', 'reddit.com',
    'tiktok.com', 'snapchat.com', 'whatsapp.com',
    'telegram.org',
    # Dev & Cloud
    'github.com', 'gitlab.com', 'stackoverflow.com',
    'vercel.app', 'netlify.app', 'heroku.com',
    'aws.amazon.com', 'cloud.google.com', 'azure.microsoft.com',
    # Shopping
    'amazon.com', 'amazon.in', 'flipkart.com', 'myntra.com',
    'ebay.com', 'walmart.com', 'meesho.com',
    # News & Info
    'wikipedia.org', 'bbc.com', 'cnn.com', 'ndtv.com',
    'timesofindia.com', 'thehindu.com',
    # Payments & Banking
    'paypal.com', 'razorpay.com', 'paytm.com',
    'phonepe.com', 'gpay.com',
    # Education
    'coursera.org', 'udemy.com', 'edx.org', 'khanacademy.org',
    'nptel.ac.in', 'swayam.gov.in',
    # Streaming
    'netflix.com', 'spotify.com', 'hotstar.com',
    'primevideo.com', 'disney.com',
    # Government
    'gov.in', 'nic.in', 'uidai.gov.in',
]

def is_valid_url(url: str) -> bool:
    """Check if the input is a valid URL format."""
    # Must start with http:// or https://
    url = url.strip()
    
    # Basic pattern check
    url_pattern = re.compile(
        r'^(https?://)'                    # http:// or https://
        r'([a-zA-Z0-9]'                   # domain start
        r'([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?'
        r'\.)'                             # dot
        r'+[a-zA-Z]{2,}'                  # TLD
        r'(/.*)?$',                        # optional path
        re.IGNORECASE
    )
    
    if not url_pattern.match(url):
        return False
    
    try:
        parsed = urlparse(url)
        return all([parsed.scheme in ('http', 'https'), parsed.netloc])
    except Exception:
        return False

def is_trusted(url: str) -> bool:
    """Check if URL belongs to a trusted domain."""
    url_lower = url.lower()
    try:
        parsed = urlparse(url_lower)
        hostname = parsed.netloc.replace('www.', '')
    except Exception:
        hostname = url_lower

    for domain in TRUSTED_DOMAINS:
        if hostname == domain or hostname.endswith('.' + domain) or domain in hostname:
            return True
    return False


class URLRequest(BaseModel):
    url: str


@app.post("/api/predict")
def predict_url(request: URLRequest):
    if not model or not label_encoder:
        raise HTTPException(status_code=500, detail="Model not loaded.")

    url = request.url.strip()

    # ---- Step 1: Validate URL format ----
    if not is_valid_url(url):
        raise HTTPException(
            status_code=400,
            detail="Invalid URL. Please enter a valid URL starting with http:// or https:// (e.g., https://google.com)"
        )

    # ---- Step 2: Check trusted domains whitelist ----
    if is_trusted(url):
        return {
            "url": url,
            "prediction": "benign",
            "threat_score": 0.0,
            "class_probabilities": {
                "benign": 1.0, "phishing": 0.0,
                "defacement": 0.0, "malware": 0.0
            },
            "is_safe": True
        }

    # ---- Step 3: Extract features for ML model ----
    features = {
        'url_length':         len(url),
        'num_dots':           url.count('.'),
        'num_hyphens':        url.count('-'),
        'num_slashes':        url.count('/'),
        'num_at_symbols':     url.count('@'),
        'num_question_marks': url.count('?'),
        'num_equals_signs':   url.count('='),
        'has_http':           1 if 'http://' in url else 0,
        'has_https':          1 if 'https://' in url else 0,
        'digit_count':        sum(c.isdigit() for c in url)
    }

    df = pd.DataFrame([features])

    try:
        prediction_encoded  = model.predict(df)[0]
        prediction_proba    = model.predict_proba(df)[0]
        prediction_label    = label_encoder.inverse_transform([prediction_encoded])[0]

        class_probs = {
            label_encoder.inverse_transform([i])[0]: float(prob)
            for i, prob in enumerate(prediction_proba)
        }

        # ---- Step 4: Confidence threshold to reduce false positives ----
        # If benign probability is above 40%, treat as benign
        benign_prob = class_probs.get('benign', 0)
        if benign_prob >= 0.40 and prediction_label != 'benign':
            prediction_label = 'benign'

        threat_score = float(max(prediction_proba) * 100)
        is_safe = prediction_label == 'benign'

        return {
            "url":                url,
            "prediction":         prediction_label,
            "threat_score":       threat_score,
            "class_probabilities": class_probs,
            "is_safe":            is_safe
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)
