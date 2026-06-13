"""History and search endpoints."""
from fastapi import APIRouter, HTTPException, Query
from core import search, recent, delete, list_models

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.get("/history")
def get_history(limit: int = Query(20, ge=1, le=100)):
    return recent(limit)


@router.get("/search")
def search_history(q: str = Query(..., min_length=1), limit: int = Query(20, ge=1, le=100)):
    return search(q, limit)


@router.delete("/{record_id}")
def delete_record(record_id: int):
    try:
        delete(record_id)
    except Exception as e:
        raise HTTPException(500, str(e))
    return {"deleted": record_id}


@router.get("/models")
def get_models():
    models = list_models()
    if not models:
        return {"models": ["llama3"], "note": "Ollama offline — showing defaults"}
    return {"models": models}
