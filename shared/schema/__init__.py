# shared/schema/__init__.py
"""
Unified schema exports for the entire platform.
"""

from .base import (
    # Type literals
    ProjectType,
    ResponsibilityLevel,
    Duration,
    Priority,
    ConfidenceLevel,
    WorkUnitType,
    
    # Core schemas
    WorkUnit,
    Project,
    ResumeProfile,
    JDExpectation,
    JobDescriptionProfile,
    ResumeFeedback,
)

from .job import (
    NormalizedJob,
    JobSearchFilters,
    JobMatchResult,
)

__all__ = [
    # Type literals
    "ProjectType",
    "ResponsibilityLevel",
    "Duration",
    "Priority",
    "ConfidenceLevel",
    "WorkUnitType",
    
    # Core schemas
    "WorkUnit",
    "Project",
    "ResumeProfile",
    "JDExpectation",
    "JobDescriptionProfile",
    "ResumeFeedback",
    
    # Job schemas
    "NormalizedJob",
    "JobSearchFilters",
    "JobMatchResult",
]
