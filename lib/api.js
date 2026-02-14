// API utility for Talora backend
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
const API_TIMEOUT = parseInt(process.env.NEXT_PUBLIC_API_TIMEOUT || '30000', 10);

// Helper to get auth token
function getToken() {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('token');
  }
  return null;
}

// Helper for timeout
function withTimeout(promise, timeoutMs) {
  return Promise.race([
    promise,
    new Promise((_, reject) =>
      setTimeout(() => reject(new Error('API request timeout')), timeoutMs)
    ),
  ]);
}

// Debug logging
function logDebug(message, data = null) {
  if (process.env.NEXT_PUBLIC_DEBUG === 'true') {
    console.log(`[API Debug] ${message}`, data || '');
  }
}

export async function apiFetch(path, options = {}) {
  const token = getToken();
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const fetchUrl = `${API_URL}${path}`;
  logDebug('Making API request', { url: fetchUrl, method: options.method || 'GET' });

  try {
    const res = await withTimeout(
      fetch(fetchUrl, {
        ...options,
        headers,
        credentials: 'include',
      }),
      API_TIMEOUT
    );

    if (!res.ok) {
      let error = { detail: res.statusText };
      try {
        error = await res.json();
      } catch (e) {
        // Response is not JSON - use status text
        logDebug('Response not JSON', { status: res.status });
      }

      const errorMessage = error.detail || error.message || res.statusText;
      logDebug('API error', { status: res.status, message: errorMessage });

      // Handle specific status codes
      if (res.status === 401) {
        // Clear token on auth error
        if (typeof window !== 'undefined') {
          localStorage.removeItem('token');
          localStorage.removeItem('user');
        }
        throw new Error('Session expired. Please login again.');
      }

      if (res.status === 422) {
        // Validation error
        if (error.detail && Array.isArray(error.detail)) {
          const fieldErrors = error.detail.map(e => `${e.loc?.[1]}: ${e.msg}`).join(', ');
          throw new Error(`Invalid input: ${fieldErrors}`);
        }
        throw new Error(errorMessage || 'Invalid input format. Please check your data.');
      }

      if (res.status === 403) {
        throw new Error('Access denied. You do not have permission to perform this action.');
      }

      if (res.status === 404) {
        throw new Error('Resource not found.');
      }

      if (res.status >= 500) {
        throw new Error('Server error. Please try again later.');
      }

      throw new Error(errorMessage || 'An error occurred. Please try again.');
    }

    const data = await res.json();
    logDebug('API response received', { path, dataKeys: Object.keys(data) });
    return data;
  } catch (error) {
    logDebug('API fetch error', { message: error.message });

    // Handle network errors
    if (error instanceof TypeError) {
      if (error.message.includes('fetch')) {
        throw new Error('Network error. Please check your connection and try again.');
      }
    }

    // Re-throw with better message
    if (error.message === 'API request timeout') {
      throw new Error('Request timeout. Please check your connection and try again.');
    }

    throw error;
  }
}

export async function login(email, password) {
  return apiFetch('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
}

export async function register(email, password) {
  return apiFetch('/auth/register', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
}

export async function getJobs(params = {}) {
  const query = new URLSearchParams(params).toString();
  const path = query ? `/jobs/search?${query}` : '/jobs/search';
  return apiFetch(path);
}


export async function getJob(jobId) {
  return apiFetch(`/jobs/${jobId}`);
}

// Autocomplete suggestions
export async function getJobTitleSuggestions(query = null) {
  const path = query ? `/autocomplete/job-titles?query=${encodeURIComponent(query)}` : '/autocomplete/job-titles';
  return apiFetch(path);
}

export async function getLocationSuggestions(query = null) {
  const path = query ? `/autocomplete/locations?query=${encodeURIComponent(query)}` : '/autocomplete/locations';
  return apiFetch(path);
}


export async function uploadResume(file) {
  const formData = new FormData();
  formData.append('file', file);
  const token = getToken();

  // Don't set Content-Type header, let browser set it with boundary for FormData
  const headers = {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  try {
    const res = await withTimeout(
      fetch(`${API_URL}/resume/upload`, {
        method: 'POST',
        body: formData,
        credentials: 'include',
        headers,
      }),
      API_TIMEOUT
    );

    if (!res.ok) {
      const error = await res.json().catch(() => ({ detail: 'Resume upload failed' }));
      throw new Error(error.detail || error.message || 'Resume upload failed');
    }

    return res.json();
  } catch (error) {
    if (error.message === 'API request timeout') {
      throw new Error('Upload timeout. Please try again.');
    }
    throw error;
  }
}

export async function getResumeStatus(jobId) {
  return apiFetch(`/resume/status/${jobId}`);
}

export async function matchResume(resumeId, jobFilters = {}, top_n = 5) {
  return apiFetch('/match', {
    method: 'POST',
    body: JSON.stringify({ resume_id: resumeId, job_filters: jobFilters, top_n }),
  });
}

/**
 * Health check for the backend
 */
export async function healthCheck() {
  try {
    const baseUrl = API_URL.replace('/api', '');
    const response = await withTimeout(
      fetch(`${baseUrl}/health`, {
        credentials: 'include',
      }),
      5000
    );
    return response.ok;
  } catch (error) {
    return false;
  }
}

/**
 * Get API status for debugging
 */
export async function apiStatus() {
  try {
    const baseUrl = API_URL.replace('/api', '');
    const response = await withTimeout(
      fetch(`${baseUrl}/`, {
        credentials: 'include',
      }),
      5000
    );
    return response.ok;
  } catch (error) {
    return false;
  }
}

// Smart Search APIs
export async function searchBySummary(summary, topN = 10) {
  const params = new URLSearchParams();
  params.append('summary', summary);
  params.append('top_n', topN);

  return apiFetch(`/smart-search/summary?${params.toString()}`, {
    method: 'POST',
  });
}

export async function searchByResume(file, topN = 10) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('top_n', topN);

  const token = getToken();
  const headers = {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  try {
    const response = await withTimeout(
      fetch(`${API_URL}/smart-search/resume`, {
        method: 'POST',
        headers,
        body: formData,
        credentials: 'include',
      }),
      API_TIMEOUT
    );

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Resume upload failed' }));
      throw new Error(error.detail || 'Resume upload failed');
    }

    return response.json();
  } catch (error) {
    if (error.message === 'API request timeout') {
      throw new Error('Upload timeout. Please try again with a smaller file.');
    }
    throw error;
  }
}

export async function getSmartSearchStatus(jobId, topN = 10) {
  return apiFetch(`/smart-search/status/${jobId}?top_n=${topN}`);
}

