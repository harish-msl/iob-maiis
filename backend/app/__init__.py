"""
IOB MAIIS - Backend Application Package
Multimodal AI-Enabled Information System

This package contains the FastAPI backend application for IOB MAIIS,
including API routes, services, models, and core functionality.

Created: 2025-01-17
Python: 3.12
FastAPI: 0.115.0
"""

__version__ = "1.0.0"
__author__ = "IOB MAIIS Team"
__description__ = "Multimodal AI-Enabled Information System - Backend"

# Import core components for easier access
from app.core.config import settings
from app.core.logging import logger

__all__ = ["settings", "logger", "__version__"]
