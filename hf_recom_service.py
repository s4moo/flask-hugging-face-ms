import os
import json
import re
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")
HUGGINGFACE_MODEL_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1" # модель

HEADERS = {
    "Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}",
    "Content-Type": "application/json"
}

# ========= ПРОМПТ =========
PROMPT_TEMPLATE = """
Вот список из 50 музыкальных треков:
{tracks}
Проанализируй его и предложи 20 новых, но похожих треков (по жанру/исполнителям) и название для этого плейлиста (что-то уникальное до 5 слов) в формате:{{ "tracks": [ "артист - название" ], "title": "название плейлиста" }}. В ответе должны быть только рекомендованные треки, ничего больше!
"""
# ===========================

@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        input_data = request.get_json()
        if not isinstance(input_data, list) or not all(isinstance(item, str) for item in input_data):
            return jsonify({"error": "Expected a JSON array of 50 track strings"}), 400

        prompt = PROMPT_TEMPLATE.format(tracks="\n".join(input_data))

        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 500,
                "temperature": 0.7,
                "return_full_text": False
            }
        }

        response = requests.post(HUGGINGFACE_MODEL_URL, headers=HEADERS, data=json.dumps(payload))
        response.raise_for_status()
        generated = response.json()

        text = generated[0].get("generated_text", "")

        # пытаемся найти JSON блок
        json_match = re.search(r'\{[\s\S]*?\}', text)
        if json_match:
            try:
                parsed_json = json.loads(json_match.group(0))
                return jsonify(parsed_json)
            except json.JSONDecodeError:
                pass

        # альтернативный парс (если ответ был не по примеру - придется настраивать для каждой модели индивидуально, они все дурят по-своему)
        track_lines = re.findall(r'\d+\.\s+(.*? - .*?)\n', text)
        title_match = re.search(r'Плейлист:\s*[\"“](.*?)[\"”]', text)

        return jsonify({
            "tracks": track_lines[:20],
            "title": title_match.group(1) if title_match else "Рекомендованный плейлист"
        })

    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
