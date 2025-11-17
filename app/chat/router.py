"""Chat API endpoints."""

import logging
from typing import Annotated

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.chat.schemas import (
    ChatRequest,
    ChatResponse,
    ChatWithMessages,
    MessageResponse,
)
from app.chat.services import ChatService
from app.config import settings
from app.db import get_db

logger = logging.getLogger(__name__)

# Constants
CHAT_NOT_FOUND_MSG = "Chat not found"
DEFAULT_MODEL_ARN = "anthropic.claude-3-sonnet-20240229-v1:0"
DEMO_USER_ID = "demo-user"

router = APIRouter(
    prefix=f"{settings.API_PREFIX}/chat",
    tags=["Chat"],
)


def get_bedrock_client():
    """Get AWS Bedrock client with configuration from settings."""
    # Check if AWS credentials are properly configured
    if not settings.AWS_ACCESS_KEY_ID or settings.AWS_ACCESS_KEY_ID == "1234":
        logger.warning("AWS credentials not properly configured")
        return None

    try:
        session = boto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_DEFAULT_REGION or "us-east-1",
        )
        return session.client("bedrock-agent-runtime")
    except Exception as e:
        logger.error("Failed to create Bedrock client: %s", e)
        return None


def get_chat_service(db: Annotated[Session, Depends(get_db)]) -> ChatService:
    """Get chat service instance."""
    return ChatService(db)


@router.post("/", response_model=MessageResponse)
async def chat(
    request: ChatRequest,
    chat_service: Annotated[ChatService, Depends(get_chat_service)],
) -> MessageResponse:
    """
    Send a message to the chat and get AI response.

    This endpoint accepts a message/prompt and uses AWS Bedrock's retrieveAndGenerate
    method to generate a response using a knowledge base.
    """
    try:
        # Get or create chat
        if request.chat_id:
            # Validate chat exists (using a dummy user_id for now)
            # In a real app, you'd get this from authentication
            chat = chat_service.get_chat(request.chat_id, DEMO_USER_ID)
            if not chat:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=CHAT_NOT_FOUND_MSG,
                )
        else:
            # Create new chat
            from app.chat.schemas import ChatCreate

            # Create a title from the message (truncate if too long)
            title = (
                request.message[:50] + "..."
                if len(request.message) > 50
                else request.message
            )

            chat_data = ChatCreate(
                title=title,
                user_id=DEMO_USER_ID,  # In a real app, get from authentication
            )
            chat_response = chat_service.create_chat(chat_data)
            request.chat_id = chat_response.id

        # Store user message
        from app.chat.schemas import MessageCreate

        user_message = MessageCreate(
            chat_id=request.chat_id,
            role="user",
            content=request.message,
        )
        chat_service.create_message(user_message)

        # Call AWS Bedrock retrieveAndGenerate
        bedrock_client = get_bedrock_client()

        # Check if Bedrock is available
        if not bedrock_client:
            # Fallback response when AWS Bedrock is not configured
            ai_response_text = (
                f"Hello! I received your message: '{request.message}'. "
                "I'm currently running in demo mode without AWS Bedrock integration. "
                "To enable full AI capabilities, please configure your AWS credentials "
                "and Bedrock settings in the .env file."
            )
        else:
            retrieve_and_generate_params = {"input": {"text": request.message}}

            # Add knowledge base configuration if available
            if settings.AWS_BEDROCK_KNOWLEDGE_BASE_ID:
                retrieve_and_generate_params["retrieveAndGenerateConfiguration"] = {
                    "type": "KNOWLEDGE_BASE",
                    "knowledgeBaseConfiguration": {
                        "knowledgeBaseId": settings.AWS_BEDROCK_KNOWLEDGE_BASE_ID,
                        "modelArn": settings.AWS_BEDROCK_MODEL_ARN or DEFAULT_MODEL_ARN,
                    },
                }
            else:
                # Fallback to external sources if no knowledge base is configured
                retrieve_and_generate_params["retrieveAndGenerateConfiguration"] = {
                    "type": "EXTERNAL_SOURCES",
                    "externalSourcesConfiguration": {
                        "modelArn": settings.AWS_BEDROCK_MODEL_ARN or DEFAULT_MODEL_ARN,
                        "sources": [
                            {
                                "sourceType": "S3",
                                "s3Location": {
                                    # Configure as needed
                                    "uri": "s3://your-bucket/documents/"
                                },
                            }
                        ],
                    },
                }

            try:
                response = bedrock_client.retrieve_and_generate(
                    **retrieve_and_generate_params
                )
                ai_response_text = response.get("output", {}).get(
                    "text", "I'm sorry, I couldn't generate a response."
                )

            except (BotoCoreError, ClientError) as e:
                logger.error("Bedrock API error: %s", e)
                ai_response_text = (
                    "I'm sorry, I'm experiencing technical difficulties with AWS Bedrock. "
                    f"Please check your AWS configuration. Error details: {str(e)}"
                )
            except Exception as e:
                logger.error("Unexpected error calling Bedrock: %s", e)
                ai_response_text = (
                    "I'm sorry, something went wrong while processing your request. "
                    f"Error: {str(e)}"
                )

        # Store AI response
        ai_message = MessageCreate(
            chat_id=request.chat_id,
            role="assistant",
            content=ai_response_text,
        )
        ai_message_response = chat_service.create_message(ai_message)

        return ai_message_response

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Unexpected error in chat endpoint: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        ) from e


@router.get("/{chat_id}", response_model=ChatWithMessages)
async def get_chat_with_messages(
    chat_id: int,
    chat_service: Annotated[ChatService, Depends(get_chat_service)],
) -> ChatWithMessages:
    """Get a chat conversation with all its messages."""
    # In a real app, get user_id from authentication
    chat = chat_service.get_chat(chat_id, DEMO_USER_ID)
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=CHAT_NOT_FOUND_MSG,
        )

    messages = chat_service.get_chat_messages(chat_id)

    chat_response = ChatResponse.model_validate(chat)
    return ChatWithMessages(**chat_response.model_dump(), messages=messages)


@router.get("/", response_model=list[ChatResponse])
async def get_user_chats(
    chat_service: Annotated[ChatService, Depends(get_chat_service)],
) -> list[ChatResponse]:
    """Get all chats for the current user."""
    # In a real app, get user_id from authentication
    return chat_service.get_user_chats(DEMO_USER_ID)


@router.delete("/{chat_id}")
async def delete_chat(
    chat_id: int,
    chat_service: Annotated[ChatService, Depends(get_chat_service)],
) -> dict:
    """Delete a chat conversation and all its messages."""
    # In a real app, get user_id from authentication
    success = chat_service.delete_chat(chat_id, DEMO_USER_ID)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=CHAT_NOT_FOUND_MSG,
        )

    return {"message": "Chat deleted successfully"}
