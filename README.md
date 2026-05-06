# TruthLens — Fake News Detector

A production-grade fake news detection web app powered by Claude AI.

## Features
- AI-powered analysis via Claude Sonnet
- Real-time confidence scoring & verdict meter
- Red flags, credibility factors, manipulation tactics
- Live dashboard with charts (verdict distribution, category breakdown)
- Session history with click-to-reuse
- Dark theme, responsive design

## Setup & Run

```bash
# 1. Install dependencies
pip install flask requests

# 2. Set your Anthropic API key (the app uses your key automatically via Claude.ai)
#    If running standalone, add to app.py headers: "x-api-key": "YOUR_KEY"

# 3. Run
python app.py

# 4. Open browser
http://localhost:5050
```

## Running on the Web

### Hugging Face Spaces
- Create a new Space with Gradio SDK
- Replace app.py with Gradio wrapper

### Render.com / Railway.app
- Push to GitHub
- Connect repo → auto-deploy
- Set PORT env variable

## Project Structure
```
├── app.py           # Flask backend + Claude API calls
├── static/
│   └── index.html   # Full dashboard frontend
└── requirements.txt
```
