from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.generate import router as generate_router
from app.routes.component import router as component_router
from app.routes.preview import router as preview_router

app = FastAPI(title='micro-saas-backend')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(generate_router)
app.include_router(component_router)
app.include_router(preview_router)
