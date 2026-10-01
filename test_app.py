import os

os.environ["LLM_PROVIDER"] = "mock"
os.environ["IMAGE_PROVIDER"] = "placeholder"

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert "ComicCraft" in response.text


def test_json_generation():
    payload = {
        "story_prompt": "A brave fox explores an enchanted forest.",
        "character_name": "Lumi",
        "setting": "enchanted forest",
        "tone": "dramatic",
        "art_style": "comic book",
    }
    response = client.post("/generate-comic/json", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert len(data["layout"]) == 5
    assert data["pdf_path"].startswith("/static/exports/")
