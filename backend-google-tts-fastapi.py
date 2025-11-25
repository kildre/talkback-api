# Google Cloud Text-to-Speech FastAPI Endpoint
# Add this to your existing FastAPI app

from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from google.cloud import texttospeech
import os

# Initialize the Google Cloud TTS client
client = texttospeech.TextToSpeechClient()

class TTSRequest(BaseModel):
    text: str
    voice: str = "en-US-Neural2-D"
    speed: float = 0.9
    pitch: float = -2.0

# Add this to your FastAPI app
@app.post("/tts")
async def text_to_speech(request: TTSRequest):
    """
    Convert text to speech using Google Cloud TTS
    Returns MP3 audio
    """
    try:
        if not request.text:
            raise HTTPException(status_code=400, detail="Text is required")

        # Set up the synthesis request
        synthesis_input = texttospeech.SynthesisInput(text=request.text)
        
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name=request.voice
        )
        
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=request.speed,
            pitch=request.pitch,
            effects_profile_ids=["headphone-class-device"]
        )

        # Perform the text-to-speech request
        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )

        # Return the audio content
        return Response(
            content=response.audio_content,
            media_type="audio/mpeg"
        )

    except Exception as e:
        print(f"TTS error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Text-to-speech failed: {str(e)}"
        )

"""
SETUP INSTRUCTIONS:

1. Install Google Cloud TTS:
   pip install google-cloud-texttospeech

2. Create Google Cloud Project & Enable TTS:
   - Go to console.cloud.google.com
   - Create a new project (or use existing)
   - Enable "Cloud Text-to-Speech API"
   - Go to "APIs & Services" > "Credentials"
   - Create Service Account
   - Download JSON key file

3. Set up authentication:
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your-service-account-key.json"

4. Add to your requirements.txt:
   google-cloud-texttospeech

5. Best HAL-like Voices (FREE tier):
   - en-US-Neural2-D (deep male, recommended)
   - en-US-Wavenet-D (deep male alternative)
   - en-GB-Neural2-B (British male)
   - en-US-Neural2-J (male)

6. Test the endpoint:
   curl -X POST http://localhost:3000/tts \
     -H "Content-Type: application/json" \
     -d '{"text":"Hello, I am TalkTalk. How may I assist you today?"}' \
     --output test.mp3

FREE TIER (Forever):
✅ 1 million characters per month FREE
✅ WaveNet & Neural2 voices included
✅ No credit card required
✅ No expiration

Usage in your FastAPI app:
1. Copy the TTSRequest class and @app.post("/tts") function
2. Add 'from google.cloud import texttospeech' at the top
3. Make sure GOOGLE_APPLICATION_CREDENTIALS is set
4. Restart your FastAPI server
"""
