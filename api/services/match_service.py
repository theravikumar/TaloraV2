# api/services/match_service.py
"""
Resume-job matching service
"""
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from api.database.models import Resume, MatchResult
from api.services.job_service import JobService
from api.utils.errors import ParsingError

# Import existing matcher
from match_engine.matcher import JobMatcher


class MatchService:
    """Service for matching resumes to jobs"""
    
    def __init__(self):
        self.job_service = JobService()
        self.matcher = JobMatcher()
    
    def match_resume_to_jobs(
        self,
        db: Session,
        resume_id: str,
        job_filters: Dict[str, Any] = None,
        top_n: int = 10,
        use_cache: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Match resume to jobs using existing matcher.
        
        Returns top N matches with scores and gaps.
        """
        # Get resume
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            raise ParsingError("Resume not found")
        
        # Check cache
        if use_cache:
            cached_matches = db.query(MatchResult).filter(
                MatchResult.resume_id == resume_id
            ).all()
            
            if cached_matches:
                # Return cached results
                return self._format_cached_matches(cached_matches, top_n)
        
        # Get jobs (with filters if provided)
        if job_filters:
            job_results = self.job_service.search_jobs(**job_filters)
            jobs = job_results["jobs"]
        else:
            jobs = self.job_service.get_all_jobs()
        
        # Match using existing matcher
        matches = self.matcher.match_jobs(resume.parsed_data, jobs)
        
        # Sort by score
        matches.sort(key=lambda x: x["score"], reverse=True)
        
        # Cache results
        self._cache_matches(db, resume_id, matches)
        
        # Return top N
        return matches[:top_n]
    
    def _cache_matches(self, db: Session, resume_id: str, matches: List[Dict[str, Any]]):
        """Cache match results in database"""
        # Delete old cache
        db.query(MatchResult).filter(MatchResult.resume_id == resume_id).delete()
        
        # Insert new results
        for match in matches[:50]:  # Cache top 50
            result = MatchResult(
                resume_id=resume_id,
                job_id=match["job"]["id"],
                match_score=match["score"],
                matched_requirements=match.get("matched_requirements", []),
                gaps=match.get("gaps", [])
            )
            db.add(result)
        
        db.commit()
    
    def _format_cached_matches(self, cached: List[MatchResult], top_n: int) -> List[Dict[str, Any]]:
        """Format cached matches for response"""
        matches = []
        for result in sorted(cached, key=lambda x: x.match_score, reverse=True)[:top_n]:
            job = self.job_service.get_job_by_id(result.job_id)
            if job:
                matches.append({
                    "job": job,
                    "match_score": result.match_score,
                    "matched_count": len(result.matched_requirements) if result.matched_requirements else 0,
                    "total_requirements": job["requirements_count"],
                    "gaps": result.gaps or []
                })
        
        return matches
    
    def compare_resumes(
        self,
        db: Session,
        resume_ids: List[str],
        job_filters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Compare multiple resumes against same jobs"""
        comparison = {}
        
        for resume_id in resume_ids:
            matches = self.match_resume_to_jobs(db, resume_id, job_filters, top_n=10)
            
            resume = db.query(Resume).filter(Resume.id == resume_id).first()
            if resume:
                comparison[resume_id] = {
                    "name": resume.parsed_data.get("name", "Unknown"),
                    "top_matches": matches[:5],
                    "avg_score": sum(m["match_score"] for m in matches) / len(matches) if matches else 0
                }
        
        return comparison
