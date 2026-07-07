"""Vercel serverless entry point.

Vercel's Python runtime looks for an ASGI `app` in files under api/.
All /api/* requests are rewritten to this function (see vercel.json); the
FastAPI app's own routes already start with /api/, and Vercel passes the
original request path through, so routing just works.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.main import app  # noqa: E402, F401
