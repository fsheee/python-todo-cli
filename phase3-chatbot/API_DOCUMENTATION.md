# Phase 3 Chatbot - API Documentation

## 🎯 Overview

RESTful API documentation for the Phase 3 AI-powered chatbot backend.

**Base URL (Development):** `http://localhost:8001`
**Base URL (Production):** `https://api.your-domain.com`

**Authentication:** JWT Bearer Token (from Phase 2 Better Auth)

---

## 📋 Table of Contents

1. [Authentication](#authentication)
2. [Endpoints](#endpoints)
3. [Data Models](#data-models)
4. [Error Handling](#error-handling)
5. [Rate Limiting](#rate-limiting)
6. [Examples](#examples)

---

## 🔐 Authentication

All endpoints (except `/` and `/health`) require JWT authentication.

### How to Authenticate

1. **Login via Phase 2:**
   ```http
   POST https://phase2-api.com/auth/login
   Content-Type: application/json

   {
     "email": "user@example.com",
     "password": "password123"
   }
   ```

   **Response:**
   ```json
   {
     "access_token": "eyJhbGciOiJIUzI1NiIs...",
     "user": {
       "id": 123,
       "email": "user@example.com"
     }
   }
   ```

2. **Use Token in Requests:**
   ```http
   Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
   ```

### Token Expiration

- **Duration:** 24 hours
- **Renewal:** Obtain new token via Phase 2 login
- **Invalid Token Response:** `401 Unauthorized`

---

## 📡 Endpoints

### 1. Root Information

**GET /**

Returns API information.

**Authentication:** None

**Response:**
```json
{
  "name": "Phase 3 Chatbot API",
  "version": "1.0.0",
  "status": "operational"
}
```

---

### 2. Health Check

**GET /health**

Check API health status.

**Authentication:** None

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-12-25T10:30:00Z"
}
```

---

### 3. Chat Endpoint

**POST /chat**

Send a message to the AI chatbot and receive a response.

**Authentication:** Required (JWT Bearer Token)

**Request Body:**
```json
{
  "message": "string (required, 1-1000 characters)",
  "session_id": "string (required, format: sess_xxxxx)"
}
```

**Request Example:**
```json
{
  "message": "Show me my tasks due today",
  "session_id": "sess_1234567890_abc"
}
```

**Response 200 OK:**
```json
{
  "response": "You have 2 tasks due today:\n\n1. 📝 Buy groceries\n2. 📞 Call dentist\n\nWould you like details on either of these?",
  "session_id": "sess_1234567890_abc",
  "timestamp": "2025-12-25T10:30:05Z"
}
```

**Response Fields:**
- `response` (string): AI-generated response text
- `session_id` (string): Same session ID from request
- `timestamp` (string): ISO 8601 timestamp of response

---

### 4. Chat History

**GET /chat/history/{session_id}**

Retrieve chat history for a specific session.

**Authentication:** Required

**Parameters:**
- `session_id` (path): Session identifier
- `limit` (query, optional): Max messages to return (default: 20, max: 100)

**Response 200 OK:**
```json
{
  "session_id": "sess_1234567890_abc",
  "messages": [
    {
      "role": "user",
      "content": "Show my tasks",
      "timestamp": "2025-12-25T10:30:00Z"
    },
    {
      "role": "assistant",
      "content": "You have 3 pending tasks...",
      "timestamp": "2025-12-25T10:30:01Z"
    }
  ],
  "total": 2
}
```

---

### 5. User Sessions

**GET /chat/sessions**

List all chat sessions for the authenticated user.

**Authentication:** Required

**Parameters:**
- `limit` (query, optional): Max sessions to return (default: 50)

**Response 200 OK:**
```json
{
  "sessions": [
    {
      "session_id": "sess_1234567890_abc",
      "started_at": "2025-12-25T09:00:00Z",
      "last_message_at": "2025-12-25T10:30:00Z",
      "message_count": 10
    }
  ],
  "total": 1
}
```

---

### 6. Delete Session

**DELETE /chat/sessions/{session_id}**

Soft delete a chat session (marks messages as deleted).

**Authentication:** Required

**Parameters:**
- `session_id` (path): Session to delete

**Response 200 OK:**
```json
{
  "message": "Session deleted successfully",
  "deleted_count": 10
}
```

---

## 📦 Data Models

### ChatRequest

```typescript
interface ChatRequest {
  message: string;      // User message (required)
  session_id: string;   // Session identifier (required)
}
```

**Validation:**
- `message`: 1-1000 characters, non-empty
- `session_id`: Must match pattern `sess_[0-9]+_[a-z0-9]+`

---

### ChatResponse

```typescript
interface ChatResponse {
  response: string;     // AI-generated response
  session_id: string;   // Session identifier
  timestamp: string;    // ISO 8601 timestamp
}
```

---

### ChatMessage

```typescript
interface ChatMessage {
  id?: number;           // Message ID
  user_id: number;       // User who sent/received message
  session_id: string;    // Session identifier
  role: "user" | "assistant" | "system";
  content: string;       // Message text
  metadata?: object;     // Optional metadata
  timestamp: string;     // ISO 8601 timestamp
  is_deleted: boolean;   // Soft delete flag
}
```

---

### ErrorResponse

```typescript
interface ErrorResponse {
  error: string;         // Human-readable error message
  code: string;          // Error code (e.g., "UNAUTHORIZED")
  timestamp: string;     // ISO 8601 timestamp
}
```

---

## ⚠️ Error Handling

### HTTP Status Codes

| Code | Meaning | When |
|------|---------|------|
| 200 | OK | Request successful |
| 201 | Created | Resource created |
| 400 | Bad Request | Invalid request data |
| 401 | Unauthorized | Missing or invalid JWT token |
| 404 | Not Found | Resource not found |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |

### Error Response Format

All errors return a consistent JSON format:

```json
{
  "error": "Human-readable error message",
  "code": "ERROR_CODE",
  "timestamp": "2025-12-25T10:30:00Z"
}
```

### Common Error Codes

| Code | Description | Resolution |
|------|-------------|------------|
| `UNAUTHORIZED` | Invalid or missing JWT | Login again to get new token |
| `VALIDATION_ERROR` | Invalid request data | Check request format |
| `NOT_FOUND` | Resource not found | Verify ID/session exists |
| `RATE_LIMIT_EXCEEDED` | Too many requests | Wait before retrying |
| `INTERNAL_ERROR` | Server error | Contact support |
| `AGENT_ERROR` | AI agent failed | Retry request |
| `BACKEND_ERROR` | Phase 2 backend error | Check Phase 2 status |

### Example Error Responses

**401 Unauthorized:**
```json
{
  "error": "Invalid or expired JWT token",
  "code": "UNAUTHORIZED",
  "timestamp": "2025-12-25T10:30:00Z"
}
```

**400 Bad Request:**
```json
{
  "error": "Message field is required",
  "code": "VALIDATION_ERROR",
  "timestamp": "2025-12-25T10:30:00Z"
}
```

**429 Rate Limit:**
```json
{
  "error": "Rate limit exceeded. Maximum 30 requests per minute.",
  "code": "RATE_LIMIT_EXCEEDED",
  "timestamp": "2025-12-25T10:30:00Z"
}
```

---

## 🚦 Rate Limiting

### Limits

- **Rate:** 30 requests per minute per user
- **Burst:** 10 additional requests allowed
- **Window:** Sliding 60-second window

### Rate Limit Headers

Response includes rate limit information:

```http
X-RateLimit-Limit: 30
X-RateLimit-Remaining: 25
X-RateLimit-Reset: 1703505030
```

### Exceeded Rate Limit

When limit exceeded, API returns:
- **Status:** 429 Too Many Requests
- **Retry-After:** Seconds until rate limit resets

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 45

{
  "error": "Rate limit exceeded",
  "code": "RATE_LIMIT_EXCEEDED"
}
```

---

## 💡 Examples

### Example 1: Create Todo via Chat

```bash
curl -X POST https://api.your-domain.com/chat \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Add buy milk to my list",
    "session_id": "sess_1234567890_abc"
  }'
```

**Response:**
```json
{
  "response": "I've added 'Buy milk' to your list. 📝\n\nWould you like to set a due date or priority?",
  "session_id": "sess_1234567890_abc",
  "timestamp": "2025-12-25T10:30:01Z"
}
```

---

### Example 2: List Todos

```bash
curl -X POST https://api.your-domain.com/chat \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Show me my pending tasks",
    "session_id": "sess_1234567890_abc"
  }'
```

**Response:**
```json
{
  "response": "You have 3 pending tasks:\n\n1. 📝 Buy milk\n2. 📞 Call dentist (High priority)\n3. 📄 Finish report (Due tomorrow)\n\nWould you like details on any of these?",
  "session_id": "sess_1234567890_abc",
  "timestamp": "2025-12-25T10:30:02Z"
}
```

---

### Example 3: Complete Todo with Context

```bash
# First, list tasks
curl -X POST https://api.your-domain.com/chat \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Show my tasks",
    "session_id": "sess_1234567890_abc"
  }'

# Then complete by reference
curl -X POST https://api.your-domain.com/chat \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I finished the first one",
    "session_id": "sess_1234567890_abc"
  }'
```

**Response:**
```json
{
  "response": "Awesome! 🎉 I've marked 'Buy milk' as completed.\n\nYou have 2 tasks remaining. Keep it up!",
  "session_id": "sess_1234567890_abc",
  "timestamp": "2025-12-25T10:30:03Z"
}
```

---

### Example 4: Multi-turn Conversation

```javascript
// JavaScript/TypeScript example
async function chatWithBot(message: string, sessionId: string) {
  const response = await fetch('https://api.your-domain.com/chat', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('jwt_token')}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ message, session_id: sessionId })
  });

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }

  return await response.json();
}

// Usage
const sessionId = 'sess_1234567890_abc';

// Create todo
const res1 = await chatWithBot('Add buy groceries', sessionId);
console.log(res1.response);
// "I've added 'Buy groceries' to your list. 📝"

// Make it high priority
const res2 = await chatWithBot('Make it high priority', sessionId);
console.log(res2.response);
// "Updated! 'Buy groceries' is now high priority. 🔴"
```

---

### Example 5: Python Client

```python
import requests

class ChatbotClient:
    def __init__(self, api_url, jwt_token):
        self.api_url = api_url
        self.headers = {
            'Authorization': f'Bearer {jwt_token}',
            'Content-Type': 'application/json'
        }

    def chat(self, message: str, session_id: str) -> dict:
        response = requests.post(
            f'{self.api_url}/chat',
            json={'message': message, 'session_id': session_id},
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

# Usage
client = ChatbotClient('https://api.your-domain.com', 'your_jwt_token')

# Send message
result = client.chat('Show me my tasks', 'sess_1234567890_abc')
print(result['response'])
```

---

## 🔧 Interactive API Documentation

### Swagger UI

Visit the interactive API documentation:

**URL:** `https://api.your-domain.com/docs`

Features:
- Try API endpoints directly from browser
- View request/response schemas
- Test authentication
- See example requests

### ReDoc

Alternative API documentation:

**URL:** `https://api.your-domain.com/redoc`

Features:
- Clean, readable format
- Organized by endpoints
- Detailed schemas
- Examples and descriptions

---

## 📞 Support

### Getting Help

1. **API Issues:** Check [Troubleshooting](#troubleshooting)
2. **Rate Limits:** Contact support to increase limits
3. **Bug Reports:** Open GitHub issue
4. **Feature Requests:** Submit via GitHub

### Response Times

- Health check: <100ms
- Chat endpoint: <2s (target)
- History endpoint: <500ms

---

## 🔒 Security Best Practices

### For API Consumers

1. **Never expose JWT tokens in client-side code**
2. **Use HTTPS in production**
3. **Implement token refresh logic**
4. **Handle 401 responses (logout user)**
5. **Sanitize user input before sending**
6. **Implement request timeouts**
7. **Rate limit client-side requests**

### Token Storage

**✅ DO:**
- Store in httpOnly cookies
- Use secure session storage
- Implement token rotation

**❌ DON'T:**
- Store in localStorage (XSS risk)
- Include in URLs
- Log tokens
- Share tokens between users

---

## 📊 Monitoring

### Health Check Endpoint

Use `/health` for uptime monitoring:

```bash
# Simple health check
curl https://api.your-domain.com/health

# With timeout
curl --max-time 5 https://api.your-domain.com/health
```

### Metrics to Monitor

- **Availability:** Uptime percentage
- **Latency:** P50, P95, P99 response times
- **Error Rate:** 4xx and 5xx responses
- **Rate Limits:** Throttled requests count

---

**API Documentation Version:** 1.0.0
**Last Updated:** 2025-12-25
**Status:** Production Ready
