# Tool Calling / Function Calling Guide

Your FastAPI chat application now supports **tool calling** (also known as function calling), allowing Claude to perform actions and retrieve information beyond just text generation.

## What is Tool Calling?

Tool calling enables Claude to:
- Execute functions to get real-time data
- Query databases
- Perform calculations
- Search through chat history
- Call external APIs

When a user asks a question, Claude decides whether to use tools to help answer it, executes them, sees the results, and incorporates that information into its response.

## Available Tools

### 1. `get_current_time`
Get the current date and time with timezone support.

**Use case**: "What time is it?", "What's today's date?", "What day of the week is it?"

### 2. `calculate`
Perform safe mathematical calculations.

**Use case**: "What's 15% of 200?", "Calculate 45 * 12 + 8"

### 3. `list_user_chats`
Retrieve user's chat conversation history.

**Use case**: "Show me my recent chats", "What conversations have I had?"

### 4. `search_chat_history`
Search through past conversations for specific keywords or topics.

**Use case**: "Did we discuss AWS before?", "Find our conversation about Python"

## Configuration

### Environment Variables

Add these to your `.env` file:

```bash
# Tool calling configuration
ENABLE_TOOLS=true  # Master switch (default: true)
ENABLED_TOOLS=  # Optional: comma-separated list of tools
```

### Global Control

**Enable all tools** (default):
```bash
ENABLE_TOOLS=true
```

**Disable all tools**:
```bash
ENABLE_TOOLS=false
```

**Enable specific tools only**:
```bash
ENABLE_TOOLS=true
ENABLED_TOOLS=get_current_time,calculate
```

### Per-Request Control

You can also disable tools for specific API requests:

```python
# Python example
response = requests.post(
    "http://localhost:8000/chat",
    json={
        "message": "What's 2 + 2?",
        "enable_tools": False  # Disable tools for this request
    }
)
```

```javascript
// JavaScript example
const response = await fetch('http://localhost:8000/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: "What's 2 + 2?",
    enable_tools: false  // Disable tools for this request
  })
});
```

## How It Works

1. **User sends message**: "What time is it in New York?"
2. **Claude analyzes**: Determines `get_current_time` tool would help
3. **Tool executes**: Gets current time with timezone
4. **Claude sees result**: Receives the time data
5. **Response generated**: "It's currently 3:45 PM EST in New York..."

## Tool Execution Flow

```
User Message
    ↓
Claude decides to use tool
    ↓
Tool executes safely
    ↓
Result returned to Claude
    ↓
Claude incorporates result
    ↓
Final response to user
```

## Safety Features

- **Allowlist approach**: Only explicitly defined tools can be called
- **Input validation**: All parameters are validated before execution
- **Error handling**: Tool failures don't crash the application
- **Logging**: All tool calls are logged for monitoring
- **Iteration limit**: Max 5 tool calling iterations to prevent loops
- **Sandboxing**: Calculations run in restricted environment

## Adding Custom Tools

To add your own tools, edit `app/chat/tools.py`:

```python
# 1. Add tool definition
TOOL_DEFINITIONS.append({
    "name": "your_tool_name",
    "description": "Clear description of what the tool does",
    "input_schema": {
        "type": "object",
        "properties": {
            "param1": {
                "type": "string",
                "description": "Description of parameter"
            }
        },
        "required": ["param1"]
    }
})

# 2. Add execution handler in ToolExecutor class
class ToolExecutor:
    def execute(self, tool_name: str, tool_input: dict) -> dict:
        # Add your tool routing
        if tool_name == "your_tool_name":
            return self._your_tool_handler(tool_input)
        # ... existing code
    
    def _your_tool_handler(self, tool_input: dict) -> dict:
        try:
            # Your tool logic here
            result = do_something(tool_input["param1"])
            return {
                "success": True,
                "result": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
```

## Example Interactions

### With Tools Enabled

**User**: "What's 15% of 250?"

**Claude**: *Uses calculate tool*
"15% of 250 is 37.5."

### Without Tools

**User**: "What's 15% of 250?"

**Claude**: *Uses knowledge base only*
"To calculate 15% of 250, multiply 250 by 0.15, which equals 37.5."

## Testing Tools

Test that tools are working:

```bash
# Test with curl
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What time is it?",
    "enable_tools": true
  }'
```

Check logs to see tool execution:
```
INFO: Executing tool: get_current_time with input: {}
```

## Troubleshooting

### Tools not being called?

1. Check `ENABLE_TOOLS=true` in .env
2. Verify `enable_tools: true` in request (if specified)
3. Check logs for tool execution attempts

### Tool execution errors?

- Review logs for specific error messages
- Verify database connectivity for DB-related tools
- Check tool input validation

### Want to disable temporarily?

```bash
# Quick disable without code changes
ENABLE_TOOLS=false uvicorn app.main:app --reload
```

## Performance Considerations

- **Latency**: Tool calling adds ~500ms-2s per tool execution
- **Iterations**: Multiple tools can be called in sequence
- **Caching**: Consider caching tool results where appropriate
- **Rate limiting**: Add rate limits for expensive operations

## Best Practices

1. **Clear descriptions**: Write detailed tool descriptions for Claude
2. **Validation**: Always validate tool inputs
3. **Error handling**: Return structured errors, don't throw
4. **Logging**: Log all tool executions for debugging
5. **Testing**: Test tools independently before integration
6. **Documentation**: Document custom tools for your team

## Migration from Non-Tool Version

Your existing chat functionality is preserved! If tools are disabled:
- Requests work exactly as before
- Knowledge Base retrieval unchanged
- Multimodal support still works
- No breaking changes

## Next Steps

- **Add custom tools** for your specific use case
- **Integrate APIs**: Weather, CRM, calendar, etc.
- **Database queries**: Let Claude query your data
- **Webhooks**: Trigger actions in external systems
- **Monitoring**: Set up alerts for tool failures
