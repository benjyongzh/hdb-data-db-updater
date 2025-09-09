"""
Vercel serverless entrypoint for FastAPI.
Maps all /api/* requests to the FastAPI app defined in main.py
"""

from main import app as fastapi_app  # FastAPI instance

# Vercel's Python runtime looks for a top-level `app` (ASGI/WSGI) in api/*.py
app = fastapi_app