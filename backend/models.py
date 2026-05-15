from pydantic import BaseModel
from typing import List, Optional, Dict

class Zone(BaseModel):
    id: str
    name: str
    latitude: float
    longitude: float
    elevation_m: float = 10.0
    population_density: int = 5000
    building_age_years: int = 20
    infrastructure_type: str = "residential"
    vegetation_density: str = "low"
    has_medical_center: bool = False

class Road(BaseModel):
    id: str
    from_zone: str
    to_zone: str
    distance: float
    risk_score: Optional[float] = 0.0
    live_traffic_congestion: float = 0.0  # 0.0 to 1.0
    road_capacity: int = 2  # 1 = alley, 4 = highway
    is_bridge_or_tunnel: bool = False

class City(BaseModel):
    name: str
    zones: List[Zone]
    roads: List[Road]

class DisasterInput(BaseModel):
    disaster_type: str  # flood, earthquake, fire
    intensity: float  # 0-10
    starting_location: str
    destination_location: Optional[str] = None

class RouteResponse(BaseModel):
    safest_route: List[str]
    shortest_route: Optional[List[str]] = None
    explanation: str
    risk_score: float
    zone_risks: Dict[str, float] = {}
