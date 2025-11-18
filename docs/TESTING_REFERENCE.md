# Testing Quick Reference Card

**IOB MAIIS - Testing Commands & Tips**

---

## 🚀 Quick Start (30 seconds)

```bash
cd frontend
npm test                    # Run all tests
npm run test:e2e           # Run E2E tests
npm run test:coverage      # Coverage report
```

---

## 📋 Common Commands

### Unit & Integration Tests

```bash
# Run all tests
npm test

# Watch mode (auto-rerun)
npm run test:watch

# With coverage
npm run test:coverage

# Specific file
npm test -- useVoice.test.ts

# Pattern matching
npm test -- --testNamePattern="Voice"

# Update snapshots
npm test -- -u

# Run in band (no parallel)
npm test -- --runInBand
```

### E2E Tests (Playwright)

```bash
# Run all E2E
npm run test:e2e

# Interactive mode
npm run test:e2e:ui

# Debug mode
npx playwright test --debug

# Headed (visible browser)
npx playwright test --headed

# Specific browser
npx playwright test --project=chromium
npx playwright test --project=firefox

# Specific file
npx playwright test chat-flow.spec.ts

# Show report
npx playwright show-report
```

---

## 🔍 Coverage

```bash
# Generate coverage
npm run test:coverage

# View HTML report
open coverage/lcov-report/index.html        # macOS
xdg-open coverage/lcov-report/index.html    # Linux
start coverage/lcov-report/index.html       # Windows
```

**Thresholds**: 70% for lines, functions, branches, statements

---

## 🧪 Test File Locations

```
frontend/tests/
├── setup.ts                    # Jest setup
├── utils/test-utils.tsx        # Helpers
├── mocks/
│   ├── handlers.ts             # API mocks
│   └── server.ts               # MSW server
├── unit/
│   └── *.test.ts(x)           # Unit tests
├── integration/
│   └── *.test.ts(x)           # Integration tests
└── e2e/
    └── *.spec.ts              # E2E tests
```

---

## 📝 Writing Tests

### Component Test

```typescript
import { screen } from '@testing-library/react';
import { renderWithProviders } from '../utils/test-utils';
import MyComponent from '@/components/MyComponent';

describe('MyComponent', () => {
  it('should render', () => {
    renderWithProviders(<MyComponent />);
    expect(screen.getByText('Hello')).toBeInTheDocument();
  });
});
```

### Hook Test

```typescript
import { renderHook, act } from '@testing-library/react';
import { useMyHook } from '@/hooks/useMyHook';

describe('useMyHook', () => {
  it('should work', async () => {
    const { result } = renderHook(() => useMyHook());
    
    await act(async () => {
      await result.current.doSomething();
    });
    
    expect(result.current.value).toBe('expected');
  });
});
```

### E2E Test

```typescript
import { test, expect } from '@playwright/test';

test('user can login', async ({ page }) => {
  await page.goto('http://localhost:3000/login');
  await page.fill('input[name="email"]', 'test@example.com');
  await page.fill('input[name="password"]', 'password');
  await page.click('button[type="submit"]');
  
  await expect(page).toHaveURL(/dashboard/);
});
```

---

## 🔧 Debugging

### Jest Debug

```bash
# Node debugger
node --inspect-brk node_modules/.bin/jest --runInBand

# Specific test
npm test -- MyComponent.test.tsx

# Print DOM
console.log(screen.debug());
```

### Playwright Debug

```bash
# Debug mode
npx playwright test --debug

# Slow motion
npx playwright test --headed --slow-mo=1000

# Screenshot
await page.screenshot({ path: 'debug.png' });

# Trace
npx playwright test --trace on
npx playwright show-trace trace.zip
```

---

## 🎯 Mock APIs (MSW)

```typescript
import { server } from '../mocks/server';
import { http, HttpResponse } from 'msw';

// Setup in test file
setupMockServer();

// Override endpoint
server.use(
  http.get('/api/data', () => {
    return HttpResponse.json({ data: 'mock' });
  })
);

// Error response
server.use(
  http.get('/api/data', () => {
    return HttpResponse.json(
      { message: 'Error' },
      { status: 500 }
    );
  })
);
```

---

## 📦 Test Utilities

```typescript
import {
  renderWithProviders,
  mockUser,
  mockAccount,
  createMockFile,
  mockFetch,
  mockLocalStorage,
} from '../utils/test-utils';

// Render with providers
renderWithProviders(<Component />);

// Use mock data
const user = mockUser;

// Mock fetch
mockFetch({ data: 'response' });

// Mock localStorage
const storage = mockLocalStorage({ key: 'value' });
```

---

## ✅ Pre-Commit Checklist

```bash
npm run type-check     # TypeScript
npm run lint           # ESLint
npm test               # Tests
npm run test:coverage  # Coverage
```

---

## 🎯 Coverage Targets

| Metric | Target |
|--------|--------|
| Lines | 70%+ |
| Functions | 70%+ |
| Branches | 70%+ |
| Statements | 70%+ |

---

## 🚨 Common Issues

### Tests Timeout
```typescript
it('slow test', async () => {
  // ...
}, 30000); // 30 seconds
```

### Flaky Tests
```bash
# Run multiple times
npm test -- --testNamePattern="flaky" --repeat=10
```

### MSW Not Working
```typescript
// Ensure server setup
setupMockServer();

// Match exact URL
http.get('http://localhost:8000/api/data', ...)
```

### Playwright Failures
```bash
# Update browsers
npx playwright install

# Check in debug mode
npx playwright test --debug
```

---

## 🔗 Quick Links

- Full Guide: `docs/TESTING_GUIDE.md`
- Quick Start: `docs/TESTING_QUICKSTART.md`
- [Jest Docs](https://jestjs.io/)
- [Playwright Docs](https://playwright.dev/)
- [Testing Library](https://testing-library.com/)

---

## 📊 CI/CD

### Triggers
- Push to `main` or `develop`
- Pull requests
- Manual dispatch

### Pipeline Jobs
1. Frontend Tests (type, lint, unit, E2E)
2. Backend Tests (lint, type, pytest)
3. Security Scan (Trivy, npm audit)
4. Docker Build
5. Integration Tests
6. Code Quality (SonarCloud, CodeQL)
7. Deploy to Staging (main only)
8. Notifications

### Status
View at: `https://github.com/YOUR_ORG/iob-maiis/actions`

---

## 🎓 Best Practices

✅ Use data-testid for stable selectors  
✅ Write descriptive test names  
✅ Clean up after tests (afterEach)  
✅ Use waitFor for async assertions  
✅ Mock external dependencies  
✅ Test user behavior, not implementation  
✅ Keep tests independent  
✅ Avoid testing implementation details

---

## 💡 Tips

- **Run tests often**: Catch bugs early
- **Write tests first**: TDD approach
- **Keep tests simple**: One assertion per test
- **Use factories**: Reusable mock data
- **Document edge cases**: Tests as documentation
- **Fix flaky tests**: Don't ignore intermittent failures

---

**Last Updated**: 2025-01-17  
**Project**: IOB MAIIS v1.0.0