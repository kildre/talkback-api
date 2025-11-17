#!/usr/bin/env python3
"""
Test script to verify AWS Bedrock credentials and access.
Run this script to check if your AWS setup is working correctly.
"""

import boto3
from botocore.exceptions import BotoCoreError, ClientError
import os
from dotenv import load_dotenv

def test_aws_credentials():
    """Test AWS credentials and Bedrock access."""
    
    # Load environment variables
    load_dotenv()
    
    access_key = os.getenv('AWS_ACCESS_KEY_ID')
    secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    region = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
    
    print("🔍 Testing AWS Bedrock Configuration...")
    print(f"Region: {region}")
    print(f"Access Key: {access_key[:10]}..." if access_key else "Access Key: Not set")
    print(f"Secret Key: {'Set' if secret_key else 'Not set'}")
    print()
    
    if not access_key or not secret_key:
        print("❌ ERROR: AWS credentials not found in .env file")
        return False
    
    if access_key.startswith('REPLACE_WITH_'):
        print("❌ ERROR: Please replace placeholder values in .env file with real credentials")
        return False
    
    try:
        # Test basic AWS connection
        session = boto3.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        
        # Test STS (to verify credentials work)
        sts_client = session.client('sts')
        identity = sts_client.get_caller_identity()
        print(f"✅ AWS Credentials Valid - Account: {identity.get('Account')}")
        print(f"   User ARN: {identity.get('Arn')}")
        print()
        
        # Test Bedrock client creation
        bedrock_client = session.client('bedrock-agent-runtime')
        print("✅ Bedrock client created successfully")
        
        # Test simple retrieve and generate call
        try:
            response = bedrock_client.retrieve_and_generate(
                input={'text': 'Hello, this is a test message'},
                retrieveAndGenerateConfiguration={
                    'type': 'EXTERNAL_SOURCES',
                    'externalSourcesConfiguration': {
                        'modelArn': 'arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0',
                        'sources': [{
                            'sourceType': 'S3',
                            's3Location': {'uri': 's3://example-bucket/'}
                        }]
                    }
                }
            )
            print("✅ Bedrock RetrieveAndGenerate API accessible")
            print(f"   Response received: {len(response.get('output', {}).get('text', ''))} characters")
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'AccessDeniedException':
                print("⚠️  WARNING: Bedrock access denied - check IAM permissions")
                print("   You may need to enable model access in Bedrock console")
            elif error_code == 'ValidationException':
                print("⚠️  INFO: API call validation failed (expected with test data)")
                print("   This means Bedrock is accessible but our test data is invalid")
            else:
                print(f"⚠️  WARNING: Bedrock API error: {error_code} - {e}")
        
        print()
        print("🎉 Configuration test completed!")
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'UnrecognizedClientException':
            print("❌ ERROR: Invalid AWS credentials")
        elif error_code == 'AccessDenied':
            print("❌ ERROR: Access denied - check IAM permissions")
        else:
            print(f"❌ ERROR: AWS API error: {error_code} - {e}")
        return False
        
    except Exception as e:
        print(f"❌ ERROR: Unexpected error: {e}")
        return False

if __name__ == "__main__":
    test_aws_credentials()