#!/usr/bin/env python3
"""Quick test script for TTS endpoint."""

import os

import requests

# Test configuration
BASE_URL = "http://localhost:8000"
TTS_ENDPOINT = f"{BASE_URL}/tts/"


def test_tts():
    """Test the TTS endpoint with a simple request."""

    # Check if credentials are set
    creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not creds_path:
        print("❌ GOOGLE_APPLICATION_CREDENTIALS not set!")
        print(
            "Run: export GOOGLE_APPLICATION_CREDENTIALS='/Users/kberres/dev/ai-chat/talkback-api/text-to-speech.json'"
        )
        return False

    if not os.path.exists(creds_path):
        print(f"❌ Credentials file not found: {creds_path}")
        return False

    print(f"✅ Using credentials: {creds_path}")

    # Test data
    test_request = {
        "text": "Hello, I am TalkTalk. How may I assist you today?",
        "voice": "en-US-Neural2-D",
        "speed": 0.9,
        "pitch": -2.0,
    }

    print(f"\n🔊 Testing TTS endpoint: {TTS_ENDPOINT}")
    print(f"📝 Text: {test_request['text']}")
    print(f"🎤 Voice: {test_request['voice']}")

    try:
        response = requests.post(TTS_ENDPOINT, json=test_request, timeout=30)

        if response.status_code == 200:
            # Save the audio file
            output_file = "test_output.mp3"
            with open(output_file, "wb") as f:
                f.write(response.content)

            file_size = len(response.content)
            print(f"\n✅ Success! Audio generated ({file_size:,} bytes)")
            print(f"💾 Saved to: {output_file}")
            print(f"\n🎵 Play it with: afplay {output_file}")
            return True
        else:
            print(f"\n❌ Error {response.status_code}: {response.text}")
            return False

    except requests.exceptions.ConnectionError:
        print("\n❌ Connection refused! Is the server running?")
        print("Start server with: uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("TTS Endpoint Test")
    print("=" * 60)

    success = test_tts()

    print("\n" + "=" * 60)
    if success:
        print("✅ All tests passed!")
    else:
        print("❌ Tests failed")
    print("=" * 60)
