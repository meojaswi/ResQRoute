import ReactMarkdown from 'react-markdown';

export default function RouteInfo({ route, city }) {
  const getZoneName = (id) => city?.zones?.find(z => z.id === id)?.name ?? id;

  return (
    <div className="route-info-horizontal">
      
      <div className="info-column">
        <h3>Safest Route</h3>
        <div className="route-list">
          {route.safest_route.map((zone, index) => (
            <span key={zone} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span className="route-zone">{getZoneName(zone)}</span>
              {index < route.safest_route.length - 1 && <span className="route-arrow" style={{color: 'var(--text-secondary)'}}>→</span>}
            </span>
          ))}
        </div>
      </div>

      <div className="info-column risk-column">
        <h3>Risk Score</h3>
        <div className="risk-meter">
          <div className="risk-bar" style={{ width: `${route.risk_score * 100}%` }}></div>
        </div>
        <p className="risk-value">{(route.risk_score * 100).toFixed(1)}%</p>
      </div>

      {route.shortest_route && (
        <div className="info-column">
          <h3>Shortest Route</h3>
          <div className="route-list">
            {route.shortest_route.map((zone, index) => (
              <span key={zone} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span className="route-zone">{getZoneName(zone)}</span>
                {index < route.shortest_route.length - 1 && <span className="route-arrow" style={{color: 'var(--text-secondary)'}}>→</span>}
              </span>
            ))}
          </div>
        </div>
      )}

      <div className="info-column explanation-column">
        <h3>AI Explanation</h3>
        <div className="explanation markdown-body">
          <ReactMarkdown>{route.explanation}</ReactMarkdown>
        </div>
      </div>

    </div>
  );
}
