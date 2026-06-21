import { describe, it, expect, beforeEach, vi } from 'vitest';

// Mock localStorage
const localStorageMock = (() => {
  let store = {};
  return {
    getItem: vi.fn((key) => store[key] ?? null),
    setItem: vi.fn((key, value) => { store[key] = value; }),
    removeItem: vi.fn((key) => { delete store[key]; }),
    clear: vi.fn(() => { store = {}; }),
  };
})();

Object.defineProperty(globalThis, 'localStorage', { value: localStorageMock });

// Must import AFTER mocking localStorage
import api from './api';

describe('api module', () => {
  beforeEach(() => {
    localStorageMock.clear();
    vi.clearAllMocks();
  });

  it('creates an axios instance with correct baseURL', () => {
    expect(api.defaults.baseURL).toBeDefined();
    expect(api.defaults.headers['Content-Type']).toBe('application/json');
  });

  it('attaches Authorization header when access_token exists', async () => {
    localStorageMock.setItem('access_token', 'test-token-123');

    // Get the request interceptor and test it
    const interceptor = api.interceptors.request.handlers[0];
    const config = { headers: {} };
    const result = interceptor.fulfilled(config);

    expect(result.headers.Authorization).toBe('Bearer test-token-123');
  });

  it('does not attach Authorization header when no token', async () => {
    const interceptor = api.interceptors.request.handlers[0];
    const config = { headers: {} };
    const result = interceptor.fulfilled(config);

    expect(result.headers.Authorization).toBeUndefined();
  });
});
