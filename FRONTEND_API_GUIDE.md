# Frontend API Integration Guide

**Backend Base URL:** `http://localhost:8000`  
**API Version:** v1  
**Last Updated:** Feb 11, 2026

---

## Quick Start Checklist

- [ ] Backend server running on port 8000
- [ ] PostgreSQL and Redis connected
- [ ] Understand JWT token flow
- [ ] Test health endpoint
- [ ] Implement authentication
- [ ] Add resume upload
- [ ] Integrate job search

---

## Table of Contents

1. [Health Check](#1-health-check)
2. [Authentication](#2-authentication)
3. [Resume Management](#3-resume-management)
4. [Job Search](#4-job-search)
5. [Error Handling](#5-error-handling)
6. [Complete Examples](#6-complete-examples)

---

## 1. Health Check

### Check System Status
**Endpoint:** `GET /health`  
**Auth Required:** No

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected"
}
```

**JavaScript Example:**
```javascript
async function checkHealth() {
  const response = await fetch('http://localhost:8000/health');
  const data = await response.json();
  console.log('Backend status:', data.status);
  return data;
}
```

---

## 2. Authentication

### 2.1 User Registration

**Endpoint:** `POST /api/auth/register`  
**Auth Required:** No

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "name": "John Doe"
}
```

**Response (Success):**
```json
{
  "user_id": "uuid-here",
  "email": "user@example.com",
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "expires_in": 86400
}
```

**JavaScript Example:**
```javascript
async function register(email, password, name) {
  const response = await fetch('http://localhost:8000/api/auth/register', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password, name })
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Registration failed');
  }
  
  const data = await response.json();
  
  // Store token in localStorage
  localStorage.setItem('authToken', data.token);
  localStorage.setItem('userId', data.user_id);
  
  return data;
}
```

**React Example:**
```jsx
import { useState } from 'react';

function RegisterForm() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const data = await register(email, password, name);
      console.log('Registered successfully', data);
      // Redirect to dashboard
      window.location.href = '/dashboard';
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input 
        type="text" 
        value={name} 
        onChange={(e) => setName(e.target.value)}
        placeholder="Full Name"
        required
      />
      <input 
        type="email" 
        value={email} 
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Email"
        required
      />
      <input 
        type="password" 
        value={password} 
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
        required
      />
      {error && <p className="error">{error}</p>}
      <button type="submit">Register</button>
    </form>
  );
}
```

---

### 2.2 User Login

**Endpoint:** `POST /api/auth/login`  
**Auth Required:** No

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response (Success):**
```json
{
  "user_id": "uuid-here",
  "email": "user@example.com",
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "expires_in": 86400
}
```

**JavaScript Example:**
```javascript
async function login(email, password) {
  const response = await fetch('http://localhost:8000/api/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password })
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Login failed');
  }
  
  const data = await response.json();
  
  // Store token
  localStorage.setItem('authToken', data.token);
  localStorage.setItem('userId', data.user_id);
  
  return data;
}
```

---

### 2.3 JWT Token Management

**Token Storage:**
- Store JWT token in `localStorage` or `sessionStorage`
- Token expires in 24 hours (86400 seconds)
- Include token in all authenticated requests

**Using Token in Requests:**
```javascript
function getAuthHeaders() {
  const token = localStorage.getItem('authToken');
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  };
}

// Example authenticated request
async function getProtectedData() {
  const response = await fetch('http://localhost:8000/api/protected', {
    headers: getAuthHeaders()
  });
  return response.json();
}
```

**Check Token Expiry:**
```javascript
function isTokenExpired() {
  const token = localStorage.getItem('authToken');
  if (!token) return true;
  
  // Decode JWT token (basic example)
  const payload = JSON.parse(atob(token.split('.')[1]));
  const expiryTime = payload.exp * 1000; // Convert to milliseconds
  
  return Date.now() >= expiryTime;
}

// Redirect to login if expired
if (isTokenExpired()) {
  window.location.href = '/login';
}
```

---

## 3. Resume Management

### 3.1 Upload Resume

**Endpoint:** `POST /api/resume/upload`  
**Auth Required:** Yes (JWT token)  
**Content-Type:** `multipart/form-data`

**Request:**
- File field name: `file`
- File type: PDF only
- Max size: 10MB

**Response (Success):**
```json
{
  "job_id": "parsing-job-uuid",
  "status": "pending",
  "message": "Processing your resume...",
  "resume": null
}
```

**JavaScript Example:**
```javascript
async function uploadResume(file) {
  const formData = new FormData();
  formData.append('file', file);
  
  const token = localStorage.getItem('authToken');
  
  const response = await fetch('http://localhost:8000/api/resume/upload', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`
    },
    body: formData
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Upload failed');
  }
  
  const data = await response.json();
  return data;
}
```

**React Example with Progress:**
```jsx
import { useState } from 'react';

function ResumeUpload() {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [jobId, setJobId] = useState(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    
    // Validate file
    if (!selectedFile) return;
    if (selectedFile.type !== 'application/pdf') {
      alert('Only PDF files are allowed');
      return;
    }
    if (selectedFile.size > 10 * 1024 * 1024) {
      alert('File size must be less than 10MB');
      return;
    }
    
    setFile(selectedFile);
  };

  const handleUpload = async () => {
    if (!file) return;
    
    setUploading(true);
    try {
      const data = await uploadResume(file);
      setJobId(data.job_id);
      
      // Start polling for status
      pollResumeStatus(data.job_id);
    } catch (err) {
      alert(err.message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div>
      <input 
        type="file" 
        accept=".pdf"
        onChange={handleFileChange}
        disabled={uploading}
      />
      <button 
        onClick={handleUpload} 
        disabled={!file || uploading}
      >
        {uploading ? 'Uploading...' : 'Upload Resume'}
      </button>
      {jobId && <p>Job ID: {jobId}</p>}
    </div>
  );
}
```

---

### 3.2 Check Resume Parsing Status

**Endpoint:** `GET /api/resume/status/{job_id}`  
**Auth Required:** Yes

**Response (Pending):**
```json
{
  "job_id": "uuid",
  "status": "pending",
  "progress": null,
  "resume": null,
  "error": null
}
```

**Response (Completed):**
```json
{
  "job_id": "uuid",
  "status": "completed",
  "progress": null,
  "resume": {
    "resume_id": "resume-uuid",
    "name": "Ravi Kumar",
    "email": "ravi@example.com",
    "phone": "+91-9608676321",
    "years_of_experience": 3.5,
    "current_role": "Senior Machine Learning Engineer",
    "skills": ["PyTorch", "TensorFlow", "AWS", ...],
    "education": [...],
    "work_experience": [...],
    "work_units": [...]
  },
  "error": null
}
```

**Response (Failed):**
```json
{
  "job_id": "uuid",
  "status": "failed",
  "progress": null,
  "resume": null,
  "error": "Unable to process resume. Please try again."
}
```

**JavaScript Example with Polling:**
```javascript
async function checkResumeStatus(jobId) {
  const token = localStorage.getItem('authToken');
  
  const response = await fetch(
    `http://localhost:8000/api/resume/status/${jobId}`,
    {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    }
  );
  
  return response.json();
}

// Poll every 2 seconds until complete
async function pollResumeStatus(jobId, maxAttempts = 30) {
  for (let i = 0; i < maxAttempts; i++) {
    const status = await checkResumeStatus(jobId);
    
    if (status.status === 'completed') {
      console.log('Resume parsed successfully!', status.resume);
      return status.resume;
    }
    
    if (status.status === 'failed') {
      throw new Error(status.error);
    }
    
    // Wait 2 seconds before next check
    await new Promise(resolve => setTimeout(resolve, 2000));
  }
  
  throw new Error('Parsing timeout');
}
```

**React Hook Example:**
```jsx
import { useState, useEffect } from 'react';

function useResumeStatus(jobId) {
  const [status, setStatus] = useState('pending');
  const [resume, setResume] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!jobId) return;

    const interval = setInterval(async () => {
      try {
        const data = await checkResumeStatus(jobId);
        setStatus(data.status);
        
        if (data.status === 'completed') {
          setResume(data.resume);
          clearInterval(interval);
        } else if (data.status === 'failed') {
          setError(data.error);
          clearInterval(interval);
        }
      } catch (err) {
        setError(err.message);
        clearInterval(interval);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [jobId]);

  return { status, resume, error };
}

// Usage
function ResumeStatus({ jobId }) {
  const { status, resume, error } = useResumeStatus(jobId);

  if (status === 'pending') {
    return <div>Processing your resume...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  if (resume) {
    return (
      <div>
        <h2>{resume.name}</h2>
        <p>{resume.current_role}</p>
        <p>Experience: {resume.years_of_experience} years</p>
        <h3>Skills:</h3>
        <ul>
          {resume.skills.map(skill => (
            <li key={skill}>{skill}</li>
          ))}
        </ul>
      </div>
    );
  }

  return null;
}
```

---

### 3.3 List User Resumes

**Endpoint:** `GET /api/resume/list`  
**Auth Required:** Yes

**Response:**
```json
{
  "resumes": [
    {
      "resume_id": "uuid",
      "filename": "ravi_resume.pdf",
      "uploaded_at": "2026-02-11T06:00:00Z",
      "is_active": true
    }
  ],
  "count": 1,
  "max_allowed": 5
}
```

**JavaScript Example:**
```javascript
async function listResumes() {
  const token = localStorage.getItem('authToken');
  
  const response = await fetch('http://localhost:8000/api/resume/list', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  return response.json();
}
```

---

## 4. Job Search

### 4.1 Search Jobs

**Endpoint:** `GET /api/jobs/search`  
**Auth Required:** No  
**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `keywords` | string | No | - | Search keywords (e.g., "data scientist") |
| `location` | string | No | - | Job location |
| `domain` | string | No | - | Job domain (e.g., "ML", "Web") |
| `limit` | integer | No | 10 | Number of results (max 100) |
| `offset` | integer | No | 0 | Pagination offset |

**Response:**
```json
{
  "total": 5,
  "jobs": [
    {
      "job_id": "linkedin-data-scientist-at-jio-4366817274",
      "job_title": "Data Scientist",
      "company_name": "Jio",
      "location": "Navi Mumbai, Maharashtra, India",
      "domain": "ML",
      "requirements_count": 0,
      "description": null,
      "requirements": null
    },
    ...
  ]
}
```

**JavaScript Example:**
```javascript
async function searchJobs(params = {}) {
  const queryParams = new URLSearchParams();
  
  if (params.keywords) queryParams.append('keywords', params.keywords);
  if (params.location) queryParams.append('location', params.location);
  if (params.domain) queryParams.append('domain', params.domain);
  if (params.limit) queryParams.append('limit', params.limit);
  if (params.offset) queryParams.append('offset', params.offset);
  
  const url = `http://localhost:8000/api/jobs/search?${queryParams.toString()}`;
  
  const response = await fetch(url);
  return response.json();
}

// Example usage
const jobs = await searchJobs({
  keywords: 'machine learning',
  location: 'Bengaluru',
  domain: 'ML',
  limit: 20
});
```

**React Component Example:**
```jsx
import { useState, useEffect } from 'react';

function JobSearch() {
  const [keywords, setKeywords] = useState('');
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [total, setTotal] = useState(0);

  const handleSearch = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const data = await searchJobs({ keywords, limit: 20 });
      setJobs(data.jobs);
      setTotal(data.total);
    } catch (err) {
      console.error('Search failed:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <form onSubmit={handleSearch}>
        <input
          type="text"
          value={keywords}
          onChange={(e) => setKeywords(e.target.value)}
          placeholder="Search jobs..."
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Searching...' : 'Search'}
        </button>
      </form>

      {total > 0 && <p>Found {total} jobs</p>}

      <div className="job-results">
        {jobs.map(job => (
          <div key={job.job_id} className="job-card">
            <h3>{job.job_title}</h3>
            <p>{job.company_name}</p>
            <p>{job.location}</p>
            <span className="domain">{job.domain}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

### 4.2 Get Job Details

**Endpoint:** `GET /api/jobs/{job_id}`  
**Auth Required:** No

**Response:**
```json
{
  "job_id": "linkedin-data-scientist-at-jio-4366817274",
  "job_title": "Data Scientist",
  "company_name": "Jio",
  "location": "Navi Mumbai, Maharashtra, India",
  "domain": "ML",
  "requirements_count": 0,
  "description": "Full job description...",
  "requirements": ["Python", "Machine Learning", ...]
}
```

**JavaScript Example:**
```javascript
async function getJobDetails(jobId) {
  const response = await fetch(`http://localhost:8000/api/jobs/${jobId}`);
  
  if (!response.ok) {
    throw new Error('Job not found');
  }
  
  return response.json();
}
```

---

## 5. Error Handling

### Common Error Responses

**400 Bad Request:**
```json
{
  "detail": "Invalid email format"
}
```

**401 Unauthorized:**
```json
{
  "detail": "Invalid or expired token"
}
```

**404 Not Found:**
```json
{
  "detail": "Job not found"
}
```

**422 Validation Error:**
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Internal server error"
}
```

### Error Handling Utility

```javascript
async function apiCall(url, options = {}) {
  try {
    const response = await fetch(url, options);
    
    if (!response.ok) {
      const error = await response.json();
      
      // Handle specific error codes
      if (response.status === 401) {
        // Token expired, redirect to login
        localStorage.removeItem('authToken');
        window.location.href = '/login';
        return;
      }
      
      throw new Error(error.detail || 'Request failed');
    }
    
    return await response.json();
  } catch (err) {
    console.error('API Error:', err);
    throw err;
  }
}
```

---

## 6. Complete Examples

### Full Authentication Flow

```javascript
// Complete auth flow
class AuthService {
  constructor() {
    this.baseURL = 'http://localhost:8000';
  }

  async register(email, password, name) {
    const response = await fetch(`${this.baseURL}/api/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, name })
    });
    
    const data = await response.json();
    if (response.ok) {
      this.setToken(data.token);
      return data;
    }
    throw new Error(data.detail);
  }

  async login(email, password) {
    const response = await fetch(`${this.baseURL}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    
    const data = await response.json();
    if (response.ok) {
      this.setToken(data.token);
      return data;
    }
    throw new Error(data.detail);
  }

  setToken(token) {
    localStorage.setItem('authToken', token);
  }

  getToken() {
    return localStorage.getItem('authToken');
  }

  logout() {
    localStorage.removeItem('authToken');
    localStorage.removeItem('userId');
  }

  isAuthenticated() {
    const token = this.getToken();
    if (!token) return false;
    
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      return Date.now() < payload.exp * 1000;
    } catch {
      return false;
    }
  }

  getAuthHeaders() {
    return {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${this.getToken()}`
    };
  }
}

// Usage
const auth = new AuthService();

// Register
await auth.register('user@example.com', 'SecurePass123!', 'John Doe');

// Login
await auth.login('user@example.com', 'SecurePass123!');

// Check if authenticated
if (auth.isAuthenticated()) {
  console.log('User is logged in');
}

// Logout
auth.logout();
```

---

### Complete Resume Upload Flow

```javascript
class ResumeService {
  constructor(baseURL = 'http://localhost:8000') {
    this.baseURL = baseURL;
  }

  async upload(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    const token = localStorage.getItem('authToken');
    
    const response = await fetch(`${this.baseURL}/api/resume/upload`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` },
      body: formData
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail);
    }
    
    return response.json();
  }

  async checkStatus(jobId) {
    const token = localStorage.getItem('authToken');
    
    const response = await fetch(
      `${this.baseURL}/api/resume/status/${jobId}`,
      {
        headers: { 'Authorization': `Bearer ${token}` }
      }
    );
    
    return response.json();
  }

  async uploadAndWait(file, onProgress) {
    // Upload
    const uploadData = await this.upload(file);
    const jobId = uploadData.job_id;
    
    if (!jobId) {
      // Already processed
      return uploadData.resume;
    }
    
    // Poll for completion
    return new Promise((resolve, reject) => {
      const interval = setInterval(async () => {
        try {
          const status = await this.checkStatus(jobId);
          
          if (onProgress) {
            onProgress(status.status);
          }
          
          if (status.status === 'completed') {
            clearInterval(interval);
            resolve(status.resume);
          } else if (status.status === 'failed') {
            clearInterval(interval);
            reject(new Error(status.error));
          }
        } catch (err) {
          clearInterval(interval);
          reject(err);
        }
      }, 2000);
      
      // Timeout after 60 seconds
      setTimeout(() => {
        clearInterval(interval);
        reject(new Error('Processing timeout'));
      }, 60000);
    });
  }
}

// Usage
const resumeService = new ResumeService();

const fileInput = document.getElementById('resume-file');
const file = fileInput.files[0];

try {
  const resume = await resumeService.uploadAndWait(
    file,
    (status) => console.log('Status:', status)
  );
  
  console.log('Resume parsed:', resume);
  console.log('Name:', resume.name);
  console.log('Skills:', resume.skills);
} catch (err) {
  console.error('Upload failed:', err);
}
```

---

### Complete Job Search with Pagination

```jsx
import { useState, useEffect } from 'react';

function JobSearchWithPagination() {
  const [keywords, setKeywords] = useState('');
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [limit] = useState(10);

  const fetchJobs = async (searchKeywords, currentPage) => {
    setLoading(true);
    try {
      const offset = (currentPage - 1) * limit;
      const data = await searchJobs({
        keywords: searchKeywords,
        limit,
        offset
      });
      
      setJobs(data.jobs);
      setTotal(data.total);
    } catch (err) {
      console.error('Search failed:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (keywords) {
      fetchJobs(keywords, page);
    }
  }, [page, keywords]);

  const handleSearch = (e) => {
    e.preventDefault();
    setPage(1); // Reset to first page
    fetchJobs(keywords, 1);
  };

  const totalPages = Math.ceil(total / limit);

  return (
    <div>
      <form onSubmit={handleSearch}>
        <input
          type="text"
          value={keywords}
          onChange={(e) => setKeywords(e.target.value)}
          placeholder="Search jobs..."
        />
        <button type="submit">Search</button>
      </form>

      {loading && <p>Loading...</p>}

      {!loading && jobs.length > 0 && (
        <>
          <p>Showing {jobs.length} of {total} jobs</p>
          
          <div className="job-list">
            {jobs.map(job => (
              <div key={job.job_id} className="job-card">
                <h3>{job.job_title}</h3>
                <p>{job.company_name}</p>
                <p>{job.location}</p>
                <button onClick={() => window.location.href = `/job/${job.job_id}`}>
                  View Details
                </button>
              </div>
            ))}
          </div>

          <div className="pagination">
            <button 
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
            >
              Previous
            </button>
            <span>Page {page} of {totalPages}</span>
            <button 
              onClick={() => setPage(p => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
            >
              Next
            </button>
          </div>
        </>
      )}
    </div>
  );
}
```

---

## Quick Reference

### All Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/health` | GET | No | Check system health |
| `/api/auth/register` | POST | No | Register new user |
| `/api/auth/login` | POST | No | Login user |
| `/api/resume/upload` | POST | Yes | Upload resume PDF |
| `/api/resume/status/{job_id}` | GET | Yes | Check parsing status |
| `/api/resume/list` | GET | Yes | List user resumes |
| `/api/jobs/search` | GET | No | Search jobs |
| `/api/jobs/{job_id}` | GET | No | Get job details |

### Authentication Headers

```javascript
{
  'Authorization': 'Bearer YOUR_JWT_TOKEN_HERE',
  'Content-Type': 'application/json'
}
```

### Common Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `404` - Not Found
- `422` - Validation Error
- `500` - Server Error

---

## Getting Help

**Issues?** Check:
1. Is backend running? (`http://localhost:8000/health`)
2. Is token valid? (Check expiry)
3. Are request headers correct?
4. Is request body formatted correctly?

**Need Support?**
- Backend repo: `https://github.com/theravikumar/TaloraV2`
- Contact: Backend team

---

**Last Updated:** Feb 11, 2026  
**Backend Version:** 1.0.0  
**Status:** Production Ready

