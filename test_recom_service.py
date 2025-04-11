import pytest
import json
from recom_service import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_invalid_json(client):
    response = client.post('/recommend', data="not json", content_type='application/json')
    assert response.status_code == 400
    assert response.json["error"] == "Invalid JSON"

def test_missing_tracks(client):
    response = client.post('/recommend', json={})
    assert response.status_code == 400
    assert response.json["error"] == "Missing 'tracks' in request"

def test_tracks_not_list(client):
    response = client.post('/recommend', json={"tracks": "not a list"})
    assert response.status_code == 400
    assert response.json["error"] == "'tracks' must be a list"

def test_tracks_wrong_length(client):
    response = client.post('/recommend', json={"tracks": ["track"] * 10})
    assert response.status_code == 400
    assert response.json["error"] == "Expected a JSON array of 50 track strings"

def test_tracks_not_strings(client):
    response = client.post('/recommend', json={"tracks": [123] * 50})
    assert response.status_code == 400
    assert response.json["error"] == "Expected a JSON array of 50 track strings"

# NOTE: мокаем, чтобы не делать реальный запрос к OpenRouter
from unittest.mock import patch

@patch("recom_service.requests.post")
def test_successful_response(mock_post, client):
    fake_response = {
        "choices": [{
            "message": {
                "content": '''{
                    "tracks": ["Artist - Song 1", "Artist - Song 2"],
                    "title": "Cool Playlist"
                }'''
            }
        }]
    }


    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = fake_response

    response = client.post('/recommend', json={"tracks": ["Track"] * 50})
    assert response.status_code == 200
    data = response.get_json()
    assert "tracks" in data
    assert "title" in data
    assert len(data["tracks"]) == 2
@patch("recom_service.requests.post")
def test_model_returns_invalid_format(mock_post, client):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {
        "choices": [{
            "message": {
                "content": "Вот какие-то треки без JSON:\n1. Artist - Song"
            }
        }]
    }

    response = client.post('/recommend', json={"tracks": ["Track"] * 50})
    assert response.status_code == 200
    data = response.get_json()
    assert data["title"] == "Рекомендованный плейлист"
    assert isinstance(data["tracks"], list)
    
@patch("recom_service.requests.post")
def test_model_returns_text_with_numbered_tracks(mock_post, client):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {
        "choices": [{
            "message": {
                "content": '''
                    Плейлист: "Мрачная синтволна"
                    1. Molchat Doma - Sudno
                    2. Boy Harsher - Pain
                '''
            }
        }]
    }

    response = client.post('/recommend', json={"tracks": ["Track"] * 50})
    assert response.status_code == 200
    data = response.get_json()
    assert data["title"] == "Мрачная синтволна"
    assert len(data["tracks"]) == 2

