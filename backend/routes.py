from fastapi import APIRouter, HTTPException
from models import City, DisasterInput, RouteResponse
from graph_utils import CityGraph
from ai_utils import get_risk_assessment, get_route_explanation

router = APIRouter(prefix="/api", tags=["routes"])

# Mock city data (Expanded 10-zone Coastal Metropolis)
mock_city = City(
    name="Metro City",
    zones=[
        # Core 10 Zones
        {"id": "z1", "name": "Downtown", "latitude": 40.7128, "longitude": -74.0060, "elevation_m": 8.5, "population_density": 35000, "building_age_years": 85, "infrastructure_type": "commercial", "vegetation_density": "low", "has_medical_center": False},
        {"id": "z2", "name": "Coastal Harbor", "latitude": 40.6895, "longitude": -74.0444, "elevation_m": 1.5, "population_density": 8000, "building_age_years": 40, "infrastructure_type": "industrial", "vegetation_density": "low", "has_medical_center": False},
        {"id": "z3", "name": "Financial District", "latitude": 40.7075, "longitude": -74.0113, "elevation_m": 5.0, "population_density": 45000, "building_age_years": 30, "infrastructure_type": "commercial", "vegetation_density": "low", "has_medical_center": True},
        {"id": "z4", "name": "Midtown", "latitude": 40.7549, "longitude": -73.9840, "elevation_m": 15.0, "population_density": 50000, "building_age_years": 50, "infrastructure_type": "commercial", "vegetation_density": "low", "has_medical_center": True},
        {"id": "z5", "name": "Central Park", "latitude": 40.7812, "longitude": -73.9665, "elevation_m": 35.0, "population_density": 500, "building_age_years": 10, "infrastructure_type": "park", "vegetation_density": "high", "has_medical_center": False},
        {"id": "z6", "name": "Westside", "latitude": 40.7850, "longitude": -73.9780, "elevation_m": 20.0, "population_density": 28000, "building_age_years": 60, "infrastructure_type": "residential", "vegetation_density": "medium", "has_medical_center": False},
        {"id": "z7", "name": "Eastside Industrial", "latitude": 40.7600, "longitude": -73.9500, "elevation_m": 8.0, "population_density": 3000, "building_age_years": 70, "infrastructure_type": "industrial", "vegetation_density": "low", "has_medical_center": False},
        {"id": "z8", "name": "Northern Suburbs", "latitude": 40.8100, "longitude": -73.9400, "elevation_m": 65.0, "population_density": 6000, "building_age_years": 15, "infrastructure_type": "residential", "vegetation_density": "high", "has_medical_center": True},
        {"id": "z9", "name": "University Campus", "latitude": 40.7300, "longitude": -73.9950, "elevation_m": 12.0, "population_density": 22000, "building_age_years": 25, "infrastructure_type": "residential", "vegetation_density": "medium", "has_medical_center": True},
        {"id": "z10", "name": "The Heights", "latitude": 40.8250, "longitude": -73.9450, "elevation_m": 145.0, "population_density": 12000, "building_age_years": 35, "infrastructure_type": "residential", "vegetation_density": "medium", "has_medical_center": False},
        
        # New 10 Zones (Expanded City)
        {"id": "z11", "name": "Airport Hub", "latitude": 40.6413, "longitude": -73.7781, "elevation_m": 4.0, "population_density": 1000, "building_age_years": 30, "infrastructure_type": "commercial", "vegetation_density": "low", "has_medical_center": False},
        {"id": "z12", "name": "Queens Residential", "latitude": 40.7282, "longitude": -73.7949, "elevation_m": 15.0, "population_density": 35000, "building_age_years": 40, "infrastructure_type": "residential", "vegetation_density": "medium", "has_medical_center": True},
        {"id": "z13", "name": "Brooklyn Navy Yard", "latitude": 40.7011, "longitude": -73.9722, "elevation_m": 2.0, "population_density": 2000, "building_age_years": 80, "infrastructure_type": "industrial", "vegetation_density": "low", "has_medical_center": False},
        {"id": "z14", "name": "Williamsburg", "latitude": 40.7081, "longitude": -73.9571, "elevation_m": 12.0, "population_density": 45000, "building_age_years": 60, "infrastructure_type": "residential", "vegetation_density": "low", "has_medical_center": True},
        {"id": "z15", "name": "Staten Island Ferry", "latitude": 40.6437, "longitude": -74.0736, "elevation_m": 1.0, "population_density": 5000, "building_age_years": 50, "infrastructure_type": "commercial", "vegetation_density": "low", "has_medical_center": False},
        {"id": "z16", "name": "Coney Island", "latitude": 40.5749, "longitude": -73.9857, "elevation_m": 1.5, "population_density": 15000, "building_age_years": 65, "infrastructure_type": "residential", "vegetation_density": "low", "has_medical_center": False},
        {"id": "z17", "name": "Bronx Zoo Area", "latitude": 40.8506, "longitude": -73.8770, "elevation_m": 25.0, "population_density": 12000, "building_age_years": 35, "infrastructure_type": "park", "vegetation_density": "high", "has_medical_center": False},
        {"id": "z18", "name": "Riverdale", "latitude": 40.8920, "longitude": -73.9101, "elevation_m": 85.0, "population_density": 8000, "building_age_years": 45, "infrastructure_type": "residential", "vegetation_density": "high", "has_medical_center": True},
        {"id": "z19", "name": "Flushing Meadows", "latitude": 40.7397, "longitude": -73.8408, "elevation_m": 6.0, "population_density": 3000, "building_age_years": 50, "infrastructure_type": "park", "vegetation_density": "medium", "has_medical_center": False},
        {"id": "z20", "name": "JFK Industrial", "latitude": 40.6602, "longitude": -73.7915, "elevation_m": 5.0, "population_density": 1500, "building_age_years": 25, "infrastructure_type": "industrial", "vegetation_density": "low", "has_medical_center": False},
    ],
    roads=[
        # Original 16 Roads
        {"id": "r1", "from_zone": "z1", "to_zone": "z3", "distance": 1.2, "live_traffic_congestion": 0.8, "road_capacity": 3, "is_bridge_or_tunnel": False},
        {"id": "r2", "from_zone": "z1", "to_zone": "z9", "distance": 2.5, "live_traffic_congestion": 0.5, "road_capacity": 2, "is_bridge_or_tunnel": False},
        {"id": "r3", "from_zone": "z2", "to_zone": "z3", "distance": 3.0, "live_traffic_congestion": 0.3, "road_capacity": 2, "is_bridge_or_tunnel": True},
        {"id": "r4", "from_zone": "z2", "to_zone": "z6", "distance": 8.5, "live_traffic_congestion": 0.2, "road_capacity": 4, "is_bridge_or_tunnel": False},
        {"id": "r5", "from_zone": "z3", "to_zone": "z4", "distance": 4.0, "live_traffic_congestion": 0.9, "road_capacity": 4, "is_bridge_or_tunnel": False},
        {"id": "r6", "from_zone": "z3", "to_zone": "z9", "distance": 3.5, "live_traffic_congestion": 0.6, "road_capacity": 2, "is_bridge_or_tunnel": False},
        {"id": "r7", "from_zone": "z9", "to_zone": "z4", "distance": 2.8, "live_traffic_congestion": 0.7, "road_capacity": 3, "is_bridge_or_tunnel": False},
        {"id": "r8", "from_zone": "z9", "to_zone": "z7", "distance": 5.0, "live_traffic_congestion": 0.4, "road_capacity": 2, "is_bridge_or_tunnel": True},
        {"id": "r9", "from_zone": "z4", "to_zone": "z5", "distance": 2.5, "live_traffic_congestion": 0.8, "road_capacity": 3, "is_bridge_or_tunnel": False},
        {"id": "r10", "from_zone": "z4", "to_zone": "z6", "distance": 3.0, "live_traffic_congestion": 0.5, "road_capacity": 3, "is_bridge_or_tunnel": False},
        {"id": "r11", "from_zone": "z4", "to_zone": "z7", "distance": 3.2, "live_traffic_congestion": 0.7, "road_capacity": 2, "is_bridge_or_tunnel": False},
        {"id": "r12", "from_zone": "z5", "to_zone": "z8", "distance": 4.5, "live_traffic_congestion": 0.2, "road_capacity": 2, "is_bridge_or_tunnel": False},
        {"id": "r13", "from_zone": "z5", "to_zone": "z10", "distance": 6.0, "live_traffic_congestion": 0.1, "road_capacity": 1, "is_bridge_or_tunnel": False},
        {"id": "r14", "from_zone": "z6", "to_zone": "z8", "distance": 3.8, "live_traffic_congestion": 0.3, "road_capacity": 3, "is_bridge_or_tunnel": False},
        {"id": "r15", "from_zone": "z7", "to_zone": "z8", "distance": 5.2, "live_traffic_congestion": 0.2, "road_capacity": 2, "is_bridge_or_tunnel": False},
        {"id": "r16", "from_zone": "z8", "to_zone": "z10", "distance": 2.0, "live_traffic_congestion": 0.1, "road_capacity": 2, "is_bridge_or_tunnel": False},
        
        # New Roads Connecting the Expanded Zones
        {"id": "r17", "from_zone": "z1", "to_zone": "z13", "distance": 1.5, "live_traffic_congestion": 0.9, "road_capacity": 4, "is_bridge_or_tunnel": True}, # Brooklyn Bridge
        {"id": "r18", "from_zone": "z3", "to_zone": "z13", "distance": 1.8, "live_traffic_congestion": 0.8, "road_capacity": 4, "is_bridge_or_tunnel": True}, # Manhattan Bridge
        {"id": "r19", "from_zone": "z13", "to_zone": "z14", "distance": 2.0, "live_traffic_congestion": 0.6, "road_capacity": 3, "is_bridge_or_tunnel": False},
        {"id": "r20", "from_zone": "z14", "to_zone": "z12", "distance": 5.5, "live_traffic_congestion": 0.7, "road_capacity": 4, "is_bridge_or_tunnel": False},
        {"id": "r21", "from_zone": "z12", "to_zone": "z19", "distance": 3.2, "live_traffic_congestion": 0.5, "road_capacity": 3, "is_bridge_or_tunnel": False},
        {"id": "r22", "from_zone": "z19", "to_zone": "z11", "distance": 6.0, "live_traffic_congestion": 0.8, "road_capacity": 4, "is_bridge_or_tunnel": False}, # Highway to Airport
        {"id": "r23", "from_zone": "z11", "to_zone": "z20", "distance": 2.5, "live_traffic_congestion": 0.4, "road_capacity": 2, "is_bridge_or_tunnel": False},
        {"id": "r24", "from_zone": "z2", "to_zone": "z15", "distance": 4.0, "live_traffic_congestion": 0.3, "road_capacity": 2, "is_bridge_or_tunnel": True}, # Bridge to SI
        {"id": "r25", "from_zone": "z15", "to_zone": "z16", "distance": 12.0, "live_traffic_congestion": 0.2, "road_capacity": 4, "is_bridge_or_tunnel": False},
        {"id": "r26", "from_zone": "z16", "to_zone": "z13", "distance": 10.5, "live_traffic_congestion": 0.6, "road_capacity": 4, "is_bridge_or_tunnel": False},
        {"id": "r27", "from_zone": "z8", "to_zone": "z18", "distance": 3.5, "live_traffic_congestion": 0.4, "road_capacity": 3, "is_bridge_or_tunnel": False},
        {"id": "r28", "from_zone": "z10", "to_zone": "z18", "distance": 4.2, "live_traffic_congestion": 0.3, "road_capacity": 3, "is_bridge_or_tunnel": False},
        {"id": "r29", "from_zone": "z10", "to_zone": "z17", "distance": 5.0, "live_traffic_congestion": 0.5, "road_capacity": 2, "is_bridge_or_tunnel": True},
        {"id": "r30", "from_zone": "z17", "to_zone": "z19", "distance": 7.5, "live_traffic_congestion": 0.7, "road_capacity": 4, "is_bridge_or_tunnel": False},
        {"id": "r31", "from_zone": "z18", "to_zone": "z17", "distance": 4.8, "live_traffic_congestion": 0.4, "road_capacity": 3, "is_bridge_or_tunnel": False},
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
        city_graph.update_edge_weights(risk_scores, request.disaster_type)

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
