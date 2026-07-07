"""FastAPI app entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .crud_routes import router as beans_router
from .db import init_db
from .suggest_routes import router as suggest_router

# Create tables on import so the on-disk SQLite DB is always ready — this runs
# under uvicorn, under the TestClient, and on any direct import. create_all is
# idempotent, so it's safe to call every startup; existing data is untouched.
init_db()

app = FastAPI(title="Coffee Bean Zine")

# Vite proxies /api in dev, but allow direct localhost access too.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(beans_router)
app.include_router(suggest_router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
