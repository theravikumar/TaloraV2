# shared/config/settings.py
"""
Configuration management using environment variables.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
load_dotenv()


class Settings:
    """
    Centralized configuration for the entire platform.
    All values loaded from .env with sensible defaults.
    """
    
    # ===== LLM Configuration =====
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.2:latest")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    # LLM request configuration
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "30"))
    
    # ===== Paths =====
    PROJECT_ROOT: Path = Path(__file__).parent.parent.parent
    DATA_DIR: Path = PROJECT_ROOT / os.getenv("DATA_DIR", "./data")
    DB_PATH: Path = PROJECT_ROOT / os.getenv("DB_PATH", "./data/jobs.db")
    FAISS_INDEX_PATH: Path = PROJECT_ROOT / os.getenv("FAISS_INDEX_PATH", "./data/faiss_index")
    CACHE_DIR: Path = DATA_DIR / "cache"
    
    # Ensure directories exist
    @classmethod
    def ensure_dirs(cls):
        """Create all necessary directories"""
        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)
        cls.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cls.FAISS_INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    # ===== Embedding Configuration =====
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-mpnet-base-v2")
    EMBEDDING_DIM: int = int(os.getenv("EMBEDDING_DIM", "768"))
    EMBEDDING_DEVICE: str = os.getenv("EMBEDDING_DEVICE", "cpu")  # or "cuda"
    
    # ===== Scraping Configuration =====
    MAX_COMPANIES: int = int(os.getenv("MAX_COMPANIES", "10"))
    MAX_JOBS_PER_COMPANY: int = int(os.getenv("MAX_JOBS_PER_COMPANY", "50"))
    SCRAPING_DELAY: float = float(os.getenv("SCRAPING_DELAY", "2.0"))  # seconds
    USER_AGENT: str = os.getenv(
        "USER_AGENT",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
    )
    PLAYWRIGHT_HEADLESS: bool = os.getenv("PLAYWRIGHT_HEADLESS", "true").lower() == "true"
    PLAYWRIGHT_TIMEOUT: int = int(os.getenv("PLAYWRIGHT_TIMEOUT", "30000"))  # ms
    
    # ===== Matching Configuration =====
    TOP_K_SIMILAR: int = int(os.getenv("TOP_K_SIMILAR", "5"))
    TOP_N_JOBS: int = int(os.getenv("TOP_N_JOBS", "50"))
    MIN_MATCH_SCORE: float = float(os.getenv("MIN_MATCH_SCORE", "0.5"))
    
    # Coverage thresholds
    MIN_REQUIRED_COVERAGE: float = 0.7  # 70% of required expectations
    MIN_PREFERRED_COVERAGE: float = 0.3  # 30% of preferred expectations
    
    # ===== Validation ===== 
    @classmethod
    def validate(cls):
        """Validate critical configuration"""
        errors = []
        
        if not cls.GROQ_API_KEY and not cls.GEMINI_API_KEY:
            errors.append("At least one LLM API key (GROQ or GEMINI) must be set")
        
        if cls.EMBEDDING_DIM not in [384, 768, 1024]:
            errors.append(f"Invalid EMBEDDING_DIM: {cls.EMBEDDING_DIM}")
        
        if errors:
            raise ValueError(f"Configuration errors:\n" + "\n".join(f"- {e}" for e in errors))
    
    # ===== Display =====
    @classmethod
    def display(cls):
        """Print current configuration (safe for logging)"""
        print("=" * 60)
        print("CONFIGURATION")
        print("=" * 60)
        print(f"Project Root: {cls.PROJECT_ROOT}")
        print(f"Data Dir: {cls.DATA_DIR}")
        print(f"Database: {cls.DB_PATH}")
        print(f"FAISS Index: {cls.FAISS_INDEX_PATH}")
        print()
        print(f"Groq API: {'[OK] Set' if cls.GROQ_API_KEY else '[ERROR] Missing'}")
        print(f"Gemini API: {'[OK] Set' if cls.GEMINI_API_KEY else '[ERROR] Missing'}")
        print()
        print(f"Embedding Model: {cls.EMBEDDING_MODEL}")
        print(f"Embedding Device: {cls.EMBEDDING_DEVICE}")
        print()
        print(f"Max Companies: {cls.MAX_COMPANIES}")
        print(f"Max Jobs/Company: {cls.MAX_JOBS_PER_COMPANY}")
        print(f"Top N Jobs: {cls.TOP_N_JOBS}")
        print("=" * 60)


# Singleton instance
settings = Settings()

# Ensure directories on import
settings.ensure_dirs()
