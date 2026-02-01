# shared/llm/gemini_client.py
"""
Google Gemini API client for high-quality LLM inference.
Used for resume normalization and match explanations.
"""

import time
from typing import Optional
import google.generativeai as genai
from google.api_core import exceptions
from shared.config import settings


class GeminiClient:
    """
    Client for Google Gemini API with retry logic.
    """
    
    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not set in environment")
        
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
        self.max_retries = settings.MAX_RETRIES
    
    def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 4096,
    ) -> str:
        """
        Get completion from Gemini.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt (prepended to prompt)
            temperature: Sampling temperature
            max_tokens: Max tokens in response
            
        Returns:
            Generated text
            
        Raises:
            exceptions.ResourceExhausted: If rate limit exceeded
            Exception: If API error occurs
        """
        
        # Gemini doesn't have separate system prompt, so prepend
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        generation_config = genai.types.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        )
        
        for attempt in range(self.max_retries):
            try:
                response = self.model.generate_content(
                    full_prompt,
                    generation_config=generation_config,
                )
                
                return response.text.strip()
                
            except exceptions.ResourceExhausted as e:
                # Rate limit - don't retry, let caller fall back
                raise e
                
            except exceptions.GoogleAPIError as e:
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"Gemini API error, retrying in {wait_time}s... ({attempt + 1}/{self.max_retries})")
                    time.sleep(wait_time)
                else:
                    raise e
                    
            except Exception as e:
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"Unexpected error, retrying in {wait_time}s... ({attempt + 1}/{self.max_retries})")
                    time.sleep(wait_time)
                else:
                    raise e
        
        raise Exception("Max retries exceeded")
    
    def test_connection(self) -> bool:
        """Test if API key is valid"""
        try:
            self.complete("Say 'OK'", max_tokens=10)
            return True
        except Exception as e:
            print(f"Gemini connection test failed: {e}")
            return False
