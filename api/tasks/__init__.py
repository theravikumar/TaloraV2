# api/tasks/__init__.py
"""
Background tasks
"""
from api.tasks.resume_parser import parse_resume_task

__all__ = ["parse_resume_task"]
