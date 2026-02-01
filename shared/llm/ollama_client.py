# shared/llm/ollama_client.py
"""
Ollama local LLM client for offline fallback.
"""

import time
import requests
from typing import Optional
from shared.config import settings


class OllamaClient:
    """
    Client for local Ollama server.
    """
    
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_MODEL
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
        Get completion from Ollama.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature
            max_tokens: Max tokens in response
            
        Returns:
            Generated text
            
        Raises:
            ConnectionError: If Ollama server not running
            Exception:  If API error occurs
        """
        
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "temperature": temperature,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
            }
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    url,
                    json=payload,
                    timeout=self.timeout,
                )
                response.raise_for_status()
                
                result = response.json()
                return result["response"].strip()
                
            except requests.ConnectionError as e:
                if attempt < self.max_retries - 1:
                    print(f"Ollama not running? Retrying... ({attempt + 1}/{self.max_retries})")
                    time.sleep(2)
                else:
                    raise ConnectionError(
                        f"Could not connect to Ollama at {self.base_url}. "
                        "Make sure Ollama is running: ollama serve"
                    )
                    
            except requests.Timeout:
                if attempt < self.max_retries - 1:
                    print(f"Ollama timeout, retrying... ({attempt + 1}/{self.max_retries})")
                    time.sleep(2)
                else:
                    raise TimeoutError("Ollama request timed out")
                    
            except Exception as e:
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"Unexpected error, retrying in {wait_time}s... ({attempt + 1}/{self.max_retries})")
                    time.sleep(wait_time)
                else:
                    raise e
        
        raise Exception("Max retries exceeded")
    
    def test_connection(self) -> bool:
        """Test if Ollama server is running"""
        try:
            self.complete("Say 'OK'", max_tokens=10)
            return True
        except Exception as e:
            print(f"Ollama connection test failed: {e}")
            return False
