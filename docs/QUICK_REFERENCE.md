# IOB MAIIS - Quick Reference Guide
**Last Updated**: January 17, 2025  
**Project Status**: 85% Complete (Backend 100%, Frontend 85%)  
**Next Task**: Banking Pages Implementation

---

## 🚀 Quick Start

```bash
# Start backend
cd backend
docker-compose up -d

# Start frontend
cd frontend
npm install
npm run dev
# Visit http://localhost:3000
```

---

## 📊 Current Status

### ✅ Complete (75%)
- **Backend**: 100% (All APIs working)
- **Frontend Infrastructure**: 100% (Types, API client, stores, utils)
- **Authentication**: 100% (Login, signup, protected routes)
- **Dashboard**: 100% (Layout, home page, navigation)
- **UI Components**: 60% (8 of 15+ components)

### ⏳ In Progress (15%)
- **Chat Interface**: ✅ 100% COMPLETE
- **Banking Pages**: 0% (Next priority)
- **Documents Page**: 0% (Medium priority)
- **Voice Interface**: 0% (Medium priority)
- **Testing**: 0% (Low priority)

---

## 📁 Key Files

### Reference These
```
src/types/index.ts              # All TypeScript definitions
src/lib/api-client.ts           # API integration (all endpoints)
src/lib/utils.ts                # 40+ utility functions
src/store/auth-store.ts         # Authentication state
src/store/banking-store.ts      # Banking state
src/store/chat-store.ts         # Chat state (NEW)
src/app/dashboard/page.tsx      # Dashboard example
src/components/dashboard/       # Navigation components
src/components/chat/            # Chat components (NEW)
```

### Chat Components (NEW - Complete)
```
src/app/dashboard/chat/page.tsx              # Chat page with sidebar
src/components/chat/ChatContainer.tsx        # Main chat with SSE streaming
src/components/chat/ChatMessage.tsx          # Message with markdown + citations
src/components/chat/ChatInput.tsx            # Input with file upload
src/components/chat/ChatSidebar.tsx          # Session management
src/store/chat-store.ts                      # Chat state management
```

---

## 🔌 API Endpoints (All Ready)

### Authentication
- `POST /api/auth/login` - Login
- `POST /api/auth/signup` - Register
- `GET /api/auth/me` - Current user
- `POST /api/auth/logout` - Logout

### Banking
- `GET /api/banking/accounts` - List accounts
- `GET /api/banking/summary` - Account summary
- `POST /api/banking/accounts` - Create account
- `POST /api/banking/accounts/{id}/deposit` - Deposit
- `POST /api/banking/accounts/{id}/withdraw` - Withdraw
- `POST /api/banking/transfer` - Transfer

### Chat (Ready to Use)
- `POST /api/chat/message` - Send message
- `POST /api/chat/stream` - Stream response (SSE)
- `WS /api/chat/ws` - WebSocket streaming
- `GET /api/chat/history` - Get history

### Documents (Ready to Use)
- `POST /api/documents/upload` - Upload file
- `GET /api/documents` - List documents
- `POST /api/documents/{id}/ocr` - Process OCR
- `POST /api/documents/{id}/ingest` - Add to vector DB

### Voice (Ready to Use)
- `POST /api/voice/transcribe` - Speech-to-text
- `POST /api/voice/synthesize` - Text-to-speech
- `POST /api/voice/audio-info` - Audio metadata

---

## 💻 Code Patterns

### Using API Client
```typescript
import { apiClient } from '@/lib/api-client';

// Send chat message
const response = await apiClient.sendMessage('Hello', {});

// Stream chat (SSE)
const stream = await apiClient.streamChat('Tell me about my accounts');

// Banking operations
const accounts = await apiClient.getAccounts();
await apiClient.deposit(accountId, 100, 'Deposit');
```

### Using Stores
```typescript
import { useAuthStore } from '@/store/auth-store';
import { useBankingStore } from '@/store/banking-store';

function MyComponent() {
  const { user, logout } = useAuthStore();
  const { accounts, fetchAccounts } = useBankingStore();
  
  useEffect(() => {
    fetchAccounts();
  }, []);
}
```

### Creating Pages
```typescript
// src/app/dashboard/mypage/page.tsx
'use client';

import { useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';

export default function MyPage() {
  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold">My Page</h1>
      <Card>
        <CardContent>Content here</CardContent>
      </Card>
    </div>
  );
}
```

---

## 🎨 UI Components Available

### Ready to Use
- `Button` - 6 variants, 4 sizes
- `Input` - Form input
- `Card` - Container with header/content/footer
- `Label` - Form labels
- `Badge` - Status indicators (7 variants)
- `Avatar` - User pictures with fallback
- `DropdownMenu` - Complete menu system
- `Separator` - Dividers

### Need to Create
- Dialog/Modal
- Select
- Tabs
- Form components
- Table
- Skeleton
- Progress
- Tooltip

---

## 🎯 Next Steps (Priority Order)

### 1. Chat Interface (4-5 hours) - HIGH
**Create**:
- `src/app/dashboard/chat/page.tsx`
- `src/components/chat/message-list.tsx`
- `src/components/chat/message-input.tsx`
- `src/components/chat/typing-indicator.tsx`
- `src/store/chat-store.ts`

**Features**:
- SSE streaming integration
- Message history
- RAG source citations
- Code syntax highlighting
- Markdown rendering

### 2. Banking Pages (4-5 hours) - HIGH
**Create**:
- `src/app/dashboard/accounts/page.tsx`
- `src/app/dashboard/accounts/[id]/page.tsx`
- `src/components/banking/account-card.tsx`
- `src/components/banking/transaction-table.tsx`
- `src/components/banking/transfer-form.tsx`

**Features**:
- Account details
- Transaction filtering
- Deposit/Withdraw/Transfer forms
- Charts and analytics

### 3. Documents Page (3-4 hours) - MEDIUM
**Create**:
- `src/app/dashboard/documents/page.tsx`
- `src/components/documents/upload-zone.tsx`
- `src/components/documents/document-list.tsx`
- `src/components/documents/ocr-viewer.tsx`

### 4. Voice Interface (3-4 hours) - MEDIUM
**Create**:
- `src/app/dashboard/voice/page.tsx`
- `src/components/voice/audio-recorder.tsx`
- `src/components/voice/transcription-display.tsx`

---

## 📚 Documentation

### Read These First
1. `FRONTEND_QUICKSTART.md` - How to use everything
2. `DASHBOARD_COMPLETE.md` - What's been built
3. `frontend/README.md` - Frontend-specific guide

### Reference
- `FRONTEND_IMPLEMENTATION_STATUS.md` - Detailed status
- `PROJECT_STATUS.md` - Overall project status
- `SESSION_COMPLETE_2025-01-17.md` - Latest session summary

### API Docs
- Backend: http://localhost:8000/api/docs
- Health: http://localhost:8000/health

---

## 🐛 Common Issues

### Backend not responding
```bash
cd backend
docker-compose up -d
docker-compose logs -f
# Check http://localhost:8000/health
```

### Frontend type errors
```bash
npm run type-check
# Restart TypeScript server in VS Code
```

### Authentication issues
```javascript
// Check in browser console
localStorage.getItem('access_token')
```

### CORS errors
- Backend should allow `http://localhost:3000`
- Check `backend/.env` file

---

## 📝 Useful Commands

```bash
# Frontend
npm run dev              # Dev server
npm run build            # Production build
npm run lint:fix         # Fix linting
npm run type-check       # Check types
npm run test             # Run tests

# Backend
docker-compose up -d     # Start services
docker-compose logs -f   # View logs
docker-compose down      # Stop services
make test                # Run tests
```

---

## 🎓 Tips

1. **Always check types** - `src/types/index.ts` has everything
2. **Use existing patterns** - Copy from dashboard home page
3. **Reference API client** - All endpoints are wrapped
4. **Use utilities** - Don't rewrite formatting functions
5. **Follow conventions** - 'use client' for interactive components
6. **Mobile first** - Design for mobile, enhance for desktop
7. **Handle errors** - Always try/catch async operations
8. **Show loading** - Use isLoading from stores

---

## 🏆 Progress Metrics

- **Total Lines**: ~14,713
- **Backend**: 9,755 lines (100% ✅)
- **Frontend**: 4,958 lines (75% 🔄)
- **Documentation**: 3,406 lines
- **Components**: 16 created
- **Pages**: 5 complete
- **Stores**: 2 active
- **Time Invested**: ~8-10 hours
- **Estimated Remaining**: ~22-28 hours

---

## 🚀 Ready to Code!

**Current Focus**: Chat Interface  
**Estimated Time**: 4-5 hours  
**Complexity**: Medium  
**Dependencies**: None (all APIs ready)

**Start Here**:
```bash
mkdir -p src/app/dashboard/chat
mkdir -p src/components/banking
mkdir -p src/app/dashboard/accounts
# Create account components and pages
```

---

## 💬 Chat Interface (NEW - Complete)

### Quick Usage

```typescript
// Navigate to chat
// http://localhost:3000/dashboard/chat

// Use chat store
import { useChatStore } from '@/store/chat-store';

const {
  sessions,              // All chat sessions
  currentSessionId,      // Active session ID
  messages,              // All messages by session
  isStreaming,           // Is AI responding?
  createSession,         // Create new chat
  addMessage,            // Add message
  startStreaming,        // Start SSE stream
  appendStreamChunk,     // Append chunk
  finishStreaming,       // Complete stream
} = useChatStore();

// Send message with files
<ChatInput 
  onSendMessage={(text, files) => handleSend(text, files)}
  maxFiles={5}
  maxFileSize={10}
/>

// Display messages with RAG sources
<ChatMessage 
  message={message}
  isStreaming={isStreaming}
/>
```

### Features Available
- ✅ Real-time SSE streaming
- ✅ Markdown + syntax highlighting
- ✅ RAG source citations
- ✅ File upload (drag-drop)
- ✅ Session management
- ✅ Mobile responsive
- ✅ Auto-scroll
- ✅ Copy messages
- ✅ Keyboard shortcuts

### SSE Streaming Example

```typescript
// Backend sends chunks
data: {"type": "content", "content": "Hello"}
data: {"type": "sources", "sources": [{...}]}
data: [DONE]

// Frontend handles
appendStreamChunk({
  type: "content",
  content: "Hello world"
});

finishStreaming([/* sources */]);
```

---

Good luck! 🎉