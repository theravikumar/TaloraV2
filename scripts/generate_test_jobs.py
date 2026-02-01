# scripts/generate_test_jobs.py
"""
Generate test job data for development.
Use this while we refine the scraper to bypass AmbitionBox's anti-bot measures.
"""

import json
from datetime import datetime

TEST_JOBS = [
    {
        "job_id": "test-001",
        "job_url": "https://example.com/job/backend-python-1",
        "source": "test_data",
        "company_name": "TechCorp",
        "company_url": "https://techcorp.com",
        "job_title": "Senior Backend Engineer",
        "location": "Bangalore",
        "work_mode": "hybrid",
        "employment_type": "full-time",
        "salary": "₹25-35 LPA",
        "experience_level": "5-8 years",
        "posted_date": "2026-01-15",
        "scraped_at": datetime.now().isoformat(),
        "last_updated": datetime.now().isoformat(),
        "domain": "backend",
        "is_active": True,
        "extraction_quality": 1.0,
        "raw_text": """
Senior Backend Engineer - Python/FastAPI

Requirements:
- 5+ years building scalable backend APIs using Python
- Strong experience with FastAPI or Django
- Expert knowledge of PostgreSQL and database optimization
- Experience handling 1M+ requests/day in production
- Must have worked with Redis or similar caching solutions

Preferred:
- Experience with Kubernetes and Docker
- Knowledge of message queues (RabbitMQ, Kafka)
- Contributions to open-source projects

Responsibilities:
- Design and develop high-performance RESTful APIs
- Optimize database queries and caching strategies
- Mentor junior developers
- Participate in system architecture decisions
        """,
    },
    {
        "job_id": "test-002",
        "job_url": "https://example.com/job/ml-engineer-1",
        "source": "test_data",
        "company_name": "AI Startup",
        "company_url": "https://aistartup.com",
        "job_title": "Machine Learning Engineer",
        "location": "Remote",
        "work_mode": "remote",
        "employment_type": "full-time",
        "salary": "₹30-45 LPA",
        "experience_level": "3-6 years",
        "posted_date": "2026-01-20",
        "scraped_at": datetime.now().isoformat(),
        "last_updated": datetime.now().isoformat(),
        "domain": "ML",
        "is_active": True,
        "extraction_quality": 1.0,
        "raw_text": """
Machine Learning Engineer

Requirements:
- 3+ years experience in ML model development and deployment
- Strong Python programming skills
- Experience with TensorFlow or PyTorch
- Knowledge of NLP and transformers
- Proven track record of deploying models to production

Preferred:
- PhD in Computer Science or related field
- Experience with LLM fine-tuning
- Publications in top-tier conferences

Responsibilities:
- Develop and deploy ML models for NLP tasks
- Fine-tune large language models
- Build ML pipelines for data processing
- Collaborate with product team on ML features
        """,
    },
{
        "job_id": "test-003",
        "job_url": "https://example.com/job/frontend-react-1",
        "source": "test_data",
        "company_name": "WebFlow Inc",
        "company_url": "https://webflow.com",
        "job_title": "Frontend Developer - React",
        "location": "Pune",
        "work_mode": "onsite",
        "employment_type": "full-time",
        "salary": "₹15-25 LPA",
        "experience_level": "2-4 years",
        "posted_date": "2026-01-25",
        "scraped_at": datetime.now().isoformat(),
        "last_updated": datetime.now().isoformat(),
        "domain": "frontend",
        "is_active": True,
        "extraction_quality": 1.0,
        "raw_text": """
Frontend Developer - React

Requirements:
- 2+ years building modern web applications with React
- Strong JavaScript/TypeScript skills
- Experience with state management (Redux, Context API)
- Knowledge of responsive design and CSS frameworks
- Understanding of web performance optimization

Preferred:
- Experience with Next.js
- Knowledge of testing frameworks (Jest, React Testing Library)
- Familiarity with GraphQL

Responsibilities:
- Build responsive user interfaces with React
- Implement complex state management logic
- Optimize application performance
- Write unit and integration tests
        """,
    },
]

def save_test_jobs():
    """Save test jobs to data directory"""
    from pathlib import Path
    output_file = Path(__file__).parent.parent / "data" / "test_jobs.json"
    
    with open(output_file, 'w') as f:
        json.dump(TEST_JOBS, f, indent=2)
    
    print(f"[OK] Saved {len(TEST_JOBS)} test jobs to {output_file}")
    return TEST_JOBS

if __name__ == "__main__":
    save_test_jobs()
