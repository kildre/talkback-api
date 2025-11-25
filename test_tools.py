"""Test script for tool calling functionality."""

import requests

# Base URL for your API
BASE_URL = "http://localhost:8000"


def test_tool_calling():
    """Test various tool calling scenarios."""

    print("=" * 60)
    print("Tool Calling Test Suite")
    print("=" * 60)

    # Test 1: Time tool
    print("\n1. Testing get_current_time tool...")
    response = requests.post(
        f"{BASE_URL}/chat",
        json={
            "message": "What time is it?",
            "enable_tools": True,
        },
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Response: {result['content'][:200]}...")

    # Test 2: Calculate tool
    print("\n2. Testing calculate tool...")
    response = requests.post(
        f"{BASE_URL}/chat",
        json={
            "message": "What's 15% of 250?",
            "enable_tools": True,
        },
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Response: {result['content'][:200]}...")

    # Test 3: Chat history
    print("\n3. Testing list_user_chats tool...")
    response = requests.post(
        f"{BASE_URL}/chat",
        json={
            "message": "Show me my recent conversations",
            "enable_tools": True,
        },
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Response: {result['content'][:200]}...")

    # Test 4: Without tools (Knowledge Base only)
    print("\n4. Testing WITHOUT tools (Knowledge Base only)...")
    response = requests.post(
        f"{BASE_URL}/chat",
        json={
            "message": "What's 2 + 2?",
            "enable_tools": False,
        },
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Response: {result['content'][:200]}...")

    # Test 5: Complex question requiring both KB and tools
    print("\n5. Testing complex query with KB + tools...")
    response = requests.post(
        f"{BASE_URL}/chat",
        json={
            "message": "Calculate 25 * 4 and then search my chat history for 'Python'",
            "enable_tools": True,
        },
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Response: {result['content'][:300]}...")

    print("\n" + "=" * 60)
    print("Tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_tool_calling()
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API.")
        print("Make sure the server is running: uvicorn app.main:app --reload")
    except Exception as e:
        print(f"Error: {e}")
