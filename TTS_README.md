# Text-to-Speech (TTS) Feature

✅ **Implementation Complete!**

Your FastAPI application now has Google Cloud Text-to-Speech functionality.

## 🎯 What's New

- **New endpoint**: `POST /tts` - Converts text to natural-sounding speech
- **Customizable voices**: 10+ neural voices (male/female)
- **Adjustable parameters**: Speed (0.25-4.0x) and pitch (-20 to +20)
- **High-quality audio**: Neural2 voices with MP3 output

## 📁 Files Added

```
app/tts/
├── __init__.py        # Module initialization
├── router.py          # TTS endpoint
└── schemas.py         # Request validation

TTS_SETUP.md           # Complete setup guide
test_tts.py            # Test script
```

## 🚀 Quick Start

### 1. Set up Google Cloud credentials

You need a Google Cloud service account with Text-to-Speech API enabled.

**Option A: Service Account Key (Easiest)**
```bash
# Download service account JSON key from Google Cloud Console
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your-key.json"
```

**Option B: Application Default Credentials**
```bash
gcloud auth application-default login
```

### 2. Test the endpoint

```bash
# Make sure server is running
uvicorn app.main:app --reload

# Test in another terminal
curl -X POST http://localhost:8000/tts/ \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, this is a test!"}' \
  -o test.mp3

# Play the audio
afplay test.mp3  # macOS
```

## 📝 API Usage

### Basic Request
```json
POST /tts/
{
  "text": "Hello, how are you today?"
}
```

### Full Request with Options
```json
POST /tts/
{
  "text": "This is a custom voice speaking slowly.",
  "voice": "en-US-Neural2-F",
  "speed": 0.8,
  "pitch": -2.0
}
```

### Response
- **Content-Type**: `audio/mpeg`
- **Body**: MP3 audio data

## 🎙️ Available Voices

| Voice | Gender | Description |
|-------|--------|-------------|
| en-US-Neural2-A | Male | Natural male voice |
| en-US-Neural2-C | Female | Warm female voice |
| en-US-Neural2-D | Male | Clear male voice (default) |
| en-US-Neural2-F | Female | Professional female voice |
| en-US-Neural2-I | Male | Young male voice |
| en-US-Neural2-J | Male | Mature male voice |

## ⚙️ Parameters

### Speed (speaking_rate)
- `0.25` - Very slow
- `0.5` - Slow
- `0.9` - Natural (default)
- `1.5` - Fast
- `2.0+` - Very fast

### Pitch
- `-20.0 to -5.0` - Deep voice
- `-2.0` - Slightly lower (default)
- `0.0` - Normal pitch
- `5.0 to 20.0` - High pitch

## 💡 Integration Examples

### Frontend (JavaScript)
```javascript
async function speakText(text) {
  const response = await fetch('http://localhost:8000/tts/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
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

### Chat + TTS
```javascript
// Get AI response
const chatResp = await fetch('http://localhost:8000/chat/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ message: "Tell me a joke" })
});
const { content } = await chatResp.json();

// Convert to speech
const ttsResp = await fetch('http://localhost:8000/tts/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ text: content })
});

const audioBlob = await ttsResp.blob();
const audio = new Audio(URL.createObjectURL(audioBlob));
audio.play();
```

### Python Client
```python
import requests

response = requests.post(
    "http://localhost:8000/tts/",
    json={
        "text": "Hello from Python!",
        "voice": "en-US-Neural2-D",
        "speed": 0.9,
        "pitch": -2.0
    }
)

with open("output.mp3", "wb") as f:
    f.write(response.content)
```

## 🧪 Testing

Run the test script:
```bash
python test_tts.py
```

This will:
- Create 4 test audio files with different voices/settings
- Test error handling
- Verify the API is working correctly

## 🔒 Security Notes

1. **Never commit service account keys** to git
2. Add `*.json` to `.gitignore`
3. Use environment variables for credentials
4. Rotate keys regularly
5. Restrict service account permissions

## 💰 Costs

Google Cloud TTS pricing (as of 2024):
- **Neural2 voices**: $16 per 1 million characters
- **Free tier**: 1 million characters/month
- Monitor usage in Google Cloud Console

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| "Could not load credentials" | Set `GOOGLE_APPLICATION_CREDENTIALS` |
| "API not enabled" | Enable Text-to-Speech API in GCP Console |
| "Permission denied" | Add "Cloud Text-to-Speech User" role |
| 503 Service Unavailable | Check Google Cloud credentials setup |

## 📚 Full Documentation

See **TTS_SETUP.md** for:
- Detailed setup instructions
- All available voices
- Advanced configuration
- Cost optimization
- Production deployment

## ✨ Next Steps

1. **Set up credentials** (see TTS_SETUP.md)
2. **Test the endpoint** with `curl` or `test_tts.py`
3. **Integrate with frontend** to make chat responses audible
4. **Customize voices** for different use cases
5. **Add voice selection UI** for user preferences

## 🎨 Use Cases

- ✅ Make chat responses audible
- ✅ Accessibility features
- ✅ Voice assistants
- ✅ Audio content generation
- ✅ Language learning apps
- ✅ Navigation/instructions

---

**Need help?** Check TTS_SETUP.md or test with: `python test_tts.py`
