# CIQ Assistant Integration Guide

## 🎯 Overview

The CIQ (Customer Information Questionnaire) Assistant is now integrated into the Starship AI FastAPI application.

## 🏗️ Architecture

### Core Components

1. **CIQ Agent Core** (`ciq_core.py`) - Main orchestration logic
2. **Session Manager** (`session_manager.py`) - Handles chat sessions and state
3. **Configuration** (`config.py`) - Parameter definitions and settings
4. **CuDo Client** (`cudo_client.py`) - External knowledge base integration
5. **FastAPI Routes** (`ciq_assistant.py`) - REST API endpoints

### **✅ API Endpoints Ready**

- **`POST /ciq_chat`** - Interactive chat with session management
- **`POST /ciq_payload`** - Parameter schema for frontend tables
- **`GET /ciq_session/{id}/progress`** - Session progress tracking
- **`POST /ciq_session/{id}/yaml`** - Final YAML generation


## 📡 API Endpoints

python -m ai.main --dev --port 8000 --config_file ../starship.yaml

"""
The API is mounted under a prefix `/starship_ai/v1`. 

## **The URLs are:**

1. **Swagger UI (Interactive API docs)**: 
   - **http://localhost:8000/starship_ai/v1/docs**

2. **ReDoc (Alternative API docs)**:
   - **http://localhost:8000/starship_ai/v1/redoc**

3. **OpenAPI JSON Schema**:
   - **http://localhost:8000/starship_ai/v1/openapi.json**

## **CIQ API endpoints will be at:**

- **http://localhost:8000/starship_ai/v1/ciq/chat**
- **http://localhost:8000/starship_ai/v1/ciq/payload**
- **http://localhost:8000/starship_ai/v1/ciq/session/{session_id}/progress**
- **http://localhost:8000/starship_ai/v1/ciq/session/{session_id}/yaml**

**Try opening http://localhost:8000/starship_ai/v1/docs in your browser now!** 🚀

The 404 error might be because you were trying to access `/docs` directly, but the FastAPI app is configured to serve all routes under the `/starship_ai/v1` prefix.
"""

### 1. Chat Endpoint
**POST** `/ciq/chat`

Interactive chat for parameter collection with AI assistance.

```json
{
  "input": "Hello, I need help with CMM configuration",
  "session_id": "optional-existing-session-id"
}
```

**Response:**
```json
{
  "response": "Hi! I'm your CIQ Assistant...",
  "session_id": "uuid-session-id",
  "progress": {
    "total_params": 32,
    "collected_count": 0,
    "progress_percentage": 0.0,
    "missing_params": ["global.alms.ipv4_ip", "..."],
    "current_param": "global.alms.ipv4_ip",
    "is_complete": false
  },
  "is_complete": false,
  "final_yaml": null
}
```

### 2. Payload Schema Endpoint
**POST** `/ciq/payload`

Returns the complete parameter schema for frontend display.

```json
{
  "input": "get schema"
}
```

**Response:**
```json
{
  "properties": {
    "alms_ipv4_ip": {
      "type": "string",
      "x-displayName": "ALMS IPv4 IP address",
      "x-order": 1
    }
  },
  "response": "CIQ schema with 32 parameters returned successfully"
}
```

### 3. Session Progress Endpoint
**GET** `/ciq/session/{session_id}/progress`

Get current progress of a session.

### 4. YAML Generation Endpoint
**POST** `/ciq/session/{session_id}/yaml`

Generates final YAML from collected parameters.

## 🔄 Chat Flow

### 1. Session Initialization
- User sends first message
- System creates new session
- Returns welcome message and first parameter question

### 2. Parameter Collection
- System asks for each parameter sequentially
- User can:
  - Provide parameter values
  - Ask technical questions (routed to CuDo)
  - Skip parameters
  - Ask general questions

### 3. Intent Classification
The system automatically classifies user input:
- **param_answer**: Direct parameter value
- **tech_query**: Technical question about CMM/parameters
- **skip_done**: User wants to skip current parameter
- **general_silly**: Off-topic or general questions

### 4. Completion
- When all parameters collected, generates final YAML
- User can download configuration file

## 🎛️ Parameter Management

### Parameter Structure
All parameters follow dot notation:
```
global.alms.ipv4_ip
global.provisioning.mcc
global.secrets.users.root_passwd
global.containers.storageclass
```

### Parameter Descriptions
Comprehensive descriptions stored in `config.py`:
```python
PARAM_DESCRIPTIONS = {
    "global.alms.ipv4_ip": "ALMS IPv4 IP address",
    "global.provisioning.mcc": "Mobile Country Code for network identification",
    # ... 32 total parameters
}
```

## 🧪 Testing

Run the integration test:
```bash
cd starship-ai
python test_ciq_integration.py
```

Tests cover:
- ✅ Configuration loading
- ✅ Session management
- ✅ CIQ agent core functionality
- ✅ Payload generation
- ✅ API endpoints (mock)

### Parameter Table Display
Use the `/ciq/payload` endpoint to populate your parameter table:

```javascript
// Get all parameters for table
const response = await fetch('/ciq/payload', {
  method: 'POST',
  body: JSON.stringify({input: 'schema'})
});
const {properties} = await response.json();

// Display in table format
Object.entries(properties).forEach(([key, schema]) => {
  addTableRow(key, schema['x-displayName'], 'Pending...');
});
```

### Chat Interface
```javascript
// Send chat message
const chatResponse = await fetch('/ciq/chat', {
  method: 'POST',
  body: JSON.stringify({
    input: userMessage,
    session_id: currentSessionId
  })
});

const {response, session_id, progress, is_complete, final_yaml} = await chatResponse.json();

// Update UI
updateProgress(progress.progress_percentage);
displayMessage(response);
if (is_complete && final_yaml) {
  showDownloadButton(final_yaml);
}
```
The frontend team can now integrate these APIs to create a seamless user experience for CMM deployment configuration.
