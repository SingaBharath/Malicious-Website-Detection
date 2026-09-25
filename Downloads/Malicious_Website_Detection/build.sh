#!/bin/bash
# Render build script - runs once during deployment

echo "=== Installing dependencies ==="
pip install -r requirements.txt

echo "=== Checking for dataset ==="
# Unzip dataset if CSV not present
if [ ! -f "malicious_phish.csv" ]; then
    if [ -f "malicious_phish.zip" ]; then
        echo "Unzipping dataset..."
        unzip malicious_phish.zip
    else
        echo "ERROR: Dataset not found! Please ensure malicious_phish.zip is in the repo."
        exit 1
    fi
fi

echo "=== Training ML model ==="
python train_model.py

echo "=== Build complete ==="
