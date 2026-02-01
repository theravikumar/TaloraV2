# shared/schema/job.py
"""
Job-related schemas for storage and retrieval.
"""

from typing import Optional, List
from datetime import datetime
from .base import JobDescriptionProfile


class NormalizedJob(dict):
    """
    Complete job representation with metadata + expectations.
    
    This is what gets stored in the database and used for matching.
    Combines:
    - Metadata (for filtering: location, salary, company)
    - JobDescriptionProfile (for matching: requirements, preferences)
    """
    
    # Primary identification
    job_id: str  # Unique identifier (UUID or hash)
    job_url: str  # Source URL (must be unique)
    source: str  # "ambitionbox", "naukri", "linkedin", etc.
    
    # Company information
    company_name: str
    company_url: Optional[str]
    
    # Job basics
    job_title: str
    location: Optional[str]
    work_mode: Optional[str]  # "remote", "hybrid", "onsite"
    employment_type: Optional[str]  # "full-time", "contract", etc.
    
    # Compensation & experience
    salary: Optional[str]  # Raw salary string from JD
    experience_level: Optional[str]  # "0-2 years", "5+ years", etc.
    
    # Timestamps
    posted_date: Optional[str]  # When job was posted
    scraped_at: datetime  # When we scraped it
    last_updated: datetime  # Last modification time
    
    # Matching data (the core)
    domain: Optional[str]  # "backend", "ML", "data", etc.
    jd_profile: JobDescriptionProfile  # Required/preferred expectations
    
    # Quality metadata
    extraction_quality: float  # 0.0-1.0 confidence in extraction
    raw_text: Optional[str]  # Original JD text (for debugging)
    
    # Status
    is_active: bool  # False if job expired/removed
    
    def __init__(self, **kwargs):
        """Initialize with validation"""
        super().__init__(**kwargs)
        # Validate required fields
        required = ["job_id", "job_url", "company_name", "job_title", "source"]
        for field in required:
            if field not in kwargs:
                raise ValueError(f"Missing required field: {field}")


class JobSearchFilters(dict):
    """
    Filters for searching jobs before matching.
    Used to narrow down candidates before expensive matching.
    """
    
    # Location filters
    locations: Optional[List[str]]  # ["Bangalore", "Remote"]
    work_modes: Optional[List[str]]  # ["remote", "hybrid"]
    
    # Experience
    min_experience: Optional[int]  # years
    max_experience: Optional[int]  # years
    
    # Domain
    domains: Optional[List[str]]  # ["backend", "ML"]
    
    # Company
    companies: Optional[List[str]]  # Specific companies
    exclude_companies: Optional[List[str]]  # Companies to skip
    
    # Salary (optional, often not disclosed)
    min_salary: Optional[float]
    
    # Recency
    posted_within_days: Optional[int]  # e.g., 30 for last month
    
    # Quality
    min_extraction_quality: float = 0.7  # Skip low-quality extractions
    
    # Status
    only_active: bool = True  # Skip expired jobs


class JobMatchResult(dict):
    """
    Result of matching one job against a resume.
    """
    
    job_id: str
    job_title: str
    company_name: str
    job_url: str
    
    # Match scores
    overall_score: float  # 0.0-1.0
    required_coverage: float  # % of required expectations met
    preferred_coverage: float  # % of preferred expectations met
    
    # Matched expectations
    matched_required: int
    total_required: int
    matched_preferred: int
    total_preferred: int
    
    # Gaps (what user is missing)
    required_gaps: List[dict]  # Critical gaps
    preferred_gaps: List[dict]  # Nice-to-have gaps
    
    # Strengths (what user has)
    strengths: List[str]
    
    # Detailed explanation (optional, LLM-generated)
    explanation: Optional[str]
    
    # Risk flags
    risk_flags: List[str]  # ["domain mismatch", "insufficient experience"]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Calculate overall score if not provided
        if "overall_score" not in kwargs:
            self["overall_score"] = (
                0.8 * kwargs.get("required_coverage", 0.0) +
                0.2 * kwargs.get("preferred_coverage", 0.0)
            )
