from flask import Flask, request, jsonify, send_from_directory
import json, re, time, os
from datetime import datetime
import urllib.request

app = Flask(__name__, static_folder='static')

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
API_KEY = os.environ.get("ANTHROPIC_API_KEY", "YOUR_API_KEY_HERE")

def call_claude(text):
    prompt = f"""You are a fake news detection AI. Analyze the following news article/headline and return ONLY a valid JSON object (no markdown, no explanation).

Article: {text[:2000]}

Return this exact JSON structure:
{{
  "verdict": "FAKE" or "REAL" or "UNCERTAIN",
  "confidence": <number 0-100>,
  "fake_score": <number 0-100>,
  "real_score": <number 0-100>,
  "summary": "<one sentence verdict explanation>",
  "red_flags": ["<flag1>", "<flag2>"],
  "credibility_factors": ["<factor1>", "<factor2>"],
  "category": "<Politics|Health|Science|Finance|Entertainment|Sports|Other>",
  "tone": "<Neutral|Sensational|Alarmist|Balanced|Biased>",
  "manipulation_tactics": ["<tactic1>"],
  "writing_quality": "<Poor|Fair|Good|Excellent>",
  "source_reliability": "<Low|Medium|High|Unknown>"
}}"""

    payload = json.dumps({
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 1000,
        "messages": [{"role": "user", "content": prompt}]
    }).encode()

    req = urllib.request.Request(
        ANTHROPIC_API_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "x-api-key": API_KEY,
            "anthropic-version": "2023-06-01"
        },
        method="POST"
    )

    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
        raw = data["content"][0]["text"].strip()
        raw = re.sub(r"```json|```", "", raw).strip()
        return json.loads(raw)


history = []


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    body = request.get_json()
    text = (body or {}).get("text", "").strip()
    if not text or len(text.split()) < 5:
        return jsonify({"error": "Please enter at least 5 words."}), 400
    try:
        result = call_claude(text)
        result["text"] = text[:200]
        result["timestamp"] = datetime.now().isoformat()
        result["id"] = str(int(time.time() * 1000))
        history.append(result)
        if len(history) > 50:
            history.pop(0)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/history")
def get_history():
    return jsonify(list(reversed(history[-20:])))


@app.route("/stats")
def get_stats():
    if not history:
        return jsonify({"total": 0, "fake": 0, "real": 0, "uncertain": 0, "avg_confidence": 0, "categories": {}})
    fake = sum(1 for h in history if h.get("verdict") == "FAKE")
    real = sum(1 for h in history if h.get("verdict") == "REAL")
    uncertain = sum(1 for h in history if h.get("verdict") == "UNCERTAIN")
    avg_conf = sum(h.get("confidence", 0) for h in history) / len(history)
    cats = {}
    for h in history:
        c = h.get("category", "Other")
        cats[c] = cats.get(c, 0) + 1
    return jsonify({
        "total": len(history),
        "fake": fake,
        "real": real,
        "uncertain": uncertain,
        "avg_confidence": round(avg_conf, 1),
        "categories": cats
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    app.run(debug=False, host="0.0.0.0", port=port)
