import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib
import warnings
warnings.filterwarnings('ignore')

print("Loading data...")
df = pd.read_csv("malicious_phish.csv")

print("Extracting features...")
df['url_length'] = df['url'].apply(len)
df['num_dots'] = df['url'].apply(lambda x: x.count('.'))
df['num_hyphens'] = df['url'].apply(lambda x: x.count('-'))
df['num_slashes'] = df['url'].apply(lambda x: x.count('/'))
df['num_at_symbols'] = df['url'].apply(lambda x: x.count('@'))
df['num_question_marks'] = df['url'].apply(lambda x: x.count('?'))
df['num_equals_signs'] = df['url'].apply(lambda x: x.count('='))
df['has_http'] = df['url'].apply(lambda x: 1 if 'http://' in x else 0)
df['has_https'] = df['url'].apply(lambda x: 1 if 'https://' in x else 0)
df['digit_count'] = df['url'].apply(lambda x: sum(c.isdigit() for c in x))

print("Encoding labels...")
le = LabelEncoder()
df['type'] = le.fit_transform(df['type'])
joblib.dump(le, "label_encoder.pkl")

# In the notebook they dropped: ["type", "url", "type_encoded"]
if 'type_encoded' in df.columns:
    df = df.drop(columns=['type_encoded'])
x = df.drop(["type", "url"], axis=1)
y = df["type"]

print("Training model...")
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.4, random_state=42)

pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('rf_classifier', RandomForestClassifier(random_state=42, n_jobs=-1, n_estimators=50))
])

pipeline.fit(x_train, y_train)

print("Saving model...")
joblib.dump(pipeline, "model.pkl")
print("Model training complete and saved.")
