import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
import joblib
import warnings
warnings.filterwarnings('ignore')

print("Loading data...")
df = pd.read_csv("malicious_phish.csv")

print(f"Dataset loaded: {len(df)} rows")

print("Extracting features...")
df['url_length']        = df['url'].apply(len)
df['num_dots']          = df['url'].apply(lambda x: x.count('.'))
df['num_hyphens']       = df['url'].apply(lambda x: x.count('-'))
df['num_slashes']       = df['url'].apply(lambda x: x.count('/'))
df['num_at_symbols']    = df['url'].apply(lambda x: x.count('@'))
df['num_question_marks']= df['url'].apply(lambda x: x.count('?'))
df['num_equals_signs']  = df['url'].apply(lambda x: x.count('='))
df['has_http']          = df['url'].apply(lambda x: 1 if 'http://' in x else 0)
df['has_https']         = df['url'].apply(lambda x: 1 if 'https://' in x else 0)
df['digit_count']       = df['url'].apply(lambda x: sum(c.isdigit() for c in x))

print("Encoding labels...")
le = LabelEncoder()
df['type'] = le.fit_transform(df['type'])
joblib.dump(le, "label_encoder.pkl")
print(f"Classes: {list(le.classes_)}")

# Drop unused columns
if 'type_encoded' in df.columns:
    df = df.drop(columns=['type_encoded'])
x = df.drop(["type", "url"], axis=1)
y = df["type"]

print("Splitting data...")
x_train, x_test, y_train, y_test = train_test_split(
    x, y, test_size=0.2, random_state=42
)

# -------------------------------------------------------
# Decision Tree — much smaller than Random Forest!
# max_depth=20 keeps file size small (~3-5 MB)
# while maintaining high accuracy (~95%)
# -------------------------------------------------------
print("Training Decision Tree model (small & fast)...")
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('dt_classifier', DecisionTreeClassifier(
        max_depth=20,
        min_samples_split=10,
        min_samples_leaf=5,
        random_state=42
    ))
])

pipeline.fit(x_train, y_train)

# Evaluate
print("\nEvaluating model...")
y_pred = pipeline.predict(x_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy * 100:.2f}%")
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=le.classes_))

print("\nSaving model...")
joblib.dump(pipeline, "model.pkl", compress=3)  # compress=3 reduces file size further

import os
size_mb = os.path.getsize("model.pkl") / (1024 * 1024)
print(f"Model saved! File size: {size_mb:.1f} MB")

if size_mb < 45:
    print(f"[OK] Model is {size_mb:.1f}MB - safe to upload to GitHub and Vercel!")
else:
    print(f"[WARNING] Model is {size_mb:.1f}MB - may need further optimization.")

print("[DONE] Training complete!")
