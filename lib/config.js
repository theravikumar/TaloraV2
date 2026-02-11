// Application Configuration and Health Check
export const API_CONFIG = {
  baseUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api',
  appName: process.env.NEXT_PUBLIC_APP_NAME || 'Telora',
  appDomain: process.env.NEXT_PUBLIC_APP_DOMAIN || 'localhost:3000',
  isDevelopment: process.env.NODE_ENV === 'development',
  isProduction: process.env.NODE_ENV === 'production',
};

// API Endpoints
export const API_ENDPOINTS = {
  auth: {
    login: '/auth/login',
    register: '/auth/register',
    heartbeat: '/auth/heartbeat',
  },
  jobs: {
    search: '/jobs/search',
    detail: (id) => `/jobs/${id}`,
  },
  resume: {
    upload: '/resume/upload',
    status: (jobId) => `/resume/status/${jobId}`,
    list: '/resume/list',
  },
  match: {
    resume: '/match',
    compare: '/match/compare',
  },
};

// UI Configuration
export const UI_CONFIG = {
  // Pagination
  jobsPerPage: 20,
  featuredJobsCount: 6,
  matchesPerPage: 10,

  // Timeouts
  statusCheckInterval: 2000, // ms
  apiTimeout: 30000, // ms
  sessionTimeout: 24 * 60 * 60, // seconds

  // File Upload
  maxUploadSizeMB: 5,
  supportedFormats: ['pdf', 'doc', 'docx', 'txt'],

  // UI Delays
  successMessageDuration: 4000, // ms
  errorMessageDuration: 5000, // ms
  redirectDelay: 1500, // ms
};

// Error Messages
export const ERROR_MESSAGES = {
  network: 'Network error. Please check your connection.',
  authentication: 'Authentication failed. Please login again.',
  fileSize: 'File is too large. Maximum size is 5MB.',
  fileFormat: 'Unsupported file format. Supported: PDF, DOC, DOCX, TXT',
  serverError: 'Server error. Please try again later.',
  notFound: 'Resource not found.',
  unauthorized: 'You are not authorized to access this resource.',
  invalidInput: 'Please check your input and try again.',
};

// Success Messages
export const SUCCESS_MESSAGES = {
  login: 'Logged in successfully!',
  register: 'Account created successfully!',
  logout: 'Logged out successfully!',
  resumeUpload: 'Resume uploaded successfully!',
  resumeProcessed: 'Resume processed successfully!',
};

// Feature Flags
export const FEATURES = {
  enableResumeParsing: true,
  enableJobMatching: true,
  enableAuthentication: true,
  enableJobSearch: true,
  enableUserComparison: false, // Not yet implemented
};

// Logging Configuration
export const LOGGING = {
  enableConsoleLogging: process.env.NODE_ENV === 'development',
  enableAnalytics: process.env.NODE_ENV === 'production',
};

// Health Check Configuration
export const HEALTH_CHECK = {
  enabled: true,
  interval: 60000, // ms (check every minute)
  endpoints: {
    backend: `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'}/../health`,
  },
};

// Get configuration status for debugging
export function getConfigStatus() {
  return {
    apiConfig: API_CONFIG,
    environment: process.env.NODE_ENV,
    apiUrl: API_CONFIG.baseUrl,
    appName: API_CONFIG.appName,
    isDev: API_CONFIG.isDevelopment,
    isProd: API_CONFIG.isProduction,
    timestamp: new Date().toISOString(),
  };
}
