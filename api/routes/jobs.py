# api/routes/jobs.py
"""
Job search routes
"""
from fastapi import APIRouter, Query
from typing import Optional

from api.models.job import JobSearchQuery, JobListResponse, JobDetail
from api.services.job_service import JobService

router = APIRouter(prefix="/api/jobs", tags=["jobs"])
job_service = JobService()


@router.get("/search", response_model=JobListResponse)
def search_jobs(
    keywords: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    employment_type: Optional[str] = Query(None),
    ids: Optional[str] = Query(None, description="Comma-separated job IDs for smart search"),
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0)
):
    """Search jobs with filters"""
    results = job_service.search_jobs(keywords, location, employment_type, ids, limit, offset)
    return JobListResponse(**results)


@router.get("/{job_id}", response_model=JobDetail)
def get_job(job_id: str):
    """Get job details by ID"""
    job = job_service.get_job_by_id(job_id)
    if not job:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Job not found")
    return JobDetail(**job)
