# ResQRoute - Quick Start Guide

Your full-stack evacuation route planning application is ready! Follow these steps to get it running.

## Prerequisites

- Python 3.8+
- Node.js 16+
- Anthropic API Key

## Setup Steps

### 1. Configure Backend Environment

```bash
cd backend
cp .env.example .env
```

Edit `.env` and add your Anthropic API key:
```
ANTHROPIC_API_KEY=your_actual_api_key_here
```

### 2. Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Start Backend Server

```bash
cd backend
python main.py
```

The API will run on `http://localhost:8000`

Check health: `http://localhost:8000/health`

### 4. Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 5. Start Frontend Dev Server

```bash
cd frontend
npm run dev
```

The app will run on `http://localhost:5173` (or `3000` if 5173 is busy)

## API Endpoints

### Get City Layout
```
GET /api/city
```

### Plan Evacuation Route
```
POST /api/plan-route
Content-Type: application/json

{
  "disaster_type": "flood",
  "intensity": 7.5,
  "starting_location": "z1",
  "destination_location": "z4"
}
```

Response:
```json
{
  "safest_route": ["z1", "z3", "z4"],
  "shortest_route": ["z1", "z2", "z4"],
  "explanation": "This route avoids the Harbor zone (z2) which has an 80% flood risk...",
  "risk_score": 0.35
}
```

> `shortest_route` will be `null` if the safest and shortest paths happen to be identical.

## Disaster Types

- `flood` - Water-based disaster
- `earthquake` - Seismic event
- `fire` - Fire-based disaster

## Zones

The mock city has 4 zones:
- `z1` - Downtown
- `z2` - Harbor
- `z3` - Park District
- `z4` - Suburbs (default evacuation destination)

## How It Works

1. User selects disaster type, intensity, start, and destination zones
2. Claude API assesses a risk score (0.0–1.0) for each zone based on disaster type
3. Risk scores are mapped from zone names → zone IDs and applied to edge weights
4. **Safest route**: Dijkstra on `safe_weight = distance × (1 + zone_risk)` — avoids dangerous zones
5. **Shortest route**: Dijkstra on raw `distance` only — ignores risk entirely
6. Both routes and an AI explanation are returned and displayed side-by-side

## Architecture Notes

### Dual-Attribute Edge Design (`graph_utils.py`)

Each road edge carries two weight attributes:

| Attribute | Set by | Modified by | Used by |
|---|---|---|---|
| `distance` | `add_roads()` | Never | `find_shortest_path()` |
| `safe_weight` | `add_roads()` | `update_edge_weights()` | `find_safest_path()` |

Raw distances are **never overwritten**, so the unweighted shortest path is always computable even after AI weights are applied.

### Per-Request Graph Instantiation (`routes.py`)

A fresh `CityGraph()` is created on every `/api/plan-route` call. This prevents edge/weight corruption that would occur if the same NetworkX graph object were mutated across multiple requests.

### AI Risk Score Pipeline (`ai_utils.py`)

Claude returns risk scores keyed by zone **name** (e.g. `"Downtown": 0.8`). Before returning, `ai_utils` remaps these to zone **IDs** (e.g. `"z1": 0.8`) so `graph_utils` lookups work correctly.

## Troubleshooting

### Backend won't start
- Check Python version: `python --version`
- Install dependencies: `pip install -r requirements.txt`
- Ensure port 8000 is free

### Frontend won't connect to backend
- Make sure backend is running on `localhost:8000`
- Check CORS is enabled (it should be by default)
- Open browser console for error messages

### Claude API errors
- Verify `ANTHROPIC_API_KEY` in `.env`
- Check API key is valid at https://console.anthropic.com
- Ensure you have API credits

## Project Structure

```
ResQRoute/
├── backend/
│   ├── main.py           # FastAPI app entry
│   ├── models.py         # Pydantic schemas
│   ├── routes.py         # API endpoints (fresh graph per request)
│   ├── graph_utils.py    # Dijkstra on distance + safe_weight attributes
│   ├── ai_utils.py       # Claude API — risk scores remapped to zone IDs
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── components/
│   │       ├── DisasterInput.jsx
│   │       ├── MapDisplay.jsx
│   │       └── RouteInfo.jsx
│   └── package.json
└── README.md
```

## Next Steps

1. Run both backend and frontend
2. Select a disaster type and intensity
3. Pick starting and destination zones
4. Click "Plan Route"
5. See the safest evacuation path and compare it against the shortest!

For college submission, highlight:
- **Dual-algorithm routing**: Two separate Dijkstra runs on different edge weights
- **AI integration**: Claude API for real-time risk assessment per zone
- **Full-stack**: FastAPI backend + React frontend
- **Core insight**: Shortest path ≠ Safest path — the AI-weighted graph proves it with a concrete counter-example
- **Solution**: Risk-penalized edge weights make dangerous zones effectively "further away"
