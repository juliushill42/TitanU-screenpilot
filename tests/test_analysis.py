"""Analysis and storage tests — mocks Ollama."""
import json
import pytest
from unittest.mock import patch, MagicMock
from src.core import save, search, recent, delete, init_db


@pytest.fixture(autouse=True)
def tmp_db(tmp_path, monkeypatch):
    db = tmp_path / "test.db"
    monkeypatch.setattr("src.core.storage.DB_PATH", db)
    init_db()


def test_save_and_recent():
    result = {"explanation": "This is a login page.", "actions": ["Enter credentials", "Click sign in"]}
    rid = save("login.png", "Username Password Login", result)
    assert rid > 0
    rows = recent(5)
    assert rows[0]["explanation"] == "This is a login page."
    assert rows[0]["actions"] == ["Enter credentials", "Click sign in"]


def test_search():
    save("err.png", "404 Not Found page error", {"explanation": "Error page.", "actions": ["Go back"]})
    results = search("404")
    assert len(results) >= 1
    assert "Error" in results[0]["explanation"]


def test_delete():
    rid = save("x.png", "some text", {"explanation": "X", "actions": []})
    delete(rid)
    rows = recent(50)
    assert all(r["id"] != rid for r in rows)


def test_analyze_mock():
    mock_response = {
        "explanation": "A GitHub repository page.",
        "actions": ["Star the repo", "Fork it", "Read the README"]
    }
    with patch("src.core.llm.httpx.Client") as MockClient:
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"response": json.dumps(mock_response)}
        MockClient.return_value.__enter__.return_value.post.return_value = mock_resp
        from src.core.llm import analyze
        result = analyze("ScreenCopilot README stars forks")
        assert result["explanation"] == "A GitHub repository page."
        assert len(result["actions"]) == 3
