# api/models/__init__.py
"""
Pydantic models for API request/response
"""
from api.models.resume import ResumeUploadResponse, ResumeParseStatus, ResumeDetail
from api.models.auth import UserRegister, UserLogin, TokenResponse
from api.models.job import JobSearchQuery, JobDetail, JobListResponse
from api.models.match import MatchRequest, MatchResponse, MatchDetail

__all__ = [
    "ResumeUploadResponse",
    "ResumeParseStatus",
    "ResumeDetail",
    "UserRegister",
    "UserLogin",
    "TokenResponse",
    "JobSearchQuery",
    "JobDetail",
    "JobListResponse",
    "MatchRequest",
    "MatchResponse",
    "MatchDetail",
]
