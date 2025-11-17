/**
 * MSW (Mock Service Worker) Handlers
 *
 * Defines mock API handlers for testing
 * - Authentication endpoints
 * - Chat/RAG endpoints
 * - Banking endpoints
 * - Document endpoints
 * - Voice endpoints
 */

import { http, HttpResponse } from 'msw';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Mock data
 */
const mockUser = {
  id: 'user-123',
  email: 'test@example.com',
  name: 'Test User',
  role: 'customer',
  createdAt: '2024-01-01T00:00:00Z',
};

const mockAccounts = [
  {
    id: 'acc-123',
    accountNumber: '1234567890',
    accountType: 'checking',
    balance: 5000.0,
    currency: 'USD',
    status: 'active',
    createdAt: '2024-01-01T00:00:00Z',
  },
  {
    id: 'acc-456',
    accountNumber: '0987654321',
    accountType: 'savings',
    balance: 15000.0,
    currency: 'USD',
    status: 'active',
    createdAt: '2024-01-01T00:00:00Z',
  },
];

const mockTransactions = [
  {
    id: 'txn-123',
    accountId: 'acc-123',
    type: 'debit',
    amount: 100.0,
    currency: 'USD',
    description: 'Grocery Store',
    status: 'completed',
    createdAt: '2024-01-15T10:00:00Z',
    category: 'shopping',
  },
  {
    id: 'txn-456',
    accountId: 'acc-123',
    type: 'credit',
    amount: 2000.0,
    currency: 'USD',
    description: 'Salary Deposit',
    status: 'completed',
    createdAt: '2024-01-01T09:00:00Z',
    category: 'income',
  },
];

const mockDocuments = [
  {
    id: 'doc-123',
    filename: 'test-document.pdf',
    fileType: 'application/pdf',
    fileSize: 1024000,
    uploadedAt: '2024-01-15T10:00:00Z',
    status: 'processed',
    pageCount: 5,
    extractedText: 'Sample extracted text from document',
    metadata: {
      author: 'Test Author',
      title: 'Test Document',
    },
  },
];

/**
 * API Handlers
 */
export const handlers = [
  // Health check
  http.get(`${API_URL}/health`, () => {
    return HttpResponse.json({
      status: 'healthy',
      timestamp: new Date().toISOString(),
      services: {
        database: 'healthy',
        redis: 'healthy',
        vector_db: 'healthy',
        llm: 'healthy',
      },
    });
  }),

  // Authentication
  http.post(`${API_URL}/auth/login`, async ({ request }) => {
    const body = await request.json() as any;

    if (body.email === 'test@example.com' && body.password === 'password') {
      return HttpResponse.json({
        user: mockUser,
        token: 'mock-jwt-token',
        expiresIn: 3600,
      });
    }

    return HttpResponse.json(
      { message: 'Invalid credentials' },
      { status: 401 }
    );
  }),

  http.post(`${API_URL}/auth/register`, async ({ request }) => {
    const body = await request.json() as any;

    return HttpResponse.json({
      user: {
        ...mockUser,
        email: body.email,
        name: body.name,
      },
      token: 'mock-jwt-token',
      expiresIn: 3600,
    }, { status: 201 });
  }),

  http.post(`${API_URL}/auth/logout`, () => {
    return HttpResponse.json({ message: 'Logged out successfully' });
  }),

  http.get(`${API_URL}/auth/me`, () => {
    return HttpResponse.json(mockUser);
  }),

  // Chat/RAG
  http.post(`${API_URL}/chat/message`, async ({ request }) => {
    const body = await request.json() as any;

    return HttpResponse.json({
      id: `msg-${Date.now()}`,
      role: 'assistant',
      content: `Mock response to: ${body.message}`,
      timestamp: new Date().toISOString(),
      metadata: {
        sources: ['mock-source'],
        confidence: 0.95,
      },
    });
  }),

  http.get(`${API_URL}/chat/history`, () => {
    return HttpResponse.json({
      messages: [
        {
          id: 'msg-1',
          role: 'user',
          content: 'Hello',
          timestamp: '2024-01-15T10:00:00Z',
        },
        {
          id: 'msg-2',
          role: 'assistant',
          content: 'Hi! How can I help you today?',
          timestamp: '2024-01-15T10:00:01Z',
        },
      ],
      total: 2,
    });
  }),

  http.delete(`${API_URL}/chat/history`, () => {
    return HttpResponse.json({ message: 'Chat history cleared' });
  }),

  // Banking - Accounts
  http.get(`${API_URL}/banking/accounts`, () => {
    return HttpResponse.json({
      accounts: mockAccounts,
      total: mockAccounts.length,
    });
  }),

  http.get(`${API_URL}/banking/accounts/:id`, ({ params }) => {
    const account = mockAccounts.find((a) => a.id === params.id);

    if (!account) {
      return HttpResponse.json(
        { message: 'Account not found' },
        { status: 404 }
      );
    }

    return HttpResponse.json(account);
  }),

  // Banking - Transactions
  http.get(`${API_URL}/banking/transactions`, ({ request }) => {
    const url = new URL(request.url);
    const accountId = url.searchParams.get('accountId');

    let transactions = mockTransactions;
    if (accountId) {
      transactions = mockTransactions.filter((t) => t.accountId === accountId);
    }

    return HttpResponse.json({
      transactions,
      total: transactions.length,
    });
  }),

  http.get(`${API_URL}/banking/transactions/:id`, ({ params }) => {
    const transaction = mockTransactions.find((t) => t.id === params.id);

    if (!transaction) {
      return HttpResponse.json(
        { message: 'Transaction not found' },
        { status: 404 }
      );
    }

    return HttpResponse.json(transaction);
  }),

  // Banking - Analytics
  http.get(`${API_URL}/banking/analytics/spending`, () => {
    return HttpResponse.json({
      categories: [
        { category: 'shopping', amount: 1200.0, count: 15 },
        { category: 'dining', amount: 450.0, count: 8 },
        { category: 'utilities', amount: 350.0, count: 3 },
        { category: 'transportation', amount: 200.0, count: 12 },
      ],
      total: 2200.0,
      period: {
        start: '2024-01-01',
        end: '2024-01-31',
      },
    });
  }),

  http.get(`${API_URL}/banking/analytics/income`, () => {
    return HttpResponse.json({
      sources: [
        { source: 'salary', amount: 5000.0, count: 2 },
        { source: 'freelance', amount: 1500.0, count: 3 },
      ],
      total: 6500.0,
      period: {
        start: '2024-01-01',
        end: '2024-01-31',
      },
    });
  }),

  // Documents
  http.get(`${API_URL}/documents`, () => {
    return HttpResponse.json({
      documents: mockDocuments,
      total: mockDocuments.length,
    });
  }),

  http.get(`${API_URL}/documents/:id`, ({ params }) => {
    const document = mockDocuments.find((d) => d.id === params.id);

    if (!document) {
      return HttpResponse.json(
        { message: 'Document not found' },
        { status: 404 }
      );
    }

    return HttpResponse.json(document);
  }),

  http.post(`${API_URL}/documents/upload`, async ({ request }) => {
    const formData = await request.formData();
    const file = formData.get('file') as File;

    return HttpResponse.json({
      id: `doc-${Date.now()}`,
      filename: file.name,
      fileType: file.type,
      fileSize: file.size,
      uploadedAt: new Date().toISOString(),
      status: 'processing',
    }, { status: 201 });
  }),

  http.delete(`${API_URL}/documents/:id`, ({ params }) => {
    return HttpResponse.json({
      message: `Document ${params.id} deleted successfully`,
    });
  }),

  http.post(`${API_URL}/documents/:id/ocr`, ({ params }) => {
    return HttpResponse.json({
      id: params.id,
      extractedText: 'Sample extracted text from OCR',
      confidence: 0.92,
      pageCount: 3,
    });
  }),

  // Voice
  http.post(`${API_URL}/voice/transcribe`, async ({ request }) => {
    const formData = await request.formData();
    const audioFile = formData.get('audio') as File;

    return HttpResponse.json({
      text: 'This is a mock transcription of the audio file',
      language: 'en',
      confidence: 0.95,
      duration: 5.2,
    });
  }),

  http.post(`${API_URL}/voice/transcribe-base64`, async ({ request }) => {
    const body = await request.json() as any;

    return HttpResponse.json({
      text: 'This is a mock transcription from base64 audio',
      language: body.language || 'en',
      confidence: 0.95,
      duration: 5.2,
    });
  }),

  http.post(`${API_URL}/voice/synthesize`, async ({ request }) => {
    const body = await request.json() as any;

    // Return mock base64 audio
    const mockAudioBase64 = 'UklGRiQAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQAAAAA=';

    return HttpResponse.json({
      audio: mockAudioBase64,
      format: 'mp3',
      duration: 2.5,
    });
  }),

  http.post(`${API_URL}/voice/synthesize-audio`, async ({ request }) => {
    const body = await request.json() as any;

    // Return mock audio blob
    const mockAudioBuffer = new ArrayBuffer(1024);
    const blob = new Blob([mockAudioBuffer], { type: 'audio/mp3' });

    return HttpResponse.arrayBuffer(await blob.arrayBuffer(), {
      headers: {
        'Content-Type': 'audio/mp3',
      },
    });
  }),

  http.get(`${API_URL}/voice/health`, () => {
    return HttpResponse.json({
      status: 'healthy',
      services: {
        stt: 'available',
        tts: 'available',
      },
    });
  }),

  // Search
  http.post(`${API_URL}/search`, async ({ request }) => {
    const body = await request.json() as any;

    return HttpResponse.json({
      results: [
        {
          id: 'result-1',
          content: `Result matching: ${body.query}`,
          score: 0.95,
          metadata: {
            source: 'document-1',
            type: 'text',
          },
        },
      ],
      total: 1,
    });
  }),
];

/**
 * Error handlers for testing error scenarios
 */
export const errorHandlers = [
  http.get(`${API_URL}/error/500`, () => {
    return HttpResponse.json(
      { message: 'Internal server error' },
      { status: 500 }
    );
  }),

  http.get(`${API_URL}/error/401`, () => {
    return HttpResponse.json(
      { message: 'Unauthorized' },
      { status: 401 }
    );
  }),

  http.get(`${API_URL}/error/404`, () => {
    return HttpResponse.json(
      { message: 'Not found' },
      { status: 404 }
    );
  }),

  http.get(`${API_URL}/error/network`, () => {
    return HttpResponse.error();
  }),
];

export default handlers;
