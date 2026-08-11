from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base
from app.routers import health_router, trails_router, hikes_router

# Initialize database tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Application Backend for JEJAK (HikerGuard GeoAI) mobile application.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(health_router)
app.include_router(trails_router)
app.include_router(hikes_router)


@app.get("/")
def root():
    return {
        "message": "Welcome to JEJAK Application Backend API",
        "docs": "/docs",
        "health": "/health"
    }
