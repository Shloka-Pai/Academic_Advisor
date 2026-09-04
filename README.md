# Elective Advisor

An agentic AI tool that recommends elective subjects based on your courses, interests, and career path. Enter your profile and get 3 personalized elective suggestions with fit scores and reasoning — powered by an LLM via OpenRouter.

## Live demo

- Frontend: `https://your-vercel-url.vercel.app`
- Backend: `https://academic-advisor-100l.onrender.com`

> Note: the backend is on Render's free tier, so it sleeps after 15 minutes of inactivity. The first request after a period of idleness may take 30–50 seconds to respond while it wakes up.

## How it works

1. You fill in your courses taken, interests, and target career path in the frontend
2. The frontend sends your profile to the FastAPI backend
3. The backend builds a structured prompt and calls an LLM through OpenRouter
4. The LLM returns 3 elective recommendations with a reason and fit score (1–10) each
5. Results are displayed as cards in the UI

## Project structure

```
Agentic AI/
├── Backend/
│   ├── app.py            # FastAPI app — prompt builder, OpenRouter call, API route
│   ├── Requirements.txt  # Python dependencies
│   └── .env              # API key (not committed)
├── Frontend/
│   └── index.html        # Single-page UI (vanilla HTML/CSS/JS)
└── .gitignore
```

## Prerequisites

- Python 3.9+
- An [OpenRouter](https://openrouter.ai) API key (free tier available)

## Setup & running locally

**1. Clone the repo**
```bash
git clone <your-repo-url>
cd "Agentic AI"
```

**2. Install backend dependencies**
```bash
cd Backend
python -m venv venv
venv\Scripts\activate       # Windows
source venv/bin/activate    # Mac/Linux
pip install -r Requirements.txt
```

**3. Add your API key**

Create `Backend/.env`:
```
OPENROUTER_API_KEY=<your_openrouter_api_key>
```

**4. Start the backend**
```bash
uvicorn app:app --reload --port 8000
```
The API will be available at `http://localhost:8000`.

**5. Run the frontend**

Open `Frontend/index.html` directly in your browser, or serve it locally:
```bash
cd Frontend
python -m http.server 5500
```
Then visit `http://localhost:5500/index.html`.

The frontend's `API_URL` points to the deployed Render backend by default. For local development, change it in `index.html`:
```js
const API_URL = "http://localhost:8000/recommend";
```

## API

### `POST /recommend`

**Request body:**
```json
{
  "courses_taken": ["Data Structures", "Statistics"],
  "interests": ["Robotics", "game design"],
  "career_path": "Machine Learning Engineer"
}
```

**Response:**
```json
{
  "recommendations": [
    {
      "elective_name": "Reinforcement Learning",
      "reason": "Directly applicable to robotics and ML engineering roles.",
      "fit_score": 9
    }
  ]
}
```

### `GET /health`

Returns `{"status": "ok"}` — useful for uptime checks.

## Deployment

- **Backend** is deployed on [Render](https://render.com) as a free-tier Web Service, with root directory set to `Backend`
- **Frontend** is deployed on [Vercel](https://vercel.com) as a static site, with root directory set to `Frontend`
- The `OPENROUTER_API_KEY` is set as an environment variable on Render, not committed to the repo
- CORS in `app.py` is currently set to `allow_origins=["*"]` for simplicity; for a production app, this should be tightened to the exact frontend URL

## Tech stack

| Layer    | Technology                          |
|----------|--------------------------------------|
| Frontend | Vanilla HTML / CSS / JavaScript       |
| Backend  | Python, FastAPI                       |
| AI       | OpenRouter (free LLM routing)         |
| Hosting  | Render (backend), Vercel (frontend)   |
