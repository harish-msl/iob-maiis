# IOB MAIIS Frontend

**Multimodal AI Banking Assistant - Frontend Application**

Modern Next.js 15 frontend with TypeScript, Tailwind CSS, and comprehensive API integration for the IOB MAIIS banking platform.

---

## 🚀 Quick Start

### Prerequisites
- Node.js >= 20.0.0
- npm >= 10.0.0
- Backend API running at `http://localhost:8000`

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

Visit [http://localhost:3000](http://localhost:3000)

---

## 📦 Technology Stack

- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript 5.6
- **Styling**: Tailwind CSS 3.4
- **UI Components**: Radix UI primitives
- **State Management**: Zustand 5.0
- **Forms**: React Hook Form + Zod validation
- **HTTP Client**: Axios 1.7
- **Icons**: Lucide React
- **Notifications**: Sonner
- **Charts**: Recharts 2.13
- **Markdown**: react-markdown + remark-gfm
- **Testing**: Jest + Playwright

---

## 📁 Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── auth/              # Authentication pages
│   │   │   ├── login/         # Login page ✅
│   │   │   └── signup/        # Signup page ✅
│   │   ├── dashboard/         # Main dashboard (TODO)
│   │   ├── layout.tsx         # Root layout ✅
│   │   └── globals.css        # Global styles ✅
│   ├── components/
│   │   └── ui/                # Reusable UI components
│   │       ├── button.tsx     # Button component ✅
│   │       ├── input.tsx      # Input component ✅
│   │       └── card.tsx       # Card components ✅
│   ├── lib/
│   │   ├── api-client.ts      # Axios API client ✅
│   │   └── utils.ts           # Helper functions ✅
│   ├── store/
│   │   ├── auth-store.ts      # Auth state ✅
│   │   └── banking-store.ts   # Banking state ✅
│   └── types/
│       └── index.ts           # TypeScript definitions ✅
├── public/                     # Static assets
├── tests/                      # Test files
├── package.json               # Dependencies
├── tsconfig.json              # TypeScript config
├── tailwind.config.ts         # Tailwind config
└── next.config.js             # Next.js config
```

---

## 🔧 Available Scripts

```bash
# Development
npm run dev              # Start dev server (http://localhost:3000)
npm run build            # Production build
npm run start            # Start production server

# Code Quality
npm run lint             # Run ESLint
npm run lint:fix         # Fix linting issues
npm run type-check       # TypeScript type checking
npm run format           # Format with Prettier

# Testing
npm run test             # Run Jest tests
npm run test:watch       # Watch mode
npm run test:coverage    # Coverage report
npm run test:e2e         # Playwright E2E tests
npm run test:e2e:ui      # E2E tests with UI

# Utilities
npm run clean            # Clean build artifacts
npm run analyze          # Bundle size analysis
```

---

## 🎨 Features

### Implemented ✅
- **Authentication**
  - Login page with form validation
  - Signup page with password confirmation
  - JWT token management
  - Auto token refresh on 401
  - Persistent sessions

- **State Management**
  - Auth store (login, logout, user management)
  - Banking store (accounts, transactions)
  - Persistent storage with Zustand

- **API Integration**
  - Complete Axios client with interceptors
  - All backend endpoints wrapped
  - Error handling and retry logic
  - Token injection and refresh

- **UI Components**
  - Button (6 variants, 4 sizes)
  - Input (styled form fields)
  - Card (composable layout)
  - Theme support (light/dark)

- **Utilities**
  - Currency formatting
  - Date/time formatting
  - File size formatting
  - Validation helpers
  - And 30+ more utilities

### Coming Soon 🔄
- Dashboard layout and navigation
- Chat interface with streaming
- Banking pages (accounts, transactions)
- Document upload and management
- Voice interaction interface
- Comprehensive testing suite

---

## 🔌 API Client Usage

The API client is available as a singleton instance:

```typescript
import { apiClient } from '@/lib/api-client';

// Authentication
await apiClient.login('user@example.com', 'password');
await apiClient.signup({ email, password, full_name });
await apiClient.logout();

// Chat
const response = await apiClient.sendMessage('Hello', { context: {} });
const stream = await apiClient.streamChat('Tell me about my accounts');

// Banking
const accounts = await apiClient.getAccounts();
const account = await apiClient.createAccount({ account_type: 'checking' });
await apiClient.deposit(accountId, 100, 'Paycheck');
await apiClient.transfer(fromId, toId, 50, 'Payment');

// Documents
const doc = await apiClient.uploadDocument(file, true);
await apiClient.processDocumentOcr(docId);

// Voice
const transcription = await apiClient.transcribeAudio(audioFile);
const audioBlob = await apiClient.synthesizeSpeech('Hello world');
```

---

## 🎯 State Management

### Using Auth Store

```typescript
import { useAuthStore } from '@/store/auth-store';

function Component() {
  const { user, login, logout, isLoading } = useAuthStore();

  const handleLogin = async () => {
    await login({ email: 'user@example.com', password: 'password' });
  };

  return (
    <div>
      {user ? (
        <p>Welcome, {user.full_name}!</p>
      ) : (
        <button onClick={handleLogin}>Login</button>
      )}
    </div>
  );
}
```

### Using Banking Store

```typescript
import { useBankingStore } from '@/store/banking-store';

function Accounts() {
  const { accounts, fetchAccounts, isLoading } = useBankingStore();

  useEffect(() => {
    fetchAccounts();
  }, []);

  return (
    <div>
      {accounts.map(account => (
        <div key={account.id}>{account.account_number}</div>
      ))}
    </div>
  );
}
```

---

## 🎨 Styling & Theming

### Tailwind CSS

```tsx
import { cn } from '@/lib/utils';

<div className={cn('text-lg font-bold', isActive && 'text-primary')}>
  Content
</div>
```

### Component Variants

```tsx
import { Button } from '@/components/ui/button';

<Button variant="default">Default</Button>
<Button variant="destructive">Delete</Button>
<Button variant="outline">Outline</Button>
<Button size="sm">Small</Button>
<Button size="lg">Large</Button>
```

### Theme Support

The app supports light and dark modes automatically via `next-themes`.

---

## 🔒 Authentication Flow

1. User submits login form
2. Form validates with Zod schema
3. `authStore.login()` calls API
4. API client stores JWT tokens
5. User redirected to dashboard
6. Protected routes check `isAuthenticated`
7. Token auto-refreshes on 401

---

## 🛠️ Development Guide

### Creating a New Page

```bash
# Create page directory
mkdir -p src/app/dashboard/accounts

# Create page component
cat > src/app/dashboard/accounts/page.tsx << 'EOF'
'use client';

export default function AccountsPage() {
  return <div>Accounts</div>;
}
EOF
```

### Adding a UI Component

```bash
# Use existing patterns from src/components/ui/
# Reference button.tsx, input.tsx, card.tsx
```

### Creating a Store

```typescript
import { create } from 'zustand';

interface MyState {
  count: number;
  increment: () => void;
}

export const useMyStore = create<MyState>((set) => ({
  count: 0,
  increment: () => set((state) => ({ count: state.count + 1 })),
}));
```

---

## 🧪 Testing

### Unit Tests

```typescript
// utils.test.ts
import { formatCurrency } from '@/lib/utils';

describe('formatCurrency', () => {
  it('formats USD correctly', () => {
    expect(formatCurrency(1000, 'USD')).toBe('$1,000.00');
  });
});
```

### E2E Tests

```typescript
// login.spec.ts
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

## 📚 Utility Functions

See `src/lib/utils.ts` for 40+ helper functions:

```typescript
import { 
  formatCurrency,
  formatDate,
  formatFileSize,
  truncate,
  maskAccountNumber,
  copyToClipboard,
  downloadBlob,
  debounce,
  throttle
} from '@/lib/utils';

// Examples
formatCurrency(1000, 'USD')           // "$1,000.00"
formatDate(new Date(), 'relative')    // "2 hours ago"
formatFileSize(1024000)               // "1.00 MB"
truncate('Long text here', 10)        // "Long text..."
maskAccountNumber('123456789')        // "*****6789"
```

---

## 🐛 Troubleshooting

### Backend Connection Issues

```typescript
// Check backend health
import { apiClient } from '@/lib/api-client';
const health = await apiClient.healthCheck();
console.log(health);
```

### Token Issues

```javascript
// Check stored tokens in browser console
localStorage.getItem('access_token')
localStorage.getItem('refresh_token')
```

### CORS Errors

Ensure backend allows frontend origin:
```python
# Backend should have:
allow_origins=["http://localhost:3000"]
```

### Type Errors

```bash
# Run type checker
npm run type-check

# Common fix: restart TypeScript server in VS Code
# Cmd+Shift+P -> "TypeScript: Restart TS Server"
```

---

## 📖 Documentation

- **Frontend Status**: See `../FRONTEND_IMPLEMENTATION_STATUS.md`
- **Quick Start**: See `../FRONTEND_QUICKSTART.md`
- **Project Status**: See `../PROJECT_STATUS.md`
- **Backend API**: http://localhost:8000/api/docs

---

## 🚀 Deployment

### Build for Production

```bash
npm run build
npm run start
```

### Environment Variables

Create `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=IOB MAIIS
NEXT_PUBLIC_APP_VERSION=1.0.0
```

### Docker Build

```bash
docker build -t iob-maiis-frontend .
docker run -p 3000:3000 iob-maiis-frontend
```

---

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Run tests: `npm run test`
4. Run linter: `npm run lint:fix`
5. Type check: `npm run type-check`
6. Submit a pull request

---

## 📊 Status

**Current Progress**: 60% Complete

- ✅ Infrastructure & configuration
- ✅ Type system (400+ lines)
- ✅ API client (380+ lines)
- ✅ Utilities (400+ lines)
- ✅ State management
- ✅ Authentication pages
- ✅ Core UI components
- ⏳ Dashboard pages (TODO)
- ⏳ Chat interface (TODO)
- ⏳ Banking pages (TODO)

---

## 📞 Support

For issues or questions:
1. Check documentation in `docs/` folder
2. Review API client: `src/lib/api-client.ts`
3. Check types: `src/types/index.ts`
4. See examples: `src/app/auth/*`

---

## 📝 License

MIT License - See LICENSE file for details

---

**Built with ❤️ by IOB MAIIS Team**