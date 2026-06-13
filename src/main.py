"""ScreenCopilot backend — FastAPI + Uvicorn."""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core import init_db
from api import screenshot_router, analysis_router

app = FastAPI(
    title="ScreenCopilot",
    description="Local AI that explains your screen in plain English.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["tauri://localhost", "http://localhost", "http://localhost:1420"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(screenshot_router)
app.include_router(analysis_router)


@app.on_event("startup")
def startup():
    init_db()


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8765, reload=False)
