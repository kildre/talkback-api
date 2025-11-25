"""Find which region contains the Knowledge Base."""

import os

import boto3
from dotenv import load_dotenv

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
KB_ID = "VG9HJ9110M"

# Common Bedrock regions
REGIONS = [
    "us-east-1",
    "us-west-2",
    "us-east-2",
    "eu-west-1",
    "eu-central-1",
    "ap-southeast-1",
    "ap-northeast-1",
]

print(f"Searching for Knowledge Base {KB_ID} across regions...")
print("=" * 60)

for region in REGIONS:
    try:
        session = boto3.Session(
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=region,
        )
        client = session.client("bedrock-agent")
        response = client.get_knowledge_base(knowledgeBaseId=KB_ID)
        kb = response.get("knowledgeBase", {})
        print(f"\n✓ FOUND in {region}!")
        print(f"  Name: {kb.get('name', 'N/A')}")
        print(f"  Status: {kb.get('status', 'N/A')}")
        print(f"  Created: {kb.get('createdAt', 'N/A')}")
        break
    except Exception:
        print(f"  {region}: Not found")
        continue
else:
    print("\n✗ Knowledge Base not found in any tested region")
