"""Main FastAPI application."""
import logging
import sys
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from backend.config import settings
from backend.api.routes import analyze, status, tree, search, qa, browse, cache
from backend.db.base import Base, engine
# Import models to ensure tables are created
from backend.models import Repository, Node, Task, PassphraseUsage
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import os
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Create database tables
logger.info("Creating database tables...")
Base.metadata.create_all(bind=engine)
logger.info("Database tables created")

# Create FastAPI app
app = FastAPI(
    title="R2CE API",
    description="API for Recursive Repository Context Engine",
    version="1.0.0",
)

@app.on_event("startup")
async def startup_event():
    logger.info("=" * 50)
    logger.info("R2CE Backend Starting")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"LLM Provider: {settings.llm_provider}")
    logger.info(f"Database URL: {settings.database_url[:20]}...")
    logger.info(f"Frontend URL: {settings.frontend_url}")
    logger.info("=" * 50)

# CORS middleware - MUST be added before exception handlers
# Allow frontend URL from environment variable, plus localhost for development
allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",  # Vite default port
    "http://127.0.0.1:5173",
]
if settings.frontend_url:
    allowed_origins.append(settings.frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers for CORS support on all responses
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with CORS headers."""
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
        headers={
            "Access-Control-Allow-Origin": request.headers.get("origin", "*"),
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions with CORS headers."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers={
            "Access-Control-Allow-Origin": request.headers.get("origin", "*"),
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )

# Exception handler to ensure CORS headers are always sent
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler to ensure CORS headers are sent even on errors."""
    import traceback
    error_trace = traceback.format_exc()
    print(f"Unhandled exception: {exc}")
    print(error_trace)
    
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"},
        headers={
            "Access-Control-Allow-Origin": request.headers.get("origin", "*"),
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )

# Include routers
app.include_router(analyze.router, prefix="/api", tags=["analyze"])
app.include_router(status.router, prefix="/api", tags=["status"])
app.include_router(tree.router, prefix="/api", tags=["tree"])
app.include_router(search.router, prefix="/api", tags=["search"])
app.include_router(qa.router, prefix="/api", tags=["qa"])
app.include_router(browse.router, prefix="/api", tags=["browse"])
app.include_router(cache.router, prefix="/api", tags=["cache"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "R2CE API", "version": "1.0.0"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}

