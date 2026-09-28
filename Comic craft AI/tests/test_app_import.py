import os

os.environ["DEMO_MODE"] = "true"
os.environ["IMAGE_PROVIDER"] = "mock"

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_homepage():

    response = client.get("/")

    assert response.status_code == 200

    assert "ComicCraft" in response.text


def test_health():

    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"


def test_json_generation():

    response = client.post(
        "/generate-comic/json",
        json={
            "story_prompt": (
                "A brave fox discovers "
                "a magical forest."
            ),
            "character_name": "Luna",
            "setting": "enchanted forest",
            "tone": "adventurous",
            "art_style": "comic book",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert len(data["panels"]) == 5

    assert data["pdf_url"].endswith(".pdf")


def test_image_generation():

    response = client.get(
        "/test-image"
    )

    assert response.status_code == 200

    assert "successful" in response.text