"""Main FastAPI application."""

import json
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from fastapi.middleware.cors import CORSMiddleware

try:
    import yaml
except ImportError:
    yaml = None

from app.config import settings
from app.routes import sessions, websocket
from app.database import engine, Base

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
        },
        {
            "url": "https://api.coddojo.com",
            "description": "Production server",
        },
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
            "name": "health",
            "description": "Health check and system status endpoints.",
        },
    ],
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(sessions.router)
app.include_router(websocket.router)


@app.on_event("startup")
async def startup():
    """Initialize database on startup."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


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


# Serve static files (React build)
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """Serve React app for all non-API routes."""
        if (
            not full_path.startswith("api")
            and not full_path.startswith("ws")
            and not full_path.startswith("static")
        ):
            index_path = os.path.join(static_dir, "index.html")
            if os.path.exists(index_path):
                return FileResponse(index_path)
        return {"error": "Not found"}
