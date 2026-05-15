from fastapi import APIRouter, HTTPException
from models import City, DisasterInput, RouteResponse
from graph_utils import CityGraph
from ai_utils import get_risk_assessment, get_route_explanation

router = APIRouter(prefix="/api", tags=["routes"])

# Mock city data (Expanded 10-zone Coastal Metropolis)
mock_city = City(
    name="Metro City",
    zones=[
        {"id": "z1", "name": "Downtown", "latitude": 40.7128, "longitude": -74.0060, "elevation_m": 8.5, "population_density": 35000},
        {"id": "z2", "name": "Coastal Harbor", "latitude": 40.6895, "longitude": -74.0444, "elevation_m": 1.5, "population_density": 8000},
        {"id": "z3", "name": "Financial District", "latitude": 40.7075, "longitude": -74.0113, "elevation_m": 5.0, "population_density": 45000},
        {"id": "z4", "name": "Midtown", "latitude": 40.7549, "longitude": -73.9840, "elevation_m": 15.0, "population_density": 50000},
        {"id": "z5", "name": "Central Park", "latitude": 40.7812, "longitude": -73.9665, "elevation_m": 35.0, "population_density": 500},
        {"id": "z6", "name": "Westside", "latitude": 40.7850, "longitude": -73.9780, "elevation_m": 20.0, "population_density": 28000},
        {"id": "z7", "name": "Eastside Industrial", "latitude": 40.7600, "longitude": -73.9500, "elevation_m": 8.0, "population_density": 3000},
        {"id": "z8", "name": "Northern Suburbs", "latitude": 40.8100, "longitude": -73.9400, "elevation_m": 65.0, "population_density": 6000},
        {"id": "z9", "name": "University Campus", "latitude": 40.7300, "longitude": -73.9950, "elevation_m": 12.0, "population_density": 22000},
        {"id": "z10", "name": "The Heights", "latitude": 40.8250, "longitude": -73.9450, "elevation_m": 145.0, "population_density": 12000},
    ],
    roads=[
        # Southern cluster
        {"id": "r1", "from_zone": "z1", "to_zone": "z3", "distance": 1.2, "risk_score": 0.0},
        {"id": "r2", "from_zone": "z1", "to_zone": "z9", "distance": 2.5, "risk_score": 0.0},
        {"id": "r3", "from_zone": "z2", "to_zone": "z3", "distance": 3.0, "risk_score": 0.0},
        {"id": "r4", "from_zone": "z2", "to_zone": "z6", "distance": 8.5, "risk_score": 0.0}, # Coastal highway
        
        # Mid cluster
        {"id": "r5", "from_zone": "z3", "to_zone": "z4", "distance": 4.0, "risk_score": 0.0},
        {"id": "r6", "from_zone": "z3", "to_zone": "z9", "distance": 3.5, "risk_score": 0.0},
        {"id": "r7", "from_zone": "z9", "to_zone": "z4", "distance": 2.8, "risk_score": 0.0},
        {"id": "r8", "from_zone": "z9", "to_zone": "z7", "distance": 5.0, "risk_score": 0.0},
        
        # Northern cluster
        {"id": "r9", "from_zone": "z4", "to_zone": "z5", "distance": 2.5, "risk_score": 0.0},
        {"id": "r10", "from_zone": "z4", "to_zone": "z6", "distance": 3.0, "risk_score": 0.0},
        {"id": "r11", "from_zone": "z4", "to_zone": "z7", "distance": 3.2, "risk_score": 0.0},
        {"id": "r12", "from_zone": "z5", "to_zone": "z8", "distance": 4.5, "risk_score": 0.0},
        {"id": "r13", "from_zone": "z5", "to_zone": "z10", "distance": 6.0, "risk_score": 0.0},
        {"id": "r14", "from_zone": "z6", "to_zone": "z8", "distance": 3.8, "risk_score": 0.0},
        {"id": "r15", "from_zone": "z7", "to_zone": "z8", "distance": 5.2, "risk_score": 0.0},
        
        # Far North
        {"id": "r16", "from_zone": "z8", "to_zone": "z10", "distance": 2.0, "risk_score": 0.0},
    ]
)

city_graph = None  # Created fresh per request — see plan_evacuation_route

@router.get("/city")
def get_city():
    """Get city layout and zones"""
    return mock_city

@router.post("/plan-route")
def plan_evacuation_route(request: DisasterInput) -> RouteResponse:
    """Plan optimal evacuation route using AI risk assessment"""

    try:
        # Get risk scores from Claude AI (returns dict keyed by zone ID)
        risk_scores = get_risk_assessment(
            request.disaster_type,
            request.intensity,
            mock_city.zones
        )

        # Build a fresh graph per request to avoid state corruption across calls
        city_graph = CityGraph()
        city_graph.add_zones(mock_city.zones)
        city_graph.add_roads(mock_city.roads)
        city_graph.update_edge_weights(risk_scores)

        destination = request.destination_location or "z4"

        # Safest route: Dijkstra on AI risk-adjusted weights
        safest_route = city_graph.find_safest_path(request.starting_location, destination)
        if not safest_route:
            raise HTTPException(status_code=404, detail="No safest route found between these zones")

        # Shortest route: Dijkstra on raw distances only (no risk penalty)
        shortest_route = city_graph.find_shortest_path(request.starting_location, destination)

        # Average risk score across zones in the safest route
        route_risk = sum(risk_scores.get(zone, 0.0) for zone in safest_route) / len(safest_route)

        # Get explanation from Claude
        explanation = get_route_explanation(safest_route, route_risk, request.disaster_type, mock_city.zones)

        return RouteResponse(
            safest_route=safest_route,
            shortest_route=shortest_route,
            explanation=explanation,
            risk_score=route_risk,
            zone_risks=risk_scores
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
def health():
    return {"status": "ok"}
