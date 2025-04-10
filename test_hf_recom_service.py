import os
import json
import pytest
from hf_recom_service import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_recommend_valid_request(monkeypatch, client):
    # мокаем ответ от Hugging Face API
    fake_hf_response = {
        "generated_text": """
1. Artist A - Song A
2. Artist B - Song B
3. Artist C - Song C
Плейлист: "Test Playlist"
"""
    }

    def mock_post(*args, **kwargs):
        class MockResponse:
            def raise_for_status(self):
                pass

            def json(self):
                return [fake_hf_response]
        return MockResponse()

    monkeypatch.setattr("hf_recom_service.requests.post", mock_post)

    payload = {
        "tracks": [f"Artist {i} - Track {i}" for i in range(1, 51)]
    }

    response = client.post("/recommend", json=payload)
    assert response.status_code == 200
    data = response.get_json()

    assert "tracks" in data
    assert "title" in data
    assert isinstance(data["tracks"], list)
    assert isinstance(data["title"], str)
    assert data["title"] == "Test Playlist"
    assert len(data["tracks"]) > 0

def test_recommend_missing_key(client):
    response = client.post("/recommend", json={"wrong_key": []})
    assert response.status_code == 400
    assert response.get_json()["error"] == "Missing 'tracks' in request"

def test_recommend_non_list(client):
    response = client.post("/recommend", json={"tracks": "not a list"})
    assert response.status_code == 400
    assert response.get_json()["error"] == "'tracks' must be a list"

def test_recommend_invalid_json(client):
    response = client.post("/recommend", data="not a json", content_type='application/json')
    assert response.status_code == 400
    assert response.get_json()["error"] == "Invalid JSON"
