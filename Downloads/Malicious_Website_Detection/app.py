from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import pandas as pd
import uvicorn
import os
import re
import httpx
from urllib.parse import urlparse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model and encoder
model_path   = "model.pkl"
encoder_path = "label_encoder.pkl"

if os.path.exists(model_path) and os.path.exists(encoder_path):
    model         = joblib.load(model_path)
    label_encoder = joblib.load(encoder_path)
else:
    model         = None
    label_encoder = None

# -------------------------------------------------------
# Trusted domains — always return Safe
# -------------------------------------------------------
TRUSTED_DOMAINS = [
    'google.com','google.co.in','google.co.uk','googleapis.com',
    'youtube.com','youtu.be','ytimg.com',
    'gmail.com','googlemail.com','accounts.google.com',
    'microsoft.com','outlook.com','live.com','hotmail.com','office.com',
    'apple.com','icloud.com','appleid.apple.com',
    'bing.com','yahoo.com','yahoo.co.in','duckduckgo.com',
    'facebook.com','fb.com','messenger.com','fbcdn.net',
    'instagram.com','twitter.com','x.com','t.co',
    'linkedin.com','pinterest.com','reddit.com','redd.it',
    'tiktok.com','snapchat.com','whatsapp.com','telegram.org',
    'github.com','gitlab.com','stackoverflow.com','npmjs.com',
    'vercel.app','netlify.app','heroku.com','railway.app',
    'amazon.com','amazon.in','flipkart.com','myntra.com',
    'ebay.com','walmart.com','meesho.com','ajio.com','nykaa.com',
    'wikipedia.org','bbc.com','cnn.com','ndtv.com',
    'timesofindia.com','thehindu.com','indiatoday.in',
    'paypal.com','razorpay.com','paytm.com','phonepe.com',
    'coursera.org','udemy.com','edx.org','khanacademy.org',
    'nptel.ac.in','swayam.gov.in','moodle.org',
    'netflix.com','spotify.com','hotstar.com','primevideo.com',
    'gov.in','nic.in','uidai.gov.in','incometax.gov.in',
    'openai.com','anthropic.com','gemini.google.com',
    'canva.com','figma.com','notion.so','slack.com','zoom.us',
    'dropbox.com','drive.google.com','docs.google.com',
]

# -------------------------------------------------------
# Suspicious TLDs commonly used in free phishing domains
# -------------------------------------------------------
SUSPICIOUS_TLDS = ['.tk', '.ml', '.ga', '.cf', '.gq', '.pw', '.top', '.xyz', '.click', '.loan']

# -------------------------------------------------------
# Suspicious keywords in URL
# -------------------------------------------------------
SUSPICIOUS_KEYWORDS = [
    'login', 'verify', 'secure', 'update', 'confirm', 'account',
    'banking', 'signin', 'paypal', 'ebay', 'amazon', 'apple',
    'microsoft', 'support', 'helpdesk', 'password', 'credential',
    'wallet', 'blockchain', 'bitcoin', 'crypto', 'free-money',
    'winner', 'prize', 'lucky', 'claim', 'reward'
]


class URLRequest(BaseModel):
    url: str


def is_valid_url(url: str) -> bool:
    """Check if input is a properly formatted URL."""
    url = url.strip()
    pattern = re.compile(
        r'^(https?://)'
        r'([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)'
        r'+[a-zA-Z]{2,}'
        r'(/.*)?$',
        re.IGNORECASE
    )
    if not pattern.match(url):
        return False
    try:
        parsed = urlparse(url)
        return all([parsed.scheme in ('http', 'https'), parsed.netloc])
    except Exception:
        return False


def is_trusted(url: str) -> bool:
    """Check if URL is a known trusted domain."""
    try:
        hostname = urlparse(url.lower()).netloc.replace('www.', '')
    except Exception:
        return False
    for domain in TRUSTED_DOMAINS:
        if hostname == domain or hostname.endswith('.' + domain):
            return True
    return False


def check_url_live(url: str):
    """
    Try to reach the URL.
    Returns: 'reachable', 'not_found', or 'unknown'
    """
    try:
        with httpx.Client(timeout=6, follow_redirects=True,
                          headers={'User-Agent': 'Mozilla/5.0'}) as client:
            resp = client.head(url)
            if resp.status_code < 400:
                return 'reachable'
            elif resp.status_code in (404, 410):
                return 'not_found'
            else:
                return 'reachable'  # site exists, might just be method-restricted
    except httpx.ConnectError:
        return 'not_found'   # DNS failed / server refused
    except httpx.TimeoutException:
        return 'unknown'     # Slow site — can't determine
    except Exception:
        return 'unknown'


def has_suspicious_patterns(url: str) -> bool:
    """Check for known phishing URL patterns."""
    url_lower = url.lower()
    # IP address instead of domain
    if re.search(r'https?://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', url_lower):
        return True
    # Suspicious TLD
    try:
        tld = '.' + urlparse(url_lower).netloc.split('.')[-1].split(':')[0]
        if tld in SUSPICIOUS_TLDS:
            return True
    except Exception:
        pass
    # Too many subdomains (e.g. paypal.com.login.verify.evil.com)
    try:
        netloc = urlparse(url_lower).netloc
        if netloc.count('.') >= 4:
            return True
    except Exception:
        pass
    # Suspicious keywords in path/domain
    suspicious_count = sum(1 for kw in SUSPICIOUS_KEYWORDS if kw in url_lower)
    if suspicious_count >= 2:
        return True
    return False


@app.post("/api/predict")
def predict_url(request: URLRequest):
    if not model or not label_encoder:
        raise HTTPException(status_code=500, detail="Model not loaded.")

    url = request.url.strip()

    # ── Step 1: Validate URL format ─────────────────────
    if not is_valid_url(url):
        raise HTTPException(
            status_code=400,
            detail="Please enter a valid URL starting with https:// or http://  (e.g., https://google.com)"
        )

    # ── Step 2: Trusted whitelist ────────────────────────
    if is_trusted(url):
        return {
            "url": url, "prediction": "benign",
            "threat_score": 0.0, "is_safe": True,
            "class_probabilities": {"benign":1.0,"phishing":0.0,"defacement":0.0,"malware":0.0},
            "note": "Verified trusted domain."
        }

    # ── Step 3: Check if website actually exists ─────────
    live_status = check_url_live(url)

    if live_status == 'not_found':
        raise HTTPException(
            status_code=404,
            detail=f"The website '{url}' does not exist or is unreachable. Please check the URL and try again."
        )

    # ── Step 4: Check for obvious phishing patterns ──────
    if has_suspicious_patterns(url):
        return {
            "url": url, "prediction": "phishing",
            "threat_score": 95.0, "is_safe": False,
            "class_probabilities": {"benign":0.05,"phishing":0.95,"defacement":0.0,"malware":0.0},
            "note": "Suspicious URL patterns detected."
        }

    # ── Step 5: ML Model prediction ──────────────────────
    features = {
        'url_length':          len(url),
        'num_dots':            url.count('.'),
        'num_hyphens':         url.count('-'),
        'num_slashes':         url.count('/'),
        'num_at_symbols':      url.count('@'),
        'num_question_marks':  url.count('?'),
        'num_equals_signs':    url.count('='),
        'has_http':            1 if 'http://' in url else 0,
        'has_https':           1 if 'https://' in url else 0,
        'digit_count':         sum(c.isdigit() for c in url)
    }

    df = pd.DataFrame([features])

    try:
        prediction_encoded = model.predict(df)[0]
        prediction_proba   = model.predict_proba(df)[0]
        prediction_label   = label_encoder.inverse_transform([prediction_encoded])[0]

        class_probs = {
            label_encoder.inverse_transform([i])[0]: float(prob)
            for i, prob in enumerate(prediction_proba)
        }

        benign_prob = class_probs.get('benign', 0)

        # If site is LIVE and benign probability is reasonable → treat as safe
        if live_status == 'reachable' and benign_prob >= 0.30:
            prediction_label = 'benign'

        # General threshold: if benign >= 45% → safe
        elif benign_prob >= 0.45:
            prediction_label = 'benign'

        threat_score = float(max(prediction_proba) * 100)
        is_safe      = prediction_label == 'benign'

        return {
            "url":                 url,
            "prediction":          prediction_label,
            "threat_score":        threat_score,
            "class_probabilities": class_probs,
            "is_safe":             is_safe,
            "note":                "Live site verified." if live_status == 'reachable' else "Site status unknown."
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)
