# job_pipeline/normalizers/job_normalizer.py
"""
Job normalization using LLM extraction.
Converts raw job description text into structured JobDescriptionProfile.
"""

import json
from typing import Dict
from shared.llm import llm_router
from shared.schema import JobDescriptionProfile
from .prompts import JOB_NORMALIZATION_PROMPT


class JobNormalizer:
    """
    Normalizes raw job descriptions into structured profiles.
    """
    
    def __init__(self):
        self.llm = llm_router
    
    def normalize(self, raw_jd_text: str) -> JobDescriptionProfile:
        """
        Normalize raw JD text into structured profile.
        
        Args:
            raw_jd_text: Raw job description text
            
        Returns:
            JobDescriptionProfile with extracted expectations
            
        Raises:
            ValueError: If LLM returns invalid JSON
            Exception: If normalization fails
        """
        
        # Build prompt
        prompt = JOB_NORMALIZATION_PROMPT.format(jd_text=raw_jd_text)
        
        # Get LLM response
        try:
            response = self.llm.complete(
                prompt=prompt,
                use_case="job_extraction",
                temperature=0.1,
                max_tokens=4096,
            )
            
            # Parse JSON
            try:
                profile = json.loads(response)
            except json.JSONDecodeError as e:
                # Try to extract JSON from response
                import re
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    profile = json.loads(json_match.group(0))
                else:
                    raise ValueError(f"LLM did not return valid JSON: {response[:500]}")
            
            # Validate structure
            self._validate_profile(profile)
            
            return profile
            
        except Exception as e:
            print(f"Error normalizing JD: {e}")
            raise e
    
    def _validate_profile(self, profile: Dict):
        """Basic validation of profile structure"""
        required_keys = ["required_expectations", "preferred_expectations"]
        for key in required_keys:
            if key not in profile:
                raise ValueError(f"Missing required key: {key}")
        
        # Validate expectations structure
        for exp_list in [profile["required_expectations"], profile["preferred_expectations"]]:
            if not isinstance(exp_list, list):
                raise ValueError("Expectations must be lists")
            
            for exp in exp_list:
                if "work_units" not in exp:
                    raise ValueError("Expectation missing work_units")
                
                for wu in exp["work_units"]:
                    required_wu_keys = ["type", "action", "object", "tools", "constraints"]
                    for k in required_wu_keys:
                        if k not in wu:
                            raise ValueError(f"WorkUnit missing key: {k}")


# Singleton
job_normalizer = JobNormalizer()
