"""Check all AWS regions for the Knowledge Base."""

import os

import boto3
from dotenv import load_dotenv

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
KB_ID = "VG9HJ9110M"

# Get all available regions
print("Getting all available AWS regions...")
ec2 = boto3.client(
    "ec2",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name="us-east-1",
)

all_regions = [region["RegionName"] for region in ec2.describe_regions()["Regions"]]

print(
    f"\nSearching for Knowledge Base {KB_ID} across ALL {len(all_regions)} AWS regions..."
)
print("=" * 60)

found = False
for region in sorted(all_regions):
    try:
        session = boto3.Session(
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=region,
        )
        client = session.client("bedrock-agent")

        # Try to get the specific KB
        response = client.get_knowledge_base(knowledgeBaseId=KB_ID)
        kb = response.get("knowledgeBase", {})
        print(f"\n✓✓✓ FOUND in {region} ✓✓✓")
        print(f"  Name: {kb.get('name', 'N/A')}")
        print(f"  Status: {kb.get('status', 'N/A')}")
        print(f"  Created: {kb.get('createdAt', 'N/A')}")
        print(f"  Description: {kb.get('description', 'N/A')}")
        found = True
        break
    except Exception as e:
        error_msg = str(e)
        if "ResourceNotFoundException" in error_msg:
            print(f"  {region}: Not found", end="\r")
        elif "AccessDeniedException" in error_msg:
            print(f"  {region}: Access denied (Bedrock not available)")
        elif "could not be found" in error_msg.lower():
            print(f"  {region}: Bedrock service not available")
        else:
            print(f"  {region}: Error - {error_msg[:50]}")
        continue

if not found:
    print("\n\n✗ Knowledge Base not found in any AWS region")
    print("\nThis could mean:")
    print("  1. The Knowledge Base is in a different AWS account")
    print("  2. The Knowledge Base has been deleted")
    print("  3. The credentials don't have permission to access it")
