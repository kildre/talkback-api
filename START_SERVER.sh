#!/bin/bash
# Quick start script for TalkTalk API with TTS support

echo "=================================================="
echo "Starting TalkTalk API Server"
echo "=================================================="

# Set Google Cloud credentials
export GOOGLE_APPLICATION_CREDENTIALS="/Users/kberres/dev/ai-chat/talkback-api/text-to-speech.json"

echo "✅ Google Cloud credentials set"
echo "📂 Using: $GOOGLE_APPLICATION_CREDENTIALS"
echo ""
echo "🚀 Starting server on http://localhost:8000"
echo "📚 API docs: http://localhost:8000/docs"
echo "🔊 TTS endpoint: http://localhost:8000/tts/"
echo ""
echo "=================================================="

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
