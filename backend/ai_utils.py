from anthropic import Anthropic
from dotenv import load_dotenv
import os
import json

# Load .env before instantiating the client so ANTHROPIC_API_KEY is available
load_dotenv()

client = Anthropic()

def get_risk_assessment(disaster_type: str, intensity: float, zones: list) -> dict:
    """Use Claude API to assess risk scores for zones based on disaster.
    Returns a dict keyed by zone ID (e.g. 'z1') so graph_utils can apply weights correctly.
    """

    # Build lookup tables: name → id, and collect names for the prompt
    name_to_id = {}
    zone_details = []
    for z in zones:
        if isinstance(z, dict):
            zone_id = z.get('id')
            zone_name = z.get('name', zone_id)
            elev = z.get('elevation_m', 10.0)
            pop = z.get('population_density', 5000)
            age = z.get('building_age_years', 20)
            infra = z.get('infrastructure_type', 'residential')
            veg = z.get('vegetation_density', 'low')
            med = z.get('has_medical_center', False)
        else:
            zone_id = getattr(z, 'id')
            zone_name = getattr(z, 'name', zone_id)
            elev = getattr(z, 'elevation_m', 10.0)
            pop = getattr(z, 'population_density', 5000)
            age = getattr(z, 'building_age_years', 20)
            infra = getattr(z, 'infrastructure_type', 'residential')
            veg = getattr(z, 'vegetation_density', 'low')
            med = getattr(z, 'has_medical_center', False)
            
        name_to_id[zone_name] = zone_id
        med_str = "Has Hospital" if med else "No Hospital"
        zone_details.append(
            f"- {zone_name} (Elev: {elev}m, Pop: {pop}, Age: {age}yrs, Type: {infra}, Veg: {veg}, {med_str})"
        )

    prompt = f"""You are an evacuation planning AI. Given a {disaster_type} disaster at intensity {intensity}/10,
    assess the risk level (0.0-1.0) for each zone. Return a JSON object with zone names as keys and risk scores as values.

    Zones with Geographic Data:
    {chr(10).join(zone_details)}

    Critical Reasoning Instructions:
    - For FLOODS: Strictly penalize zones with low elevation (e.g. < 5m are extremely dangerous, > 50m are very safe).
    - For FIRES: Heavily penalize zones with 'high' vegetation density and high population density.
    - For EARTHQUAKES: Heavily penalize zones with older building ages (Age > 50yrs) and high population density due to structural collapse.
    - MEDICAL CENTERS: If a zone has a hospital, significantly REDUCE its risk score (make it safer) so evacuees are routed toward medical care.
    - INFRASTRUCTURE: Industrial zones carry high risk of secondary hazards (explosions/chemicals) during fires and earthquakes.

    Return ONLY valid JSON, no other text."""

    message = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    try:
        raw = message.content[0].text.strip()
        # Strip markdown code fences if Claude wraps the JSON
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        name_keyed = json.loads(raw)
        # Remap from zone name → zone ID so graph_utils lookups work correctly
        id_keyed = {name_to_id.get(name, name): score for name, score in name_keyed.items()}
        return id_keyed
    except (json.JSONDecodeError, IndexError):
        import re
        # Last resort: find a JSON object anywhere in the response
        match = re.search(r'\{[^{}]+\}', message.content[0].text, re.DOTALL)
        if match:
            try:
                name_keyed = json.loads(match.group())
                return {name_to_id.get(name, name): score for name, score in name_keyed.items()}
            except json.JSONDecodeError:
                pass
        # Fallback: assign 0.5 risk to every zone ID
        return {zone_id: 0.5 for zone_id in name_to_id.values()}

def get_route_explanation(route: list, risk_score: float, disaster_type: str, zones: list = None) -> str:
    """Use Claude API to explain why this route was chosen"""

    if zones:
        id_to_name = {}
        for z in zones:
            z_id = z.get('id') if isinstance(z, dict) else getattr(z, 'id')
            z_name = z.get('name', z_id) if isinstance(z, dict) else getattr(z, 'name', z_id)
            id_to_name[z_id] = z_name
        route_names = [id_to_name.get(r, r) for r in route]
    else:
        route_names = route

    prompt = f"""Briefly explain (2-3 sentences) why this evacuation route was recommended for a {disaster_type} disaster.
    Route: {' -> '.join(route_names)}
    Overall risk score: {risk_score:.2f}

    Mention key factors like avoiding high-risk zones or congestion areas."""

    message = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=512,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return message.content[0].text
