# api/routes/match.py
"""
Matching routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.database import get_db
from api.models.match import MatchRequest, MatchResponse, CompareRequest, CompareResponse, MatchDetail
from api.services.match_service import MatchService
from api.utils.errors import ParsingError

router = APIRouter(prefix="/api/match", tags=["match"])
match_service = MatchService()


@router.post("", response_model=MatchResponse)
def match_resume(request: MatchRequest, db: Session = Depends(get_db)):
    """Match resume to jobs"""
    try:
        matches = match_service.match_resume_to_jobs(
            db,
            request.resume_id,
            request.job_filters,
            request.top_n
        )
        
        return MatchResponse(matches=[MatchDetail(**m) for m in matches])
        
    except ParsingError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/compare", response_model=CompareResponse)
def compare_resumes(request: CompareRequest, db: Session = Depends(get_db)):
    """Compare multiple resumes"""
    comparison = match_service.compare_resumes(
        db,
        request.resume_ids,
        request.job_filters
    )
    
    return CompareResponse(comparison=comparison)
