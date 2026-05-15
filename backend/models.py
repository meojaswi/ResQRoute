from pydantic import BaseModel
from typing import List, Optional, Dict

class Zone(BaseModel):
    id: str
    name: str
    latitude: float
    longitude: float
    elevation_m: float = 10.0
    population_density: int = 5000
    risk_level: Optional[str] = "low"  # low, medium, high
    disaster_types: Optional[List[str]] = []

class Road(BaseModel):
    id: str
    from_zone: str
    to_zone: str
    distance: float
    risk_score: Optional[float] = 0.0

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
