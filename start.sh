#!/bin/bash
echo "🚀 Starting ResumeAI on Railway..."
python -m gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120 --workers 1