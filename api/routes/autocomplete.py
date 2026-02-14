# api/routes/autocomplete.py
"""
Autocomplete routes for search suggestions
"""
from fastapi import APIRouter, Query
from typing import Optional, List

from api.services.job_service import JobService

router = APIRouter(prefix="/api/autocomplete", tags=["autocomplete"])
job_service = JobService()


@router.get("/job-titles", response_model=List[str])
def get_job_title_suggestions(
    query: Optional[str] = Query(None, description="Filter job titles by query string")
):
    """Get unique job titles for autocomplete"""
    return job_service.get_unique_job_titles(query)


@router.get("/locations", response_model=List[str])
def get_location_suggestions(
    query: Optional[str] = Query(None, description="Filter locations by query string")
):
    """Get unique locations for autocomplete"""
    return job_service.get_unique_locations(query)
