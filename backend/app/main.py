import sys
from pathlib import Path

# Ensure project root is always on sys.path
_root = str(Path(__file__).resolve().parent.parent.parent)
if _root not in sys.path:
    sys.path.insert(0, _root)

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.core.config import settings
from backend.app.database.connection import init_db, SessionLocal
from backend.app.database.seed import seed_demo_data_if_empty
from backend.app.api.routes import health, executions, memories, dashboard


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite database schema
    init_db()
    
    # Auto-seed initial multi-agent executions if database is empty (e.g. after ephemeral cloud restarts)
    db = SessionLocal()
    try:
        seed_demo_data_if_empty(db)
    finally:
        db.close()
        
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description="ContextCraft - Smart Memory-Orchestration Middleware for LangGraph Multi-Agent Systems",
    version="1.0.0",
    lifespan=lifespan,
)

# Enable CORS for frontend development and production deployments
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=r"^https?:\/\/.*\.vercel\.app$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount versioned API routes
app.include_router(health.router, prefix=settings.API_V1_PREFIX)
app.include_router(executions.router, prefix=settings.API_V1_PREFIX)
app.include_router(memories.router, prefix=settings.API_V1_PREFIX)
app.include_router(dashboard.router, prefix=settings.API_V1_PREFIX)


@app.get("/")
def root():
    return {
        "service": settings.APP_NAME,
        "docs": "/docs",
        "health": f"{settings.API_V1_PREFIX}/health",
        "mock_mode": settings.MOCK_MODE,
    }
