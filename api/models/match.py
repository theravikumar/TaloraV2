# api/models/match.py
"""
Matching-related Pydantic models
"""
from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class MatchRequest(BaseModel):
    """Match resume to jobs"""
    resume_id: str
    job_filters: Optional[Dict[str, Any]] = None
    top_n: int = 10


class MatchDetail(BaseModel):
    """Single match result"""
    job: Dict[str, Any]
    match_score: float
    matched_count: int
    total_requirements: int
    gaps: List[Dict[str, Any]]


class MatchResponse(BaseModel):
    """Matching results"""
    matches: List[MatchDetail]


class CompareRequest(BaseModel):
    """Compare multiple resumes"""
    resume_ids: List[str]
    job_filters: Optional[Dict[str, Any]] = None


class CompareResponse(BaseModel):
    """Comparison results"""
    comparison: Dict[str, Any]
