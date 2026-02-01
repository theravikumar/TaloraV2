# api/models/resume.py
"""
Resume-related Pydantic models
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class ResumeUploadResponse(BaseModel):
    """Response after resume upload"""
    job_id: Optional[str] = None
    status: str  # pending, completed
    message: str
    resume: Optional[Dict[str, Any]] = None


class ResumeParseStatus(BaseModel):
    """Resume parsing job status"""
    job_id: str
    status: str  # pending, processing, completed, failed
    progress: Optional[int] = None
    resume: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class ResumeDetail(BaseModel):
    """Resume details"""
    resume_id: str
    filename: str
    uploaded_at: datetime
    summary: Dict[str, Any]  # Name, years, top skills
    
    class Config:
        from_attributes = True


class ResumeListResponse(BaseModel):
    """List of user's resumes"""
    resumes: List[ResumeDetail]
    count: int
    max_allowed: int = 5
