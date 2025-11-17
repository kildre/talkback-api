# AWS Bedrock Configuration Guide

## Current Status
The chat endpoint is currently running in **demo mode** without AWS Bedrock integration. It will provide helpful fallback responses.

## To Enable AWS Bedrock Integration

### 1. AWS Prerequisites
- Valid AWS account with Bedrock access
- Bedrock service enabled in your region
- Knowledge base created in AWS Bedrock (optional)
- Proper IAM permissions for Bedrock operations

### 2. Required Environment Variables
Update your `.env` file with:

```env
# Replace with your actual AWS credentials
AWS_ACCESS_KEY_ID=AKIA...your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_access_key
AWS_DEFAULT_REGION=us-east-1

# Optional: Knowledge Base Configuration
AWS_BEDROCK_KNOWLEDGE_BASE_ID=YOUR_KB_ID

# Optional: Custom Model ARN (defaults to Claude 3 Sonnet)
AWS_BEDROCK_MODEL_ARN=arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0
```

### 3. Model ARN Format
Correct format for model ARNs:
- Claude 3 Sonnet: `arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0`
- Claude 3 Haiku: `arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-haiku-20240307-v1:0`

### 4. IAM Permissions Required
Your AWS user/role needs these permissions:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:RetrieveAndGenerate",
                "bedrock:Retrieve",
                "bedrock:InvokeModel"
            ],
            "Resource": "*"
        }
    ]
}
```

### 5. Testing the Configuration
1. Update `.env` with real credentials
2. Restart the server
3. Test the `/chat/` endpoint
4. Check server logs for any AWS-specific errors

## Demo Mode Response
When AWS Bedrock is not configured, the API will respond with:
> "Hello! I received your message: '[your message]'. I'm currently running in demo mode without AWS Bedrock integration. To enable full AI capabilities, please configure your AWS credentials and Bedrock settings in the .env file."

## Troubleshooting
- **UnrecognizedClientException**: Invalid AWS credentials
- **AccessDeniedException**: Insufficient IAM permissions
- **ValidationException**: Invalid model ARN or knowledge base ID
- **ModelNotReadyException**: Model not available in your region