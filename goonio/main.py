import uvicorn
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

# Import settings and logger from our core module
from .core.config import settings
from .core.logger import setup_logger, logger

# Import the API router
from .api.router import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Asynchronous context manager for FastAPI's lifespan events.
    Handles startup and shutdown logic.
    """
    setup_logger(level=settings.LOG_LEVEL)
    logger.log("GOONIO", f"Goonio Addon v{settings.ADDON_VERSION} starting up...")
    yield
    logger.log("GOONIO", "Goonio Addon shutting down.")

# Initialize the FastAPI application
app = FastAPI(
    title=settings.ADDON_NAME,
    version=settings.ADDON_VERSION,
    description=settings.ADDON_DESCRIPTION,
    lifespan=lifespan,
    redoc_url=None,
)

# Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- NEW LOGGING MIDDLEWARE ---
@app.middleware("http")
async def log_requests_middleware(request: Request, call_next):
    """
    Middleware to log incoming requests, but filter out successful health checks.
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    # Condition: Do NOT log if the path is /health AND the status code is 200.
    # All other requests, including failed health checks, will be logged.
    if not (request.url.path == "/health" and response.status_code == 200):
        logger.log(
            "API",
            f'{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s'
        )
    
    return response

# Include the main API router
app.include_router(api_router)

@app.get("/health", tags=["General"])
async def health_check():
    """
    Health check endpoint. Render uses this to verify the service is running.
    """
    return {"status": "ok"}

# This block allows running the server directly for local development if needed
if __name__ == "__main__":
    uvicorn.run(
        "goonio.main:app",
        host=settings.FASTAPI_HOST,
        port=settings.FASTAPI_PORT,
        reload=True
    )
