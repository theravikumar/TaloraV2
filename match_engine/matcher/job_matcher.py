# match_engine/matcher/job_matcher.py
"""
Job Matcher - Matches resume against multiple jobs and ranks them.
"""

from typing import Dict, List
from .work_unit_matcher import work_unit_matcher


class JobMatcher:
    """
    Matches resume against jobs and ranks by fit.
    
    Process:
    1. For each job, match work units
    2. Calculate overall score
    3. Rank jobs by score
    4. Return top N matches
    """
    
    def __init__(self):
        self.wu_matcher = work_unit_matcher
    
    def match_jobs(
        self,
        resume_profile: Dict,
        jobs: List[Dict],
        top_n: int = 10
    ) -> List[Dict]:
        """
        Match resume against multiple jobs.
        
        Args:
            resume_profile: Normalized resume
            jobs: List of jobs with jd_profile
            top_n: Number of top matches to return
            
        Returns:
            List of job matches sorted by score (best first)
        """
        matches = []
        
        resume_units = resume_profile.get('work_units', [])
        
        for job in jobs:
            jd_profile = job.get('jd_profile')
            if not jd_profile:
                continue  # Skip jobs without normalized profile
            
            job_units = jd_profile.get('work_units', [])
            
            # Match work units
            match_result = self.wu_matcher.match_resume_to_job(
                resume_units,
                job_units
            )
            
            # Build result
            job_match = {
                'job': job,
                'score': match_result['overall_score'],
                'coverage': match_result['coverage'],
                'matched_count': match_result['matched_count'],
                'total_requirements': match_result['total_requirements'],
                'matches': match_result['matches'],
                'gaps': match_result['gaps']
            }
            
            matches.append(job_match)
        
        # Sort by score (descending)
        matches.sort(key=lambda x: x['score'], reverse=True)
        
        return matches[:top_n]
    
    def get_match_summary(self, job_match: Dict) -> str:
        """
        Get human-readable summary of a job match.
        
        Args:
            job_match: Result from match_jobs()
            
        Returns:
            Summary string
        """
        job = job_match['job']
        score = job_match['score']
        coverage = job_match['coverage']
        matched = job_match['matched_count']
        total = job_match['total_requirements']
        
        summary = []
        summary.append(f"Job: {job.get('job_title', 'Unknown')} at {job.get('company_name', 'Unknown')}")
        summary.append(f"Match Score: {score:.1%}")
        summary.append(f"Requirements Met: {matched}/{total} ({coverage:.1%})")
        
        if job_match['gaps']:
            summary.append(f"Gaps: {len(job_match['gaps'])} requirements not fully met")
        
        return '\n'.join(summary)


# Singleton
job_matcher = JobMatcher()
