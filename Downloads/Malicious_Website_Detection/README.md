# 🛡️ Malicious Website Detection

A machine learning-powered web application that detects malicious websites using URL-based lexical and host features.

## 📋 Overview

This project uses a trained ML classifier to predict whether a given URL is:
- ✅ **Benign** – Safe to visit
- ⚠️ **Phishing** – Attempts to steal credentials
- 💀 **Malware** – Hosts malicious software
- 🖼️ **Defacement** – Altered website content

## 🚀 Features

- Real-time URL analysis via REST API
- FastAPI backend with CORS support
- Responsive frontend (HTML/CSS/JS)
- Trained on the [Malicious URLs dataset](https://www.kaggle.com/datasets/sid321axn/malicious-urls-dataset)

## 🧠 ML Model

- **Algorithm**: Random Forest Classifier
- **Features**: URL length, dot count, hyphen count, slash count, special character counts, HTTP/HTTPS presence, digit count
- **Dataset**: `malicious_phish.csv` (~450K URLs)
- **Classes**: benign, phishing, defacement, malware

## 🗂️ Project Structure

```
Malicious_Website_Detection/
├── app.py              # FastAPI backend
├── train_model.py      # Model training script
├── requirements.txt    # Python dependencies
├── vercel.json         # Vercel deployment config
├── frontend/
│   ├── index.html      # Main webpage
│   ├── style.css       # Styling
│   └── script.js       # Frontend logic
└── Malicious_website_Detection.ipynb  # Jupyter notebook (EDA + training)
```

## ⚙️ Local Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Train the model (requires malicious_phish.csv)
python train_model.py

# Run the app
python app.py
```

Open your browser at `http://localhost:8000`

## 🌐 Deployment

This app is deployed on **Vercel**. The `model.pkl` and `label_encoder.pkl` files are required at runtime.

> **Note:** `model.pkl` (~150MB) and `malicious_phish.csv` (~45MB) are excluded from this repo due to size limits. Run `train_model.py` to regenerate them.

## 📊 Notebook

See `Malicious_website_Detection.ipynb` for full EDA, feature engineering, model comparison, and evaluation.
