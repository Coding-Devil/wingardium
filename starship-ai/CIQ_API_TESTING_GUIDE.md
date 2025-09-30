# CIQ API Testing Guide - Swagger UI Visualization

## 🚀 Quick Start

### 1. Start the Server
```bash
cd src
python -m ai.main --dev --port 8000 --config_file ../starship.yaml
```

### 2. Access Swagger UI
Open your browser and navigate to:
**http://localhost:8000/starship_ai/v1/docs**

---

## 📋 CIQ API Endpoints Overview

The CIQ Assistant provides **4 main endpoints** for CMM deployment configuration:

### **1. POST /ciq/payload** - Generate Schema
**Purpose**: Get all required parameters schema for CMM deployment

**Endpoint**: `/starship_ai/v1/ciq/payload`

**Request Body**:
```json
{
  "input": "Get CMM deployment parameters"
}
```

**Response**:
```json
{
  "properties": {
    "alms_ipv4_ip": {
      "type": "string",
      "x_displayName": "ALMS IPv4 IP Address",
      "x_order": 1
    },
    "mcc": {
      "type": "string",
      "x_displayName": "Mobile Country Code",
      "x_order": 2
    },
    ...
  },
  "response": "CIQ schema with 30 parameters returned successfully"
}
```

---

### **2. POST /ciq/chat** - Interactive Chat Session
**Purpose**: Start or continue a conversational parameter collection session

**Endpoint**: `/starship_ai/v1/ciq/chat`

#### **Start New Session**:
```json
{
  "input": "Hello, I need help with CMM configuration"
}
```

**Response**:
```json
{
  "response": "Welcome! I'll help you collect CMM deployment parameters. Let's start with ALMS settings. What is the ALMS IPv4 IP address?",
  "session_id": "abc123-def456-ghi789",
  "progress": {
    "total_params": 30,
    "collected_count": 0,
    "missing_count": 30,
    "progress_percentage": 0.0,
    "missing_params": ["alms_ipv4_ip", "mcc", ...]
  },
  "is_complete": false,
  "final_yaml": null
}
```

#### **Continue Session** (provide parameter value):
```json
{
  "input": "192.168.1.100",
  "session_id": "abc123-def456-ghi789"
}
```

**Response**:
```json
{
  "response": "Got it! ALMS IPv4: 192.168.1.100. Next, please provide the Mobile Country Code (MCC):",
  "session_id": "abc123-def456-ghi789",
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

---

### **3. GET /ciq/session/{session_id}/progress** - Check Progress
**Purpose**: Check the current progress of a parameter collection session

**Endpoint**: `/starship_ai/v1/ciq/session/{session_id}/progress`

**Path Parameter**: `session_id` (e.g., "abc123-def456-ghi789")

**Response**:
```json
{
  "total_params": 30,
  "collected_count": 15,
  "missing_count": 15,
  "progress_percentage": 50.0,
  "missing_params": [
    "nrf_endpoint_fqdn",
    "nssf_endpoint_port",
    ...
  ]
}
```

---

### **4. POST /ciq/session/{session_id}/yaml** - Generate Final YAML
**Purpose**: Generate the final deployment YAML from collected parameters

**Endpoint**: `/starship_ai/v1/ciq/session/{session_id}/yaml`

**Path Parameter**: `session_id` (e.g., "abc123-def456-ghi789")

**Response**:
```json
{
  "yaml_content": "global:\n  alms:\n    ipv4_ip: 192.168.1.100\n  provisioning:\n    mcc: 310\n...",
  "session_id": "abc123-def456-ghi789",
  "parameters_count": 30,
  "generated_at": 1234567890.123
}
```

---

## 🧪 Complete Testing Workflow in Swagger UI

### **Step 1: Get Parameters Schema** (Optional)
1. Expand **POST /ciq/payload**
2. Click **"Try it out"**
3. Enter request body:
   ```json
   {
     "input": "Show me all parameters"
   }
   ```
4. Click **"Execute"**
5. Review all 30+ required parameters

### **Step 2: Start Chat Session**
1. Expand **POST /ciq/chat**
2. Click **"Try it out"**
3. Enter request body:
   ```json
   {
     "input": "I need to configure CMM deployment"
   }
   ```
4. Click **"Execute"**
5. **IMPORTANT**: Copy the `session_id` from the response!

### **Step 3: Provide Parameters Conversationally**
For each subsequent interaction:
1. Use **POST /ciq/chat** again
2. Include the `session_id`
3. Provide parameter values or ask questions:
   ```json
   {
     "input": "192.168.1.100",
     "session_id": "YOUR_SESSION_ID"
   }
   ```
4. The agent will guide you to the next parameter

### **Step 4: Check Progress Anytime**
1. Expand **GET /ciq/session/{session_id}/progress**
2. Click **"Try it out"**
3. Enter your `session_id`
4. Click **"Execute"**
5. See completion percentage and remaining parameters

### **Step 5: Generate Final YAML**
Once `is_complete` is `true`:
1. Expand **POST /ciq/session/{session_id}/yaml**
2. Click **"Try it out"**
3. Enter your `session_id`
4. Click **"Execute"**
5. Get the complete deployment YAML

---

## 📊 Sample Complete Conversation Flow

```
User: "Hello, I need CMM configuration help"
Agent: "Welcome! Let's start. What's the ALMS IPv4 IP?"
Progress: 0/30 (0%)

User: "192.168.1.100"
Agent: "Got it! Now, what's the Mobile Country Code (MCC)?"
Progress: 1/30 (3.3%)

User: "310"
Agent: "Perfect! Next, the Mobile Network Code (MNC)?"
Progress: 2/30 (6.7%)

User: "Can you tell me what MNC is?"
Agent: "MNC is a 2-3 digit code that identifies your mobile network..."
Progress: 2/30 (6.7%) - no change, just Q&A

User: "260"
Agent: "Great! Now I need the primary DNN..."
Progress: 3/30 (10%)

... continue until 30/30 ...

Agent: "All parameters collected! Generating YAML..."
Progress: 30/30 (100%)
is_complete: true
final_yaml: <complete YAML content>
```

---

## 🎯 Testing Tips

### **What You Can Do in Swagger**:
- ✅ Test each endpoint independently
- ✅ See real-time request/response
- ✅ View all available parameters and schemas
- ✅ Test error scenarios (invalid session_id, incomplete sessions)
- ✅ Copy/paste curl commands for CLI testing

### **Conversational Features to Test**:
- Ask questions: "What is MCC?"
- Provide values: "192.168.1.100"
- Request clarification: "Can you explain this parameter?"
- Skip ahead: "I want to set the root password"
- Review progress: Check progress endpoint anytime

### **Error Scenarios to Test**:
- Invalid session_id (404 error)
- Generating YAML before completion (400 error)
- Expired sessions (404 error)
- Invalid parameter values

---

## 🔍 What to Look For in Swagger UI

When you open **http://localhost:8000/starship_ai/v1/docs**:

### **CIQ Assistant Section** (Green Box):
You'll see 4 endpoints grouped under "CIQ Assistant":
- `POST /ciq/payload` (green)
- `POST /ciq/chat` (green)
- `GET /ciq/session/{session_id}/progress` (blue)
- `POST /ciq/session/{session_id}/yaml` (green)

### **Each Endpoint Shows**:
- **Summary**: Brief description
- **Description**: Detailed explanation
- **Request Body**: Expected input format with examples
- **Responses**: All possible responses (200, 400, 404, 500)
- **Schemas**: Model definitions with field types

### **Interactive Features**:
- **Try it out**: Test directly in browser
- **Execute**: Send real requests to your server
- **curl**: Copy command for terminal testing
- **Clear**: Reset the form

---

## 📝 Expected Parameters List

The CIQ agent collects **30+ parameters** including:

**Network Configuration**:
- alms_ipv4_ip, alms_ipv4_gw, alms_ipv4_cidr
- primary_dns_ip
- mcc, mnc, network_name, network_short_name

**Service Endpoints**:
- nrf_endpoint_fqdn, nrf_endpoint_port
- nssf_endpoint_fqdn, nssf_endpoint_port

**DNN Configuration**:
- dnn1, dnn2, sd1, sd2, sd3

**Security (Passwords)**:
- root_passwd, cmm_passwd, cmmsecurity_passwd
- cgw_passwd, cbamuser_passwd, sam5620_passwd
- rsp_passwd, ca4mn_passwd, dcae_dfc_passwd
- diagnostic_passwd, trainee_passwd

**System Settings**:
- timezone, storageclass
- alms_type, alms_interface, alms_host_interface

---

## 🚦 Status Codes

- **200**: Success
- **400**: Bad Request (e.g., session not complete for YAML generation)
- **404**: Not Found (e.g., invalid session_id)
- **422**: Validation Error (e.g., missing required fields)
- **500**: Internal Server Error

---

## 🔧 Troubleshooting

### Server Not Starting?
```bash
# Make sure you're in the src directory
cd src

# Check if port 8000 is available
netstat -ano | findstr :8000

# Try a different port if needed
python -m ai.main --dev --port 8080 --config_file ../starship.yaml
```

### Can't Access Swagger?
- Verify URL: **http://localhost:8000/starship_ai/v1/docs**
- Check server logs for errors
- Ensure no firewall blocking

### Session Expired?
- Sessions have a timeout (default: 30 minutes)
- Start a new session with POST /ciq/chat

---

## 📚 Additional Resources

- **OpenAPI Schema**: http://localhost:8000/starship_ai/v1/openapi.json
- **ReDoc Alternative**: http://localhost:8000/starship_ai/v1/redoc
- **Health Check**: http://localhost:8000/starship_ai/v1/health

---

**Happy Testing! 🎉**

For issues or questions, check the server logs or review the `CIQ_INTEGRATION_README.md` file.
