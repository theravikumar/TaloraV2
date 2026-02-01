# shared/schema/base.py
"""
Core schema definitions for the job matching platform.
These schemas are used across both job-pipeline and match-engine.
"""

from typing import List, Optional, Literal, TypedDict, Dict


# -----------------------------
# Common Type Literals
# -----------------------------

ProjectType = Literal[
    "professional",
    "personal",
    "academic",
    "open_source",
]

ResponsibilityLevel = Literal[
    "assisted",
    "independent",
    "ownership",
    "leadership",
]

Duration = Literal[
    "short",  # < 3 months
    "medium",  # 3-12 months  
    "long",  # > 12 months
]

Priority = Literal[
    "required",
    "preferred",
]

ConfidenceLevel = Literal[
    "explicit",  # Clearly stated in text
    "implicit",  # Inferred from context
]

WorkUnitType = Literal[
    "evidence",  # What someone DID (resume)
    "requirement",  # What someone MUST do (JD)
]


# -----------------------------
# WorkUnit (Core Primitive)
# -----------------------------

class WorkUnit(TypedDict):
    """
    Atomic unit of work - the smallest meaningful piece used for:
    - Matching (compare evidence vs requirements)
    - Embeddings (semantic similarity)
    - Gap analysis (identify missing skills/experience)
    
    Examples:
    Resume (evidence): "Built RESTful API using FastAPI handling 1M requests/day"
    - type: "evidence"
    - action: "Built"
    - object: "RESTful API"
    - tools: ["FastAPI"]
    - constraints: ["1M requests/day", "high performance"]
    - outcome: "Reduced latency by 40%"
    
    JD (requirement): "Develop scalable APIs using modern Python frameworks"
    - type: "requirement"
    - action: "Develop"
    - object: "scalable APIs"
    - tools: ["Python frameworks"]
    - constraints: ["scalable", "production-grade"]
    - outcome: None
    """
    
    type: WorkUnitType  # NEW: distinguish evidence vs requirement
    action: str  # Verb: "Built", "Developed", "Designed", etc.
    object: str  # What was acted upon: "API", "ML model", etc.
    tools: List[str]  # Technologies used: ["FastAPI", "PostgreSQL"]
    constraints: List[str]  # Requirements: ["scalable", "1M users", "real-time"]
    outcome: Optional[str]  # Result/impact: "Reduced cost by 30%"


# -----------------------------
# Project (Resume Context)
# -----------------------------

class Project(TypedDict):
    """
    Groups multiple WorkUnits under shared context.
    Used only for resumes to organize experience.
    """
    
    name: Optional[str]  # Project name
    domain: str  # "backend", "ML", "data engineering", etc.
    project_type: ProjectType
    duration: Optional[Duration]
    responsibility_level: ResponsibilityLevel  # Critical for matching
    work_units: List[WorkUnit]  # type: "evidence"


# -----------------------------
# Resume Profile
# -----------------------------

class ResumeProfile(TypedDict):
    """
    Normalized resume representation.
    Contains all evidence of what the person has done.
    """
    
    projects: List[Project]
    missing_signals: List[str]  # For resume improvement suggestions


# -----------------------------
# JD Expectation
# -----------------------------

class JDExpectation(TypedDict):
    """
    One expectation from a job description.
    Can be required or preferred.
    """
    
    priority: Priority  # required vs preferred
    confidence: ConfidenceLevel  # explicit vs inferred
    work_units: List[WorkUnit]  # type: "requirement"


# -----------------------------
# Job Description Profile
# -----------------------------

class JobDescriptionProfile(TypedDict):
    """
    Normalized JD representation - only expectations.
    Metadata (title, company, location) stored separately in NormalizedJob.
    """
    
    role: Optional[str]
    domain: Optional[str]
    required_expectations: List[JDExpectation]
    preferred_expectations: List[JDExpectation]


# -----------------------------
# Resume Feedback (NEW)
# -----------------------------

class ResumeFeedback(TypedDict):
    """
    Feedback for resume improvement.
    Generated after resume normalization.
    """
    
    overall_quality: float  # 0.0 to 1.0
    strengths: List[str]  # What's good
    missing_signals: List[Dict[str, str]]  # What to add
    # Each missing signal:
    # {
    #   "issue": "No metrics in project X",
    #   "impact": "Can't assess scale",
    #   "suggestion": "Add: request volume, latency, etc."
    # }
    suggested_improvements: List[Dict[str, str]]
    # Each improvement:
    # {
    #   "what": "Add constraints",
    #   "why": "Shows complexity handled",
    #   "how": "Mention scale, performance requirements"
    # }
