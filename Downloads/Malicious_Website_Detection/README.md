# 🛡️ Malicious Website Detection

> A machine learning-powered web application that detects malicious URLs in real-time using lexical and host-based features.

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?logo=fastapi)
![scikit-learn](https://img.shields.io/badge/scikit--learn-ML-orange?logo=scikit-learn)
![Vercel](https://img.shields.io/badge/Deploy-Vercel-black?logo=vercel)

---

## 📌 What It Does

Paste any URL and the app will classify it as:

| Label | Meaning |
|-------|---------|
| ✅ **Benign** | Safe to visit |
| ⚠️ **Phishing** | Tries to steal your credentials |
| 💀 **Malware** | Hosts malicious software |
| 🖼️ **Defacement** | Webpage content has been altered |

---

## 🗂️ Project Structure

```
Malicious_Website_Detection/
│
├── app.py                          # FastAPI backend (REST API)
├── train_model.py                  # Script to train the ML model
├── update_nb.py                    # Notebook sync utility
├── requirements.txt                # Python dependencies
├── vercel.json                     # Vercel deployment config
├── label_encoder.pkl               # Saved label encoder
├── model.pkl                       # Trained ML model (generated locally)
├── malicious_phish.csv             # Dataset (not in repo - too large)
│
└── frontend/
    ├── index.html                  # Main webpage UI
    ├── style.css                   # Styles
    └── script.js                   # Frontend logic
```

---

## 🧠 ML Model Details

- **Algorithm**: Random Forest Classifier
- **Dataset**: [Malicious URLs Dataset](https://www.kaggle.com/datasets/sid321axn/malicious-urls-dataset) (~450K URLs)
- **Classes**: `benign`, `phishing`, `defacement`, `malware`
- **Features Used**:
  - URL length
  - Number of dots, hyphens, slashes
  - Presence of `@`, `?`, `=` symbols
  - HTTP vs HTTPS
  - Digit count in URL

---

## ⚙️ Local Setup & Run

### Step 1 — Clone the repo

```bash
git clone https://github.com/SingaBharath/Malicious-Website-Detection.git
cd Malicious-Website-Detection
```

### Step 2 — Create a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Download the dataset

Download `malicious_phish.csv` from [Kaggle](https://www.kaggle.com/datasets/sid321axn/malicious-urls-dataset) and place it in the project root.

### Step 5 — Train the model

```bash
python train_model.py
```

This generates `model.pkl` and `label_encoder.pkl`.

### Step 6 — Run the app

```bash
python app.py
```

Open your browser at **http://localhost:8000** 🎉

---

## 🚀 Deploy to Vercel (Step-by-Step)

> **Important:** Vercel has a **50MB limit** on serverless functions. Since `model.pkl` is ~150MB, follow this **two-part deployment strategy**:
>
> - **Frontend** → Deploy on Vercel (free, instant)
> - **Backend API** → Deploy on [Render](https://render.com) (free tier available)

---

### 🌐 Part 1: Deploy Frontend on Vercel

#### Option A: Via Vercel Website (Recommended for beginners)

1. Go to **[vercel.com](https://vercel.com)** and sign in with GitHub
2. Click **"Add New Project"**
3. Import your repo: `SingaBharath/Malicious-Website-Detection`
4. In **"Framework Preset"**, select **Other**
5. Set **Root Directory** to `frontend`
6. Click **"Deploy"**

Your frontend will be live at a URL like:
`https://malicious-website-detection.vercel.app`

---

#### Option B: Via Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy from the frontend folder
cd frontend
vercel

# Follow the prompts:
# - Set up and deploy? → Yes
# - Which scope? → your account
# - Link to existing project? → No
# - Project name? → malicious-website-detection
# - Directory → ./
# - Override settings? → No
```

---

### 🖥️ Part 2: Deploy Backend (FastAPI) on Render

Since `model.pkl` is too large for Vercel, deploy the Python backend on **Render**:

1. Go to **[render.com](https://render.com)** and sign in with GitHub
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repo: `SingaBharath/Malicious-Website-Detection`
4. Fill in settings:
   - **Name**: `malicious-website-detection-api`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`
5. Click **"Create Web Service"**

> ⚠️ **Note**: You must upload `model.pkl` to Render or use Render's persistent disk. The file is excluded from GitHub due to its 150MB size.

---

### 🔗 Connect Frontend to Backend

Once your backend is deployed on Render (e.g., `https://your-api.onrender.com`), update the API URL in `frontend/script.js`:

```js
// Change this line:
const API_URL = "http://localhost:8000";

// To your Render backend URL:
const API_URL = "https://your-api.onrender.com";
```

Then redeploy the frontend on Vercel.

---

## 📊 Jupyter Notebook

The file `Malicious_website_Detection.ipynb` contains:
- Exploratory Data Analysis (EDA)
- Feature engineering
- Model comparison (Random Forest, Decision Tree, etc.)
- Evaluation metrics (accuracy, confusion matrix, etc.)

---

## 🧪 API Reference

### `POST /api/predict`

**Request:**
```json
{
  "url": "http://suspicious-login.tk/paypal/verify"
}
```

**Response:**
```json
{
  "url": "http://suspicious-login.tk/paypal/verify",
  "prediction": "phishing",
  "threat_score": 94.3,
  "class_probabilities": {
    "benign": 0.02,
    "phishing": 0.94,
    "defacement": 0.02,
    "malware": 0.02
  },
  "is_safe": false
}
```

---

## 📦 Dependencies

```
fastapi
uvicorn
joblib
pandas
scikit-learn
pydantic
python-multipart
```

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first.

---

## 📝 License

This project is open source under the [MIT License](LICENSE).
