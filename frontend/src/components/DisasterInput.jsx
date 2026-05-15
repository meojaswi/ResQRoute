import { useState } from 'react';

export default function DisasterInput({ onPlanRoute, loading, city }) {
  const [disaster, setDisaster] = useState('flood');
  const [intensity, setIntensity] = useState(5);
  const [start, setStart] = useState('z1');
  const [end, setEnd] = useState('z4');

  const handleStartChange = (e) => {
    const newStart = e.target.value;
    setStart(newStart);
    // If the new start matches current end, pick the first zone that isn't newStart
    if (newStart === end && city?.zones) {
      const fallback = city.zones.find(z => z.id !== newStart);
      if (fallback) setEnd(fallback.id);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (start === end) return;
    onPlanRoute({
      disaster_type: disaster,
      intensity: parseFloat(intensity),
      starting_location: start,
      destination_location: end,
    });
  };

  const availableDestinations = city?.zones?.filter(z => z.id !== start) ?? [];

  return (
    <form onSubmit={handleSubmit} className="disaster-input-horizontal">
      <div className="input-group">
        <label htmlFor="disaster">Disaster Type</label>
        <select id="disaster" value={disaster} onChange={(e) => setDisaster(e.target.value)}>
          <option value="flood">🌊 Flood</option>
          <option value="earthquake">🏚️ Earthquake</option>
          <option value="fire">🔥 Fire</option>
        </select>
      </div>

      <div className="input-group">
        <label htmlFor="intensity">Intensity: <span>{intensity}</span></label>
        <input id="intensity" type="range" min="1" max="10" value={intensity} onChange={(e) => setIntensity(e.target.value)} />
      </div>

      <div className="input-group">
        <label htmlFor="start">Starting Zone</label>
        <select id="start" value={start} onChange={handleStartChange}>
          {city?.zones ? city.zones.map(zone => (
            <option key={zone.id} value={zone.id}>{zone.name}</option>
          )) : <option value="z1">Loading...</option>}
        </select>
      </div>

      <div className="input-group">
        <label htmlFor="end">Destination Zone</label>
        <select id="end" value={end} onChange={(e) => setEnd(e.target.value)}>
          {availableDestinations.length > 0
            ? availableDestinations.map(zone => (
                <option key={zone.id} value={zone.id}>{zone.name}</option>
              ))
            : <option value="z4">Loading...</option>}
        </select>
      </div>

      <div className="input-group action-group">
        <button type="submit" disabled={loading || start === end}>
          {loading ? '🔄 Planning...' : '📍 Plan Route'}
        </button>
      </div>
    </form>
  );
}
