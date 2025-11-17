/**
 * Test Utilities
 *
 * Provides custom render functions and test helpers for:
 * - React Testing Library with providers
 * - Mock factories for common data structures
 * - Test helpers for async operations
 * - Custom matchers and assertions
 */

import React, { ReactElement } from 'react';
import { render, RenderOptions, RenderResult } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

/**
 * All Providers Wrapper
 * Wraps components with all necessary providers for testing
 */
interface AllProvidersProps {
  children: React.ReactNode;
}

const AllProviders: React.FC<AllProvidersProps> = ({ children }) => {
  return <>{children}</>;
};

/**
 * Custom render function with all providers
 */
interface CustomRenderOptions extends Omit<RenderOptions, 'wrapper'> {
  route?: string;
}

export function renderWithProviders(
  ui: ReactElement,
  options?: CustomRenderOptions
): RenderResult {
  const { route = '/', ...renderOptions } = options || {};

  // Mock router if route is provided
  if (route !== '/') {
    window.history.pushState({}, 'Test page', route);
  }

  return render(ui, {
    wrapper: AllProviders,
    ...renderOptions,
  });
}

/**
 * Setup user event for interactions
 */
export function setupUserEvent() {
  return userEvent.setup();
}

/**
 * Mock Factories
 */

export const mockUser = {
  id: 'user-123',
  email: 'test@example.com',
  name: 'Test User',
  role: 'customer',
  createdAt: '2024-01-01T00:00:00Z',
};

export const mockAccount = {
  id: 'acc-123',
  accountNumber: '1234567890',
  accountType: 'checking',
  balance: 5000.0,
  currency: 'USD',
  status: 'active',
  createdAt: '2024-01-01T00:00:00Z',
};

export const mockTransaction = {
  id: 'txn-123',
  accountId: 'acc-123',
  type: 'debit',
  amount: 100.0,
  currency: 'USD',
  description: 'Test transaction',
  status: 'completed',
  createdAt: '2024-01-15T10:00:00Z',
  category: 'shopping',
};

export const mockDocument = {
  id: 'doc-123',
  filename: 'test-document.pdf',
  fileType: 'application/pdf',
  fileSize: 1024000,
  uploadedAt: '2024-01-15T10:00:00Z',
  status: 'processed',
  pageCount: 5,
  extractedText: 'Sample extracted text',
  metadata: {
    author: 'Test Author',
    title: 'Test Document',
  },
};

export const mockChatMessage = {
  id: 'msg-123',
  role: 'user' as const,
  content: 'What is my account balance?',
  timestamp: '2024-01-15T10:00:00Z',
  metadata: {},
};

export const mockChatResponse = {
  id: 'msg-124',
  role: 'assistant' as const,
  content: 'Your current account balance is $5,000.00.',
  timestamp: '2024-01-15T10:00:01Z',
  metadata: {
    sources: ['account-data'],
    confidence: 0.95,
  },
};

/**
 * Mock API Response Helpers
 */

export function mockApiSuccess<T>(data: T, delay = 0) {
  return new Promise<T>((resolve) => {
    setTimeout(() => resolve(data), delay);
  });
}

export function mockApiError(message: string, status = 500, delay = 0) {
  return new Promise((_, reject) => {
    setTimeout(() => {
      reject({
        response: {
          status,
          data: { message },
        },
      });
    }, delay);
  });
}

/**
 * Wait Helpers
 */

export function wait(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export async function waitForMs(ms: number): Promise<void> {
  await wait(ms);
}

/**
 * Local Storage Mock Helpers
 */

export function mockLocalStorage(data: Record<string, string> = {}) {
  const store: Record<string, string> = { ...data };

  const mock = {
    getItem: jest.fn((key: string) => store[key] || null),
    setItem: jest.fn((key: string, value: string) => {
      store[key] = value;
    }),
    removeItem: jest.fn((key: string) => {
      delete store[key];
    }),
    clear: jest.fn(() => {
      Object.keys(store).forEach((key) => delete store[key]);
    }),
  };

  Object.defineProperty(window, 'localStorage', {
    value: mock,
    writable: true,
  });

  return mock;
}

/**
 * Fetch Mock Helpers
 */

export function mockFetch(response: any, options: { status?: number; ok?: boolean } = {}) {
  const { status = 200, ok = true } = options;

  global.fetch = jest.fn(() =>
    Promise.resolve({
      ok,
      status,
      json: () => Promise.resolve(response),
      text: () => Promise.resolve(JSON.stringify(response)),
      blob: () => Promise.resolve(new Blob([JSON.stringify(response)])),
      headers: new Headers(),
    } as Response)
  );

  return global.fetch as jest.Mock;
}

export function mockFetchError(message: string, status = 500) {
  global.fetch = jest.fn(() =>
    Promise.resolve({
      ok: false,
      status,
      statusText: message,
      json: () => Promise.reject(new Error(message)),
      text: () => Promise.reject(new Error(message)),
      headers: new Headers(),
    } as Response)
  );

  return global.fetch as jest.Mock;
}

/**
 * File Mock Helpers
 */

export function createMockFile(
  name: string,
  size: number,
  type: string,
  content: string = ''
): File {
  const blob = new Blob([content], { type });
  const file = new File([blob], name, { type });
  Object.defineProperty(file, 'size', { value: size });
  return file;
}

export function createMockFileList(files: File[]): FileList {
  const fileList = {
    length: files.length,
    item: (index: number) => files[index] || null,
    [Symbol.iterator]: function* () {
      for (const file of files) {
        yield file;
      }
    },
  };

  // Add indexed properties
  files.forEach((file, index) => {
    Object.defineProperty(fileList, index, {
      value: file,
      enumerable: true,
    });
  });

  return fileList as FileList;
}

/**
 * Audio Mock Helpers (for voice tests)
 */

export function createMockAudioBlob(durationMs = 1000): Blob {
  const arrayBuffer = new ArrayBuffer(durationMs * 44.1); // Mock audio data
  return new Blob([arrayBuffer], { type: 'audio/webm' });
}

export function mockMediaRecorder(options: {
  onDataAvailable?: (event: { data: Blob }) => void;
  onStop?: () => void;
} = {}) {
  const { onDataAvailable, onStop } = options;

  const recorder = {
    start: jest.fn(),
    stop: jest.fn(() => {
      if (onDataAvailable) {
        onDataAvailable({ data: createMockAudioBlob() });
      }
      if (onStop) {
        onStop();
      }
    }),
    pause: jest.fn(),
    resume: jest.fn(),
    state: 'inactive',
    ondataavailable: onDataAvailable || null,
    onstop: onStop || null,
    onerror: null,
  };

  (global.MediaRecorder as any) = jest.fn(() => recorder);
  (global.MediaRecorder as any).isTypeSupported = jest.fn(() => true);

  return recorder;
}

/**
 * WebSocket Mock Helpers
 */

export function mockWebSocket() {
  const listeners: Record<string, Function[]> = {};

  const ws = {
    send: jest.fn(),
    close: jest.fn(),
    addEventListener: jest.fn((event: string, handler: Function) => {
      if (!listeners[event]) {
        listeners[event] = [];
      }
      listeners[event].push(handler);
    }),
    removeEventListener: jest.fn((event: string, handler: Function) => {
      if (listeners[event]) {
        listeners[event] = listeners[event].filter((h) => h !== handler);
      }
    }),
    readyState: 1, // OPEN
    trigger: (event: string, data?: any) => {
      if (listeners[event]) {
        listeners[event].forEach((handler) => handler(data));
      }
    },
  };

  (global.WebSocket as any) = jest.fn(() => ws);

  return ws;
}

/**
 * Assertion Helpers
 */

export function expectToBeInDocument(element: HTMLElement | null) {
  expect(element).toBeInTheDocument();
}

export function expectNotToBeInDocument(element: HTMLElement | null) {
  expect(element).not.toBeInTheDocument();
}

export function expectToHaveTextContent(element: HTMLElement | null, text: string) {
  expect(element).toHaveTextContent(text);
}

/**
 * Re-export everything from React Testing Library
 */
export * from '@testing-library/react';
export { userEvent };

/**
 * Default export with custom render
 */
export default {
  render: renderWithProviders,
  setupUserEvent,
  mockUser,
  mockAccount,
  mockTransaction,
  mockDocument,
  mockChatMessage,
  mockChatResponse,
  mockApiSuccess,
  mockApiError,
  wait,
  waitForMs,
  mockLocalStorage,
  mockFetch,
  mockFetchError,
  createMockFile,
  createMockFileList,
  createMockAudioBlob,
  mockMediaRecorder,
  mockWebSocket,
};
