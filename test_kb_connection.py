"""Test script to diagnose AWS Bedrock Knowledge Base connection issues."""

import os

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get configuration
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_DEFAULT_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
AWS_BEDROCK_KNOWLEDGE_BASE_ID = os.getenv("AWS_BEDROCK_KNOWLEDGE_BASE_ID")
AWS_BEDROCK_MODEL_ARN = os.getenv("AWS_BEDROCK_MODEL_ARN")

print("=" * 60)
print("AWS Bedrock Knowledge Base Connection Test")
print("=" * 60)
print("\nConfiguration:")
print(f"  Region: {AWS_DEFAULT_REGION}")
print(f"  Knowledge Base ID: {AWS_BEDROCK_KNOWLEDGE_BASE_ID}")
print(f"  Model ARN: {AWS_BEDROCK_MODEL_ARN}")
print(
    f"  Access Key ID: {AWS_ACCESS_KEY_ID[:10]}..."
    if AWS_ACCESS_KEY_ID
    else "  Access Key ID: Not set"
)
print()

# Test 1: Check credentials
print("Test 1: Checking AWS credentials...")
try:
    session = boto3.Session(
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_DEFAULT_REGION,
    )
    sts_client = session.client("sts")
    identity = sts_client.get_caller_identity()
    print("✓ Credentials valid")
    print(f"  Account: {identity['Account']}")
    print(f"  User ARN: {identity['Arn']}")
except Exception as e:
    print(f"✗ Credentials check failed: {e}")
    exit(1)

# Test 2: List available Knowledge Bases
print("\nTest 2: Listing available Knowledge Bases...")
try:
    bedrock_agent_client = session.client("bedrock-agent")
    response = bedrock_agent_client.list_knowledge_bases()

    if response.get("knowledgeBaseSummaries"):
        print(f"✓ Found {len(response['knowledgeBaseSummaries'])} Knowledge Base(s):")
        for kb in response["knowledgeBaseSummaries"]:
            print(f"  - ID: {kb['knowledgeBaseId']}")
            print(f"    Name: {kb.get('name', 'N/A')}")
            print(f"    Status: {kb.get('status', 'N/A')}")
    else:
        print("✗ No Knowledge Bases found in this region")
        print("  Tip: Check if your Knowledge Base is in the correct region")
except ClientError as e:
    error_code = e.response.get("Error", {}).get("Code", "Unknown")
    if error_code == "AccessDeniedException":
        print("✗ Access denied - missing permissions")
        print("  Required permission: bedrock:ListKnowledgeBases")
    else:
        print(f"✗ Failed to list Knowledge Bases: {e}")
except Exception as e:
    print(f"✗ Unexpected error: {e}")

# Test 3: Try to retrieve Knowledge Base details
print(
    f"\nTest 3: Checking specific Knowledge Base ({AWS_BEDROCK_KNOWLEDGE_BASE_ID})..."
)
try:
    bedrock_agent_client = session.client("bedrock-agent")
    response = bedrock_agent_client.get_knowledge_base(
        knowledgeBaseId=AWS_BEDROCK_KNOWLEDGE_BASE_ID
    )
    kb = response.get("knowledgeBase", {})
    print("✓ Knowledge Base found!")
    print(f"  Name: {kb.get('name', 'N/A')}")
    print(f"  Status: {kb.get('status', 'N/A')}")
    print(f"  Created: {kb.get('createdAt', 'N/A')}")
except ClientError as e:
    error_code = e.response.get("Error", {}).get("Code", "Unknown")
    if error_code == "ResourceNotFoundException":
        print(f"✗ Knowledge Base not found in region {AWS_DEFAULT_REGION}")
        print("  Possible issues:")
        print("    1. Wrong region - check AWS console for correct region")
        print("    2. Knowledge Base ID is incorrect")
        print("    3. Knowledge Base was deleted")
    elif error_code == "AccessDeniedException":
        print("✗ Access denied - missing permissions")
        print("  Required permission: bedrock:GetKnowledgeBase")
    else:
        print(f"✗ Error: {e}")
except Exception as e:
    print(f"✗ Unexpected error: {e}")

# Test 4: Test retrieveAndGenerate
print("\nTest 4: Testing retrieveAndGenerate API...")
try:
    bedrock_runtime_client = session.client("bedrock-agent-runtime")
    response = bedrock_runtime_client.retrieve_and_generate(
        input={"text": "Hello, this is a test query."},
        retrieveAndGenerateConfiguration={
            "type": "KNOWLEDGE_BASE",
            "knowledgeBaseConfiguration": {
                "knowledgeBaseId": AWS_BEDROCK_KNOWLEDGE_BASE_ID,
                "modelArn": AWS_BEDROCK_MODEL_ARN,
            },
        },
    )
    print("✓ retrieveAndGenerate API call successful!")
    output_text = response.get("output", {}).get("text", "")
    print(f"  Response preview: {output_text[:100]}...")
except ClientError as e:
    error_code = e.response.get("Error", {}).get("Code", "Unknown")
    if error_code == "ResourceNotFoundException":
        print("✗ Knowledge Base not found")
        print(f"  Error: {e}")
    elif error_code == "AccessDeniedException":
        print("✗ Access denied - missing permissions")
        print("  Required permissions:")
        print("    - bedrock:InvokeModel")
        print("    - bedrock:RetrieveAndGenerate")
    elif error_code == "ValidationException":
        print("✗ Validation error (check model ARN format)")
        print(f"  Error: {e}")
    else:
        print(f"✗ Error: {e}")
except Exception as e:
    print(f"✗ Unexpected error: {e}")

print("\n" + "=" * 60)
print("Diagnosis complete")
print("=" * 60)
