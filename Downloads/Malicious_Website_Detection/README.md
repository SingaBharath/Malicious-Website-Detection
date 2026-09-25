<div align="center">

# 🛡️ Malicious Website Detection

**An AI-powered real-time URL threat detection system using Machine Learning**

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-ML-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![Vercel](https://img.shields.io/badge/Deployed-Vercel-000000?style=for-the-badge&logo=vercel&logoColor=white)](https://vercel.com)

**🌐 Live Demo → [malicious-website-detection-s5pq.vercel.app](https://malicious-website-detection-s5pq.vercel.app)**

</div>

---

## 📖 About This Project

This project is an end-to-end **Malicious Website Detection System** that leverages Machine Learning to classify URLs in real-time. It was developed as part of original research exploring the effectiveness of different ML classifiers on URL-based threat detection.

The system analyzes a given URL using **lexical features** (structural properties of the URL string) and classifies it into one of four categories:

| Category | Description |
|----------|-------------|
| ✅ **Benign** | Safe website — no threats detected |
| 🎣 **Phishing** | Designed to steal user credentials |
| 💀 **Malware** | Hosts or distributes malicious software |
| 🖼️ **Defacement** | Website content has been illegitimately altered |

---

## 📄 Research Paper

<table>
<tr>
<td width="80" align="center">📑</td>
<td>

**Title:** A Comparative Analysis of Machine Learning Classifiers for Malicious Website Detection via Lexical and Host Features

**Author:** SingaBharath

**Domain:** Cybersecurity · Machine Learning · Web Security

**Status:** `Research Work`

> This system is the practical implementation of the research. The paper evaluates multiple ML classifiers — including Decision Trees, Random Forests, and others — on a large-scale dataset of 650,000+ URLs, comparing their accuracy, precision, recall, and F1-scores in detecting web-based threats.

</td>
</tr>
</table>

---

## 🧠 How It Works

```
User inputs URL
      │
      ▼
┌─────────────────────┐
│  1. URL Validation  │  ── Rejects non-URL inputs (e.g., random text)
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  2. Trusted Check   │  ── 50+ known safe domains (Google, Flipkart, etc.)
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  3. Live URL Check  │  ── Checks if website actually exists on the internet
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  4. Pattern Check   │  ── IP address URLs, suspicious TLDs, phishing keywords
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  5. ML Classifier   │  ── Decision Tree trained on 650K+ URLs
└────────┬────────────┘
         │
         ▼
    Final Result
```

---

## 🤖 ML Model Details

| Property | Value |
|----------|-------|
| **Algorithm** | Decision Tree Classifier |
| **Dataset** | [Malicious URLs Dataset – Kaggle](https://www.kaggle.com/datasets/sid321axn/malicious-urls-dataset) |
| **Total Records** | 651,191 URLs |
| **Model Accuracy** | 92.26% |
| **Model Size** | ~0.4 MB (Vercel-compatible) |
| **Features Used** | URL length, dot count, hyphen count, slash count, `@` symbols, `?`, `=`, HTTP/HTTPS flag, digit count |

### Classification Report

| Class | Precision | Recall | F1-Score |
|-------|-----------|--------|----------|
| Benign | 0.94 | 0.97 | 0.96 |
| Defacement | 0.93 | 0.97 | 0.95 |
| Malware | 0.94 | 0.89 | 0.91 |
| Phishing | 0.79 | 0.69 | 0.74 |
| **Overall** | **0.92** | **0.92** | **0.92** |

---

## 🗂️ Project Structure

```
Malicious-Website-Detection/
│
├── 📄 app.py                          # FastAPI backend with 5-layer detection
├── 🧠 train_model.py                  # ML model training script
├── 📊 Malicious_website_Detection.ipynb  # Full EDA + model comparison notebook
├── 🔧 requirements.txt                # Python dependencies
├── ⚙️  vercel.json                     # Vercel deployment config
├── 🤖 model.pkl                       # Trained Decision Tree model (0.4 MB)
├── 🏷️  label_encoder.pkl               # Class label encoder
│
└── 📁 frontend/
    ├── 🌐 index.html                  # Main UI
    ├── 🎨 style.css                   # Styling
    └── ⚡ script.js                   # Frontend logic & validation
```

---

## 🚀 Local Setup

```bash
# 1. Clone the repository
git clone https://github.com/SingaBharath/Malicious-Website-Detection.git
cd Malicious-Website-Detection/Downloads/Malicious_Website_Detection

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Download dataset from Kaggle and place malicious_phish.csv in root
# https://www.kaggle.com/datasets/sid321axn/malicious-urls-dataset

# 5. Train the model
python train_model.py

# 6. Run the app
python app.py
```

Open **http://localhost:8000** in your browser.

---

## 🌐 API Reference

### `POST /api/predict`

**Request:**
```json
{
  "url": "https://suspicious-paypal-verify.tk/login"
}
```

**Response (Threat):**
```json
{
  "url": "https://suspicious-paypal-verify.tk/login",
  "prediction": "phishing",
  "threat_score": 95.0,
  "is_safe": false,
  "class_probabilities": {
    "benign": 0.05,
    "phishing": 0.95,
    "defacement": 0.0,
    "malware": 0.0
  },
  "note": "Suspicious URL patterns detected."
}
```

**Response (Safe):**
```json
{
  "url": "https://google.com",
  "prediction": "benign",
  "threat_score": 0.0,
  "is_safe": true,
  "note": "Verified trusted domain."
}
```

---

## 🔒 Detection Layers

| Layer | Check | Purpose |
|-------|-------|---------|
| 1 | **URL Format Validation** | Rejects non-URLs (plain text, keywords) |
| 2 | **Trusted Domain Whitelist** | 50+ verified safe domains |
| 3 | **Live URL Reachability** | Checks if website actually exists |
| 4 | **Suspicious Pattern Analysis** | IP URLs, free TLDs (`.tk`, `.ml`), phishing keywords |
| 5 | **ML Model Classification** | Decision Tree on 650K+ URL dataset |

---

## 📦 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python, FastAPI, Uvicorn |
| **ML** | scikit-learn, pandas, joblib |
| **HTTP Checks** | httpx |
| **Frontend** | HTML5, CSS3, Vanilla JS |
| **Hosting** | Vercel |
| **Version Control** | GitHub |

---

## 📝 License

This project is open source under the [MIT License](LICENSE).

---

<div align="center">

**Made with ❤️ by [SingaBharath](https://github.com/SingaBharath)**

⭐ Star this repo if you found it useful!

</div>
