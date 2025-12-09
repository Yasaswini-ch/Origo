from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import api as api_router

app = FastAPI(title='origo-fallback-backend')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)

@app.get('/health')
def health():
    return {'status': 'ok'}

app.include_router(api_router.router, prefix='/api')
