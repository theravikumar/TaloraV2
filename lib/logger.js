// Logging utilities for development and debugging
const isDev = process.env.NODE_ENV === 'development';

export const logger = {
  log: (...args) => {
    if (isDev) console.log('[Telora]', ...args);
  },
  error: (...args) => {
    if (isDev) console.error('[Telora Error]', ...args);
  },
  warn: (...args) => {
    if (isDev) console.warn('[Telora Warning]', ...args);
  },
  info: (...args) => {
    if (isDev) console.info('[Telora Info]', ...args);
  },
};

// Health check utility
export async function checkBackendHealth() {
  try {
    const baseUrl = process.env.NEXT_PUBLIC_API_URL?.replace('/api', '') || 'http://localhost:8000';
    const response = await fetch(
      `${baseUrl}/health`,
      {
        method: 'GET',
        credentials: 'include',
      }
    );
    return {
      healthy: response.ok,
      status: response.status,
      message: response.ok ? 'Backend is running' : 'Backend returned an error',
    };
  } catch (error) {
    return {
      healthy: false,
      status: null,
      message: `Backend is unreachable: ${error.message}`,
    };
  }
}

// API connectivity check
export async function checkAPIConnectivity() {
  try {
    const baseUrl = process.env.NEXT_PUBLIC_API_URL?.replace('/api', '') || 'http://localhost:8000';
    const response = await fetch(
      `${baseUrl}/`,
      {
        method: 'GET',
        credentials: 'include',
      }
    );
    return response.ok;
  } catch (error) {
    return false;
  }
}
