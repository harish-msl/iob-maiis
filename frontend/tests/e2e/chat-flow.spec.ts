/**
 * E2E Tests for Chat Flow
 *
 * Tests critical user flows:
 * - User login and authentication
 * - Chat interaction with streaming responses
 * - Document upload and OCR processing
 * - Voice recording and transcription
 * - Banking data queries
 */

import { test, expect, Page } from '@playwright/test';

const BASE_URL = process.env.BASE_URL || 'http://localhost:3000';
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

test.describe('Chat Flow E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the app
    await page.goto(BASE_URL);
  });

  test.describe('Authentication Flow', () => {
    test('should allow user to login', async ({ page }) => {
      // Navigate to login page
      await page.goto(`${BASE_URL}/login`);

      // Fill in credentials
      await page.fill('input[name="email"]', 'test@example.com');
      await page.fill('input[name="password"]', 'password');

      // Click login button
      await page.click('button[type="submit"]');

      // Wait for navigation to dashboard
      await page.waitForURL(`${BASE_URL}/dashboard`);

      // Verify user is logged in
      await expect(page.locator('text=Dashboard')).toBeVisible();
    });

    test('should show error on invalid credentials', async ({ page }) => {
      await page.goto(`${BASE_URL}/login`);

      await page.fill('input[name="email"]', 'wrong@example.com');
      await page.fill('input[name="password"]', 'wrongpassword');
      await page.click('button[type="submit"]');

      // Verify error message appears
      await expect(page.locator('text=/invalid credentials/i')).toBeVisible();
    });

    test('should allow user to logout', async ({ page }) => {
      // Login first
      await page.goto(`${BASE_URL}/login`);
      await page.fill('input[name="email"]', 'test@example.com');
      await page.fill('input[name="password"]', 'password');
      await page.click('button[type="submit"]');
      await page.waitForURL(`${BASE_URL}/dashboard`);

      // Click logout
      await page.click('[data-testid="user-menu"]');
      await page.click('text=Logout');

      // Verify redirected to login
      await page.waitForURL(`${BASE_URL}/login`);
    });
  });

  test.describe('Chat Interaction', () => {
    test.beforeEach(async ({ page }) => {
      // Login before each chat test
      await page.goto(`${BASE_URL}/login`);
      await page.fill('input[name="email"]', 'test@example.com');
      await page.fill('input[name="password"]', 'password');
      await page.click('button[type="submit"]');
      await page.waitForURL(`${BASE_URL}/dashboard`);

      // Navigate to chat
      await page.click('text=Chat');
      await page.waitForURL(`${BASE_URL}/chat`);
    });

    test('should send a message and receive response', async ({ page }) => {
      const message = 'What is my account balance?';

      // Type message
      await page.fill('[data-testid="chat-input"]', message);

      // Send message
      await page.click('[data-testid="send-button"]');

      // Verify user message appears
      await expect(page.locator(`text=${message}`)).toBeVisible();

      // Wait for assistant response
      await expect(page.locator('[data-testid="assistant-message"]').last()).toBeVisible({
        timeout: 10000,
      });

      // Verify response is not empty
      const responseText = await page.locator('[data-testid="assistant-message"]').last().textContent();
      expect(responseText).toBeTruthy();
      expect(responseText!.length).toBeGreaterThan(0);
    });

    test('should handle streaming responses', async ({ page }) => {
      await page.fill('[data-testid="chat-input"]', 'Tell me about my transactions');
      await page.click('[data-testid="send-button"]');

      // Wait for streaming indicator
      await expect(page.locator('[data-testid="typing-indicator"]')).toBeVisible();

      // Wait for response to complete
      await expect(page.locator('[data-testid="typing-indicator"]')).not.toBeVisible({
        timeout: 15000,
      });

      // Verify message is displayed
      await expect(page.locator('[data-testid="assistant-message"]').last()).toBeVisible();
    });

    test('should display chat history', async ({ page }) => {
      // Send first message
      await page.fill('[data-testid="chat-input"]', 'Hello');
      await page.click('[data-testid="send-button"]');
      await page.waitForTimeout(2000);

      // Send second message
      await page.fill('[data-testid="chat-input"]', 'What accounts do I have?');
      await page.click('[data-testid="send-button"]');
      await page.waitForTimeout(2000);

      // Verify both messages are visible
      await expect(page.locator('text=Hello')).toBeVisible();
      await expect(page.locator('text=What accounts do I have?')).toBeVisible();

      // Verify multiple assistant responses
      const assistantMessages = await page.locator('[data-testid="assistant-message"]').count();
      expect(assistantMessages).toBeGreaterThanOrEqual(2);
    });

    test('should clear chat history', async ({ page }) => {
      // Send a message
      await page.fill('[data-testid="chat-input"]', 'Test message');
      await page.click('[data-testid="send-button"]');
      await page.waitForTimeout(2000);

      // Clear history
      await page.click('[data-testid="chat-menu"]');
      await page.click('text=Clear History');

      // Confirm dialog
      await page.click('button:has-text("Confirm")');

      // Verify messages are cleared
      await expect(page.locator('text=Test message')).not.toBeVisible();
    });

    test('should support keyboard shortcuts', async ({ page }) => {
      // Type message
      await page.fill('[data-testid="chat-input"]', 'Test message');

      // Press Enter to send
      await page.keyboard.press('Enter');

      // Verify message was sent
      await expect(page.locator('text=Test message')).toBeVisible();

      // Type multiline message with Shift+Enter
      await page.fill('[data-testid="chat-input"]', 'Line 1');
      await page.keyboard.press('Shift+Enter');
      await page.fill('[data-testid="chat-input"]', 'Line 1\nLine 2');

      // Verify multiline input
      const inputValue = await page.inputValue('[data-testid="chat-input"]');
      expect(inputValue).toContain('\n');
    });
  });

  test.describe('Document Upload and OCR', () => {
    test.beforeEach(async ({ page }) => {
      // Login and navigate to documents
      await page.goto(`${BASE_URL}/login`);
      await page.fill('input[name="email"]', 'test@example.com');
      await page.fill('input[name="password"]', 'password');
      await page.click('button[type="submit"]');
      await page.waitForURL(`${BASE_URL}/dashboard`);
      await page.click('text=Documents');
      await page.waitForURL(`${BASE_URL}/documents`);
    });

    test('should upload a document', async ({ page }) => {
      // Create a test file
      const fileContent = 'Test document content';
      const fileName = 'test-document.txt';

      // Upload file
      const fileInput = await page.locator('input[type="file"]');
      await fileInput.setInputFiles({
        name: fileName,
        mimeType: 'text/plain',
        buffer: Buffer.from(fileContent),
      });

      // Verify upload success message
      await expect(page.locator('text=/uploaded successfully/i')).toBeVisible({
        timeout: 10000,
      });

      // Verify document appears in list
      await expect(page.locator(`text=${fileName}`)).toBeVisible();
    });

    test('should process document with OCR', async ({ page }) => {
      // Upload a PDF (mock)
      const fileInput = await page.locator('input[type="file"]');
      await fileInput.setInputFiles({
        name: 'test.pdf',
        mimeType: 'application/pdf',
        buffer: Buffer.from('Mock PDF content'),
      });

      // Wait for upload
      await page.waitForTimeout(2000);

      // Click OCR button
      await page.click('[data-testid="ocr-button"]');

      // Wait for processing
      await expect(page.locator('text=/processing/i')).toBeVisible();
      await expect(page.locator('text=/processing/i')).not.toBeVisible({
        timeout: 15000,
      });

      // Verify extracted text is shown
      await expect(page.locator('[data-testid="extracted-text"]')).toBeVisible();
    });

    test('should use document in chat context', async ({ page }) => {
      // Upload document first
      const fileInput = await page.locator('input[type="file"]');
      await fileInput.setInputFiles({
        name: 'bank-statement.pdf',
        mimeType: 'application/pdf',
        buffer: Buffer.from('Mock bank statement'),
      });

      await page.waitForTimeout(2000);

      // Navigate to chat
      await page.click('text=Chat');
      await page.waitForURL(`${BASE_URL}/chat`);

      // Ask question about the document
      await page.fill('[data-testid="chat-input"]', 'What information is in my bank statement?');
      await page.click('[data-testid="send-button"]');

      // Wait for response
      await expect(page.locator('[data-testid="assistant-message"]').last()).toBeVisible({
        timeout: 10000,
      });

      // Verify source citation
      await expect(page.locator('[data-testid="source-document"]')).toBeVisible();
    });
  });

  test.describe('Voice Features', () => {
    test.beforeEach(async ({ page, context }) => {
      // Grant microphone permission
      await context.grantPermissions(['microphone']);

      // Login and navigate to chat
      await page.goto(`${BASE_URL}/login`);
      await page.fill('input[name="email"]', 'test@example.com');
      await page.fill('input[name="password"]', 'password');
      await page.click('button[type="submit"]');
      await page.waitForURL(`${BASE_URL}/dashboard`);
      await page.click('text=Chat');
    });

    test('should open voice recorder', async ({ page }) => {
      // Click microphone button
      await page.click('[data-testid="voice-button"]');

      // Verify voice modal opens
      await expect(page.locator('[data-testid="voice-modal"]')).toBeVisible();
      await expect(page.locator('[data-testid="record-button"]')).toBeVisible();
    });

    test('should record audio', async ({ page }) => {
      // Open voice recorder
      await page.click('[data-testid="voice-button"]');

      // Start recording
      await page.click('[data-testid="record-button"]');

      // Verify recording indicator
      await expect(page.locator('[data-testid="recording-indicator"]')).toBeVisible();

      // Wait for 2 seconds
      await page.waitForTimeout(2000);

      // Stop recording
      await page.click('[data-testid="stop-button"]');

      // Verify recording stopped
      await expect(page.locator('[data-testid="recording-indicator"]')).not.toBeVisible();
    });

    test('should transcribe recorded audio', async ({ page }) => {
      // Open voice recorder
      await page.click('[data-testid="voice-button"]');

      // Record and stop
      await page.click('[data-testid="record-button"]');
      await page.waitForTimeout(2000);
      await page.click('[data-testid="stop-button"]');

      // Click transcribe button
      await page.click('[data-testid="transcribe-button"]');

      // Wait for transcription
      await expect(page.locator('[data-testid="transcription-result"]')).toBeVisible({
        timeout: 10000,
      });

      // Verify transcribed text is not empty
      const transcription = await page.locator('[data-testid="transcription-result"]').textContent();
      expect(transcription).toBeTruthy();
    });

    test('should use transcription in chat', async ({ page }) => {
      // Open voice recorder
      await page.click('[data-testid="voice-button"]');

      // Record, stop, and transcribe
      await page.click('[data-testid="record-button"]');
      await page.waitForTimeout(2000);
      await page.click('[data-testid="stop-button"]');
      await page.click('[data-testid="transcribe-button"]');

      // Wait for transcription
      await page.waitForTimeout(3000);

      // Click "Use in Chat" button
      await page.click('[data-testid="use-transcription-button"]');

      // Verify text appears in chat input
      const inputValue = await page.inputValue('[data-testid="chat-input"]');
      expect(inputValue.length).toBeGreaterThan(0);

      // Close voice modal
      await page.click('[data-testid="close-voice-modal"]');

      // Send message
      await page.click('[data-testid="send-button"]');

      // Verify message sent
      await expect(page.locator('[data-testid="assistant-message"]')).toBeVisible({
        timeout: 10000,
      });
    });

    test('should test text-to-speech', async ({ page }) => {
      // Open voice controls
      await page.click('[data-testid="voice-button"]');

      // Go to TTS tab
      await page.click('text=Text-to-Speech');

      // Enter text
      await page.fill('[data-testid="tts-input"]', 'Hello, this is a test');

      // Click speak button
      await page.click('[data-testid="speak-button"]');

      // Verify speaking indicator
      await expect(page.locator('[data-testid="speaking-indicator"]')).toBeVisible();

      // Wait for speech to complete
      await expect(page.locator('[data-testid="speaking-indicator"]')).not.toBeVisible({
        timeout: 10000,
      });
    });
  });

  test.describe('Banking Queries', () => {
    test.beforeEach(async ({ page }) => {
      // Login
      await page.goto(`${BASE_URL}/login`);
      await page.fill('input[name="email"]', 'test@example.com');
      await page.fill('input[name="password"]', 'password');
      await page.click('button[type="submit"]');
      await page.waitForURL(`${BASE_URL}/dashboard`);
    });

    test('should query account balance', async ({ page }) => {
      // Navigate to chat
      await page.click('text=Chat');

      // Ask about balance
      await page.fill('[data-testid="chat-input"]', 'What is my account balance?');
      await page.click('[data-testid="send-button"]');

      // Wait for response
      await expect(page.locator('[data-testid="assistant-message"]').last()).toBeVisible({
        timeout: 10000,
      });

      // Verify response contains balance information
      const response = await page.locator('[data-testid="assistant-message"]').last().textContent();
      expect(response).toMatch(/\$|balance|account/i);
    });

    test('should view transaction history', async ({ page }) => {
      // Navigate to banking
      await page.click('text=Banking');

      // Click on transactions
      await page.click('text=Transactions');

      // Verify transactions table is visible
      await expect(page.locator('[data-testid="transactions-table"]')).toBeVisible();

      // Verify at least one transaction is shown
      const transactionCount = await page.locator('[data-testid="transaction-row"]').count();
      expect(transactionCount).toBeGreaterThan(0);
    });

    test('should filter transactions', async ({ page }) => {
      await page.click('text=Banking');
      await page.click('text=Transactions');

      // Open filter
      await page.click('[data-testid="filter-button"]');

      // Select category
      await page.selectOption('[data-testid="category-filter"]', 'shopping');

      // Apply filter
      await page.click('[data-testid="apply-filter"]');

      // Verify filtered results
      await page.waitForTimeout(1000);
      const transactions = await page.locator('[data-testid="transaction-row"]').all();

      for (const transaction of transactions) {
        const category = await transaction.getAttribute('data-category');
        expect(category).toBe('shopping');
      }
    });

    test('should view spending analytics', async ({ page }) => {
      await page.click('text=Banking');
      await page.click('text=Analytics');

      // Verify chart is visible
      await expect(page.locator('[data-testid="spending-chart"]')).toBeVisible();

      // Verify category breakdown
      await expect(page.locator('[data-testid="category-breakdown"]')).toBeVisible();
    });
  });

  test.describe('Error Handling', () => {
    test('should handle API errors gracefully', async ({ page }) => {
      // Login
      await page.goto(`${BASE_URL}/login`);
      await page.fill('input[name="email"]', 'test@example.com');
      await page.fill('input[name="password"]', 'password');
      await page.click('button[type="submit"]');
      await page.waitForURL(`${BASE_URL}/dashboard`);

      // Navigate to chat
      await page.click('text=Chat');

      // Simulate API error by sending to error endpoint (if implemented)
      await page.fill('[data-testid="chat-input"]', '/error/500');
      await page.click('[data-testid="send-button"]');

      // Verify error message is shown
      await expect(page.locator('text=/error|failed/i')).toBeVisible({
        timeout: 10000,
      });
    });

    test('should handle network errors', async ({ page, context }) => {
      // Login first
      await page.goto(`${BASE_URL}/login`);
      await page.fill('input[name="email"]', 'test@example.com');
      await page.fill('input[name="password"]', 'password');
      await page.click('button[type="submit"]');
      await page.waitForURL(`${BASE_URL}/dashboard`);

      // Go offline
      await context.setOffline(true);

      // Try to send a message
      await page.click('text=Chat');
      await page.fill('[data-testid="chat-input"]', 'Test message');
      await page.click('[data-testid="send-button"]');

      // Verify offline error message
      await expect(page.locator('text=/network|offline|connection/i')).toBeVisible();

      // Go back online
      await context.setOffline(false);
    });
  });

  test.describe('Responsive Design', () => {
    test('should work on mobile viewport', async ({ page }) => {
      // Set mobile viewport
      await page.setViewportSize({ width: 375, height: 667 });

      await page.goto(`${BASE_URL}/login`);
      await page.fill('input[name="email"]', 'test@example.com');
      await page.fill('input[name="password"]', 'password');
      await page.click('button[type="submit"]');

      // Verify mobile layout
      await expect(page.locator('[data-testid="mobile-nav"]')).toBeVisible();

      // Test mobile navigation
      await page.click('[data-testid="mobile-menu-button"]');
      await expect(page.locator('[data-testid="mobile-menu"]')).toBeVisible();
    });

    test('should work on tablet viewport', async ({ page }) => {
      // Set tablet viewport
      await page.setViewportSize({ width: 768, height: 1024 });

      await page.goto(`${BASE_URL}/login`);
      await page.fill('input[name="email"]', 'test@example.com');
      await page.fill('input[name="password"]', 'password');
      await page.click('button[type="submit"]');

      // Verify tablet layout works
      await expect(page.locator('text=Dashboard')).toBeVisible();
    });
  });
});
