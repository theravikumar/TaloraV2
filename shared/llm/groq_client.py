# shared/llm/groq_client.py
"""
Groq API client for fast, free LLM inference.
Used primarily for job extraction.
"""

import time
from typing import Optional
from groq import Groq, RateLimitError, APIError
from shared.config import settings


class GroqClient:
    """
    Client for Groq API with retry logic and error handling.
    """
    
    def __init__(self):
        if not settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not set in environment")
        
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL
        self.max_retries = settings.MAX_RETRIES
        self.timeout = settings.REQUEST_TIMEOUT
    
    def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 4096,
    ) -> str:
        """
        Get completion from Groq.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Max tokens in response
            
        Returns:
            Generated text
            
        Raises:
            RateLimitError: If rate limit exceeded (caller should fallback)
            APIError: If API error occurs
        """
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    timeout=self.timeout,
                )
                
                return response.choices[0].message.content.strip()
                
            except RateLimitError as e:
                # Don't retry on rate limit - let caller fallback to another LLM
                raise e
                
            except APIError as e:
                if attempt < self.max_retries - 1:
                    # Exponential backoff
                    wait_time = 2 ** attempt
                    print(f"Groq API error, retrying in {wait_time}s... ({attempt + 1}/{self.max_retries})")
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
            print(f"Groq connection test failed: {e}")
            return False
