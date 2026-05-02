#!/bin/bash
set -e

echo "=== Starting Smart Agriculture AI ==="
echo "Working directory: $(pwd)"
echo "Files: $(ls)"

# Train model if not already trained
if [ ! -f "model/artifacts/crop_model.pkl" ]; then
    echo "=== Training ML model ==="
    python model/generate_data.py
    python model/train.py
else
    echo "=== Model already trained, skipping ==="
fi

echo "=== Starting Gunicorn ==="
exec gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120 --log-level info
