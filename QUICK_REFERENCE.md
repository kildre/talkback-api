# Tool Calling Quick Reference

## 🚀 Quick Start

```bash
# 1. Tools are enabled by default
# 2. Test it:
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What time is it?"}'
```

## 🛠️ Available Tools

| Tool | Description | Example Query |
|------|-------------|---------------|
| `get_current_time` | Current date/time | "What time is it?" |
| `calculate` | Math operations | "What's 15% of 250?" |
| `list_user_chats` | Chat history | "Show my recent chats" |
| `search_chat_history` | Search messages | "Find mentions of Python" |

## ⚙️ Configuration

### Global Enable/Disable (.env)
```bash
ENABLE_TOOLS=true   # Enable tools
ENABLE_TOOLS=false  # Disable tools
```

### Selective Tools (.env)
```bash
ENABLED_TOOLS=get_current_time,calculate
```

### Per-Request Control (API)
```json
{
  "message": "What's 2+2?",
  "enable_tools": false
}
```

## 📝 Example Requests

### With Tools Enabled
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What time is it and what is 10 * 5?",
    "enable_tools": true
  }'
```

### Without Tools
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is 10 * 5?",
    "enable_tools": false
  }'
```

## 🔍 Verify Tool Usage

Check logs for:
```
INFO: Executing tool: <tool_name> with input: <parameters>
```

## 🚨 Troubleshooting

| Issue | Solution |
|-------|----------|
| Tools not called | Check `ENABLE_TOOLS=true` in .env |
| Tool errors | Check logs for error details |
| High latency | Reduce enabled tools or add caching |
| Wrong results | Verify tool input validation |

## 📚 Documentation

- **Full Guide**: `TOOL_CALLING.md`
- **Implementation**: `IMPLEMENTATION_SUMMARY.md`
- **Code**: `app/chat/tools.py`
- **Tests**: `test_tools.py`

## ➕ Add Custom Tool

```python
# In app/chat/tools.py

# 1. Add definition
TOOL_DEFINITIONS.append({
    "name": "your_tool",
    "description": "What it does",
    "input_schema": {
        "type": "object",
        "properties": {
            "param": {"type": "string"}
        },
        "required": ["param"]
    }
})

# 2. Add handler
def _your_tool(self, tool_input: dict) -> dict:
    try:
        result = process(tool_input["param"])
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

## 🎯 Use Cases

- ✅ Real-time data (time, weather, stocks)
- ✅ Calculations and conversions
- ✅ Database queries
- ✅ Search and retrieval
- ✅ API integrations
- ✅ Notifications
- ✅ File operations

## 🔒 Safety

- ✅ Only allowlisted tools
- ✅ Input validation
- ✅ Error isolation
- ✅ Audit logging
- ✅ Iteration limits
- ✅ Sandboxed execution

## 📊 Performance

- **Latency**: +0.5-2s per tool
- **Iterations**: Max 5 per request
- **Tokens**: Increased usage
- **Optimization**: Cache results
