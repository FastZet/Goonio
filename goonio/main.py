import uvicorn
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
from .core.logger import setup_logger, logger
from .api.router import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logger(level=settings.LOG_LEVEL)
    logger.log("GOONIO", f"Goonio Addon v{settings.ADDON_VERSION} starting up...")
    yield
    logger.log("GOONIO", "Goonio Addon shutting down.")

app = FastAPI(
    title=settings.ADDON_NAME,
    version=settings.ADDON_VERSION,
    description=settings.ADDON_DESCRIPTION,
    lifespan=lifespan,
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    if not (request.url.path == "/health" and response.status_code == 200):
        logger.log(
            "API",
            f'{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s'
        )
    
    return response

app.include_router(api_router)

@app.get("/health", tags=["General"])
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(
        "goonio.main:app",
        host=settings.FASTAPI_HOST,
        port=settings.FASTAPI_PORT,
        log_config=None,
        reload=True
    )
else:
    # This block is for production on Render (when run by Gunicorn)
    # Disable Gunicorn's default loggers
    import logging
    gunicorn_error_logger = logging.getLogger("gunicorn.error")
    gunicorn_error_logger.setLevel(logging.CRITICAL)
    gunicorn_access_logger = logging.getLogger("gunicorn.access")
    gunicorn_access_logger.setLevel(logging.CRITICAL)
