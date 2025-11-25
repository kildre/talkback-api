#!/bin/bash

# TalkBack API Startup Script

echo "Starting TalkBack API..."

# Check if virtual environment exists
if [ ! -d "venv" ] && [ ! -d ".venv" ]; then
    echo "No virtual environment found. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
    echo "Installing dependencies..."
    pip install -e .
    pip install -e ".[dev]"
else
    # Activate virtual environment
    if [ -d "venv" ]; then
        source venv/bin/activate
    else
        source .venv/bin/activate
    fi
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "WARNING: .env file not found. Please create one with your AWS credentials."
    exit 1
fi

# Set Google Cloud credentials for Text-to-Speech
export GOOGLE_APPLICATION_CREDENTIALS="/Users/kberres/dev/ai-chat/talkback-api/text-to-speech.json"
echo "Google Cloud credentials set: $GOOGLE_APPLICATION_CREDENTIALS"

# Start the FastAPI server with uvicorn
echo "Starting uvicorn server on http://localhost:8000"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
