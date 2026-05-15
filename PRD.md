## ADA Layer
### Graph Model
```
Nodes = intersections / zones
Edges = roads with weights (distance, time, risk score)
Edge weights are dynamic — updated by AI predictions

```

### Algorithms to implement & compare:
## AI Layer

Each of these feeds into edge weight recalculation:

| AI Prediction | How |
|---|---|
| Dangerous zones | Classify areas as high/medium/low risk (rule-based or simple ML) |
| Traffic congestion | Time-of-day heuristic or mock sensor data |
| Road block probability | % chance a road is blocked, added as edge weight multiplier |
| Safest route | Weighted combo of distance + risk score |



## Tech Stack
```
Backend   →  FastAPI
Graph     →  NetworkX (Python)
Map UI    →  Leaflet.js (free, interactive maps) or plain canvas grid
AI        →  Claude API (risk prediction + route explanation)
Data      →  Mock city graph JSON (you design the city layout)
Frontend  →  Vanilla JS or React
```

## Core Flow
```
User inputs: Disaster type + starting location
            ↓
Claude API → predicts risk scores per zone
            ↓
Graph edge weights updated dynamically
            ↓
Run Dijkstra / A* on updated graph
            ↓
Output: Safest evacuation route on map
      + AI explanation ("Avoid Zone B — 80% road block probability")
      + Comparison: shortest vs safest route
```

## Features to Build
```
- City graph builder — define zones, roads, connections
- Disaster input panel — select flood / earthquake / fire + intensity
- AI risk engine — Claude API assigns risk scores to zones
- Route planner — run multiple algorithms, highlight best path
- Map visualization — color zones by danger, draw evacuation route
- Comparison view — shortest path vs safest path side by side
- AI explanation panel — "Here's why this route was chosen"
```
## Core problem solution
```
- Clear problem → graph model → algorithm → AI enhancement pipeline
- "Classical Dijkstra finds shortest path, but our AI-weighted graph finds the safest path — which may not be the shortest" — examiners love this
```

