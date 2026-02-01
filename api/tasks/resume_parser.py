# api/tasks/resume_parser.py
"""
Background task for async resume parsing
"""
import asyncio
import logging
from pathlib import Path
from datetime import datetime
from sqlalchemy.orm import Session

from api.database.models import ParsingJob, Resume
from api.database.postgres import SessionLocal
from api.utils.errors import ParsingError, ERROR_MESSAGES
from api.utils.file_validation import calculate_file_hash

# Import existing resume normalizer
from match_engine.resume.resume_normalizer import ResumeNormalizer
from shared.llm.router import llm_router

logger = logging.getLogger(__name__)


async def parse_resume_task(job_id: str, file_path: Path, session_id: str = None, user_id: str = None):
    """
    Async task to parse resume PDF using existing backend.
    
    Updates ParsingJob status in database.
    """
    db: Session = SessionLocal()
    
    try:
        # Get parsing job
        job = db.query(ParsingJob).filter(ParsingJob.id == job_id).first()
        if not job:
            logger.error(f"Parsing job {job_id} not found")
            return
        
        # Update status
        job.status = "processing"
        db.commit()
        
        # Initialize resume normalizer
        normalizer = ResumeNormalizer()
        
        # Parse resume with LLM fallback
        parsed_resume = None
        last_error = None
        
        # Try each LLM provider
        for provider_name in ["groq", "gemini", "ollama"]:
            try:
                logger.info(f"Trying {provider_name} for resume parsing")
                
                # Set provider in router
                llm_router.set_provider(provider_name)
                
                # Parse resume
                parsed_resume = await asyncio.to_thread(
                    normalizer.normalize_from_file,
                    str(file_path)
                )
                
                if parsed_resume:
                    logger.info(f"Resume parsed successfully with {provider_name}")
                    break
                    
            except Exception as e:
                logger.warning(f"{provider_name} failed: {str(e)}")
                last_error = e
                continue
        
        if not parsed_resume:
            raise ParsingError(f"All LLM providers failed: {str(last_error)}")
        
        # Calculate file hash
        with open(file_path, "rb") as f:
            file_hash = calculate_file_hash(f.read())
        
        # Save resume to database
        resume = Resume(
            user_id=user_id,
            filename=file_path.name,
            pdf_path=str(file_path),
            file_hash=file_hash,
            parsed_data=parsed_resume
        )
        db.add(resume)
        db.commit()
        db.refresh(resume)
        
        # Update parsing job - completed
        job.status = "completed"
        job.result = {
            "resume_id": resume.id,
            "name": parsed_resume.get("name"),
            "years_of_experience": parsed_resume.get("years_of_experience"),
            "skills": parsed_resume.get("skills", [])[:10],  # Top 10 skills
            "work_units": len(parsed_resume.get("work_units", []))
        }
        job.completed_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Resume parsing completed: {job_id}")
        
    except Exception as e:
        logger.error(f"Resume parsing failed: {job_id}, error: {str(e)}")
        
        # Update job status - failed
        if job:
            job.status = "failed"
            job.error_message = ERROR_MESSAGES["parse_failed"]
            job.completed_at = datetime.utcnow()
            db.commit()
    
    finally:
        db.close()
