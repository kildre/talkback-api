"""Test script for Text-to-Speech functionality."""

import requests

BASE_URL = "http://localhost:8000"


def test_tts():
    """Test TTS endpoint with various configurations."""

    print("=" * 60)
    print("Text-to-Speech Test")
    print("=" * 60)

    # Test 1: Basic TTS
    print("\n1. Testing basic TTS...")
    response = requests.post(
        f"{BASE_URL}/tts/",
        json={
            "text": "Hello! This is a test of the text to speech system.",
        },
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        with open("test_basic.mp3", "wb") as f:
            f.write(response.content)
        print("✓ Saved to test_basic.mp3")
    else:
        print(f"✗ Error: {response.text}")

    # Test 2: Custom voice
    print("\n2. Testing with female voice...")
    response = requests.post(
        f"{BASE_URL}/tts/",
        json={
            "text": "This is a different voice speaking.",
            "voice": "en-US-Neural2-F",
        },
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        with open("test_voice.mp3", "wb") as f:
            f.write(response.content)
        print("✓ Saved to test_voice.mp3")

    # Test 3: Slow, deep voice
    print("\n3. Testing slow, deep voice...")
    response = requests.post(
        f"{BASE_URL}/tts/",
        json={
            "text": "This is a slow and deep voice.",
            "voice": "en-US-Neural2-D",
            "speed": 0.7,
            "pitch": -5.0,
        },
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        with open("test_deep.mp3", "wb") as f:
            f.write(response.content)
        print("✓ Saved to test_deep.mp3")

    # Test 4: Fast, high voice
    print("\n4. Testing fast, high voice...")
    response = requests.post(
        f"{BASE_URL}/tts/",
        json={
            "text": "This is a fast and high pitched voice.",
            "voice": "en-US-Neural2-F",
            "speed": 1.3,
            "pitch": 5.0,
        },
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        with open("test_high.mp3", "wb") as f:
            f.write(response.content)
        print("✓ Saved to test_high.mp3")

    # Test 5: Empty text (should fail)
    print("\n5. Testing error handling (empty text)...")
    response = requests.post(
        f"{BASE_URL}/tts/",
        json={
            "text": "",
        },
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 400:
        print("✓ Correctly rejected empty text")
    else:
        print(f"✗ Unexpected response: {response.text}")

    print("\n" + "=" * 60)
    print("Tests completed!")
    print("=" * 60)
    print("\nTo play audio files:")
    print("  macOS:  afplay test_basic.mp3")
    print("  Linux:  mpg123 test_basic.mp3")
    print("  Windows: start test_basic.mp3")


if __name__ == "__main__":
    try:
        test_tts()
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API.")
        print("Make sure the server is running: uvicorn app.main:app --reload")
    except Exception as e:
        print(f"Error: {e}")
