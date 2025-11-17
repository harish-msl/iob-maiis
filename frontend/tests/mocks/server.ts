/**
 * MSW Server Setup
 *
 * Configures Mock Service Worker for testing
 * - Node.js server for Jest tests
 * - Browser server for Playwright tests
 */

import { setupServer } from 'msw/node';
import { handlers } from './handlers';

/**
 * Setup MSW server with default handlers
 */
export const server = setupServer(...handlers);

/**
 * Start server before all tests
 */
export function setupMockServer() {
  // Start server before all tests
  beforeAll(() => {
    server.listen({
      onUnhandledRequest: 'warn',
    });
  });

  // Reset handlers after each test
  afterEach(() => {
    server.resetHandlers();
  });

  // Clean up after all tests
  afterAll(() => {
    server.close();
  });
}

/**
 * Re-export server for custom test setup
 */
export default server;
