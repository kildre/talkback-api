# TalkTalk API - Setup Complete! 🎉

## ✅ What's Been Set Up

### 1. Google Cloud Text-to-Speech
- ✅ Package installed: `google-cloud-texttospeech`
- ✅ Service keys in place:
  - `talktalk-servicekey.json`
  - `text-to-speech.json`
- ✅ Environment configured in `.env`
- ✅ TTS endpoint integrated at `/tts/`

### 2. Tool Calling / Function Calling
- ✅ 4 built-in tools available:
  - `get_current_time` - Get current date/time
  - `calculate` - Perform calculations
  - `list_user_chats` - List user's chat history
  - `search_chat_history` - Search past conversations
- ✅ Configuration in `.env` (can enable/disable globally)
- ✅ Per-request control in chat API

---

## 🚀 Quick Start

### Start the Server

**Option 1: Using the start script (recommended)**
```bash
./START_SERVER.sh
```

**Option 2: Manual start**
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/Users/kberres/dev/ai-chat/talkback-api/text-to-speech.json"
uvicorn app.main:app --reload
```

### Server URLs
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **TTS Endpoint**: http://localhost:8000/tts/

---

## 🧪 Test Everything

### Test TTS Endpoint
```bash
# Quick test script (checks credentials, makes request, saves audio)
python test_tts_quick.py

# Or manual curl test
curl -X POST http://localhost:8000/tts/ \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello, I am TalkTalk. How may I assist you today?"}' \
  --output test.mp3

# Play the audio (macOS)
afplay test.mp3
```

### Test Tool Calling
```bash
python test_tools.py
```

---

## 📋 Configuration Files

### `.env` - Environment Variables
```bash
# Google Cloud TTS
GOOGLE_APPLICATION_CREDENTIALS="/Users/kberres/dev/ai-chat/talkback-api/text-to-speech.json"

# Tool Calling
ENABLE_TOOLS=true
# ENABLED_TOOLS=get_current_time,calculate  # Optional: limit which tools
```

### Service Keys Location
```
/Users/kberres/dev/ai-chat/talkback-api/
├── talktalk-servicekey.json      # General service account
└── text-to-speech.json           # TTS-specific key (currently in use)
```

---

## 🎙️ TTS Voices Available

### Best HAL-like Voices (all FREE tier)
| Voice Name | Description | Use Case |
|------------|-------------|----------|
| `en-US-Neural2-D` | Deep male (default) | HAL 9000 style |
| `en-US-Wavenet-D` | Deep male alternative | Classic robot |
| `en-GB-Neural2-B` | British male | Sophisticated AI |
| `en-US-Neural2-J` | Male voice | Professional |

### TTS Request Format
```json
{
  "text": "Hello, how can I help you?",
  "voice": "en-US-Neural2-D",
  "speed": 0.9,
  "pitch": -2.0
}
```

---

## 🔧 API Endpoints

### Chat with Tool Calling
```bash
POST /chat/
{
  "message": "What time is it?",
  "enable_tools": true  # Optional, defaults to true
}
```

### Text-to-Speech
```bash
POST /tts/
{
  "text": "Hello world",
  "voice": "en-US-Neural2-D",
  "speed": 0.9,
  "pitch": -2.0
}
```

---

## 📁 Project Structure

```
talkback-api/
├── app/
│   ├── main.py                    # App entry point
│   ├── chat/
│   │   ├── router.py             # Chat endpoint with tool calling
│   │   └── tools.py              # Tool definitions & execution
│   └── tts/
│       ├── router.py             # TTS endpoint
│       └── schemas.py            # TTS request/response schemas
├── .env                          # Environment configuration
├── text-to-speech.json           # Google Cloud TTS credentials
├── talktalk-servicekey.json      # Alternative service key
├── START_SERVER.sh               # Server start script
├── test_tts_quick.py             # TTS test script
└── test_tools.py                 # Tool calling test script
```

---

## 💡 Usage Examples

### Frontend Integration - TTS

```javascript
// Convert text to speech
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
  
  const audioBlob = await response.blob();
  const audioUrl = URL.createObjectURL(audioBlob);
  const audio = new Audio(audioUrl);
  audio.play();
}
```

### Frontend Integration - Chat with Tools

```javascript
// Send chat message with tools enabled
async function sendMessage(message) {
  const response = await fetch('http://localhost:8000/chat/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message: message,
      enable_tools: true  // Enable tool calling
    })
  });
  
  const data = await response.json();
  return data.response;
}
```

---

## 🎯 Next Steps

1. **Start the server**: `./START_SERVER.sh`
2. **Test TTS**: `python test_tts_quick.py`
3. **Test Tools**: `python test_tools.py`
4. **Try the API docs**: http://localhost:8000/docs
5. **Integrate with frontend**: Use examples above

---

## 📚 Documentation Files

- `TOOL_CALLING.md` - Complete tool calling documentation
- `TTS_SETUP.md` - Detailed TTS setup guide
- `TTS_README.md` - Quick TTS reference
- `IMPLEMENTATION_SUMMARY.md` - Technical implementation details
- `QUICK_REFERENCE.md` - Quick reference for all features

---

## 🆓 Cost Information

### Google Cloud TTS - Free Tier
- ✅ **1 million characters/month FREE** (forever)
- ✅ Includes Neural2 and WaveNet voices
- ✅ No credit card required to start
- ✅ No expiration

### Typical Usage
- Average response: ~100 characters
- Free tier = ~10,000 responses/month
- After free tier: $4 per 1M characters (Neural2)

---

## 🔒 Security Notes

1. **Service keys** (`*.json`) are in `.gitignore` - never commit them!
2. **AWS credentials** in `.env` - keep secure
3. **CORS** is configured for `localhost:5173` only
4. **Tool calling** can be disabled per-request or globally

---

## ❓ Troubleshooting

### TTS not working?
```bash
# Check credentials are set
echo $GOOGLE_APPLICATION_CREDENTIALS

# Should output: /Users/kberres/dev/ai-chat/talkback-api/text-to-speech.json

# If not, run:
export GOOGLE_APPLICATION_CREDENTIALS="/Users/kberres/dev/ai-chat/talkback-api/text-to-speech.json"
```

### Server won't start?
```bash
# Check if port 8000 is in use
lsof -i :8000

# Install dependencies
pip install -e .
```

### Tools not working?
Check `.env`:
```bash
ENABLE_TOOLS=true
```

---

## 🎉 You're All Set!

Both features are ready to use:
- 🔊 **Text-to-Speech** with HAL-like voices
- 🛠️ **Function Calling** with 4 built-in tools

Run `./START_SERVER.sh` to begin! 🚀
