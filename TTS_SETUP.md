# Text-to-Speech Setup Guide

## Overview

Text-to-speech functionality has been added using Google Cloud Text-to-Speech API. This allows your chat application to convert text responses to natural-sounding audio.

## Prerequisites

### 1. Google Cloud Account
- Create a Google Cloud account at https://cloud.google.com/
- Enable the Text-to-Speech API in your project

### 2. Authentication
You need to set up Google Cloud credentials. Choose one option:

#### Option A: Service Account Key (Recommended for Development)
1. Go to Google Cloud Console → IAM & Admin → Service Accounts
2. Create a service account with "Cloud Text-to-Speech User" role
3. Create and download a JSON key file
4. Set environment variable:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your-service-account-key.json"
   ```

#### Option B: Application Default Credentials (Production)
1. Install gcloud CLI: https://cloud.google.com/sdk/docs/install
2. Run: `gcloud auth application-default login`

### 3. Add to .env (Optional)
```bash
# Google Cloud Text-to-Speech Configuration
GOOGLE_APPLICATION_CREDENTIALS="/path/to/your-service-account-key.json"
```

## Installation

Install the required package:
```bash
pip install google-cloud-texttospeech
```

Or reinstall all dependencies:
```bash
pip install -e .
```

## API Endpoint

### POST /tts

Convert text to speech audio.

**Request Body:**
```json
{
  "text": "Hello, this is a test of text to speech!",
  "voice": "en-US-Neural2-D",
  "speed": 0.9,
  "pitch": -2.0
}
```

**Parameters:**
- `text` (required): Text to convert to speech
- `voice` (optional): Voice name (default: "en-US-Neural2-D")
- `speed` (optional): Speaking rate 0.25-4.0 (default: 0.9)
- `pitch` (optional): Voice pitch -20.0 to 20.0 (default: -2.0)

**Response:**
- Content-Type: `audio/mpeg`
- Returns MP3 audio data

## Available Voices

### English (US) - Neural2 Voices
- `en-US-Neural2-A` - Male
- `en-US-Neural2-C` - Female
- `en-US-Neural2-D` - Male
- `en-US-Neural2-E` - Female
- `en-US-Neural2-F` - Female
- `en-US-Neural2-G` - Female
- `en-US-Neural2-H` - Female
- `en-US-Neural2-I` - Male
- `en-US-Neural2-J` - Male

### Other Languages
See full list: https://cloud.google.com/text-to-speech/docs/voices

## Usage Examples

### cURL
```bash
curl -X POST http://localhost:8000/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, this is a test!",
    "voice": "en-US-Neural2-D",
    "speed": 0.9,
    "pitch": -2.0
  }' \
  --output speech.mp3
```

### Python
```python
import requests

response = requests.post(
    "http://localhost:8000/tts",
    json={
        "text": "Hello, this is a test!",
        "voice": "en-US-Neural2-D",
        "speed": 0.9,
        "pitch": -2.0
    }
)

with open("speech.mp3", "wb") as f:
    f.write(response.content)
```

### JavaScript/Frontend
```javascript
async function textToSpeech(text) {
  const response = await fetch('http://localhost:8000/tts', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      text: text,
      voice: 'en-US-Neural2-D',
      speed: 0.9,
      pitch: -2.0
    })
  });

  const blob = await response.blob();
  const audio = new Audio(URL.createObjectURL(blob));
  audio.play();
}
```

## Integration with Chat

You can combine TTS with your chat endpoint to make responses audible:

```javascript
// Get chat response
const chatResponse = await fetch('http://localhost:8000/chat/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ message: "Tell me about AI" })
});

const data = await chatResponse.json();

// Convert response to speech
const ttsResponse = await fetch('http://localhost:8000/tts', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    text: data.content,
    voice: 'en-US-Neural2-D',
    speed: 0.9,
    pitch: -2.0
  })
});

const audioBlob = await ttsResponse.blob();
const audio = new Audio(URL.createObjectURL(audioBlob));
audio.play();
```

## Voice Customization

### Speed (Speaking Rate)
- `0.25` - Very slow
- `0.5` - Slow
- `1.0` - Normal
- `1.5` - Fast
- `2.0+` - Very fast

### Pitch
- Negative values: Lower pitch (deeper voice)
- `0.0`: Default pitch
- Positive values: Higher pitch

### Examples
```json
{
  "text": "This is a deep, slow voice",
  "voice": "en-US-Neural2-D",
  "speed": 0.7,
  "pitch": -5.0
}
```

```json
{
  "text": "This is a high, fast voice",
  "voice": "en-US-Neural2-F",
  "speed": 1.3,
  "pitch": 5.0
}
```

## Cost Considerations

Google Cloud Text-to-Speech pricing (as of 2024):
- Neural2 voices: $16 per 1 million characters
- Free tier: 1 million characters per month

Monitor your usage in Google Cloud Console.

## Troubleshooting

### "Could not load credentials"
- Ensure `GOOGLE_APPLICATION_CREDENTIALS` is set correctly
- Verify the service account key file exists and is valid

### "API not enabled"
- Enable Text-to-Speech API in Google Cloud Console
- Project → APIs & Services → Enable APIs and Services

### "Permission denied"
- Ensure service account has "Cloud Text-to-Speech User" role
- Check project billing is enabled

### "Invalid voice name"
- Use exact voice names from the official list
- Check language code matches voice name

## Testing

Test the endpoint:
```bash
# Simple test
curl -X POST http://localhost:8000/tts \
  -H "Content-Type: application/json" \
  -d '{"text": "Testing one two three"}' \
  -o test.mp3

# Play the audio (macOS)
afplay test.mp3

# Play the audio (Linux)
mpg123 test.mp3
```

## Security Notes

1. **Never commit service account keys** to version control
2. Add `*.json` to `.gitignore` for key files
3. Use environment variables for credentials
4. Rotate service account keys regularly
5. Restrict service account permissions to minimum required

## Next Steps

1. Install the package: `pip install google-cloud-texttospeech`
2. Set up Google Cloud credentials
3. Test the endpoint with cURL
4. Integrate with your frontend
5. Add voice selection UI in your chat interface
6. Consider caching audio for repeated phrases
