"""FastAPI application entry point.

Serves the JSON API under /api and the built React frontend (if present) as
static files. On startup it creates the SQLite schema and seeds the reference
catalogs + demo project.
"""
from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from .seed import init_db
from .auth import require_auth
from .routers import catalog, projects, climate, scheduling, reports, auth_router
from fastapi import Depends

app = FastAPI(title="Smart Irrigation Scheduling Platform — FAO-56", version="1.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auth endpoints are public; everything else requires a valid bearer token.
app.include_router(auth_router.router)
_protected = [Depends(require_auth)]
app.include_router(catalog.router, dependencies=_protected)
app.include_router(projects.router, dependencies=_protected)
app.include_router(climate.router, dependencies=_protected)
app.include_router(scheduling.router, dependencies=_protected)
app.include_router(reports.router, dependencies=_protected)


@app.on_event("startup")
def _startup():
    init_db(with_sample=True)


@app.get("/api/health")
def health():
    return {"status": "ok", "platform": "FAO-56 Smart Irrigation"}


# --- Serve the built frontend (frontend/dist) if it exists ------------------
FRONTEND_DIST = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend", "dist")

if os.path.isdir(FRONTEND_DIST):
    # A separate assets/ dir only exists for multi-file builds. The single-file
    # build inlines everything into index.html, so guard the mount.
    _assets = os.path.join(FRONTEND_DIST, "assets")
    if os.path.isdir(_assets):
        app.mount("/assets", StaticFiles(directory=_assets), name="assets")

    @app.get("/{full_path:path}")
    def spa(full_path: str):
        if full_path.startswith("api/"):
            return JSONResponse({"detail": "Not found"}, status_code=404)
        index = os.path.join(FRONTEND_DIST, "index.html")
        return FileResponse(index)
else:
    @app.get("/")
    def root():
        return {"message": "API running. Build the frontend (npm run build) to serve the UI.",
                "docs": "/docs"}
