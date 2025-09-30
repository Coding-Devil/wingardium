# CIQ API Swagger UI Visualization

## 🌐 Access Point
**URL**: http://localhost:8000/starship_ai/v1/docs

---

## 📊 API Endpoints Summary

```
┌─────────────────────────────────────────────────────────────────┐
│                    CIQ ASSISTANT APIs                            │
│                    (4 Endpoints Total)                           │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ 1️⃣  POST /ciq/payload                                [Schema]    │
├─────────────────────────────────────────────────────────────────┤
│   Get all required CMM deployment parameters schema             │
│   Input: Simple text request                                    │
│   Output: 30+ parameter definitions with display names          │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ 2️⃣  POST /ciq/chat                                   [Chat]      │
├─────────────────────────────────────────────────────────────────┤
│   Interactive conversational parameter collection               │
│   Input: User message + optional session_id                     │
│   Output: AI response + progress + session state                │
│   Features:                                                      │
│     ✓ Stateful conversation                                     │
│     ✓ Parameter validation                                      │
│     ✓ Q&A support                                               │
│     ✓ Progress tracking                                         │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ 3️⃣  GET /ciq/session/{session_id}/progress          [Progress]  │
├─────────────────────────────────────────────────────────────────┤
│   Check current collection progress                             │
│   Input: session_id (path parameter)                            │
│   Output: Detailed progress metrics                             │
│     • Total parameters: 30                                      │
│     • Collected: X                                              │
│     • Missing: Y                                                │
│     • Percentage: Z%                                            │
│     • List of remaining parameters                              │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ 4️⃣  POST /ciq/session/{session_id}/yaml             [Generate]  │
├─────────────────────────────────────────────────────────────────┤
│   Generate final deployment YAML                                │
│   Input: session_id (path parameter)                            │
│   Output: Complete YAML configuration                           │
│   Requires: All 30 parameters collected (100% complete)         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Complete Workflow Visualization

```
START
  │
  ├─> [Optional] POST /ciq/payload
  │       └─> View all 30 required parameters
  │
  ├─> POST /ciq/chat (New Session)
  │       ├─> Input: "I need CMM configuration"
  │       └─> Output: session_id + first question
  │
  ├─> POST /ciq/chat (Continue)
  │       ├─> Input: Parameter value + session_id
  │       ├─> Output: Confirmation + next question
  │       └─> Repeat until 100% complete
  │               │
  │               ├─> Can check progress anytime:
  │               │   GET /ciq/session/{id}/progress
  │               │
  │               └─> Can ask questions:
  │                   "What is MCC?"
  │
  └─> POST /ciq/session/{id}/yaml
          ├─> Input: session_id
          └─> Output: Final YAML configuration
              
END (YAML Ready for Deployment)
```

---

## 📋 Request/Response Examples

### **1. Start New Session**
```json
REQUEST:  POST /ciq/chat
{
  "input": "Help me with CMM configuration"
}

RESPONSE: 200 OK
{
  "response": "Welcome! I'll guide you through collecting 30 CMM parameters. First, what's the ALMS IPv4 IP address?",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "progress": {
    "total_params": 30,
    "collected_count": 0,
    "missing_count": 30,
    "progress_percentage": 0.0
  },
  "is_complete": false,
  "final_yaml": null
}
```

### **2. Provide Parameter**
```json
REQUEST:  POST /ciq/chat
{
  "input": "192.168.1.100",
  "session_id": "550e8400-e29b-41d4-a716-446655440000"
}

RESPONSE: 200 OK
{
  "response": "Perfect! ALMS IPv4 IP: 192.168.1.100 ✓\n\nNext parameter (2/30): Mobile Country Code (MCC)\nPlease provide the 3-digit MCC:",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "progress": {
    "total_params": 30,
    "collected_count": 1,
    "missing_count": 29,
    "progress_percentage": 3.33
  },
  "is_complete": false,
  "final_yaml": null
}
```

### **3. Check Progress**
```json
REQUEST:  GET /ciq/session/550e8400-e29b-41d4-a716-446655440000/progress

RESPONSE: 200 OK
{
  "total_params": 30,
  "collected_count": 15,
  "missing_count": 15,
  "progress_percentage": 50.0,
  "missing_params": [
    "nrf_endpoint_fqdn",
    "nrf_endpoint_port",
    "nssf_endpoint_fqdn",
    ...
  ]
}
```

### **4. Generate YAML**
```json
REQUEST:  POST /ciq/session/550e8400-e29b-41d4-a716-446655440000/yaml

RESPONSE: 200 OK
{
  "yaml_content": "global:\n  alms:\n    ipv4_ip: 192.168.1.100\n    ipv4_gw: 192.168.1.1\n    ipv4_cidr: 24\n  provisioning:\n    mcc: 310\n    mnc: 260\n  ...",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "parameters_count": 30,
  "generated_at": 1704067200.123
}
```

---

## 🎨 What You'll See in Swagger UI

### **Header Section**
```
┌──────────────────────────────────────────────────────────┐
│  🚀 Starship AI API                          v1.0.0      │
│  Nokia Proprietary Internal Use Only                     │
├──────────────────────────────────────────────────────────┤
│  [Authorize] button - for authentication (if enabled)    │
└──────────────────────────────────────────────────────────┘
```

### **CIQ Assistant Group** (Expandable)
```
▼ CIQ Assistant
  AI CIQ Assistant APIs.
  
  ├─ POST   /starship_ai/v1/ciq/payload
  │  Generate CIQ payload schema
  │  [Try it out] [Parameters] [Request body] [Responses]
  │
  ├─ POST   /starship_ai/v1/ciq/chat
  │  CIQ chat endpoint
  │  [Try it out] [Parameters] [Request body] [Responses]
  │
  ├─ GET    /starship_ai/v1/ciq/session/{session_id}/progress
  │  Get CIQ session progress
  │  [Try it out] [Parameters] [Responses]
  │
  └─ POST   /starship_ai/v1/ciq/session/{session_id}/yaml
     Generate YAML for CIQ session
     [Try it out] [Parameters] [Responses]
```

### **Request Body Editor**
When you click "Try it out":
```
┌──────────────────────────────────────────────────────────┐
│ Request body                                             │
├──────────────────────────────────────────────────────────┤
│ {                                                        │
│   "input": "string",           ← Editable JSON          │
│   "session_id": "string"                                │
│ }                                                        │
├──────────────────────────────────────────────────────────┤
│ [Execute] [Clear]                                        │
└──────────────────────────────────────────────────────────┘
```

### **Response Viewer**
After clicking "Execute":
```
┌──────────────────────────────────────────────────────────┐
│ Server response                                          │
├──────────────────────────────────────────────────────────┤
│ Code: 200 ✓                                             │
│ Details: Successful Response                             │
├──────────────────────────────────────────────────────────┤
│ Response body                                            │
│ {                                                        │
│   "response": "Welcome! I'll help...",                  │
│   "session_id": "550e8400-...",                         │
│   "progress": { ... },                                  │
│   "is_complete": false                                  │
│ }                                                        │
├──────────────────────────────────────────────────────────┤
│ Response headers                                         │
│ content-type: application/json                          │
│ [Download] [Copy]                                        │
└──────────────────────────────────────────────────────────┘
```

---

## 🎯 Key Features to Test

### **Conversational AI**
- ✅ Natural language input
- ✅ Context-aware responses
- ✅ Parameter validation with feedback
- ✅ Question answering capability

### **Session Management**
- ✅ Persistent state across requests
- ✅ Progress tracking
- ✅ Session expiration handling
- ✅ Multiple concurrent sessions

### **Parameter Collection**
- ✅ 30+ parameters with metadata
- ✅ Guided collection workflow
- ✅ Validation rules
- ✅ Default values where applicable

### **YAML Generation**
- ✅ Dynamic YAML creation
- ✅ Proper structure and formatting
- ✅ All collected parameters integrated
- ✅ Ready for deployment

---

## 📊 Swagger UI Color Coding

- **🟢 POST** = Green (Create/Submit operations)
- **🔵 GET** = Blue (Read/Retrieve operations)
- **🟡 PUT** = Yellow (Update operations)
- **🔴 DELETE** = Red (Delete operations)

---

## 🔗 Quick Links

| Resource | URL |
|----------|-----|
| **Swagger UI** | http://localhost:8000/starship_ai/v1/docs |
| **ReDoc** | http://localhost:8000/starship_ai/v1/redoc |
| **OpenAPI JSON** | http://localhost:8000/starship_ai/v1/openapi.json |
| **Health Check** | http://localhost:8000/starship_ai/v1/health |

---

## 🚀 Getting Started Command

```bash
# Navigate to src directory
cd c:\Users\gokulnv\Documents\starship-ai\src

# Start the server
python -m ai.main --dev --port 8000 --config_file ../starship.yaml

# Open browser to:
http://localhost:8000/starship_ai/v1/docs
```

---

## 💡 Pro Tips

1. **Keep session_id handy**: Copy it immediately after starting a session
2. **Use progress endpoint**: Check status without interrupting the chat flow
3. **Test error cases**: Try generating YAML before completion to see error handling
4. **Explore schemas**: Click on model names to see detailed field definitions
5. **Copy curl commands**: Use the provided curl for scripting/automation

---

**Ready to test? Start the server and open Swagger UI!** 🎉
