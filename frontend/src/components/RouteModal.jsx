import React, { useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { MapContainer, TileLayer, Marker, Polyline, Tooltip, useMap } from 'react-leaflet';
import L from 'leaflet';

function MapBoundsFitter({ bounds }) {
  const map = useMap();
  useEffect(() => {
    if (bounds && bounds.isValid()) {
      map.fitBounds(bounds, { padding: [30, 30] });
    }
  }, [map, bounds]);
  return null;
}

export default function RouteModal({ route, city, onClose, isModalOpen }) {
  if (!isModalOpen || !route) return null;

  const getZoneName = (id) => city?.zones?.find(z => z.id === id)?.name ?? id;
  const getZoneCoords = (id) => {
    const z = city?.zones?.find(z => z.id === id);
    return z ? [z.latitude, z.longitude] : null;
  };

  const routeZoneIds = new Set([
    ...(route.safest_route || []),
    ...(route.shortest_route || [])
  ]);
  const routeZones = (city?.zones || []).filter(z => routeZoneIds.has(z.id));

  const safestCoords = (route.safest_route || []).map(getZoneCoords).filter(Boolean);
  const shortestCoords = (route.shortest_route || []).map(getZoneCoords).filter(Boolean);
  const allCoords = [...safestCoords, ...shortestCoords];
  const bounds = allCoords.length > 0 ? L.latLngBounds(allCoords) : null;

  const getRiskColor = (score) => {
    if (score < 0.3) return '#00ff88';
    if (score < 0.7) return '#ffaa00';
    return '#ff3366';
  };

  const createMarkerIcon = (color) => L.divIcon({
    className: 'custom-zone-marker',
    html: `<div style="background:${color};width:12px;height:12px;border-radius:50%;border:2px solid white;box-shadow:0 0 8px ${color};margin-top:-6px;margin-left:-6px;"></div>`,
    iconSize: [12, 12],
    iconAnchor: [6, 6],
  });

  const riskPct = (route.risk_score * 100).toFixed(1);

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-card modal-3col" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close-btn" onClick={onClose}>&times;</button>

        {/* 3-column body */}
        <div className="modal-3col-body">
          {/* COLUMN 1 — Data cards */}
          <div className="modal-col modal-col-data">
            <div className="modal-info-card">
              <h3>Safest Route</h3>
              <div className="route-list">
                {route.safest_route.map((zone, i) => (
                  <React.Fragment key={zone}>
                    <span className="route-zone">{getZoneName(zone)}</span>
                    {i < route.safest_route.length - 1 && <span className="route-arrow">→</span>}
                  </React.Fragment>
                ))}
              </div>
            </div>

            <div className="modal-info-card">
              <h3>Risk Score</h3>
              <div className="risk-meter-container">
                <div className="risk-meter inline-meter">
                  <div className="risk-bar" style={{ width: `${Math.min(route.risk_score * 100, 100)}%` }}></div>
                </div>
                <span className="risk-value-inline">{riskPct}%</span>
              </div>
            </div>

            {route.shortest_route && (
              <div className="modal-info-card">
                <h3>Shortest Route</h3>
                <div className="route-list">
                  {route.shortest_route.map((zone, i) => (
                    <React.Fragment key={zone}>
                      <span className="route-zone">{getZoneName(zone)}</span>
                      {i < route.shortest_route.length - 1 && <span className="route-arrow">→</span>}
                    </React.Fragment>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* COLUMN 2 — Mini map */}
          <div className="modal-col modal-col-map">
            <div className="mini-map-container">
              <MapContainer
                center={[40.7128, -74.0060]}
                zoom={12}
                zoomControl={false}
                scrollWheelZoom={false}
                dragging={false}
                doubleClickZoom={false}
                touchZoom={false}
                style={{ height: '100%', width: '100%', borderRadius: '10px', background: '#0a0a0a' }}
              >
                <TileLayer url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png" />
                {safestCoords.length > 1 && (
                  <Polyline positions={safestCoords} color="#00e5ff" weight={4} opacity={0.9} />
                )}
                {shortestCoords.length > 1 && (
                  <Polyline positions={shortestCoords} color="#ffaa00" weight={3} dashArray="6, 10" opacity={0.7} />
                )}
                {routeZones.map(z => (
                  <Marker
                    key={z.id}
                    position={[z.latitude, z.longitude]}
                    icon={createMarkerIcon(getRiskColor(route.zone_risks?.[z.id] || 0))}
                  >
                    <Tooltip direction="top" offset={[0, -8]}>{z.name}</Tooltip>
                  </Marker>
                ))}
                {bounds && <MapBoundsFitter bounds={bounds} />}
              </MapContainer>

              <div className="mini-map-legend">
                <div className="mini-legend-item">
                  <div className="mini-legend-safest"></div>
                  <span>Safest Route</span>
                </div>
                {route.shortest_route && (
                  <div className="mini-legend-item">
                    <div className="mini-legend-shortest"></div>
                    <span>Shortest Route</span>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* COLUMN 3 — AI Explanation */}
          <div className="modal-col modal-col-ai">
            <h3 className="modal-section-label">AI Explanation</h3>
            <div className="modal-ai-body">
              <ReactMarkdown>{route.explanation}</ReactMarkdown>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
