# match_engine/resume/resume_normalizer.py
"""
Resume Normalizer - Extracts structured data from resumes using LLM.
Converts PDF resume → ResumeProfile with WorkUnits
"""

import PyPDF2
from typing import Dict, List
from pathlib import Path
import json
import re

from shared.llm import llm_router
from shared.schema import ResumeProfile, WorkUnit


class ResumeNormalizer:
    """
    Normalizes resumes into structured ResumeProfile objects.
    
    Process:
    1. Extract text from PDF
    2. Use LLM to parse resume structure
    3. Extract work units (evidence of skills/experience)
    4. Validate and return ResumeProfile
    """
    
    def __init__(self):
        self.llm = llm_router
    
    def normalize_from_pdf(self, pdf_path: str) -> Dict:
        """
        Normalize a PDF resume.
        
        Args:
            pdf_path: Path to PDF resume file
            
        Returns:
            ResumeProfile dictionary
        """
        # 1. Extract text
        resume_text = self._extract_text_from_pdf(pdf_path)
        
        # 2. Normalize with LLM
        profile = self.normalize_from_text(resume_text)
        
        return profile
    
    def normalize_from_text(self, resume_text: str) -> Dict:
        """
        Normalize resume text using LLM.
        
        Args:
            resume_text: Raw resume text
            
        Returns:
            ResumeProfile dictionary
        """
        # Build prompt
        prompt = self._build_resume_prompt(resume_text)
        
        # Get LLM response (using Groq since Gemini quota exhausted)
        response = self.llm.complete(
            prompt,
            use_case="job_extraction"  # Routes to Groq
        )
        
        # Parse JSON response
        profile = self._parse_llm_response(response)
        
        return profile
    
    def _extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF file"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                text_parts = []
                for page in pdf_reader.pages:
                    text_parts.append(page.extract_text())
                
                full_text = "\n\n".join(text_parts)
                
                # Clean up text
                full_text = re.sub(r'\s+', ' ', full_text)
                full_text = full_text.strip()
                
                return full_text
                
        except Exception as e:
            raise Exception(f"Failed to extract text from PDF: {e}")
    
    def _build_resume_prompt(self, resume_text: str) -> str:
        """Build LLM prompt for resume parsing"""
        return f"""Extract structured information from this resume and return ONLY valid JSON.

RESUME TEXT:
{resume_text}

Extract the following information and return as JSON:

{{
  "name": "Full name",
  "email": "email@example.com",
  "phone": "phone number",
  "years_of_experience": 3.5,
  "current_role": "Current job title",
  "skills": ["skill1", "skill2", "skill3"],
  "education": [
    {{
      "degree": "Degree name",
      "institution": "University name",
      "year": 2021,
      "field": "Field of study"
    }}
  ],
  "work_experience": [
    {{
      "title": "Job title",
      "company": "Company name",
      "duration": "Aug 2024 - Present",
      "description": "Brief description of role and achievements"
    }}
  ],
  "work_units": [
    {{
      "type": "evidence",
      "action": "developed|implemented|designed|led|etc",
      "object": "what was worked on",
      "tools": ["tool1", "tool2"],
      "constraints": ["constraint1"],
      "impact": "measurable impact if mentioned",
      "domain": "backend|frontend|ML|devops|etc",
      "proficiency": "beginner|intermediate|advanced|expert"
    }}
  ]
}}

CRITICAL INSTRUCTIONS:
1. Extract ALL work units from experience section
2. Each project/achievement = separate work unit
3. Include tools/technologies used
4. Set proficiency based on years and depth of experience
5. Domain should be: backend, frontend, ML, devops, fullstack, mobile, or general
6. Return ONLY the JSON, no other text

JSON:"""
    
    def _parse_llm_response(self, response: str) -> Dict:
        """Parse and validate LLM JSON response"""
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
            else:
                json_str = response
            
            # Parse JSON
            profile = json.loads(json_str)
            
            # Basic validation
            required_fields = ['name', 'work_units']
            for field in required_fields:
                if field not in profile:
                    raise ValueError(f"Missing required field: {field}")
            
            # Ensure work_units is list
            if not isinstance(profile['work_units'], list):
                profile['work_units'] = []
            
            # Set defaults
            profile.setdefault('years_of_experience', 0)
            profile.setdefault('skills', [])
            profile.setdefault('education', [])
            profile.setdefault('work_experience', [])
            
            return profile
            
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse LLM response as JSON: {e}\nResponse: {response}")
        except Exception as e:
            raise Exception(f"Failed to parse resume: {e}")


# Singleton
resume_normalizer = ResumeNormalizer()
