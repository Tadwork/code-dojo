"""Main FastAPI application."""

import json
import logging
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import Response, FileResponse
from fastapi.middleware.cors import CORSMiddleware

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]

from app.config import settings
from app.routes import sessions, websocket, execution
from app.database import engine, Base

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="CodeDojo API",
    description="""
    ## CodeDojo - Collaborative Coding Interview Practice Platform
    
    A real-time collaborative coding environment for conducting technical interviews.
    
    ### Features
    
    * **Session Management**: Create and manage coding interview sessions
    * **Real-time Collaboration**: Multiple users can edit code simultaneously via WebSockets
    * **Multi-language Support**: Syntax highlighting and execution for multiple programming languages
    * **Safe Code Execution**: Execute code safely in the browser using Web Workers and Pyodide
    
    ### API Endpoints
    
    * **Sessions**: Create and retrieve coding sessions
    * **WebSocket**: Real-time code synchronization and collaboration
    * **Health**: Application health check
    * **Execution**: Secure server-side code execution
    
    ### Authentication
    
    Currently, the API does not require authentication. This is suitable for development and can be extended for production use.
    """,
    version="0.1.0",
    contact={
        "name": "CodeDojo API Support",
        "url": "https://github.com/yourusername/code-dojo",
    },
    license_info={
        "name": "MIT",
    },
    servers=[
        {
            "url": "http://localhost:8000",
            "description": "Development server",
        }
    ],
    tags_metadata=[
        {
            "name": "sessions",
            "description": "Operations related to coding interview sessions. Create new sessions and retrieve existing ones.",
        },
        {
            "name": "websocket",
            "description": "WebSocket endpoints for real-time collaboration. Connect to sync code changes, language updates, and cursor positions.",
        },
        {
            "name": "execution",
            "description": "Execute code on the server.",
        },
        {
            "name": "health",
            "description": "Health check and system status endpoints.",
        },
    ],
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes BEFORE static files so /api/* and /ws/* take precedence
app.include_router(sessions.router)
app.include_router(websocket.router)
app.include_router(execution.router, prefix="/api", tags=["execution"])


from app.services.piston import ensure_languages_installed

@app.on_event("startup")
async def startup():
    """Initialize database and services on startup."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Initialize Piston languages in background
    # We do this without awaiting to not block startup, or await if critical.
    # Logic in ensure_languages_installed handles errors gracefully.
    await ensure_languages_installed()


@app.get(
    "/api/openapi.json",
    tags=["health"],
    summary="OpenAPI Specification (JSON)",
    description="Get the OpenAPI specification in JSON format.",
    include_in_schema=False,
)
async def get_openapi_json():
    """Get OpenAPI specification as JSON."""
    return app.openapi()


@app.get(
    "/api/openapi.yaml",
    tags=["health"],
    summary="OpenAPI Specification (YAML)",
    description="Get the OpenAPI specification in YAML format.",
    include_in_schema=False,
)
async def get_openapi_yaml():
    """Get OpenAPI specification as YAML."""
    openapi_schema = app.openapi()
    if yaml:
        yaml_schema = yaml.dump(openapi_schema, default_flow_style=False, sort_keys=False)
        return Response(content=yaml_schema, media_type="application/x-yaml")
    else:
        # If PyYAML is not installed, return JSON instead
        return Response(content=json.dumps(openapi_schema, indent=2), media_type="application/json")


@app.get(
    "/api/health",
    tags=["health"],
    summary="Health Check",
    description="Check the health status of the API server.",
    response_description="Server health status and environment information",
    responses={
        200: {
            "description": "Server is healthy",
            "content": {
                "application/json": {"example": {"status": "healthy", "environment": "development"}}
            },
        }
    },
)
async def health_check():
    """
    Health check endpoint.

    Returns the current health status of the API server and the environment it's running in.
    """
    return {"status": "healthy", "environment": settings.environment}


# Serve static files (React build) AFTER API routes so /api/* and /ws/* are not caught here
static_dir = Path(__file__).resolve().parent.parent / "static"

# Serve static assets (CSS, JS bundles with hashes) when present
static_assets_dir = static_dir / "static"
if static_assets_dir.exists():
    app.mount("/static", StaticFiles(directory=static_assets_dir), name="static")


@app.get("/")
async def serve_root():
    """Serve the root index.html."""
    index_file = static_dir / "index.html"
    logger.info(f"Serving root. Checking for index file at: {index_file}")
    if index_file.exists():
        return FileResponse(index_file)
    logger.error(f"Root index file not found at: {index_file}")
    raise HTTPException(status_code=404, detail="SPA index not found")


@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    """Serve React app for all non-API routes."""
    # Skip API routes explicitly just in case regex catches them
    if full_path.startswith("api/") or full_path.startswith("ws/"):
        raise HTTPException(status_code=404, detail="Not found")

    index_file = static_dir / "index.html"
    logger.info(
        f"Serve SPA for path: {full_path}. Index file: {index_file}, exists: {index_file.exists()}"
    )

    if index_file.exists():
        return FileResponse(index_file)

    logger.error(f"SPA index not found for path: {full_path}")
    raise HTTPException(status_code=404, detail="SPA index not found")
