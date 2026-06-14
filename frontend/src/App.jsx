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
  const [selectedField, setSelectedField] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [apiOnline, setApiOnline] = useState(true);
  const [flash, setFlash] = useState(false);
  const [terminalFeedback, setTerminalFeedback] = useState(null);

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

  // Dynamic Theme: Update global CSS variables based on dominant field in real-time
  useEffect(() => {
    const root = document.documentElement;
    const meta = getFieldMeta(dominant || 'engineering');
    const color = meta.color;
    const glow = meta.glow;
    
    root.style.setProperty('--neon-purple', color);
    root.style.setProperty('--glow-text', `0 0 10px ${color}66, 0 0 20px ${color}33`);
  }, [dominant, fieldMasses]);

  const handleSignalSubmit = async (payload) => {
    setSubmitting(true);
    try {
      const res = await fetch(`${API_BASE}/signal`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const result = await res.json().catch(() => ({}));

      if (result.status?.includes('command') || result.message) {
        setTerminalFeedback({
          type: result.status === 'error' ? 'error' : 'command',
          text: result.message || 'Command executed.',
        });
      } else if (result.error) {
        setTerminalFeedback({ type: 'error', text: result.error });
      } else {
        setTerminalFeedback({
          type: 'signal',
          text: `Signal assigned -> ${result.dominant_attractor ?? 'unknown'} | score ${result.final_score ?? 0} | backend ${result.active_backend ?? 'semantic'}`,
        });
      }

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

  const handleCoreClick = (fieldKey) => {
    setSelectedField(fieldKey);
  };

  const getFieldMeta = (fieldKey) => {
    const defaults = {
      engineering: { label: 'Engineering', color: '#BC13FE', glow: 'rgba(188,19,254,0.4)' },
      fitness:     { label: 'Fitness',     color: '#FF8C00', glow: 'rgba(255,140,0,0.4)'  },
      be_fluent:   { label: 'Be Fluent',   color: '#5ba8e8', glow: 'rgba(91,168,232,0.4)' },
    };

    if (defaults[fieldKey]) return defaults[fieldKey];

    const fields = Object.keys(fieldMasses);
    const index = fields.indexOf(fieldKey);
    const hue = index !== -1 ? (index * 137.5) % 360 : 200;
    const color = `hsl(${hue}, 85%, 65%)`;
    const glow = `hsla(${hue}, 85%, 65%, 0.4)`;
    const label = fieldKey
      .split(/[_-]/)
      .map(w => w.charAt(0).toUpperCase() + w.slice(1))
      .join(' ');

    return { label, color, glow };
  };

  const latestEvent  = events[events.length - 1] || {};
  const currentState = latestEvent.state || 'Friction';
  const finalScore   = latestEvent.final_score ?? 0;
  const driftDelta   = latestEvent.physics_params?.identity_snapshot?.drift_delta ?? 0;

  if (loading) {
    return (
      <>
        <Nebula3DBackground events={events} fieldMasses={fieldMasses} connections={connections} currentState={currentState} />
        <div className="loading-screen">
          <div className="loading-text">Initializing Semantic Observatory</div>
        </div>
      </>
    );
  }

  const efficiency = latestEvent.effort_signals?.efficiency_ratio ?? null;

  const getAtmosphericGlow = (fieldKey) => {
    const meta = getFieldMeta(fieldKey);
    if (!meta) return 'transparent';
    if (meta.color.startsWith('hsl')) {
      return meta.color.replace('hsl', 'hsla').replace(')', ', 0.07)');
    }
    return `${meta.color}12`;
  };

  return (
    <>
      <Nebula3DBackground
        events={events}
        fieldMasses={fieldMasses}
        connections={connections}
        currentState={currentState}
        finalScore={finalScore}
        driftDelta={driftDelta}
        onCoreClick={handleCoreClick}
      />

      {/* Atmospheric Room Bloom / Light Bleed Overlay */}
      <div style={{
        position: 'fixed',
        inset: 0,
        background: `radial-gradient(circle at 50% 50%, ${getAtmosphericGlow(dominant || 'engineering')} 0%, transparent 68%)`,
        pointerEvents: 'none',
        zIndex: 0,
        transition: 'background 1.5s cubic-bezier(0.16, 1, 0.3, 1)',
      }} />

      <div 
        className={`app-container animate-in ${flash ? 'signal-flash' : ''}`}
        // Asegura que la UI esté por encima del fondo y el overlay
        style={{ position: 'relative', zIndex: 10 }}
      >

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
        <SignalInput
          onSubmit={handleSignalSubmit}
          isLoading={submitting}
          feedback={terminalFeedback}
          onInputChange={() => setTerminalFeedback(null)}
        />

      </div>

      {/* ── CENTRAL FLOATING HUD POPUP: Core Diagnostics ── */}
      {selectedField && (() => {
        const meta = getFieldMeta(selectedField);
        const mass = fieldMasses[selectedField] ?? 0;
        const pct = Math.round(mass * 100);

        // Filter events where this field was aligned/active
        const contributingEvents = events
          .filter(ev => {
            const alignments = ev.physics_params?.all_alignments || {};
            return (alignments[selectedField] ?? 0) > 0.05;
          })
          .slice(-5)
          .reverse();

        // Compute semantic correlations
        const fieldConnections = Object.entries(connections)
          .filter(([key]) => key.includes(selectedField))
          .map(([key, value]) => {
            const otherField = key.replace(`${selectedField}:`, '').replace(`:${selectedField}`, '');
            const otherMeta = getFieldMeta(otherField);
            return { key, otherField, label: otherMeta.label, strength: value, color: otherMeta.color };
          });

        return (
          <div className="core-popup-overlay animate-fade-in" onClick={() => setSelectedField(null)}>
            <div 
              className="core-popup-card animate-slide-up" 
              style={{ 
                '--core-color': meta.color, 
                '--core-glow': meta.glow,
                borderColor: meta.color,
                boxShadow: `0 0 30px ${meta.glow}, inset 0 0 15px rgba(255,255,255,0.02)`
              }}
              onClick={(e) => e.stopPropagation()}
            >
              <button className="core-popup-close" onClick={() => setSelectedField(null)}>×</button>
              
              <div className="popup-badge" style={{ color: meta.color, borderColor: `${meta.color}33` }}>
                System Core Active
              </div>
              
              <h2 className="popup-title" style={{ color: meta.color, textShadow: `0 0 12px ${meta.glow}` }}>
                {meta.label} Diagnostics
              </h2>
              
              <div className="popup-mass-row">
                <span className="mass-label">Identity Orbit Share:</span>
                <span className="mass-value" style={{ color: meta.color }}>{pct}%</span>
              </div>
              
              <div className="popup-section">
                <h3>Feeding Signals <span className="section-subtitle">(Recent inputs affecting this core)</span></h3>
                <div className="popup-signals-list">
                  {contributingEvents.map((ev, idx) => {
                    const alignment = ev.physics_params?.all_alignments?.[selectedField] ?? 0;
                    const contrib = alignment * ev.final_score * 10;
                    return (
                      <div key={idx} className="popup-signal-item">
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '2px' }}>
                          <span className="signal-time">[{new Date(ev.timestamp).toLocaleTimeString()}]</span>
                          <span className="signal-contrib" style={{ color: contrib >= 0 ? '#5ba8e8' : '#FF8C00' }}>
                            {contrib >= 0 ? '+' : ''}{contrib.toFixed(2)}% Mass
                          </span>
                        </div>
                        <p className="signal-desc">{ev.action_text}</p>
                      </div>
                    );
                  })}
                  {contributingEvents.length === 0 && (
                    <div className="empty-signals">No recent feeding signals recorded.</div>
                  )}
                </div>
              </div>

              <div className="popup-section">
                <h3>Semantic Tension Lines <span className="section-subtitle">(Correlations with other cores)</span></h3>
                <div className="popup-correlations-list">
                  {fieldConnections.map((conn, idx) => {
                    const corrPct = Math.round(conn.strength * 100);
                    let description = "Fricción. Campos operando de forma aislada.";
                    if (conn.strength > 0.6) {
                      description = "Alta Sincronicidad. El hiperfoco alimenta directamente esta conexión.";
                    } else if (conn.strength > 0.25) {
                      description = "Co-activación moderada. Puente neuronal establecido.";
                    }
                    return (
                      <div key={idx} className="popup-correlation-item">
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '5px' }}>
                          <span className="corr-field" style={{ color: conn.color }}>{conn.label}</span>
                          <span className="corr-strength">{corrPct}% Correlation</span>
                        </div>
                        <div className="corr-bar-bg">
                          <div className="corr-bar-fill" style={{ width: `${corrPct}%`, background: conn.color }} />
                        </div>
                        <p className="corr-desc">{description}</p>
                      </div>
                    );
                  })}
                  {fieldConnections.length === 0 && (
                    <div className="empty-signals">No semantic correlations computed.</div>
                  )}
                </div>
              </div>
            </div>
          </div>
        );
      })()}
    </>
  );
}

export default App;
