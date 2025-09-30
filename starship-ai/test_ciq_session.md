# CIQ Chat Session Testing Guide

## Test a Complete CIQ Chat Session

### 1. Start New Session
```bash
curl -X POST "http://localhost:8000/starship_ai/v1/ciq_chat" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Hello, I need help with CMM configuration"
  }'
```

### 2. Continue Conversation (use session_id from step 1)
```bash
curl -X POST "http://localhost:8000/starship_ai/v1/ciq_chat" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "I want to configure ALMS settings",
    "session_id": "YOUR_SESSION_ID_HERE"
  }'
```

### 3. Provide Parameter Values
```bash
curl -X POST "http://localhost:8000/starship_ai/v1/ciq_chat" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "192.168.1.100",
    "session_id": "YOUR_SESSION_ID_HERE"
  }'
```

### 4. Check Session Progress
```bash
curl -X GET "http://localhost:8000/starship_ai/v1/ciq_session/YOUR_SESSION_ID_HERE/progress"
```

### 5. Generate Final YAML (when session is complete)
```bash
curl -X POST "http://localhost:8000/starship_ai/v1/ciq_session/YOUR_SESSION_ID_HERE/yaml"
```

## Sample Conversation Flow

1. **User**: "Hello, I need help with CMM configuration"
   - **Agent**: Welcomes and asks for first parameter

2. **User**: "I want to configure ALMS"
   - **Agent**: Asks for ALMS IPv4 IP address

3. **User**: "192.168.1.100"
   - **Agent**: Collects IP, asks for next parameter (e.g., MCC)

4. **User**: "310"
   - **Agent**: Collects MCC, asks for next parameter

5. Continue until all parameters are collected...

6. **Final**: Agent generates complete YAML configuration

## Expected Response Structure

Each chat response includes:
- `response`: The agent's message
- `session_id`: Session identifier
- `progress`: Object with collection progress
- `is_complete`: Boolean indicating if all parameters collected
- `final_yaml`: Generated YAML (when complete)

## Testing Tips

- Always include the `session_id` in follow-up messages
- Check `progress.progress_percentage` to see completion status
- When `is_complete` is true, the `final_yaml` will contain the generated configuration
- Use realistic values for parameters (IP addresses, MCCs, etc.)
