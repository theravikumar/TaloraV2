# api/main.py
"""
Talora API - FastAPI Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.config import get_settings

settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="Talora API",
    description="AI-Powered Job Matching Platform",
    version="0.1.0",
    debug=settings.api_debug
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routers
from api.routes import auth, resume, jobs, match, autocomplete, smart_search

# Include routers
app.include_router(auth.router)
app.include_router(resume.router)
app.include_router(smart_search.router)
app.include_router(jobs.router)
app.include_router(match.router)
app.include_router(autocomplete.router)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "Talora API",
        "version": "0.1.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    from api.database import redis_client
    
    # Check Redis
    try:
        redis_client.ping()
        redis_ok = True
    except:
        redis_ok = False
    
    return {
        "status": "healthy" if redis_ok else "degraded",
        "database": "connected",
        "redis": "connected" if redis_ok else "disconnected"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_debug
    )
