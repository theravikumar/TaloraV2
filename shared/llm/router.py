# shared/llm/router.py
"""
Unified LLM router with smart fallback logic.
Routes requests to appropriate LLM based on use case and availability.
"""

from typing import Optional, Literal
from .groq_client import GroqClient
from .gemini_client import GeminiClient
from .ollama_client import OllamaClient


UseCase = Literal["job_extraction", "resume_normalization", "match_explanation", "resume_feedback"]


class LLMRouter:
    """
    Smart LLM router that:
    1. Routes to appropriate LLM based on use case
    2. Falls back gracefully on errors
    3. Optimizes for cost and speed
    
    Routing strategy:
    - job_extraction: Groq (fast, free) → Ollama (offline)
    - resume_normalization: Gemini (accurate) → Ollama (offline)
    - match_explanation: Gemini (accurate, low volume) → Ollama
    - resume_feedback: Gemini (accurate) → Ollama
    """
    
    def __init__(self):
        self.groq = None
        self.gemini = None
        self.ollama = None
        
        # Lazy initialization
        self._init_clients()
    
    def _init_clients(self):
        """Initialize available LLM clients"""
        try:
            self.groq = GroqClient()
            print("[OK] Groq client initialized")
        except Exception as e:
            print(f"[ERROR] Groq unavailable: {e}")
        
        try:
            self.gemini = GeminiClient()
            print("[OK] Gemini client initialized")
        except Exception as e:
            print(f"[ERROR] Gemini unavailable: {e}")
        
        try:
            self.ollama = OllamaClient()
            # Don't test connection (Ollama might not be running yet)
            print("[OK] Ollama client initialized (not tested)")
        except Exception as e:
            print(f"[ERROR] Ollama unavailable: {e}")
    
    def complete(
        self,
        prompt: str,
        use_case: UseCase = "job_extraction",
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 4096,
    ) -> str:
        """
        Get LLM completion with automatic fallback.
        
        Args:
            prompt: User prompt
            use_case: What this is for (determines routing)
            system_prompt: Optional system prompt
            temperature: Sampling temperature
            max_tokens: Max tokens in response
            
        Returns:
            Generated text
            
        Raises:
            Exception: If all LLMs fail
        """
        
        if use_case == "job_extraction":
            return self._route_job_extraction(prompt, system_prompt, temperature, max_tokens)
        elif use_case in ["resume_normalization", "match_explanation", "resume_feedback"]:
            return self._route_high_quality(prompt, system_prompt, temperature, max_tokens)
        else:
            raise ValueError(f"Unknown use case: {use_case}")
    
    def _route_job_extraction(
        self, 
        prompt: str, 
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int,
    ) -> str:
        """
        Route job extraction: Groq (fast) → Ollama (offline)
        """
        errors = []
        
        # Try Groq first (fastest, free)
        if self.groq:
            try:
                return self.groq.complete(prompt, system_prompt, temperature, max_tokens)
            except Exception as e:
                errors.append(f"Groq failed: {e}")
                print(f"Groq failed, falling back to Ollama...")
        
        # Fallback to Ollama
        if self.ollama:
            try:
                return self.ollama.complete(prompt, system_prompt, temperature, max_tokens)
            except Exception as e:
                errors.append(f"Ollama failed: {e}")
        
        raise Exception(f"All LLMs failed for job_extraction:\n" + "\n".join(errors))
    
    def _route_high_quality(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int,
    ) -> str:
        """
        Route high-quality tasks: Gemini (accurate) → Ollama (offline)
        """
        errors = []
        
        # Try Gemini first (most accurate for resume/matching)
        if self.gemini:
            try:
                return self.gemini.complete(prompt, system_prompt, temperature, max_tokens)
            except Exception as e:
                errors.append(f"Gemini failed: {e}")
                print(f"Gemini failed, falling back to Ollama...")
        
        # Fallback to Ollama
        if self.ollama:
            try:
                return self.ollama.complete(prompt, system_prompt, temperature, max_tokens)
            except Exception as e:
                errors.append(f"Ollama failed: {e}")
        
        raise Exception(f"All LLMs failed for high-quality task:\n" + "\n".join(errors))
    
    def test_all(self):
        """Test all available LLM clients"""
        print("\n" + "=" * 60)
        print("TESTING LLM CLIENTS")
        print("=" * 60)
        
        if self.groq:
            print("Testing Groq...", end=" ")
            if self.groq.test_connection():
                print("PASS")
            else:
                print("FAIL")
        
        if self.gemini:
            print("Testing Gemini...", end=" ")
            if self.gemini.test_connection():
                print("PASS")
            else:
                print("FAIL")
        
        if self.ollama:
            print("Testing Ollama...", end=" ")
            if self.ollama.test_connection():
                print("PASS")
            else:
                print("FAIL (might not be running)")
        
        print("=" * 60 + "\n")


# Singleton instance
llm_router = LLMRouter()
