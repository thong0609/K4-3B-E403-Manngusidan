"""
main.py — FastAPI app entry point cho ScriptScout (Track C3)
"""
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import init_db
from routes.sessions import router as sessions_router
from routes.sources import router as sources_router
from routes.scripts import router as scripts_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)

app = FastAPI(
    title="ScriptScout API",
    description=(
        "Agent tự tìm tài liệu web và viết kịch bản video có dẫn nguồn.\n\n"
        "Track C3 — K4 Hackathon 2026"
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — cho phép frontend hoặc Postman gọi khi phát triển
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Khởi tạo DB khi app start
@app.on_event("startup")
def on_startup():
    init_db()
    logging.getLogger(__name__).info("Database initialized.")


from pathlib import Path
from fastapi.staticfiles import StaticFiles

# Mount routes
app.include_router(sessions_router)
app.include_router(sources_router)
app.include_router(scripts_router)

# Mount Frontend UI
frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/app", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")


@app.get("/", tags=["Health"])
def root():
    return {
        "service": "ScriptScout API",
        "version": "1.0.0",
        "app_ui": "/app/",
        "docs": "/docs",
        "endpoints": {
            "1_create_session": "POST /api/sessions",
            "2_start_search": "POST /api/sessions/{id}/search",
            "3_check_sources": "GET /api/sessions/{id}/sources",
            "4_toggle_source": "PATCH /api/sessions/{id}/sources/{code}",
            "5_add_source": "POST /api/sessions/{id}/sources",
            "6_generate_script": "POST /api/sessions/{id}/script",
            "7_rewrite_partial": "PATCH /api/sessions/{id}/script/rewrite",
            "8_cite_sentence": "GET /api/sessions/{id}/cite/{n}",
            "9_export": "GET /api/sessions/{id}/export?format=json|markdown",
        },
    }
