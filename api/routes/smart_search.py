# api/routes/smart_search.py
"""
Smart search routes for summary-based and resume-based job matching
"""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional
import uuid
from pathlib import Path

from api.database import get_db
from api.database.models import ParsingJob, Resume
from api.models.match import MatchResponse, MatchDetail
from api.services.match_service import MatchService
from api.utils.file_validation import validate_pdf, calculate_file_hash
from api.utils.errors import FileValidationError, ParsingError
from api.tasks.resume_parser import parse_resume_task
from api.config import get_settings

settings = get_settings()
router = APIRouter(prefix="/api/smart-search", tags=["smart-search"])
match_service = MatchService()


@router.post("/summary", response_model=MatchResponse)
def search_by_summary(
    summary: str,
    top_n: Optional[int] = 10,
    db: Session = Depends(get_db)
):
    """
    Search jobs by user summary/description (semantic matching).
    
    Args:
        summary: User's profile description (skills, experience, goals)
        top_n: Number of top matches to return
        
    Returns:
        Matched jobs ranked by semantic similarity
    """
    if not summary or len(summary.strip()) < 10:
        raise HTTPException(status_code=400, detail="Summary too short (min 10 characters)")
    
    # Create a temporary resume-like structure from summary
    temp_resume_data = {
        "summary": summary,
        "work_units": _extract_work_units_from_summary(summary)
    }
    
    # Get all jobs
    from api.services.job_service import JobService
    job_service = JobService()
    jobs = job_service.get_all_jobs()
    
    # Match using existing matcher
    matches = match_service.matcher.match_jobs(
        resume_profile=temp_resume_data,
        jobs=jobs,
        top_n=top_n
    )
    
    # Format response
    formatted_matches = [
        {
            "job": m["job"],
            "match_score": m["score"],
            "matched_count": m["matched_count"],
            "total_requirements": m["total_requirements"],
            "gaps": m["gaps"]
        }
        for m in matches
    ]
    
    return MatchResponse(matches=[MatchDetail(**m) for m in formatted_matches])


@router.post("/resume", response_model=dict)
async def search_by_resume(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    top_n: Optional[int] = 10,
    db: Session = Depends(get_db)
):
    """
    Upload resume and get matched jobs (async).
    
    Returns job_id for polling and eventual match results.
    """
    try:
        # Validate file
        content = await validate_pdf(file)
        file_hash = calculate_file_hash(content)
        
        # Check for existing resume
        existing = db.query(Resume).filter(Resume.file_hash == file_hash).first()
        if existing:
            # Resume already parsed - return matches immediately
            matches = match_service.match_resume_to_jobs(
                db,
                existing.id,
                top_n=top_n
            )
            return {
                "status": "completed",
                "resume_id": existing.id,
                "matches": matches,
                "result": {
                     "name": existing.parsed_data.get("name"),
                     "years_of_experience": existing.parsed_data.get("years_of_experience"),
                     "skills": existing.parsed_data.get("skills", [])[:10],
                     "work_units": len(existing.parsed_data.get("work_units", []))
                }
            }
        
        # Save file
        upload_dir = Path(settings.upload_dir) / "temp"
        upload_dir.mkdir(parents=True, exist_ok=True)
        file_path = upload_dir / f"{uuid.uuid4()}_{file.filename}"
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Create parsing job
        job = ParsingJob(
            filename=file.filename,
            status="pending"
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        
        # Start background parsing
        background_tasks.add_task(parse_resume_task, job.id, file_path)
        
        return {
            "status": "processing",
            "job_id": job.id,
            "message": "Resume is being processed. Poll /status/{job_id} for results."
        }
        
    except FileValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/status/{job_id}")
def get_match_status(
    job_id: str,
    top_n: Optional[int] = 10,
    db: Session = Depends(get_db)
):
    """
    Get status of resume processing and matches.
    """
    job = db.query(ParsingJob).filter(ParsingJob.id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    response = {
        "job_id": job.id,
        "status": job.status
    }
    
    if job.status == "completed" and job.result:
        # Include parsed result
        response["result"] = job.result
        
        #  Get matches
        resume_id = job.result.get("resume_id")
        if resume_id:
            try:
                matches = match_service.match_resume_to_jobs(
                    db,
                    resume_id,
                    top_n=top_n
                )
                response["matches"] = matches
            except ParsingError:
                response["error"] = "Resume found but matching failed"
    
    elif job.status == "failed":
        response["error"] = job.error_message
    
    return response


def _extract_work_units_from_summary(summary: str) -> list:
    """
    Extract work units from summary text (simplified version).
    
    For now, creates a single work unit with the summary.
    TODO: Use LLM to extract structured skills/experience.
    """
    return [{
        "role": "Candidate",
        "skills": summary.split(),  # Simple word extraction
        "description": summary,
        "duration_years": 0  # Unknown from summary
    }]
