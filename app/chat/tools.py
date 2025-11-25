"""Tool definitions and execution for Claude function calling."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.chat.services import ChatService
from app.config import settings

logger = logging.getLogger(__name__)

# Tool definitions in Claude's expected format
TOOL_DEFINITIONS = [
    {
        "name": "get_current_time",
        "description": (
            "Get the current date and time. Useful for time-sensitive queries, "
            "scheduling, or when users ask about 'today', 'now', etc."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "timezone": {
                    "type": "string",
                    "description": "Timezone (e.g., 'America/New_York'). Defaults to UTC.",
                }
            },
        },
    },
    {
        "name": "calculate",
        "description": (
            "Perform mathematical calculations. Supports basic arithmetic, "
            "percentages, and simple expressions. Use this when users ask for "
            "calculations, conversions, or math operations."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Mathematical expression to evaluate (e.g., '10 * 5 + 3')",
                }
            },
            "required": ["expression"],
        },
    },
    {
        "name": "list_user_chats",
        "description": (
            "Retrieve a list of the user's previous chat conversations. "
            "Useful when users ask about their history, past conversations, "
            "or want to reference previous discussions."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "number",
                    "description": "Maximum number of chats to return (default: 10)",
                }
            },
        },
    },
    {
        "name": "search_chat_history",
        "description": (
            "Search through the user's chat history for specific keywords or topics. "
            "Returns relevant messages from past conversations."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query to find in chat history",
                },
                "limit": {
                    "type": "number",
                    "description": "Maximum number of results (default: 5)",
                },
            },
            "required": ["query"],
        },
    },
]


class ToolExecutor:
    """Executes tool calls requested by Claude."""

    def __init__(self, db: Session | None = None, user_id: str | None = None):
        """Initialize tool executor."""
        self.db = db
        self.user_id = user_id or "demo-user"
        self.chat_service = ChatService(db) if db else None

    def execute(self, tool_name: str, tool_input: dict[str, Any]) -> dict[str, Any]:
        """
        Execute a tool and return its result.

        Args:
            tool_name: Name of the tool to execute
            tool_input: Input parameters for the tool

        Returns:
            Dict with 'success', 'result', and optional 'error' keys
        """
        try:
            # Route to appropriate tool handler
            if tool_name == "get_current_time":
                return self._get_current_time(tool_input)
            elif tool_name == "calculate":
                return self._calculate(tool_input)
            elif tool_name == "list_user_chats":
                return self._list_user_chats(tool_input)
            elif tool_name == "search_chat_history":
                return self._search_chat_history(tool_input)
            else:
                return {
                    "success": False,
                    "error": f"Unknown tool: {tool_name}",
                }
        except Exception as e:
            logger.error("Tool execution error for %s: %s", tool_name, e)
            return {
                "success": False,
                "error": f"Tool execution failed: {str(e)}",
            }

    def _get_current_time(self, tool_input: dict[str, Any]) -> dict[str, Any]:
        """Get current date and time."""
        try:
            now = datetime.now()
            timezone = tool_input.get("timezone", "UTC")

            return {
                "success": True,
                "result": {
                    "datetime": now.isoformat(),
                    "date": now.strftime("%Y-%m-%d"),
                    "time": now.strftime("%H:%M:%S"),
                    "day_of_week": now.strftime("%A"),
                    "timezone": timezone,
                    "timestamp": int(now.timestamp()),
                },
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _calculate(self, tool_input: dict[str, Any]) -> dict[str, Any]:
        """Perform safe mathematical calculation."""
        try:
            expression = tool_input.get("expression", "")

            # Security: Only allow safe math operations
            allowed_chars = set("0123456789+-*/()%. ")
            if not all(c in allowed_chars for c in expression):
                return {
                    "success": False,
                    "error": "Invalid characters in expression. Only numbers and basic operators allowed.",
                }

            # Evaluate safely
            result = eval(expression, {"__builtins__": {}}, {})

            return {
                "success": True,
                "result": {
                    "expression": expression,
                    "answer": result,
                },
            }
        except ZeroDivisionError:
            return {"success": False, "error": "Division by zero"}
        except Exception as e:
            return {"success": False, "error": f"Calculation error: {str(e)}"}

    def _list_user_chats(self, tool_input: dict[str, Any]) -> dict[str, Any]:
        """List user's chat history."""
        try:
            if not self.chat_service:
                return {"success": False, "error": "Database not available"}

            limit = tool_input.get("limit", 10)
            chats = self.chat_service.get_chats(self.user_id, limit=limit)

            chat_list = [
                {
                    "id": chat.id,
                    "title": chat.title,
                    "created_at": chat.created_at.isoformat(),
                    "updated_at": chat.updated_at.isoformat(),
                }
                for chat in chats
            ]

            return {
                "success": True,
                "result": {
                    "total_chats": len(chat_list),
                    "chats": chat_list,
                },
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _search_chat_history(self, tool_input: dict[str, Any]) -> dict[str, Any]:
        """Search through user's chat history."""
        try:
            if not self.chat_service:
                return {"success": False, "error": "Database not available"}

            query = tool_input.get("query", "")
            limit = tool_input.get("limit", 5)

            # Get all user chats
            chats = self.chat_service.get_chats(self.user_id, limit=50)

            # Search through messages
            results = []
            for chat in chats:
                chat_with_messages = self.chat_service.get_chat(chat.id, self.user_id)
                if chat_with_messages:
                    for message in chat_with_messages.messages:
                        if query.lower() in message.content.lower():
                            results.append(
                                {
                                    "chat_id": chat.id,
                                    "chat_title": chat.title,
                                    "message_id": message.id,
                                    "role": message.role,
                                    "content": message.content[:200]
                                    + ("..." if len(message.content) > 200 else ""),
                                    "created_at": message.created_at.isoformat(),
                                }
                            )
                            if len(results) >= limit:
                                break
                if len(results) >= limit:
                    break

            return {
                "success": True,
                "result": {
                    "query": query,
                    "total_results": len(results),
                    "results": results,
                },
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


def get_enabled_tools() -> list[dict[str, Any]]:
    """
    Get list of enabled tools based on configuration.

    Returns:
        List of tool definitions that are currently enabled
    """
    # Check if tools are globally enabled
    if not getattr(settings, "ENABLE_TOOLS", True):
        return []

    # Get list of specifically enabled tools
    enabled_tools_str = getattr(settings, "ENABLED_TOOLS", None)
    if enabled_tools_str:
        enabled_names = [name.strip() for name in enabled_tools_str.split(",")]
        return [tool for tool in TOOL_DEFINITIONS if tool["name"] in enabled_names]

    # Return all tools if no specific filter
    return TOOL_DEFINITIONS


def is_tools_enabled() -> bool:
    """Check if tools are enabled globally."""
    return getattr(settings, "ENABLE_TOOLS", True)
