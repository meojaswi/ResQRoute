# ResQRoute - AI-Powered Evacuation Route Planner

A full-stack application for planning optimal evacuation routes during disasters using graph algorithms and AI risk assessment.

## Features

- 🗺️ **Interactive City Map** - Visualize zones and roads with Leaflet.js
- 🤖 **AI Risk Assessment** - Claude API predicts danger zones based on disaster type
- 🛣️ **Smart Route Planning** - Dijkstra/A* algorithms find the safest path, not just the shortest
- 📊 **Route Comparison** - See shortest vs safest path side-by-side
- 📝 **AI Explanations** - Get reasoning for why each route was chosen

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | FastAPI + NetworkX |
| Frontend | React + Vite + Leaflet.js |
| AI | Claude API |
| Graph DB | Python NetworkX |

## Project Structure

```
ResQRoute/
├── backend/           # FastAPI server
│   ├── main.py        # App entry point
│   ├── models.py      # Pydantic models
│   ├── graph_utils.py # Graph algorithms
│   ├── ai_utils.py    # Claude API integration
│   ├── routes.py      # API endpoints
│   └── requirements.txt
├── frontend/          # React app
│   ├── src/
│   ├── public/
│   └── package.json
└── README.md
```

## Setup

### Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Add your ANTHROPIC_API_KEY to .env
python main.py
```

Backend runs on `http://localhost:8000`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:5173`

## API Endpoints

- `GET /api/city` - Get city layout
- `POST /api/plan-route` - Plan evacuation route
  - Body: `{ disaster_type, intensity, starting_location, destination_location }`

## How It Works

1. User selects disaster type and intensity
2. Claude API assesses risk scores for each zone
3. Graph edge weights are updated based on risks
4. Dijkstra's algorithm finds the safest path
5. Route and explanation displayed on map

## For College Assessment

**Problem Statement**: Shortest path ≠ Safest path. Classical routing algorithms don't account for dynamic disaster-specific risks.

**Solution**: Combine graph algorithms with AI to:
- Dynamically reweight edges based on predicted risks
- Compare shortest vs safest routes
- Provide explainable AI reasoning

This demonstrates integration of classical CS (graph theory) with modern AI.

## License

MIT
