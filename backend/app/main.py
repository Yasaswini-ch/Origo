"""Main FastAPI application entrypoint.

This module configures the application, CORS, database, and includes routers.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app import models as all_models  # ensure all models are registered with Base
from app.routes.items import router as items_router
from app.routers.analytics import router as analytics_router
from app.routers.projects import router as projects_router
from app.routers.feedback import router as feedback_router
from app.routers.admin import router as admin_router
from app.routers.ml import router as ml_router


app = FastAPI(title='generic-saas-app')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


"""Create all database tables on startup so the SQLite file is ready to use.

Importing the legacy and analytics models above ensures that SQLAlchemy's
metadata registry is fully populated before calling ``create_all``.
"""
Base.metadata.create_all(bind=engine)

# Include item CRUD routes and new analytics-related routers.
app.include_router(items_router)
app.include_router(analytics_router, prefix="/api/analytics", tags=["analytics"])
app.include_router(projects_router, prefix="/api/projects", tags=["projects"])
app.include_router(feedback_router, prefix="/api/feedback", tags=["feedback"])
app.include_router(admin_router, prefix="/api/admin", tags=["admin"])
app.include_router(ml_router, prefix="/api/ml", tags=["ml"])
