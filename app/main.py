import logging
import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.routers import research

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Indorexia", description="UMKM Research Tool")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(research.router)


@app.get("/api/health")
async def health():
    return {"status": "ok"}


dist = Path("frontend/dist")
if dist.exists():
    app.mount("/assets", StaticFiles(directory=str(dist / "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        if full_path.startswith("api/"):
            from fastapi.exceptions import HTTPException
            raise HTTPException(status_code=404)
        file_path = dist / full_path
        if file_path.is_file():
            return FileResponse(str(file_path))
        index = dist / "index.html"
        if index.exists():
            return FileResponse(str(index))
        from fastapi.exceptions import HTTPException
        raise HTTPException(status_code=404)
