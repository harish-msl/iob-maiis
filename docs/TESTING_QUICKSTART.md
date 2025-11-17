# Testing Quick Start Guide

**IOB MAIIS - Get Started with Testing in 5 Minutes**

---

## 🚀 Quick Setup

### 1. Install Dependencies

```bash
cd frontend
npm install --legacy-peer-deps
```

### 2. Install Playwright Browsers

```bash
npx playwright install
```

### 3. Run Your First Test

```bash
# Unit tests
npm test

# E2E tests
npm run test:e2e
```

---

## 📋 Common Commands

### Unit Tests

```bash
# Run all unit tests
npm test

# Watch mode (auto-rerun on changes)
npm run test:watch

# With coverage report
npm run test:coverage

# Run specific test file
npm test -- useVoice.test.ts

# Run tests matching a pattern
npm test -- --testNamePattern="Voice"
```

### Integration Tests

```bash
# Run integration tests only
npm test -- tests/integration

# Run specific integration test
npm test -- chat.test.tsx
```

### E2E Tests

```bash
# Run all E2E tests
npm run test:e2e

# Run in UI mode (interactive)
npm run test:e2e:ui

# Run on specific browser
npx playwright test --project=chromium
npx playwright test --project=firefox

# Debug mode (step through tests)
npx playwright test --debug

# Headed mode (watch browser)
npx playwright test --headed
```

---

## 🎯 Quick Test Examples

### Example 1: Test a Component

```typescript
// tests/unit/MyComponent.test.tsx
import { screen } from '@testing-library/react';
import { renderWithProviders } from '../utils/test-utils';
import MyComponent from '@/components/MyComponent';

describe('MyComponent', () => {
  it('should render correctly', () => {
    renderWithProviders(<MyComponent />);
    
    expect(screen.getByText('Hello World')).toBeInTheDocument();
  });
});
```

### Example 2: Test a Hook

```typescript
// tests/unit/useMyHook.test.ts
import { renderHook, act } from '@testing-library/react';
import { useMyHook } from '@/hooks/useMyHook';

describe('useMyHook', () => {
  it('should update state', async () => {
    const { result } = renderHook(() => useMyHook());
    
    await act(async () => {
      await result.current.doSomething();
    });
    
    expect(result.current.value).toBe('expected');
  });
});
```

### Example 3: Test API Integration

```typescript
// tests/integration/api.test.tsx
import { server } from '../mocks/server';
import { http, HttpResponse } from 'msw';
import { setupMockServer } from '../mocks/server';

setupMockServer();

describe('API Integration', () => {
  it('should fetch data successfully', async () => {
    server.use(
      http.get('/api/data', () => {
        return HttpResponse.json({ success: true });
      })
    );
    
    // Test your component that calls the API
  });
});
```

### Example 4: E2E Test

```typescript
// tests/e2e/login.spec.ts
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

## 🔍 Viewing Test Results

### Coverage Report

```bash
# Generate coverage
npm run test:coverage

# Open HTML report in browser
# macOS
open coverage/lcov-report/index.html

# Linux
xdg-open coverage/lcov-report/index.html

# Windows
start coverage/lcov-report/index.html
```

### Playwright Report

```bash
# After running E2E tests
npx playwright show-report
```

---

## 🐛 Debugging Tests

### Debug Unit Tests

```bash
# Run single test file
npm test -- MyComponent.test.tsx

# Use console.log in tests
console.log(screen.debug()); // Prints DOM

# VSCode debugger
# Set breakpoint, then press F5
```

### Debug E2E Tests

```bash
# Debug mode with Playwright Inspector
npx playwright test --debug

# Headed + slow motion
npx playwright test --headed --slow-mo=1000

# Take screenshots
await page.screenshot({ path: 'debug.png' });
```

---

## ✅ Pre-Commit Checklist

```bash
# 1. Run type check
npm run type-check

# 2. Run linter
npm run lint

# 3. Run tests
npm test

# 4. Check coverage
npm run test:coverage
```

---

## 📊 Coverage Targets

| Type | Target |
|------|--------|
| **Lines** | 70%+ |
| **Functions** | 70%+ |
| **Branches** | 70%+ |
| **Statements** | 70%+ |

---

## 🎓 Testing Best Practices

### ✅ Do's

- **Write descriptive test names**
  ```typescript
  it('should display error when API returns 500')
  ```

- **Use data-testid for stable selectors**
  ```typescript
  <button data-testid="submit-button">Submit</button>
  await page.click('[data-testid="submit-button"]');
  ```

- **Clean up after tests**
  ```typescript
  afterEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
  });
  ```

- **Use waitFor for async assertions**
  ```typescript
  await waitFor(() => {
    expect(screen.getByText('Loaded')).toBeVisible();
  });
  ```

### ❌ Don'ts

- **Don't use implementation details**
  ```typescript
  // ❌ Bad
  expect(component.state.value).toBe('test');
  
  // ✅ Good
  expect(screen.getByText('test')).toBeInTheDocument();
  ```

- **Don't make tests dependent on each other**
  ```typescript
  // ❌ Bad
  let sharedState;
  test('1', () => { sharedState = 'value'; });
  test('2', () => { expect(sharedState).toBe('value'); });
  ```

- **Don't skip cleanup**
  ```typescript
  // ❌ Bad: memory leaks
  
  // ✅ Good
  afterEach(() => {
    cleanup();
  });
  ```

---

## 🆘 Common Issues

### Issue: "Tests timeout"

```typescript
// Solution: Increase timeout
it('slow test', async () => {
  // test code
}, 30000); // 30 seconds
```

### Issue: "Cannot find module"

```bash
# Solution: Check path aliases in jest.config.ts
moduleNameMapper: {
  '^@/(.*)$': '<rootDir>/src/$1',
}
```

### Issue: "Playwright tests fail"

```bash
# Solution: Update browsers
npx playwright install

# Check for errors in debug mode
npx playwright test --debug
```

### Issue: "MSW not intercepting"

```typescript
// Solution: Ensure server is set up
import { setupMockServer } from '../mocks/server';
setupMockServer();

// Match exact URL
http.get('http://localhost:8000/api/data', ...)
```

---

## 📚 Next Steps

1. **Read full guide**: See `docs/TESTING_GUIDE.md`
2. **Explore examples**: Check `tests/` directory
3. **Write tests**: Start with unit tests, then integration, then E2E
4. **Run CI**: Push to trigger GitHub Actions

---

## 🔗 Quick Links

- [Jest Docs](https://jestjs.io/)
- [React Testing Library](https://testing-library.com/react)
- [Playwright Docs](https://playwright.dev/)
- [MSW Docs](https://mswjs.io/)

---

## 🎯 Test Your Knowledge

Try writing a test for:
1. ✅ A button click that updates text
2. ✅ An API call that returns data
3. ✅ A form submission flow
4. ✅ An error handling scenario
5. ✅ A user login flow (E2E)

---

**Need help?** Check the full testing guide or ask the team!

**Last Updated**: 2025-01-17