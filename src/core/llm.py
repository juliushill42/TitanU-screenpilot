"""Local LLM analysis via Ollama."""
import httpx
import json


OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "llama3"

SYSTEM_PROMPT = """You are ScreenCopilot, a local AI assistant that explains what is happening on a user's screen.
Given extracted text from a screenshot, you:
1. Explain what the screen is showing in plain English (2-3 sentences max)
2. List 3-5 concrete action suggestions the user could take next

Be direct and specific. No filler, no hedging. Focus on what matters.

Respond ONLY as valid JSON in this exact shape:
{
  "explanation": "string",
  "actions": ["string", "string", ...]
}"""


def analyze(ocr_text: str, model: str = DEFAULT_MODEL) -> dict:
    """Send OCR text to local Ollama model and return structured analysis."""
    if not ocr_text.strip():
        return {
            "explanation": "No text could be extracted from this screenshot.",
            "actions": ["Try a clearer screenshot", "Ensure the content is not purely graphical"]
        }

    prompt = f"Screenshot text:\n\n{ocr_text}\n\nAnalyze this."

    payload = {
        "model": model,
        "prompt": prompt,
        "system": SYSTEM_PROMPT,
        "stream": False,
        "options": {"temperature": 0.3, "num_predict": 512}
    }

    try:
        with httpx.Client(timeout=60.0) as client:
            resp = client.post(OLLAMA_URL, json=payload)
            resp.raise_for_status()
            raw = resp.json().get("response", "")
            # Strip markdown fences if present
            raw = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            return json.loads(raw)
    except json.JSONDecodeError:
        return {"explanation": raw, "actions": []}
    except httpx.ConnectError:
        raise RuntimeError("Ollama is not running. Start it with: ollama serve")
    except httpx.HTTPStatusError as e:
        raise RuntimeError(f"Ollama error {e.response.status_code}: {e.response.text}")


def list_models() -> list[str]:
    """Return available Ollama models."""
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.get("http://localhost:11434/api/tags")
            resp.raise_for_status()
            return [m["name"] for m in resp.json().get("models", [])]
    except Exception:
        return []
