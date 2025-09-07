"""
Vercel serverless entrypoint for FastAPI.
Maps all /api/* requests to the FastAPI app defined in main.py
"""

from main import app  # FastAPI instance

