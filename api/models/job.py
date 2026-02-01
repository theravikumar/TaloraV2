# api/models/job.py
"""
Job-related Pydantic models
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class JobSearchQuery(BaseModel):
    """Job search query parameters"""
    keywords: Optional[str] = None
    location: Optional[str] = None
    domain: Optional[str] = None
    limit: int = 20
    offset: int = 0


class JobDetail(BaseModel):
    """Job details"""
    job_id: str
    job_title: str
    company_name: str
    location: str
    domain: Optional[str]
    requirements_count: int
    description: Optional[str] = None
    requirements: Optional[List[Dict[str, Any]]] = None


class JobListResponse(BaseModel):
    """Job search results"""
    total: int
    jobs: List[JobDetail]
