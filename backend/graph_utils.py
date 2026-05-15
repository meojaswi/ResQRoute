import networkx as nx
from typing import List, Dict
from models import Zone, Road

class CityGraph:
    def __init__(self):
        self.graph = nx.Graph()

    def add_zones(self, zones: List[Zone]):
        """Add zones (nodes) to the graph"""
        for zone in zones:
            self.graph.add_node(zone.id, name=zone.name, lat=zone.latitude, lon=zone.longitude)

    def add_roads(self, roads: List[Road]):
        """Add roads (edges) to the graph with weights"""
        for road in roads:
            self.graph.add_edge(
                road.from_zone, road.to_zone,
                distance=road.distance,   # raw distance — never overwritten
                safe_weight=road.distance,  # risk-adjusted weight — updated later
                risk=road.risk_score,
                live_traffic_congestion=road.live_traffic_congestion,
                road_capacity=road.road_capacity,
                is_bridge_or_tunnel=road.is_bridge_or_tunnel
            )

    def update_edge_weights(self, risk_scores: Dict[str, float], disaster_type: str):
        for u, v, data in self.graph.edges(data=True):
            base_distance = data['distance']
            zone_risk = max(
                risk_scores.get(u, 0.0),
                risk_scores.get(v, 0.0)   # both zones, not just destination
            )
            
            # Start with the base exponential zone risk penalty
            weight_multiplier = 1 + (zone_risk ** 2 * 10)
            
            # Traffic and capacity modifiers
            congestion = data.get('live_traffic_congestion', 0.0)
            capacity = data.get('road_capacity', 1)
            
            # High congestion heavily penalizes the route. High capacity slightly mitigates it.
            traffic_penalty = 1 + (congestion * 2) / max(capacity, 1)
            weight_multiplier *= traffic_penalty
            
            # Catastrophic structural penalties
            if data.get('is_bridge_or_tunnel', False):
                if disaster_type.lower() in ["flood", "earthquake"]:
                    weight_multiplier *= 50  # Basically severs the route
            
            data['safe_weight'] = base_distance * weight_multiplier

    def find_shortest_path(self, start: str, end: str) -> List[str]:
        """Find shortest path by raw distance only (ignores risk)."""
        try:
            return nx.shortest_path(self.graph, start, end, weight='distance')
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return []

    def find_safest_path(self, start: str, end: str) -> List[str]:
        """Find safest path using AI risk-adjusted weights (Dijkstra on safe_weight)."""
        try:
            return nx.shortest_path(self.graph, start, end, weight='safe_weight')
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return []
