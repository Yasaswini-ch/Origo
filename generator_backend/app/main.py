from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from time import perf_counter

from .routes.generate import router as generate_router
from .routes.component import router as component_router
from .routes.preview import router as preview_router
from .routes.projects import router as projects_router
from .routes.quality import router as quality_router
from .routers.validate_zip import router as validate_zip_router
from .routes.phase5 import router as phase5_router
from .utils.errors import OrigoError

logging.basicConfig(level=logging.INFO, format='%(levelname)s [%(name)s] %(message)s')
logger = logging.getLogger("app")

app = FastAPI(title='Origo Generator API')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start = perf_counter()
        response = None
        try:
            response = await call_next(request)
            return response
        finally:
            duration_ms = (perf_counter() - start) * 1000
            status = getattr(response, 'status_code', 'NA')
            logger.info(f"%s %s -> %s (%.1fms)", request.method, request.url.path, status, duration_ms)


app.add_middleware(RequestLoggingMiddleware)

app.include_router(generate_router)
app.include_router(component_router)
app.include_router(preview_router)
app.include_router(projects_router)
app.include_router(quality_router)
app.include_router(phase5_router)
app.include_router(validate_zip_router)


@app.exception_handler(OrigoError)
async def handle_origo_error(_, exc: OrigoError):
    return JSONResponse(status_code=exc.http_status, content=exc.to_response())


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("generator_backend.app.main:app", host="127.0.0.1", port=8000, reload=True)
