# Frontend Quick Start Guide

**Project**: IOB MAIIS Frontend  
**Last Updated**: 2025-01-17  
**Status**: 60% Complete - Ready for Dashboard Implementation

---

## 🚀 Getting Started

### Prerequisites
- Node.js >= 20.0.0
- npm >= 10.0.0
- Backend API running at `http://localhost:8000`

### Installation

```bash
cd frontend
npm install
```

### Development Server

```bash
npm run dev
# Opens at http://localhost:3000
```

### Available Scripts

```bash
npm run dev          # Start development server
npm run build        # Production build
npm run start        # Start production server
npm run lint         # Run ESLint
npm run lint:fix     # Fix linting issues
npm run type-check   # TypeScript type checking
npm run test         # Run Jest tests
npm run test:e2e     # Run Playwright E2E tests
```

---

## ✅ What's Already Implemented

### Core Infrastructure (100%)
- ✅ Next.js 15 with App Router
- ✅ TypeScript configuration
- ✅ Tailwind CSS with custom theme
- ✅ ESLint + Prettier
- ✅ All dependencies installed

### Type System (100%)
- ✅ Complete TypeScript definitions in `/src/types/index.ts`
- ✅ User, Banking, Chat, Document, Voice types
- ✅ API request/response types
- ✅ Form validation types

### API Integration (100%)
- ✅ Axios client with interceptors in `/src/lib/api-client.ts`
- ✅ Automatic token refresh on 401
- ✅ All backend endpoints wrapped
- ✅ Error handling and retry logic

### State Management (100%)
- ✅ Auth store (login, signup, logout)
- ✅ Banking store (accounts, transactions)
- ✅ Persistent storage with Zustand

### Utilities (100%)
- ✅ Currency, date, time formatting
- ✅ File size, number formatting
- ✅ Account masking, validation
- ✅ 30+ helper functions in `/src/lib/utils.ts`

### UI Components (30%)
- ✅ Button with variants
- ✅ Input component
- ✅ Card components
- ⏳ 20+ more components needed

### Pages (20%)
- ✅ Root layout with theme provider
- ✅ Login page (`/auth/login`)
- ✅ Signup page (`/auth/signup`)
- ⏳ Dashboard pages needed

---

## 🎯 Next Steps (Priority Order)

### Phase 1: Dashboard Core (Est: 3-4 hours)

#### 1.1 Create Dashboard Layout
Create `/src/app/dashboard/layout.tsx`:
- Main layout with sidebar
- Top navigation bar
- User menu dropdown
- Mobile responsive menu
- Protected route wrapper

#### 1.2 Create Dashboard Home
Create `/src/app/dashboard/page.tsx`:
- Account overview cards
- Balance summary
- Recent transactions
- Quick actions
- Charts and statistics

#### 1.3 Add UI Components
Complete shadcn/ui components:
- Label
- Form
- Dialog
- Select
- Dropdown Menu
- Tabs
- Avatar
- Badge

### Phase 2: Chat Interface (Est: 3-4 hours)

Create `/src/app/dashboard/chat/page.tsx`:
- Chat message components
- Input with file upload
- SSE streaming integration
- WebSocket support
- Message history
- RAG source citations

### Phase 3: Banking Pages (Est: 3-4 hours)

Create `/src/app/dashboard/accounts/`:
- Accounts list view
- Account details
- Transaction history
- Deposit/Withdraw forms
- Transfer form
- Charts and analytics

### Phase 4: Documents & Voice (Est: 3-4 hours)

Create:
- `/src/app/dashboard/documents/page.tsx`
- `/src/app/dashboard/voice/page.tsx`

---

## 📁 Project Structure

```
frontend/src/
├── app/
│   ├── auth/
│   │   ├── login/page.tsx ✅
│   │   └── signup/page.tsx ✅
│   ├── dashboard/         ⏳ CREATE NEXT
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   ├── accounts/
│   │   ├── chat/
│   │   ├── documents/
│   │   └── voice/
│   ├── layout.tsx ✅
│   ├── globals.css ✅
│   └── page.tsx ⏳
├── components/
│   ├── ui/               ⏳ 30% complete
│   ├── chat/             ⏳ TODO
│   ├── banking/          ⏳ TODO
│   └── shared/           ⏳ TODO
├── lib/
│   ├── api-client.ts ✅
│   └── utils.ts ✅
├── store/
│   ├── auth-store.ts ✅
│   └── banking-store.ts ✅
└── types/
    └── index.ts ✅
```

---

## 🔌 API Endpoints Ready to Use

All endpoints are available via the `apiClient` singleton:

```typescript
import { apiClient } from '@/lib/api-client';

// Authentication
await apiClient.login(email, password);
await apiClient.signup({ email, password, full_name });
await apiClient.logout();
const user = await apiClient.getCurrentUser();

// Chat
const response = await apiClient.sendMessage(message, context);
const stream = await apiClient.streamChat(message, context);
const history = await apiClient.getChatHistory();

// Banking
const accounts = await apiClient.getAccounts();
const account = await apiClient.createAccount({ account_type: 'checking' });
const txns = await apiClient.getTransactions(accountId);
await apiClient.deposit(accountId, amount, description);
await apiClient.withdraw(accountId, amount, description);
await apiClient.transfer(fromId, toId, amount, description);
const summary = await apiClient.getAccountSummary();

// Documents
const doc = await apiClient.uploadDocument(file, true);
const docs = await apiClient.getDocuments();
const ocr = await apiClient.processDocumentOcr(docId);
await apiClient.ingestDocument(docId);

// Voice
const transcription = await apiClient.transcribeAudio(file, 'en');
const audioBlob = await apiClient.synthesizeSpeech(text, 'en');
const info = await apiClient.getAudioInfo(file);
```

---

## 🎨 Design System

### Colors (CSS Variables)
```css
--primary: Blue (#3b82f6)
--secondary: Gray
--destructive: Red
--success: Green
--warning: Orange
```

### Components Pattern
```typescript
import { Button } from '@/components/ui/button';

<Button variant="default">Click Me</Button>
<Button variant="outline">Outline</Button>
<Button variant="destructive">Delete</Button>
<Button size="sm">Small</Button>
<Button size="lg">Large</Button>
```

### Utilities
```typescript
import { formatCurrency, formatDate, cn } from '@/lib/utils';

formatCurrency(1000, 'USD') // "$1,000.00"
formatDate(new Date(), 'relative') // "2 hours ago"
cn('base-class', condition && 'conditional-class')
```

---

## 🔐 Authentication Flow

### Login Flow
1. User fills login form
2. Form validates with Zod schema
3. `authStore.login()` called
4. API client sends credentials
5. Tokens stored in localStorage
6. User redirected to `/dashboard`

### Protected Routes
```typescript
// Use in dashboard layout
'use client';
import { useAuthStore } from '@/store/auth-store';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

export default function DashboardLayout({ children }) {
  const { isAuthenticated, fetchUser } = useAuthStore();
  const router = useRouter();

  useEffect(() => {
    fetchUser().catch(() => router.push('/auth/login'));
  }, []);

  if (!isAuthenticated) return <div>Loading...</div>;
  return <div>{children}</div>;
}
```

---

## 💾 State Management Patterns

### Using Auth Store
```typescript
import { useAuthStore } from '@/store/auth-store';

function Component() {
  const { user, login, logout, isLoading } = useAuthStore();
  
  // User is automatically populated
  console.log(user?.email);
}
```

### Using Banking Store
```typescript
import { useBankingStore } from '@/store/banking-store';

function AccountsList() {
  const { accounts, fetchAccounts, isLoading } = useBankingStore();
  
  useEffect(() => {
    fetchAccounts();
  }, []);
  
  return <div>{accounts.map(acc => ...)}</div>;
}
```

---

## 🧪 Testing

### Unit Tests
```typescript
// Example: utils.test.ts
import { formatCurrency } from '@/lib/utils';

describe('formatCurrency', () => {
  it('formats USD correctly', () => {
    expect(formatCurrency(1000, 'USD')).toBe('$1,000.00');
  });
});
```

### E2E Tests
```typescript
// Example: login.spec.ts
import { test, expect } from '@playwright/test';

test('user can login', async ({ page }) => {
  await page.goto('/auth/login');
  await page.fill('input[type="email"]', 'test@example.com');
  await page.fill('input[type="password"]', 'password123');
  await page.click('button[type="submit"]');
  await expect(page).toHaveURL('/dashboard');
});
```

---

## 🐛 Debugging Tips

### Check API Connection
```typescript
// In browser console
import { apiClient } from '@/lib/api-client';
await apiClient.healthCheck();
```

### View Store State
```typescript
// In component
import { useAuthStore } from '@/store/auth-store';
console.log(useAuthStore.getState());
```

### API Errors
All API errors are caught and formatted:
```typescript
try {
  await apiClient.login(email, password);
} catch (error) {
  console.error(error.message); // User-friendly message
  console.error(error.status);  // HTTP status code
}
```

---

## 🎓 Code Examples

### Dashboard Card Component
```typescript
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { formatCurrency } from '@/lib/utils';

export function AccountCard({ account }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{account.account_type}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">
          {formatCurrency(account.balance, account.currency)}
        </div>
        <p className="text-sm text-muted-foreground">
          {account.account_number}
        </p>
      </CardContent>
    </Card>
  );
}
```

### Chat Message Component
```typescript
import { ChatMessage } from '@/types';
import { formatTime } from '@/lib/utils';
import ReactMarkdown from 'react-markdown';

export function Message({ message }: { message: ChatMessage }) {
  const isUser = message.role === 'user';
  
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-[80%] rounded-lg p-4 ${
        isUser ? 'bg-primary text-primary-foreground' : 'bg-muted'
      }`}>
        <ReactMarkdown className="markdown-content">
          {message.content}
        </ReactMarkdown>
        <div className="text-xs opacity-70 mt-2">
          {formatTime(message.timestamp)}
        </div>
      </div>
    </div>
  );
}
```

---

## 📚 Resources

### Documentation
- Backend API Docs: `http://localhost:8000/api/docs`
- Next.js Docs: https://nextjs.org/docs
- Tailwind CSS: https://tailwindcss.com/docs
- Radix UI: https://www.radix-ui.com/primitives
- Zustand: https://docs.pmnd.rs/zustand

### Helpful Commands
```bash
# Type check
npm run type-check

# Lint and fix
npm run lint:fix

# Build production
npm run build

# Analyze bundle
ANALYZE=true npm run build
```

---

## 🚨 Common Issues

### Issue: API 401 Errors
**Solution**: Check that backend is running and tokens are valid
```bash
# In frontend
localStorage.getItem('access_token')

# Test backend
curl http://localhost:8000/health
```

### Issue: CORS Errors
**Solution**: Backend should allow frontend origin
```python
# Backend should have:
allow_origins=["http://localhost:3000"]
```

### Issue: Type Errors
**Solution**: Run type check and fix imports
```bash
npm run type-check
```

---

## ✨ Best Practices

1. **Always use TypeScript types** - Import from `/src/types/index.ts`
2. **Use API client** - Never use fetch/axios directly
3. **Use stores for state** - Don't prop drill
4. **Use utility functions** - Don't repeat formatting logic
5. **Handle errors** - Always try/catch async operations
6. **Show loading states** - Use `isLoading` from stores
7. **Mobile first** - Design responsive from the start
8. **Accessibility** - Add ARIA labels and keyboard nav

---

## 🎯 Current Focus: Dashboard Layout

**Create these files next**:

1. `/src/app/dashboard/layout.tsx` - Main dashboard shell
2. `/src/app/dashboard/page.tsx` - Dashboard home
3. `/src/components/ui/label.tsx` - Form label
4. `/src/components/ui/dialog.tsx` - Modal dialogs
5. `/src/components/ui/select.tsx` - Dropdown select
6. `/src/components/dashboard/sidebar.tsx` - Navigation sidebar
7. `/src/components/dashboard/navbar.tsx` - Top nav bar

**Time Estimate**: 3-4 hours  
**Priority**: HIGH  
**Blocking**: All other dashboard pages

---

## 📞 Need Help?

1. Check `/src/types/index.ts` for available types
2. Check `/src/lib/api-client.ts` for API methods
3. Check `/src/lib/utils.ts` for helper functions
4. Review `/src/store/*` for state management examples
5. Look at completed pages in `/src/app/auth/*`

---

**Ready to continue? Start with dashboard layout!** 🚀