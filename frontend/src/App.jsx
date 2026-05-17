import React, { useState, useEffect } from 'react';
import MetricCard from './components/MetricCard';
import SignalInput from './components/SignalInput';
import IdentityFields from './components/IdentityFields';
import Nebula3DBackground from './components/Nebula3DBackground';

const API_BASE = 'http://localhost:8000/api';

function App() {
  const [events, setEvents] = useState([]);
  const [fieldMasses, setFieldMasses] = useState({});
  const [connections, setConnections] = useState({});
  const [dominant, setDominant] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [apiOnline, setApiOnline] = useState(true);
  const [flash, setFlash] = useState(false);

  const fetchData = async () => {
    try {
      const [eventsRes, massRes] = await Promise.all([
        fetch(`${API_BASE}/events`),
        fetch(`${API_BASE}/field-mass`),
      ]);

      const eventsData = await eventsRes.json();
      const massData   = await massRes.json();

      setEvents(eventsData.events || []);
      setFieldMasses(massData.field_masses || {});
      setConnections(massData.connections || {});
      setDominant(massData.dominant || null);
      setApiOnline(true);
    } catch (error) {
      console.error('Failed to fetch data:', error);
      setApiOnline(false);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // Dynamic Theme: Update global CSS variables based on dominant field
  useEffect(() => {
    const root = document.documentElement;
    const FIELD_COLORS = {
      engineering: '#BC13FE',
      fitness:     '#FF8C00',
      be_fluent:   '#5ba8e8',
    };
    
    const color = FIELD_COLORS[dominant] || '#BC13FE';
    root.style.setProperty('--neon-purple', color);
    root.style.setProperty('--glow-text', `0 0 10px ${color}66, 0 0 20px ${color}33`);
  }, [dominant]);

  const handleSignalSubmit = async (payload) => {
    setSubmitting(true);
    try {
      const res = await fetch(`${API_BASE}/signal`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (res.ok) {
        setFlash(true);
        setTimeout(() => setFlash(false), 600);
        await fetchData();
      }
    } catch (error) {
      console.error('Failed to submit signal:', error);
    } finally {
      setSubmitting(false);
    }
  };

  const latestEvent  = events[events.length - 1] || {};
  const currentState = latestEvent.state || 'Friction';
  const finalScore   = latestEvent.final_score ?? 0;
  const driftDelta   = latestEvent.physics_params?.identity_snapshot?.drift_delta ?? 0;

  if (loading) {
    return (
      <>
        <Nebula3DBackground fieldMasses={fieldMasses} connections={connections} currentState={currentState} />
        <div className="loading-screen">
          <div className="loading-text">Initializing Semantic Observatory</div>
        </div>
      </>
    );
  }

  const efficiency = latestEvent.effort_signals?.efficiency_ratio ?? null;

  return (
    <>
      <Nebula3DBackground
        fieldMasses={fieldMasses}
        connections={connections}
        currentState={currentState}
        finalScore={finalScore}
        driftDelta={driftDelta}
      />

      <div className={`app-container animate-in ${flash ? 'signal-flash' : ''}`}>

        {/* ── TOP LEFT: Identifier ── */}
        <header className="header">
          <h1>Nebula</h1>
          <div className="header-status">
            <div className={`status-dot ${apiOnline ? 'online' : 'offline'}`} />
            {apiOnline ? 'Telemetry Online' : 'Observatory Disconnected'}
          </div>
        </header>

        {/* ── TOP RIGHT: Live metrics + Identity Fields ── */}
        <div className="metrics-grid">
          <MetricCard
            title="Total Signals"
            value={events.length}
          />
          <MetricCard
            title="Last Impulse"
            value={finalScore >= 0 ? `+${finalScore.toFixed(3)}` : finalScore.toFixed(3)}
            color={finalScore >= 0.1 ? 'var(--neon-purple)' : finalScore < 0 ? 'var(--warning-orange)' : 'var(--text-muted)'}
          />
          <MetricCard
            title="Identity Drift"
            value={driftDelta.toFixed(4)}
          />
          <MetricCard
            title="Efficiency"
            value={efficiency !== null ? efficiency.toFixed(2) : '—'}
            delta={efficiency !== null ? (efficiency >= 1 ? '+Optimal' : '-Sub') : null}
          />

          {/* Identity field mass bars live inside the metrics column */}
          <div style={{ gridColumn: '1 / -1', marginTop: '8px' }}>
            <IdentityFields fieldMasses={fieldMasses} dominant={dominant} />
          </div>
        </div>

        {/* ── MIDDLE LEFT: Telemetry feed ── */}
        <div className="telemetry-feed" style={{ overflowY: 'auto', pointerEvents: 'auto' }}>
          {events.slice(-50).reverse().map((ev, idx) => {
            const stateColor = ev.state === 'Friction'
              ? 'var(--neon-purple)'
              : ev.state === 'Black Hole'
              ? 'var(--warning-orange)'
              : 'var(--text-muted)';
            return (
              <div key={idx} className="signal-item">
                <div className="signal-meta">
                  [{new Date(ev.timestamp).toLocaleTimeString()}]&nbsp;
                  {ev.category.toUpperCase()}&nbsp;
                  <span style={{ color: stateColor }}>• {ev.state}</span>
                </div>
                <div className="signal-text">{ev.action_text}</div>
                <div className="signal-stats">
                  <span>IMP: {ev.final_score?.toFixed(3) ?? '0'}</span>
                  <span>DOM: {ev.dominant_attractor ?? '—'}</span>
                  <span>DRF: {ev.physics_params?.identity_snapshot?.drift_delta?.toFixed(4) ?? '0'}</span>
                </div>
              </div>
            );
          })}
          {events.length === 0 && (
            <div style={{ color: 'var(--text-dim)', fontFamily: 'var(--font-mono)', fontSize: '0.9rem' }}>
              Awaiting signals...
            </div>
          )}
        </div>

        {/* ── BOTTOM LEFT: Command input ── */}
        <SignalInput onSubmit={handleSignalSubmit} isLoading={submitting} />

      </div>
    </>
  );
}

export default App;
