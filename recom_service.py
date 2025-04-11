from flask import Flask, request, jsonify
import os
import requests
from dotenv import load_dotenv
from werkzeug.exceptions import BadRequest
import re
import json
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = "deepseek/deepseek-chat"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


@app.errorhandler(BadRequest)
def handle_bad_request(e):
    return jsonify({"error": "Invalid JSON"}), 400


@app.route("/recommend", methods=["POST"])
def recommend():
    try:
        data = request.get_json()
    except BadRequest:
        return jsonify({"error": "Invalid JSON"}), 400

    if not data or "tracks" not in data:
        return jsonify({"error": "Missing 'tracks' in request"}), 400

    tracks = data["tracks"]
    if not isinstance(tracks, list):
        return jsonify({"error": "'tracks' must be a list"}), 400

    if len(tracks) != 50 or not all(isinstance(track, str) for track in tracks):
        return jsonify({"error": "Expected a JSON array of 50 track strings"}), 400

    # промпт
    prompt = f"""
        Вот список из 50 музыкальных треков:
        {tracks}

        Проанализируй его и предложи 20 похожих треков (по жанру/исполнителям) и название для этого плейлиста (до 5 слов) строго в формате:

        {{
        "tracks": ["артист - название"],
        "title": "название плейлиста"
        }}

        Название должно быть очень уникальным и отражать суть
        """

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
                {"role": "system", "content": "Ты музыкальный рекомендатор."},
                {"role": "user", "content": prompt.strip()}
        ]
    }

    response = requests.post(
        OPENROUTER_URL,
        headers=headers,
        json=payload
    )
    response.raise_for_status()

    result_tmp = response.json()
    result = result_tmp["choices"][0]["message"]["content"]

    # ===ОТЛАДКА=== 
    print("=== RAW RESPONSE FROM MODEL ===")
    print(result)
    print("=== END RAW RESPONSE ===")

    # парсинг ответа
    try:
        match = re.search(r'\{\s*"tracks":\s*\[.*?\],\s*"title":\s*".*?"\s*\}', result, re.DOTALL)
        if match:
            parsed_dict = json.loads(match.group(0))
        else:
            # если аи решил проигнорить шаблон в промпте
            title_match = re.search(r'Плейлист:\s*"(.*?)"', result)
            tracks = []
            for line in result.strip().splitlines():
                if re.match(r"^\d+\.\s+.+\s+-\s+.+", line.strip()):
                    tracks.append(re.sub(r"^\d+\.\s+", "", line.strip()))
            parsed_dict = {
                "title": title_match.group(1) if title_match else "Рекомендованный плейлист",
                "tracks": tracks
            }
    except Exception:
        parsed_dict = {"title": "Рекомендованный плейлист", "tracks": []}

    return jsonify(parsed_dict)


if __name__ == '__main__':
    app.run(debug=True)
