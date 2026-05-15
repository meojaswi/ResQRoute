import React, { useState } from 'react';
import './App.css';
import DisasterInput from './components/DisasterInput';
import MapDisplay from './components/MapDisplay';
import RouteModal from './components/RouteModal';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    this.setState({ errorInfo });
    console.error("ErrorBoundary caught an error", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '20px', background: '#ffebee', color: '#c62828' }}>
          <h2>Something went wrong in React.</h2>
          <details style={{ whiteSpace: 'pre-wrap' }}>
            {this.state.error && this.state.error.toString()}
            <br />
            {this.state.errorInfo && this.state.errorInfo.componentStack}
          </details>
        </div>
      );
    }
    return this.props.children;
  }
}

function App() {
  const [route, setRoute] = useState(null);
  const [loading, setLoading] = useState(false);
  const [city, setCity] = useState(null);
  const [error, setError] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handlePlanRoute = async (disasterData) => {
    setLoading(true);
    setError(null);
    setRoute(null);
    try {
      const response = await fetch('http://localhost:8000/api/plan-route', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(disasterData),
      });
      const data = await response.json();
      if (!response.ok) {
        setError(data.detail || 'Route planning failed. Check the backend logs.');
      } else {
        setRoute(data);
        setIsModalOpen(true);
      }
    } catch (err) {
      setError('Cannot reach backend. Is it running on port 8000?');
    }
    setLoading(false);
  };

  const fetchCity = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/city');
      const data = await response.json();
      setCity(data);
    } catch (error) {
      console.error('Failed to fetch city:', error);
    }
  };

  return (
    <ErrorBoundary>
      <div className="app">
        <header className="app-header">
          <h1>🚨 ResQRoute</h1>
          <p>AI-Powered Evacuation Route Planner</p>
        </header>

        {error && (
          <div className="error-banner">
            ⚠️ {error}
          </div>
        )}

        <div className="app-container">
          <div className="top-controls-bar">
            <DisasterInput onPlanRoute={handlePlanRoute} loading={loading} city={city} />
          </div>

          <main className="app-main map-section">
            <MapDisplay city={city} route={route} onLoadMap={fetchCity} />
          </main>
        </div>

        <RouteModal 
          route={route} 
          city={city}
          isModalOpen={isModalOpen} 
          onClose={() => setIsModalOpen(false)} 
        />
      </div>
    </ErrorBoundary>
  );
}

export default App;

