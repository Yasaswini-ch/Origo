"""Main FastAPI application entrypoint.

This module configures the application, CORS, database, and includes routers.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.models.models import Base, engine
from app.routes.items import router as items_router


app = FastAPI(title='generic-saas-app')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


# Create all database tables on startup so the SQLite file is ready to use.
Base.metadata.create_all(bind=engine)

# Include item CRUD routes under the /api/items prefix.
app.include_router(items_router)
