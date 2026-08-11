from app.routers.health import router as health_router
from app.routers.trails import router as trails_router
from app.routers.hikes import router as hikes_router

__all__ = ["health_router", "trails_router", "hikes_router"]
