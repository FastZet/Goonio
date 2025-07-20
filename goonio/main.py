import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import settings and logger from our core module
from .core.config import settings
from .core.logger import setup_logger, logger

# Import the API router (we will create this in the next step)
from .api.router import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Asynchronous context manager for FastAPI's lifespan events.
    This is the preferred way to handle startup and shutdown logic.
    """
    # Setup the logger on startup
    setup_logger(level=settings.LOG_LEVEL)
    logger.log("GOONIO", f"Goonio Addon v{settings.ADDON_VERSION} starting up...")
    yield
    # Any cleanup logic would go here on shutdown
    logger.log("GOONIO", "Goonio Addon shutting down.")

# Initialize the FastAPI application
app = FastAPI(
    title=settings.ADDON_NAME,
    version=settings.ADDON_VERSION,
    description=settings.ADDON_DESCRIPTION,
    lifespan=lifespan,
    redoc_url=None, # Disable the ReDoc documentation
)

# Add CORS (Cross-Origin Resource Sharing) middleware
# This is crucial for Stremio web to be able to communicate with the addon
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the main API router
# All our addon's endpoints (/manifest.json, /stream/..., etc.) will be defined here
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
        reload=True # Reloads the server on code changes
    )
