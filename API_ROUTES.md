# IOB MAIIS API Routes Documentation

## Base URL
- **Development**: `http://localhost:8000`
- **Production**: `https://your-domain.com`

## API Documentation
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI Schema**: http://localhost:8000/api/openapi.json

---

## Authentication Routes (`/api/auth`)

### Sign Up
- **POST** `/api/auth/signup`
- **Description**: Register a new user account
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "SecurePass123!",
    "full_name": "John Doe",
    "phone": "+1234567890" // optional
  }
  ```
- **Response**: `UserResponse` (201 Created)

### Login
- **POST** `/api/auth/login`
- **Description**: Authenticate user and get tokens
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "SecurePass123!"
  }
  ```
- **Response**: `LoginResponse` with access/refresh tokens

### Refresh Token
- **POST** `/api/auth/refresh`
- **Description**: Get new access token using refresh token
- **Request Body**:
  ```json
  {
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
  ```
- **Response**: New access token

### Logout
- **POST** `/api/auth/logout`
- **Description**: Logout current user
- **Headers**: `Authorization: Bearer <access_token>`
- **Response**: Success message

### Get Current User
- **GET** `/api/auth/me`
- **Description**: Get authenticated user information
- **Headers**: `Authorization: Bearer <access_token>`
- **Response**: `UserResponse`

### Update Profile
- **PUT** `/api/auth/me`
- **Description**: Update current user profile
- **Headers**: `Authorization: Bearer <access_token>`
- **Request Body**:
  ```json
  {
    "full_name": "Updated Name",
    "phone": "+1234567890",
    "bio": "User bio",
    "avatar_url": "https://..."
  }
  ```

### Change Password
- **POST** `/api/auth/change-password`
- **Description**: Change user password
- **Headers**: `Authorization: Bearer <access_token>`
- **Request Body**:
  ```json
  {
    "current_password": "OldPass123!",
    "new_password": "NewSecurePass456!"
  }
  ```

---

## Chat Routes (`/api/chat`)

### Send Chat Message
- **POST** `/api/chat/message`
- **Description**: Send a message to AI assistant with RAG
- **Headers**: `Authorization: Bearer <access_token>`
- **Request Body**:
  ```json
  {
    "message": "How do I transfer money?",
    "conversation_history": [],
    "stream": false
  }
  ```
- **Response**: AI response with context

### Stream Chat (WebSocket)
- **WebSocket** `/api/chat/ws`
- **Description**: Real-time streaming chat
- **Headers**: `Authorization: Bearer <access_token>`

### Chat History
- **GET** `/api/chat/history`
- **Description**: Get user's chat history
- **Headers**: `Authorization: Bearer <access_token>`
- **Query Params**: `limit`, `offset`

### Health Check
- **GET** `/api/chat/health`
- **Description**: Check RAG service health
- **Response**: Service status

### Ingest Document
- **POST** `/api/chat/ingest`
- **Description**: Ingest document into knowledge base (admin only)
- **Headers**: `Authorization: Bearer <access_token>`
- **Request Body**:
  ```json
  {
    "text": "Long document text...",
    "metadata": {
      "type": "policy",
      "category": "loans"
    },
    "chunk_size": 500,
    "chunk_overlap": 50
  }
  ```

---

## Banking Routes (`/api/banking`)

### List Accounts
- **GET** `/api/banking/accounts`
- **Description**: Get user's bank accounts
- **Headers**: `Authorization: Bearer <access_token>`

### Get Account Details
- **GET** `/api/banking/accounts/{account_id}`
- **Description**: Get specific account details
- **Headers**: `Authorization: Bearer <access_token>`

### Create Account
- **POST** `/api/banking/accounts`
- **Description**: Create new bank account
- **Headers**: `Authorization: Bearer <access_token>`
- **Request Body**:
  ```json
  {
    "account_type": "savings",
    "account_name": "My Savings"
  }
  ```

### Get Transactions
- **GET** `/api/banking/accounts/{account_id}/transactions`
- **Description**: Get account transactions
- **Headers**: `Authorization: Bearer <access_token>`
- **Query Params**: `limit`, `offset`, `start_date`, `end_date`

### Transfer Money
- **POST** `/api/banking/transfer`
- **Description**: Transfer money between accounts
- **Headers**: `Authorization: Bearer <access_token>`
- **Request Body**:
  ```json
  {
    "from_account_id": 1,
    "to_account_id": 2,
    "amount": 100.50,
    "description": "Payment"
  }
  ```

### Get Account Balance
- **GET** `/api/banking/accounts/{account_id}/balance`
- **Description**: Get current account balance
- **Headers**: `Authorization: Bearer <access_token>`

---

## Document Routes (`/api/documents`)

### Upload Document
- **POST** `/api/documents/upload`
- **Description**: Upload and process document with OCR
- **Headers**: `Authorization: Bearer <access_token>`
- **Content-Type**: `multipart/form-data`
- **Form Data**:
  - `file`: Document file (PDF, image, etc.)
  - `document_type`: Type of document (optional)

### List Documents
- **GET** `/api/documents`
- **Description**: Get user's uploaded documents
- **Headers**: `Authorization: Bearer <access_token>`
- **Query Params**: `limit`, `offset`, `document_type`

### Get Document
- **GET** `/api/documents/{document_id}`
- **Description**: Get specific document details
- **Headers**: `Authorization: Bearer <access_token>`

### Delete Document
- **DELETE** `/api/documents/{document_id}`
- **Description**: Delete a document
- **Headers**: `Authorization: Bearer <access_token>`

### Process Document (OCR)
- **POST** `/api/documents/{document_id}/process`
- **Description**: Trigger OCR processing for document
- **Headers**: `Authorization: Bearer <access_token>`

### Get Extracted Text
- **GET** `/api/documents/{document_id}/text`
- **Description**: Get OCR extracted text
- **Headers**: `Authorization: Bearer <access_token>`

---

## Voice Routes (`/api/voice`)

### Speech to Text
- **POST** `/api/voice/transcribe`
- **Description**: Convert audio to text
- **Headers**: `Authorization: Bearer <access_token>`
- **Content-Type**: `multipart/form-data`
- **Form Data**:
  - `audio_file`: Audio file (WAV, MP3, etc.)
  - `language`: Language code (default: "en")

### Text to Speech
- **POST** `/api/voice/synthesize`
- **Description**: Convert text to speech
- **Headers**: `Authorization: Bearer <access_token>`
- **Request Body**:
  ```json
  {
    "text": "Hello, how can I help you?",
    "voice": "en-US-Standard-A",
    "language": "en-US"
  }
  ```
- **Response**: Audio file (binary)

### Voice Chat
- **POST** `/api/voice/chat`
- **Description**: Voice-to-voice chat with AI
- **Headers**: `Authorization: Bearer <access_token>`
- **Content-Type**: `multipart/form-data`
- **Form Data**:
  - `audio_file`: Voice message
  - `return_audio`: Boolean (whether to return audio response)

---

## Health & Monitoring

### Application Health
- **GET** `/health`
- **Description**: Check application health
- **Response**:
  ```json
  {
    "status": "healthy",
    "timestamp": 1234567890,
    "services": {
      "database": "healthy",
      "redis": "healthy",
      "qdrant": "healthy"
    },
    "version": "1.0.0",
    "environment": "development"
  }
  ```

### Metrics (Prometheus)
- **GET** `/metrics`
- **Description**: Prometheus metrics endpoint
- **Access**: Internal only (restricted to Docker network)

---

## Frontend Configuration

Update your frontend API client to use these routes. Example:

```typescript
// src/lib/api/client.ts
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const API_ENDPOINTS = {
  auth: {
    signup: '/api/auth/signup',
    login: '/api/auth/login',
    refresh: '/api/auth/refresh',
    logout: '/api/auth/logout',
    me: '/api/auth/me',
    updateProfile: '/api/auth/me',
    changePassword: '/api/auth/change-password',
  },
  chat: {
    message: '/api/chat/message',
    ws: '/api/chat/ws',
    history: '/api/chat/history',
    health: '/api/chat/health',
    ingest: '/api/chat/ingest',
  },
  banking: {
    accounts: '/api/banking/accounts',
    accountDetail: (id: number) => `/api/banking/accounts/${id}`,
    transactions: (id: number) => `/api/banking/accounts/${id}/transactions`,
    transfer: '/api/banking/transfer',
    balance: (id: number) => `/api/banking/accounts/${id}/balance`,
  },
  documents: {
    upload: '/api/documents/upload',
    list: '/api/documents',
    detail: (id: number) => `/api/documents/${id}`,
    delete: (id: number) => `/api/documents/${id}`,
    process: (id: number) => `/api/documents/${id}/process`,
    text: (id: number) => `/api/documents/${id}/text`,
  },
  voice: {
    transcribe: '/api/voice/transcribe',
    synthesize: '/api/voice/synthesize',
    chat: '/api/voice/chat',
  },
};
```

---

## Authentication

All protected routes require a JWT access token in the Authorization header:

```
Authorization: Bearer <access_token>
```

### Token Lifecycle
- **Access Token**: Valid for 30 minutes
- **Refresh Token**: Valid for 7 days

When the access token expires, use the refresh token endpoint to get a new access token.

---

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Error message",
  "request_id": "uuid-v4",
  "error_type": "ErrorType"
}
```

### Common HTTP Status Codes
- `200 OK`: Success
- `201 Created`: Resource created
- `400 Bad Request`: Validation error
- `401 Unauthorized`: Missing or invalid token
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Invalid data
- `500 Internal Server Error`: Server error

---

## Rate Limiting

Rate limits are applied per IP address:
- **General endpoints**: 100 requests/minute
- **Auth endpoints**: 10 requests/minute
- **Upload endpoints**: 20 requests/minute

---

## CORS

The API allows cross-origin requests from:
- `http://localhost:3000` (development)
- Your production frontend domain

---

## Testing

### Using cURL

```bash
# Sign up
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test@12345","full_name":"Test User"}'

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test@12345"}'

# Get user info (requires token)
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer <your_access_token>"
```

### Using the Swagger UI

Visit http://localhost:8000/api/docs to:
- Explore all endpoints interactively
- Test API calls with authentication
- View request/response schemas
- Generate code snippets

---

## WebSocket Endpoints

### Chat WebSocket
- **URL**: `ws://localhost:8000/api/chat/ws?token=<access_token>`
- **Protocol**: WebSocket
- **Messages**: JSON formatted
- **Example**:
  ```javascript
  const ws = new WebSocket(`ws://localhost:8000/api/chat/ws?token=${accessToken}`);
  
  ws.onopen = () => {
    ws.send(JSON.stringify({
      type: 'message',
      content: 'Hello AI!'
    }));
  };
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('AI Response:', data);
  };
  ```

---

## Notes

1. **All timestamps** are in ISO 8601 format (UTC)
2. **All monetary amounts** are in decimal format (e.g., 100.50)
3. **File uploads** use multipart/form-data
4. **Passwords** must be at least 8 characters with uppercase, lowercase, and digit
5. **Email addresses** are validated and must be unique

---

Last Updated: 2025-11-19