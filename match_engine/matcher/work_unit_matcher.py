# match_engine/matcher/work_unit_matcher.py
"""
WorkUnit Matcher - Compares individual work units from resume vs job requirements.
Uses embedding similarity + LLM for intelligent matching.
"""

import numpy as np
from typing import Dict, List, Tuple

from shared.embeddings import embedding_generator


class WorkUnitMatcher:
    """
    Matches resume work units against job requirement work units.
    
    Scoring:
    - Embedding similarity: 0-1 (cosine similarity)
    - Domain match: +0.2 bonus if domains match
    - Proficiency match: +0.1 if resume >= job requirement
    - Tool overlap: +0.1 * (overlap_ratio)
    
    Final score: 0-1.5 (capped at 1.0)
    """
    
    def __init__(self):
        self.embedder = embedding_generator
    
    def match_units(
        self,
        resume_unit: Dict,
        job_unit: Dict
    ) -> Dict:
        """
        Match a single resume work unit against a job work unit.
        
        Args:
            resume_unit: Work unit from resume (evidence)
            job_unit: Work unit from job (requirement)
            
        Returns:
            Match result with score and explanation
        """
        # 1. Get embedding similarity
        resume_text = self._unit_to_text(resume_unit)
        job_text = self._unit_to_text(job_unit)
        
        embeddings = self.embedder.embed_batch([resume_text, job_text])
        resume_emb = embeddings[0]
        job_emb = embeddings[1]
        
        similarity = self._cosine_similarity(resume_emb, job_emb)
        
        # 2. Domain bonus
        domain_bonus = 0.2 if resume_unit.get('domain') == job_unit.get('domain') else 0.0
        
        # 3. Proficiency bonus
        prof_bonus = self._proficiency_bonus(
            resume_unit.get('proficiency', 'beginner'),
            job_unit.get('proficiency', 'beginner')
        )
        
        # 4. Tool overlap bonus
        tool_bonus = self._tool_overlap_bonus(
            resume_unit.get('tools', []),
            job_unit.get('tools', [])
        )
        
        # 5. Calculate final score
        raw_score = similarity + domain_bonus + prof_bonus + tool_bonus
        final_score =min(raw_score, 1.0)  # Cap at 1.0
        
        return {
            'score': final_score,
            'similarity': similarity,
            'domain_match': domain_bonus > 0,
            'proficiency_sufficient': prof_bonus > 0,
            'matching_tools': self._get_matching_tools(
                resume_unit.get('tools', []),
                job_unit.get('tools', [])
            ),
            'resume_unit': resume_unit,
            'job_unit': job_unit
        }
    
    def match_resume_to_job(
        self,
        resume_units: List[Dict],
        job_units: List[Dict]
    ) -> Dict:
        """
        Match all resume work units against all job work units.
        
        Strategy:
        - For each job requirement, find best matching resume evidence
        - Calculate coverage (% of job requirements matched)
        - Identify gaps (unmatched job requirements)
        
        Returns:
            Match result with overall score and detailed matches
        """
        matches = []
        
        # For each job requirement, find best resume match
        for job_unit in job_units:
            if job_unit.get('type') != 'requirement':
                continue
            
            best_match = None
            best_score = 0.0
            
            for resume_unit in resume_units:
                if resume_unit.get('type') != 'evidence':
                    continue
                
                match = self.match_units(resume_unit, job_unit)
                
                if match['score'] > best_score:
                    best_score = match['score']
                    best_match = match
            
            matches.append({
                'job_requirement': job_unit,
                'best_match': best_match,
                'score': best_score,
                'is_match': best_score >= 0.6  # 60% threshold
            })
        
        # Calculate statistics
        total_requirements = len([m for m in matches])
        matched_requirements = len([m for m in matches if m['is_match']])
        
        coverage = matched_requirements / total_requirements if total_requirements > 0 else 0.0
        
        # Find gaps (low-scoring requirements)
        gaps = [m for m in matches if not m['is_match']]
        
        return {
            'matches': matches,
            'coverage': coverage,
            'matched_count': matched_requirements,
            'total_requirements': total_requirements,
            'gaps': gaps,
            'overall_score': coverage  # Simple average for now
        }
    
    def _unit_to_text(self, unit: Dict) -> str:
        """Convert work unit to text for embedding"""
        parts = []
        
        if unit.get('action'):
            parts.append(unit['action'])
        if unit.get('object'):
            parts.append(unit['object'])
        if unit.get('tools'):
            parts.append(' '.join(unit['tools']))
        if unit.get('constraints'):
            parts.append(' '.join(unit['constraints']))
        if unit.get('domain'):
            parts.append(unit['domain'])
        
        return ' '.join(parts)
    
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return float(dot_product / (norm_a * norm_b))
    
    def _proficiency_bonus(self, resume_prof: str, job_prof: str) -> float:
        """Calculate bonus if resume proficiency meets job requirement"""
        prof_levels = {
            'beginner': 1,
            'intermediate': 2,
            'advanced': 3,
            'expert': 4
        }
        
        resume_level = prof_levels.get(resume_prof.lower(), 1)
        job_level = prof_levels.get(job_prof.lower(), 1)
        
        return 0.1 if resume_level >= job_level else 0.0
    
    def _tool_overlap_bonus(self, resume_tools: List[str], job_tools: List[str]) -> float:
        """Calculate bonus based on tool overlap"""
        if not job_tools:
            return 0.0
        
        resume_tools_lower = [t.lower() for t in resume_tools]
        job_tools_lower = [t.lower() for t in job_tools]
        
        overlap = len(set(resume_tools_lower) & set(job_tools_lower))
        ratio = overlap / len(job_tools_lower)
        
        return 0.1 * ratio
    
    def _get_matching_tools(self, resume_tools: List[str], job_tools: List[str]) -> List[str]:
        """Get list of matching tools"""
        resume_tools_lower = {t.lower() for t in resume_tools}
        job_tools_lower = {t.lower() for t in job_tools}
        
        matching = resume_tools_lower & job_tools_lower
        
        # Return original casing from resume
        return [t for t in resume_tools if t.lower() in matching]


# Singleton
work_unit_matcher = WorkUnitMatcher()
