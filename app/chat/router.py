"""Chat API endpoints."""

import logging
from typing import Annotated, Any

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
from app.chat.tools import ToolExecutor, get_enabled_tools
from app.config import settings
from app.db import get_db

logger = logging.getLogger(__name__)

# Constants
CHAT_NOT_FOUND_MSG = "Chat not found"
DEFAULT_MODEL_ARN = "us.anthropic.claude-sonnet-4-6"
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


async def handle_tool_calling(
    message: str, chat_service: ChatService, db: Session
) -> str:
    """
    Handle chat requests with tool calling support.

    Args:
        message: User's message
        chat_service: Chat service instance
        db: Database session

    Returns:
        AI response text
    """
    try:
        session = boto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_DEFAULT_REGION or "us-east-1",
        )
        bedrock_runtime = session.client("bedrock-runtime")
        tool_executor = ToolExecutor(db=db, user_id=DEMO_USER_ID)

        # Get enabled tools
        tools = get_enabled_tools()
        if not tools:
            # Fall back to non-tool mode
            bedrock_client = get_bedrock_client()
            return await handle_knowledge_base_query(message, bedrock_client)

        # Initial conversation with tools
        messages = [{"role": "user", "content": [{"text": message}]}]
        max_iterations = 5  # Prevent infinite loops
        iteration = 0

        while iteration < max_iterations:
            iteration += 1

            # Call Claude with tools
            response = bedrock_runtime.converse(
                modelId=DEFAULT_MODEL_ARN,
                messages=messages,
                toolConfig={"tools": tools},
                inferenceConfig={
                    "temperature": 0.7,
                    "maxTokens": 2048,
                },
            )

            # Add assistant response to conversation
            output = response.get("output", {})
            message_output = output.get("message", {})
            messages.append(message_output)

            # Check stop reason
            stop_reason = response.get("stopReason")

            if stop_reason == "tool_use":
                # Execute tools
                tool_results = []
                for content_block in message_output.get("content", []):
                    if "toolUse" in content_block:
                        tool_use = content_block["toolUse"]
                        tool_name = tool_use["name"]
                        tool_input = tool_use["input"]
                        tool_use_id = tool_use["toolUseId"]

                        logger.info(
                            "Executing tool: %s with input: %s", tool_name, tool_input
                        )

                        # Execute tool
                        result = tool_executor.execute(tool_name, tool_input)

                        # Format result for Claude
                        tool_results.append(
                            {
                                "toolResult": {
                                    "toolUseId": tool_use_id,
                                    "content": [{"json": result}],
                                }
                            }
                        )

                # Add tool results to conversation
                messages.append({"role": "user", "content": tool_results})

            elif stop_reason == "end_turn":
                # Claude is done, extract final response
                final_text = ""
                for content_block in message_output.get("content", []):
                    if "text" in content_block:
                        final_text += content_block["text"]
                return final_text or "I couldn't generate a response."

            else:
                # Other stop reasons (max_tokens, etc.)
                logger.warning("Unexpected stop reason: %s", stop_reason)
                final_text = ""
                for content_block in message_output.get("content", []):
                    if "text" in content_block:
                        final_text += content_block["text"]
                return final_text or "I reached my response limit."

        return "I've reached the maximum number of tool iterations."

    except (BotoCoreError, ClientError) as e:
        logger.error("Bedrock tool calling error: %s", e)
        return f"I encountered an error with tool calling: {str(e)}"
    except Exception as e:
        logger.error("Unexpected tool calling error: %s", e)
        return f"An unexpected error occurred: {str(e)}"


async def handle_knowledge_base_query(message: str, bedrock_client: Any) -> str:
    """
    Handle chat requests using Knowledge Base (no tools).

    Args:
        message: User's message
        bedrock_client: Bedrock client instance

    Returns:
        AI response text
    """
    try:
        # Enhanced prompt with agentic behavior
        enhanced_prompt = (
            "You are an intelligent AI agent with access to a knowledge base. "
            "Your role is to not just answer questions, but to guide users "
            "through multi-step processes and help them achieve their goals.\n\n"
            f"User's question: {message}\n\n"
            "Instructions for your response:\n"
            "- Provide detailed, factual information from the knowledge base\n"
            "- Format your response using markdown for better readability\n"
            "- Use **bold** for list numbers, headings, and key terms\n"
            "- Use proper heading levels (##, ###) for main sections\n"
            "- Use bullet points or numbered lists where appropriate\n\n"
            "AGENTIC BEHAVIORS:\n"
            "- After answering, ALWAYS suggest 2-3 relevant next steps or actions\n"
            "- If the question is ambiguous, ask clarifying questions\n"
            "- If you identify potential follow-up topics, mention them\n"
            "- If there's a multi-step process, break it down and offer to guide them\n"
            "- Proactively point out related considerations or potential issues\n"
            "- End with: 'What would you like to explore next?' or similar\n\n"
            "- If information is not in the knowledge base, clearly state that\n"
            "- Be conversational, helpful, and proactive in your guidance\n"
            "- Cite specific sources when available"
        )

        retrieve_and_generate_params = {"input": {"text": enhanced_prompt}}

        # Add knowledge base configuration if available
        if settings.AWS_BEDROCK_KNOWLEDGE_BASE_ID:
            model_arn = settings.AWS_BEDROCK_MODEL_ARN or (
                f"arn:aws:bedrock:{settings.AWS_DEFAULT_REGION or 'us-east-1'}"
                f"::foundation-model/{DEFAULT_MODEL_ARN}"
            )
            retrieve_and_generate_params["retrieveAndGenerateConfiguration"] = {
                "type": "KNOWLEDGE_BASE",
                "knowledgeBaseConfiguration": {
                    "knowledgeBaseId": settings.AWS_BEDROCK_KNOWLEDGE_BASE_ID,
                    "modelArn": model_arn,
                    "retrievalConfiguration": {
                        "vectorSearchConfiguration": {
                            "numberOfResults": 10,
                            "overrideSearchType": "HYBRID",
                        }
                    },
                    "generationConfiguration": {
                        "inferenceConfig": {
                            "textInferenceConfig": {
                                "temperature": 0.7,
                                "maxTokens": 2048,
                            }
                        },
                        "promptTemplate": {
                            "textPromptTemplate": (
                                "You are an intelligent AI agent with access "
                                "to a knowledge base. Your role is to guide users, "
                                "suggest next steps, and help them achieve their goals.\n\n"
                                "Context from knowledge base:\n"
                                "$search_results$\n\n"
                                "User's question: $query$\n\n"
                                "Provide a comprehensive response that:\n"
                                "1. Answers the question using context above\n"
                                "2. Uses markdown formatting: **bold** for list "
                                "numbers and headings; ## for sections\n"
                                "3. ALWAYS suggests 2-3 relevant next steps\n"
                                "4. Asks clarifying questions if needed\n"
                                "5. Identifies related topics worth exploring\n"
                                "6. For multi-step processes, offers to guide them\n"
                                "7. Ends with 'What would you like to explore next?'\n\n"
                                "If context lacks information, acknowledge this and "
                                "suggest alternative approaches. Be proactive and helpful."
                            )
                        },
                    },
                },
            }

        response = bedrock_client.retrieve_and_generate(**retrieve_and_generate_params)
        return response.get("output", {}).get("text", "I couldn't generate a response.")

    except (BotoCoreError, ClientError) as e:
        logger.error("Bedrock API error: %s", e)
        return (
            "I'm sorry, I'm experiencing technical difficulties "
            "with AWS Bedrock. Please check your AWS configuration. "
            f"Error details: {str(e)}"
        )
    except Exception as e:
        logger.error("Unexpected error calling Bedrock: %s", e)
        return f"I'm sorry, something went wrong while processing your request. Error: {str(e)}"


@router.post("/", response_model=MessageResponse)
async def chat(
    request: ChatRequest,
    chat_service: Annotated[ChatService, Depends(get_chat_service)],
    db: Annotated[Session, Depends(get_db)],
) -> MessageResponse:
    """
    Send a message to the chat and get AI response.

    This endpoint accepts a message/prompt with optional images and documents,
    and uses AWS Bedrock's retrieveAndGenerate or converse API methods
    to generate a response using a knowledge base with multimodal support.

    Supports:
    - Text messages
    - Image analysis (JPEG, PNG, GIF, WebP)
    - Document processing (PDF, CSV, DOC, DOCX, XLS, XLSX, HTML, TXT, MD)
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

            # Generate a meaningful title using AI
            title = chat_service.generate_chat_title(request.message)
            logger.info(f"Generated chat title: {title}")

            chat_data = ChatCreate(
                title=title,
                user_id=DEMO_USER_ID,  # In a real app, get from authentication
            )
            chat_response = chat_service.create_chat(chat_data)
            request.chat_id = chat_response.id
            logger.info(
                f"Created new chat with ID: {chat_response.id} and title: {title}"
            )

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
            # Check if multimodal content is present
            has_images = request.images and len(request.images) > 0
            has_documents = request.documents and len(request.documents) > 0

            # Use Converse API for multimodal content (images/documents)
            if has_images or has_documents:
                try:
                    # Build multimodal message content
                    message_content = []

                    # Add text content
                    message_content.append({"text": request.message})

                    # Add images
                    if has_images:
                        for img in request.images:
                            message_content.append(
                                {"image": {"format": img.format, "source": img.source}}
                            )

                    # Add documents
                    if has_documents:
                        for doc in request.documents:
                            message_content.append(
                                {
                                    "document": {
                                        "format": doc.format,
                                        "name": doc.name,
                                        "source": doc.source,
                                    }
                                }
                            )

                    # Create Bedrock Runtime client for Converse API
                    session = boto3.Session(
                        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                        region_name=settings.AWS_DEFAULT_REGION or "us-east-1",
                    )
                    bedrock_runtime = session.client("bedrock-runtime")

                    # Use Converse API with multimodal support
                    model_id = DEFAULT_MODEL_ARN

                    response = bedrock_runtime.converse(
                        modelId=model_id,
                        messages=[{"role": "user", "content": message_content}],
                        inferenceConfig={
                            "temperature": 0.7,
                            "maxTokens": 2048,
                        },
                    )

                    ai_response_text = (
                        response.get("output", {})
                        .get("message", {})
                        .get("content", [{}])[0]
                        .get("text", "I couldn't process the multimodal content.")
                    )

                except (BotoCoreError, ClientError) as e:
                    logger.error("Bedrock Converse API error: %s", e)
                    ai_response_text = (
                        "I'm sorry, I encountered an error processing "
                        f"the multimodal content. Error: {str(e)}"
                    )
                except Exception as e:
                    logger.error("Unexpected error with multimodal content: %s", e)
                    ai_response_text = (
                        "I'm sorry, something went wrong processing "
                        f"the content. Error: {str(e)}"
                    )
            else:
                # Use standard retrieveAndGenerate for text-only queries
                # Check if tools are enabled for this request
                tools_enabled = (
                    request.enable_tools
                    and settings.ENABLE_TOOLS
                    and get_enabled_tools()
                )

                # If tools enabled, try tool calling first with Converse API
                if tools_enabled:
                    ai_response_text = await handle_tool_calling(
                        request.message, chat_service, db
                    )
                else:
                    # Use Knowledge Base without tools
                    ai_response_text = await handle_knowledge_base_query(
                        request.message, bedrock_client
                    )
                # Enhanced prompt with agentic behavior
                enhanced_prompt = (
                    "You are an intelligent AI agent with access to a knowledge base. "
                    "Your role is to not just answer questions, but to guide users "
                    "through multi-step processes and help them achieve their goals.\n\n"
                    f"User's question: {request.message}\n\n"
                    "Instructions for your response:\n"
                    "- Provide detailed, factual information from the knowledge base\n"
                    "- Format your response using markdown for better readability\n"
                    "- Use **bold** for list numbers, headings, and key terms\n"
                    "- Use proper heading levels (##, ###) for main sections\n"
                    "- Use bullet points or numbered lists where appropriate\n\n"
                    "AGENTIC BEHAVIORS:\n"
                    "- After answering, ALWAYS suggest 2-3 relevant next steps or actions\n"
                    "- If the question is ambiguous, ask clarifying questions\n"
                    "- If you identify potential follow-up topics, mention them\n"
                    "- If there's a multi-step process, break it down and offer to guide them\n"
                    "- Proactively point out related considerations or potential issues\n"
                    "- End with: 'What would you like to explore next?' or similar\n\n"
                    "- If information is not in the knowledge base, clearly state that\n"
                    "- Be conversational, helpful, and proactive in your guidance\n"
                    "- Cite specific sources when available"
                )

                retrieve_and_generate_params = {"input": {"text": enhanced_prompt}}

                # Add knowledge base configuration if available
                if settings.AWS_BEDROCK_KNOWLEDGE_BASE_ID:
                    # Construct model ARN with proper format if needed
                    model_arn = settings.AWS_BEDROCK_MODEL_ARN or (
                        f"arn:aws:bedrock:{settings.AWS_DEFAULT_REGION or 'us-east-1'}"
                        f"::foundation-model/{DEFAULT_MODEL_ARN}"
                    )
                    retrieve_and_generate_params["retrieveAndGenerateConfiguration"] = {
                        "type": "KNOWLEDGE_BASE",
                        "knowledgeBaseConfiguration": {
                            "knowledgeBaseId": settings.AWS_BEDROCK_KNOWLEDGE_BASE_ID,
                            "modelArn": model_arn,
                            "retrievalConfiguration": {
                                "vectorSearchConfiguration": {
                                    "numberOfResults": 10,
                                    "overrideSearchType": "HYBRID",
                                }
                            },
                            "generationConfiguration": {
                                "inferenceConfig": {
                                    "textInferenceConfig": {
                                        "temperature": 0.7,
                                        "maxTokens": 2048,
                                    }
                                },
                                "promptTemplate": {
                                    "textPromptTemplate": (
                                        "You are an intelligent AI agent with access "
                                        "to a knowledge base. Your role is to guide users, "
                                        "suggest next steps, and help them achieve their goals.\n\n"
                                        "Context from knowledge base:\n"
                                        "$search_results$\n\n"
                                        "User's question: $query$\n\n"
                                        "Provide a comprehensive response that:\n"
                                        "1. Answers the question using context above\n"
                                        "2. Uses markdown formatting: **bold** for list "
                                        "numbers and headings; ## for sections\n"
                                        "3. ALWAYS suggests 2-3 relevant next steps\n"
                                        "4. Asks clarifying questions if needed\n"
                                        "5. Identifies related topics worth exploring\n"
                                        "6. For multi-step processes, offers to guide them\n"
                                        "7. Ends with 'What would you like to explore next?'\n\n"
                                        "If context lacks information, acknowledge this and "
                                        "suggest alternative approaches. Be proactive and helpful."
                                    )
                                },
                            },
                        },
                    }
                else:
                    # Fallback to external sources if no knowledge base is configured
                    retrieve_and_generate_params["retrieveAndGenerateConfiguration"] = {
                        "type": "EXTERNAL_SOURCES",
                        "externalSourcesConfiguration": {
                            "modelArn": settings.AWS_BEDROCK_MODEL_ARN
                            or DEFAULT_MODEL_ARN,
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
                        "I'm sorry, I'm experiencing technical difficulties "
                        "with AWS Bedrock. Please check your AWS configuration. "
                        f"Error details: {str(e)}"
                    )
                except Exception as e:
                    logger.error("Unexpected error calling Bedrock: %s", e)
                    ai_response_text = (
                        "I'm sorry, something went wrong while processing "
                        f"your request. Error: {str(e)}"
                    )

        # Store AI response
        ai_message = MessageCreate(
            chat_id=request.chat_id,
            role="assistant",
            content=ai_response_text,
        )
        ai_message_response = chat_service.create_message(ai_message)

        # Add voice settings to the response
        from app.chat.schemas import VoiceSettings

        response_dict = ai_message_response.model_dump()
        response_dict["voice_settings"] = VoiceSettings().model_dump()

        return MessageResponse(**response_dict)

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
