"""Screenshot upload and processing endpoint."""
import base64
import tempfile
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel

from core import extract_text, extract_text_from_bytes, analyze, save

router = APIRouter(prefix="/screenshot", tags=["screenshot"])


class AnalyzeB64Request(BaseModel):
    image_b64: str
    filename: str = "screenshot.png"
    model: str = "llama3"


class AnalysisResult(BaseModel):
    id: int
    explanation: str
    actions: list[str]
    ocr_text: str


@router.post("/upload", response_model=AnalysisResult)
async def upload_screenshot(file: UploadFile = File(...), model: str = "llama3"):
    """Accept a multipart file upload, OCR it, analyze with LLM, persist."""
    data = await file.read()
    if not data:
        raise HTTPException(400, "Empty file")
    try:
        ocr_text = extract_text_from_bytes(data)
    except Exception as e:
        raise HTTPException(422, f"OCR failed: {e}")
    try:
        result = analyze(ocr_text, model=model)
    except RuntimeError as e:
        raise HTTPException(503, str(e))
    record_id = save(file.filename, ocr_text, result)
    return AnalysisResult(id=record_id, ocr_text=ocr_text, **result)


@router.post("/analyze-b64", response_model=AnalysisResult)
async def analyze_base64(req: AnalyzeB64Request):
    """Accept a base64-encoded image (from Tauri drag-drop), OCR + analyze."""
    try:
        data = base64.b64decode(req.image_b64)
    except Exception:
        raise HTTPException(400, "Invalid base64 payload")
    try:
        ocr_text = extract_text_from_bytes(data)
    except Exception as e:
        raise HTTPException(422, f"OCR failed: {e}")
    try:
        result = analyze(ocr_text, model=req.model)
    except RuntimeError as e:
        raise HTTPException(503, str(e))
    record_id = save(req.filename, ocr_text, result)
    return AnalysisResult(id=record_id, ocr_text=ocr_text, **result)
