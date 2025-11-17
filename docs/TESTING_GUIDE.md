# Testing Guide

**IOB MAIIS - Multimodal AI-Enabled Information System**  
**Comprehensive Testing Documentation**

---

## Table of Contents

1. [Overview](#overview)
2. [Testing Strategy](#testing-strategy)
3. [Test Setup](#test-setup)
4. [Unit Testing](#unit-testing)
5. [Integration Testing](#integration-testing)
6. [End-to-End Testing](#end-to-end-testing)
7. [Test Coverage](#test-coverage)
8. [CI/CD Pipeline](#cicd-pipeline)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)

---

## Overview

This guide covers the complete testing infrastructure for IOB MAIIS, including:

- **Unit Tests**: Component and hook testing with Jest + React Testing Library
- **Integration Tests**: API integration tests with MSW (Mock Service Worker)
- **E2E Tests**: End-to-end user flow testing with Playwright
- **CI/CD**: Automated testing pipeline with GitHub Actions

### Testing Stack

**Frontend:**
- Jest 29.7.0 - Test runner
- React Testing Library 16.0.1 - Component testing
- Playwright 1.48.2 - E2E testing
- MSW (Mock Service Worker) - API mocking
- ts-jest - TypeScript support

**Backend:**
- pytest - Test runner
- pytest-asyncio - Async test support
- httpx - HTTP client for testing
- pytest-cov - Coverage reporting

---

## Testing Strategy

### Test Pyramid

```
        /\
       /  \
      / E2E \          10% - Critical user flows
     /______\
    /        \
   /   INT    \        30% - API & service integration
  /____________\
 /              \
/     UNIT       \     60% - Component & function logic
/__________________\
```

### Coverage Goals

- **Unit Tests**: 70%+ coverage
- **Integration Tests**: 80%+ coverage of API endpoints
- **E2E Tests**: 100% coverage of critical user flows

### Critical User Flows (E2E)

1. **Authentication Flow**
   - User login/logout
   - Token refresh
   - Permission handling

2. **Chat Interaction**
   - Send message and receive response
   - Streaming responses
   - Message history management

3. **Document Management**
   - Upload document
   - OCR processing
   - Document search and retrieval

4. **Voice Features**
   - Record audio
   - Transcribe speech-to-text
   - Text-to-speech synthesis
   - Use transcription in chat

5. **Banking Operations**
   - View account balance
   - Transaction history
   - Spending analytics

---

## Test Setup

### Prerequisites

```bash
# Install Node.js 20.x
node --version  # v20.x.x

# Install dependencies
cd frontend
npm install --legacy-peer-deps

# Install Playwright browsers
npx playwright install
```

### Environment Variables

Create `.env.test` in the frontend directory:

```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000

# Test Configuration
NODE_ENV=test
CI=false

# Optional: Test credentials
TEST_EMAIL=test@example.com
TEST_PASSWORD=password
```

### Configuration Files

**Jest Configuration** (`jest.config.ts`)
- Located at: `frontend/jest.config.ts`
- Setup file: `frontend/tests/setup.ts`
- Coverage thresholds: 70% for all metrics

**Playwright Configuration** (`playwright.config.ts`)
- Located at: `frontend/playwright.config.ts`
- Test directory: `frontend/tests/e2e/`
- Multiple browser support (Chrome, Firefox, Safari)

---

## Unit Testing

### Running Unit Tests

```bash
# Run all unit tests
npm test

# Run in watch mode
npm run test:watch

# Run with coverage
npm run test:coverage

# Run specific test file
npm test -- useVoice.test.ts

# Run tests matching pattern
npm test -- --testNamePattern="Voice"
```

### Writing Unit Tests

#### Component Testing

```typescript
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { renderWithProviders } from '../utils/test-utils';
import MyComponent from '@/components/MyComponent';

describe('MyComponent', () => {
  const user = userEvent.setup();

  it('should render correctly', () => {
    renderWithProviders(<MyComponent />);
    
    expect(screen.getByText('Expected Text')).toBeInTheDocument();
  });

  it('should handle user interaction', async () => {
    renderWithProviders(<MyComponent />);
    
    const button = screen.getByRole('button', { name: /click me/i });
    await user.click(button);
    
    await waitFor(() => {
      expect(screen.getByText('Result')).toBeVisible();
    });
  });
});
```

#### Hook Testing

```typescript
import { renderHook, act, waitFor } from '@testing-library/react';
import { useMyHook } from '@/hooks/useMyHook';

describe('useMyHook', () => {
  it('should initialize with default state', () => {
    const { result } = renderHook(() => useMyHook());
    
    expect(result.current.value).toBe(initialValue);
  });

  it('should update state on action', async () => {
    const { result } = renderHook(() => useMyHook());
    
    await act(async () => {
      await result.current.updateValue('new value');
    });
    
    expect(result.current.value).toBe('new value');
  });
});
```

#### API Mocking with MSW

```typescript
import { server } from '../mocks/server';
import { http, HttpResponse } from 'msw';
import { setupMockServer } from '../mocks/server';

setupMockServer();

describe('API Tests', () => {
  it('should handle successful API call', async () => {
    server.use(
      http.get('/api/data', () => {
        return HttpResponse.json({ data: 'mock data' });
      })
    );

    // Test implementation
  });

  it('should handle API error', async () => {
    server.use(
      http.get('/api/data', () => {
        return HttpResponse.json(
          { message: 'Error' },
          { status: 500 }
        );
      })
    );

    // Test error handling
  });
});
```

### Test Utilities

Located at: `frontend/tests/utils/test-utils.tsx`

**Available Utilities:**
- `renderWithProviders()` - Render with all providers
- `setupUserEvent()` - Setup user interaction
- `mockFetch()` - Mock fetch API
- `mockLocalStorage()` - Mock localStorage
- `createMockFile()` - Create mock File object
- `mockMediaRecorder()` - Mock MediaRecorder for voice tests
- `mockWebSocket()` - Mock WebSocket connections

**Mock Factories:**
- `mockUser` - Mock user object
- `mockAccount` - Mock bank account
- `mockTransaction` - Mock transaction
- `mockDocument` - Mock document
- `mockChatMessage` - Mock chat message

---

## Integration Testing

### Running Integration Tests

```bash
# Run integration tests
npm test -- tests/integration

# Run with coverage
npm test -- tests/integration --coverage

# Run specific integration test
npm test -- chat.test.tsx
```

### Writing Integration Tests

```typescript
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { renderWithProviders } from '../utils/test-utils';
import { setupMockServer } from '../mocks/server';
import { server } from '../mocks/server';
import { http, HttpResponse } from 'msw';

setupMockServer();

describe('Feature Integration Tests', () => {
  beforeEach(() => {
    // Reset mocks before each test
    localStorage.clear();
  });

  it('should complete full user flow', async () => {
    const user = userEvent.setup();

    // Setup API mock
    server.use(
      http.post('/api/action', async ({ request }) => {
        const body = await request.json();
        return HttpResponse.json({ success: true, data: body });
      })
    );

    // Render component
    renderWithProviders(<FeatureComponent />);

    // Interact with UI
    await user.type(screen.getByRole('textbox'), 'Test input');
    await user.click(screen.getByRole('button', { name: /submit/i }));

    // Verify results
    await waitFor(() => {
      expect(screen.getByText('Success')).toBeVisible();
    });
  });
});
```

### Testing Streaming Responses

```typescript
it('should handle streaming chat responses', async () => {
  server.use(
    http.post('/chat/stream', async () => {
      const encoder = new TextEncoder();
      const stream = new ReadableStream({
        start(controller) {
          controller.enqueue(encoder.encode('data: {"content":"Hello"}\n\n'));
          controller.enqueue(encoder.encode('data: {"content":" world"}\n\n'));
          controller.enqueue(encoder.encode('data: [DONE]\n\n'));
          controller.close();
        },
      });

      return new Response(stream, {
        headers: { 'Content-Type': 'text/event-stream' },
      });
    })
  );

  // Test streaming implementation
});
```

---

## End-to-End Testing

### Running E2E Tests

```bash
# Run all E2E tests
npm run test:e2e

# Run in UI mode (interactive)
npm run test:e2e:ui

# Run specific test file
npx playwright test chat-flow.spec.ts

# Run in headed mode (see browser)
npx playwright test --headed

# Run on specific browser
npx playwright test --project=chromium
npx playwright test --project=firefox
npx playwright test --project=webkit

# Debug mode
npx playwright test --debug
```

### Writing E2E Tests

```typescript
import { test, expect } from '@playwright/test';

test.describe('Feature E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000');
  });

  test('should complete user flow', async ({ page }) => {
    // Navigate
    await page.click('text=Feature');

    // Fill form
    await page.fill('[data-testid="input"]', 'Test data');
    
    // Submit
    await page.click('[data-testid="submit-button"]');

    // Verify result
    await expect(page.locator('[data-testid="result"]')).toBeVisible({
      timeout: 10000,
    });

    // Take screenshot
    await page.screenshot({ path: 'test-result.png' });
  });

  test('should handle errors gracefully', async ({ page }) => {
    // Trigger error condition
    await page.click('[data-testid="error-trigger"]');

    // Verify error message
    await expect(page.locator('text=/error/i')).toBeVisible();
  });
});
```

### Mobile Testing

```typescript
test('should work on mobile', async ({ page }) => {
  // Set mobile viewport
  await page.setViewportSize({ width: 375, height: 667 });

  await page.goto('http://localhost:3000');

  // Test mobile-specific features
  await expect(page.locator('[data-testid="mobile-nav"]')).toBeVisible();
});
```

### Testing with Authentication

```typescript
test.describe('Authenticated Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Login
    await page.goto('http://localhost:3000/login');
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'password');
    await page.click('button[type="submit"]');
    await page.waitForURL('http://localhost:3000/dashboard');
  });

  test('should access protected route', async ({ page }) => {
    await page.click('text=Protected Feature');
    await expect(page).toHaveURL(/protected/);
  });
});
```

---

## Test Coverage

### Viewing Coverage Reports

```bash
# Generate coverage report
npm run test:coverage

# Open HTML report
open coverage/lcov-report/index.html  # macOS
xdg-open coverage/lcov-report/index.html  # Linux
start coverage/lcov-report/index.html  # Windows
```

### Coverage Thresholds

Configured in `jest.config.ts`:

```typescript
coverageThresholds: {
  global: {
    branches: 70,
    functions: 70,
    lines: 70,
    statements: 70,
  },
}
```

### Excluding Files from Coverage

Files excluded from coverage:
- `*.d.ts` - Type definitions
- `*.stories.tsx` - Storybook stories
- `__tests__/**` - Test files
- `src/types/**` - Type definitions
- `src/config/**` - Configuration files
- `src/app/**` - Next.js app directory routes

---

## CI/CD Pipeline

### GitHub Actions Workflow

Location: `.github/workflows/ci.yml`

**Pipeline Stages:**

1. **Frontend Tests**
   - Type checking (TypeScript)
   - Linting (ESLint)
   - Unit tests with coverage
   - E2E tests with Playwright
   - Build verification

2. **Backend Tests**
   - Linting (Ruff)
   - Type checking (mypy)
   - Unit tests with pytest
   - Coverage reporting

3. **Security Scanning**
   - Trivy vulnerability scanner
   - npm audit (frontend)
   - pip safety check (backend)

4. **Docker Build**
   - Frontend image build
   - Backend image build
   - Layer caching

5. **Integration Tests**
   - Full stack with Docker Compose
   - Health checks
   - API integration tests

6. **Deployment** (on main branch)
   - Build and push to ECR
   - Deploy to ECS staging
   - Smoke tests

### Running CI Locally

```bash
# Install act (GitHub Actions local runner)
brew install act  # macOS
# or download from: https://github.com/nektos/act

# Run entire workflow
act

# Run specific job
act -j frontend-test

# Run with secrets
act -s GITHUB_TOKEN=xxx
```

### CI Environment Variables

Required secrets in GitHub:
- `AWS_ACCESS_KEY_ID` - AWS credentials
- `AWS_SECRET_ACCESS_KEY` - AWS credentials
- `SONAR_TOKEN` - SonarCloud token
- `SLACK_WEBHOOK` - Slack notifications
- `CODECOV_TOKEN` - Codecov integration

---

## Best Practices

### 1. Test Naming

```typescript
// ✅ Good: Descriptive test names
it('should display error when API returns 500', async () => {});
it('should transcribe audio and fill chat input', async () => {});

// ❌ Bad: Vague test names
it('works correctly', async () => {});
it('test API', async () => {});
```

### 2. Arrange-Act-Assert Pattern

```typescript
it('should update state on button click', async () => {
  // Arrange
  renderWithProviders(<Component />);
  const user = userEvent.setup();
  
  // Act
  await user.click(screen.getByRole('button'));
  
  // Assert
  expect(screen.getByText('Updated')).toBeVisible();
});
```

### 3. Use Data Test IDs

```typescript
// Component
<button data-testid="submit-button">Submit</button>

// Test
await page.click('[data-testid="submit-button"]');
```

### 4. Avoid Test Interdependence

```typescript
// ✅ Good: Each test is independent
beforeEach(() => {
  localStorage.clear();
  server.resetHandlers();
});

// ❌ Bad: Tests depend on each other
test('test 1', () => { globalState = 'value'; });
test('test 2', () => { expect(globalState).toBe('value'); });
```

### 5. Mock External Dependencies

```typescript
// Mock API calls
server.use(http.get('/api/data', () => HttpResponse.json(mockData)));

// Mock timers
jest.useFakeTimers();
jest.advanceTimersByTime(1000);
jest.useRealTimers();

// Mock modules
jest.mock('@/lib/api', () => ({
  fetchData: jest.fn(() => Promise.resolve(mockData)),
}));
```

### 6. Clean Up After Tests

```typescript
afterEach(() => {
  jest.clearAllMocks();
  localStorage.clear();
  sessionStorage.clear();
});

afterAll(() => {
  server.close();
});
```

### 7. Test Error Boundaries

```typescript
it('should handle errors gracefully', async () => {
  // Trigger error
  server.use(
    http.get('/api/data', () => HttpResponse.error())
  );

  renderWithProviders(<Component />);

  // Verify error handling
  await expect(screen.findByText(/error/i)).resolves.toBeVisible();
});
```

### 8. Accessibility Testing

```typescript
import { axe, toHaveNoViolations } from 'jest-axe';

expect.extend(toHaveNoViolations);

it('should have no accessibility violations', async () => {
  const { container } = renderWithProviders(<Component />);
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});
```

---

## Troubleshooting

### Common Issues

#### 1. Tests Timeout

```typescript
// Increase timeout for specific test
it('slow test', async () => {
  // test code
}, 30000); // 30 seconds

// Or globally in jest.config.ts
testTimeout: 10000,
```

#### 2. Flaky Tests

```bash
# Run test multiple times to identify flakiness
npm test -- --testNamePattern="flaky test" --runInBand --repeat=10
```

```typescript
// Use waitFor for async assertions
await waitFor(() => {
  expect(screen.getByText('Loaded')).toBeVisible();
}, { timeout: 5000 });
```

#### 3. MSW Not Intercepting Requests

```typescript
// Ensure server is started in setup.ts
import { setupMockServer } from './mocks/server';
setupMockServer();

// Check handlers match the exact URL
server.use(
  http.get('http://localhost:8000/api/data', () => {
    return HttpResponse.json({ data: 'mock' });
  })
);
```

#### 4. Playwright Tests Failing

```bash
# Update browsers
npx playwright install

# Run in debug mode
npx playwright test --debug

# Check screenshots/videos
npx playwright show-report
```

#### 5. Memory Leaks in Tests

```typescript
// Clean up in afterEach
afterEach(() => {
  cleanup(); // React Testing Library cleanup
  jest.clearAllTimers();
  jest.restoreAllMocks();
});
```

### Debugging Tips

**Jest Debugging:**
```bash
# Run with Node debugger
node --inspect-brk node_modules/.bin/jest --runInBand

# Use VSCode debugger
# Add to .vscode/launch.json:
{
  "type": "node",
  "request": "launch",
  "name": "Jest Debug",
  "program": "${workspaceFolder}/node_modules/.bin/jest",
  "args": ["--runInBand"],
  "console": "integratedTerminal"
}
```

**Playwright Debugging:**
```bash
# Debug specific test
npx playwright test --debug chat-flow.spec.ts

# Headed mode with slow motion
npx playwright test --headed --slow-mo=1000

# Trace viewer
npx playwright test --trace on
npx playwright show-trace trace.zip
```

---

## Quick Reference

### Test Commands

```bash
# Frontend
npm test                 # Run unit tests
npm run test:watch       # Watch mode
npm run test:coverage    # With coverage
npm run test:e2e         # E2E tests
npm run test:e2e:ui      # E2E with UI

# Backend
pytest                   # Run all tests
pytest -v                # Verbose
pytest --cov=app         # With coverage
pytest -k "test_name"    # Specific test
pytest -m "integration"  # By marker
```

### File Structure

```
frontend/
├── tests/
│   ├── setup.ts                 # Jest setup
│   ├── utils/
│   │   └── test-utils.tsx       # Test utilities
│   ├── mocks/
│   │   ├── handlers.ts          # MSW handlers
│   │   └── server.ts            # MSW server
│   ├── unit/
│   │   └── *.test.ts(x)        # Unit tests
│   ├── integration/
│   │   └── *.test.ts(x)        # Integration tests
│   └── e2e/
│       └── *.spec.ts            # E2E tests
├── jest.config.ts               # Jest config
└── playwright.config.ts         # Playwright config
```

---

## Additional Resources

- [Jest Documentation](https://jestjs.io/)
- [React Testing Library](https://testing-library.com/react)
- [Playwright Documentation](https://playwright.dev/)
- [MSW Documentation](https://mswjs.io/)
- [Testing Best Practices](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library)

---

**Last Updated**: 2025-01-17  
**Maintained By**: IOB MAIIS Team