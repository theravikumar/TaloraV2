# api/routes/resume.py
"""
Resume upload and management routes  
"""
import uuid
import asyncio
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from api.database import get_db
from api.database.models import ParsingJob, Resume
from api.models.resume import ResumeUploadResponse, ResumeParseStatus, ResumeListResponse, ResumeDetail
from api.utils.file_validation import validate_pdf, calculate_file_hash
from api.utils.errors import FileValidationError
from api.tasks.resume_parser import parse_resume_task
from api.config import get_settings

settings = get_settings()
router = APIRouter(prefix="/api/resume", tags=["resume"])


@router.post("/upload", response_model=ResumeUploadResponse)
async def upload_resume(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload and parse resume (async)"""
    try:
        # Validate file
        content = await validate_pdf(file)
        file_hash = calculate_file_hash(content)
        
        # Check for duplicate
        existing = db.query(Resume).filter(Resume.file_hash == file_hash).first()
        if existing:
            return ResumeUploadResponse(
                status="completed",
                message="Resume already processed",
                resume={
                    "resume_id": existing.id,
                    **existing.parsed_data
                }
            )
        
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
        
        # Start background task
        background_tasks.add_task(parse_resume_task, job.id, file_path)
        
        return ResumeUploadResponse(
            job_id=job.id,
            status="pending",
            message="Processing your resume..."
        )
        
    except FileValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/status/{job_id}", response_model=ResumeParseStatus)
def get_parsing_status(job_id: str, db: Session = Depends(get_db)):
    """Get resume parsing status"""
    job = db.query(ParsingJob).filter(ParsingJob.id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    response = ResumeParseStatus(
        job_id=job.id,
        status=job.status
    )
    
    if job.status == "completed":
        response.resume = job.result
    elif job.status == "failed":
        response.error = job.error_message
    
    return response


@router.get("/list", response_model=ResumeListResponse)
def list_resumes(db: Session = Depends(get_db)):
    """List user's saved resumes (placeholder - needs auth)"""
    # TODO: Get user_id from JWT token
    resumes = db.query(Resume).filter(Resume.user_id != None).limit(5).all()
    
    resume_list = [
        ResumeDetail(
            resume_id=r.id,
            filename=r.filename,
            uploaded_at=r.uploaded_at,
            summary={
                "name": r.parsed_data.get("name"),
                "years_of_experience": r.parsed_data.get("years_of_experience")
            }
        )
        for r in resumes
    ]
    
    return ResumeListResponse(
        resumes=resume_list,
        count=len(resume_list),
        max_allowed=5
    )
