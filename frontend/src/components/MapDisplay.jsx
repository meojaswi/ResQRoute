import { useEffect, useMemo } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import L from 'leaflet';

// Create a custom icon factory for colored markers
const createZoneIcon = (riskScore) => {
  let color = '#4caf50'; // Green for low risk
  if (riskScore >= 0.7) {
    color = '#f44336'; // Red for high risk
  } else if (riskScore >= 0.3) {
    color = '#ff9800'; // Orange for medium risk
  }

  return L.divIcon({
    className: 'custom-zone-marker',
    html: `<div style="background-color: ${color}; width: 24px; height: 24px; border-radius: 50%; border: 3px solid white; box-shadow: 0 0 4px rgba(0,0,0,0.4);"></div>`,
    iconSize: [24, 24],
    iconAnchor: [12, 12],
    popupAnchor: [0, -12],
  });
};

export default function MapDisplay({ city, route, onLoadMap }) {
  useEffect(() => {
    if (!city) {
      onLoadMap();
    }
  }, [city, onLoadMap]);

  // Compute map center and bounds based on zones
  const center = useMemo(() => {
    if (!city || city.zones.length === 0) return [40.73, -74.00];
    const lats = city.zones.map(z => z.latitude);
    const lons = city.zones.map(z => z.longitude);
    return [
      (Math.max(...lats) + Math.min(...lats)) / 2,
      (Math.max(...lons) + Math.min(...lons)) / 2
    ];
  }, [city]);

  // Create a dictionary for quick zone coordinate lookups
  const zoneCoords = useMemo(() => {
    if (!city) return {};
    return city.zones.reduce((acc, zone) => {
      acc[zone.id] = [zone.latitude, zone.longitude];
      return acc;
    }, {});
  }, [city]);

  if (!city) {
    return (
      <div className="map-container">
        <h2>City Map</h2>
        <p>Loading map data...</p>
      </div>
    );
  }

  // Get risk score for a zone, default to 0 (green) if no route planned
  const getRiskScore = (zoneId) => {
    if (!route || !route.zone_risks) return 0;
    return route.zone_risks[zoneId] || 0;
  };

  // Helper to build polyline positions from a list of zone IDs
  const getPathPositions = (pathZoneIds) => {
    return pathZoneIds.map(id => zoneCoords[id]).filter(Boolean);
  };

  return (
    <div className="map-container">
      <h2>City Map - {city.name}</h2>
      
      <div className="leaflet-wrapper">
        <MapContainer center={center} zoom={13} scrollWheelZoom={true} style={{ height: '100%', width: '100%', borderRadius: '8px' }}>
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          />

          {/* Draw all roads as background lines */}
          {city.roads.map(road => {
            const start = zoneCoords[road.from_zone];
            const end = zoneCoords[road.to_zone];
            if (!start || !end) return null;
            return (
              <Polyline
                key={road.id}
                positions={[start, end]}
                color="#aaaaaa"
                weight={3}
                opacity={0.5}
              />
            );
          })}

          {/* Draw Shortest Route (if different from safest) */}
          {route && route.shortest_route && (
            <Polyline
              positions={getPathPositions(route.shortest_route)}
              color="#ff9800"
              weight={6}
              opacity={0.7}
              dashArray="10, 10"
            />
          )}

          {/* Draw Safest Route */}
          {route && route.safest_route && (
            <Polyline
              positions={getPathPositions(route.safest_route)}
              color="#2196f3"
              weight={6}
              opacity={0.9}
            />
          )}

          {/* Draw Zones as Markers */}
          {city.zones.map(zone => (
            <Marker
              key={zone.id}
              position={[zone.latitude, zone.longitude]}
              icon={createZoneIcon(getRiskScore(zone.id))}
            >
              <Popup>
                <strong>{zone.name}</strong><br />
                ID: {zone.id}<br />
                {route && route.zone_risks && (
                  <span>Risk Score: {(getRiskScore(zone.id) * 100).toFixed(0)}%</span>
                )}
              </Popup>
            </Marker>
          ))}
        </MapContainer>
      </div>

      <div className="map-legend">
        <span className="legend-item"><span className="dot green"></span> Low Risk</span>
        <span className="legend-item"><span className="dot orange"></span> Medium Risk</span>
        <span className="legend-item"><span className="dot red"></span> High Risk</span>
        <span className="legend-item"><span className="line blue"></span> Safest Route</span>
        <span className="legend-item"><span className="line dashed-orange"></span> Shortest Route</span>
      </div>
    </div>
  );
}
