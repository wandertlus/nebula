import React, { useState, useEffect } from 'react';
import MetricCard from './components/MetricCard';
import IdentityChart from './components/IdentityChart';
import SignalInput from './components/SignalInput';
import { Activity, Brain, Target, Zap } from 'lucide-react';

const API_BASE = 'http://localhost:8000/api';

function App() {
  const [events, setEvents] = useState([]);
  const [state, setState] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  const fetchData = async () => {
    try {
      const [eventsRes, stateRes] = await Promise.all([
        fetch(`${API_BASE}/events`),
        fetch(`${API_BASE}/state`)
      ]);
      
      const eventsData = await eventsRes.json();
      const stateData = await stateRes.json();
      
      setEvents(eventsData.events || []);
      setState(stateData);
    } catch (error) {
      console.error("Failed to fetch data:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleSignalSubmit = async (payload) => {
    setSubmitting(true);
    try {
      const res = await fetch(`${API_BASE}/signal`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        await fetchData(); // Refresh all data
      }
    } catch (error) {
      console.error("Failed to submit signal:", error);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return <div style={{ display: 'flex', height: '100vh', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>Initializing Cerebral Cortex...</div>;
  }

  const latestEvent = events[events.length - 1] || {};
  const efficiency = latestEvent.effort_signals?.efficiency_ratio || 1.0;
  
  return (
    <div className="app-container">
      <header className="header">
        <h1>Nebula Engine</h1>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-muted)' }}>
          <div style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--success-green)', boxShadow: '0 0 10px var(--success-green)' }} />
          System Online
        </div>
      </header>

      <div className="metrics-grid">
        <MetricCard 
          title="Total Signals" 
          value={events.length} 
          icon={Activity} 
        />
        <MetricCard 
          title="Last State" 
          value={latestEvent.state || 'Unknown'} 
          color={latestEvent.state === 'Friction' ? 'var(--neon-purple)' : latestEvent.state === 'Degenerate Matter' ? 'var(--warning-orange)' : 'var(--text-main)'}
          icon={Brain} 
        />
        <MetricCard 
          title="Identity Drift" 
          value={latestEvent.physics_params?.identity_snapshot?.drift_delta?.toFixed(4) || '0.0000'} 
          icon={Target} 
        />
        <MetricCard 
          title="Efficiency Ratio" 
          value={efficiency.toFixed(2)} 
          delta={efficiency >= 1 ? '+Optimal' : '-Suboptimal'}
          icon={Zap} 
        />
      </div>

      <div className="charts-grid">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          <IdentityChart data={events} />
          <SignalInput onSubmit={handleSignalSubmit} isLoading={submitting} />
        </div>
        
        <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column' }}>
          <h3 style={{ fontSize: '1rem', color: 'var(--text-main)', marginBottom: '16px' }}>Recent Signals</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', overflowY: 'auto', flex: 1, maxHeight: '500px', paddingRight: '8px' }}>
            {events.slice(-10).reverse().map((ev, idx) => (
              <div key={idx} style={{ padding: '12px', background: 'rgba(255,255,255,0.03)', borderRadius: '8px', borderLeft: `3px solid ${ev.state === 'Friction' ? 'var(--neon-purple)' : 'var(--warning-orange)'}` }}>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '4px' }}>{new Date(ev.timestamp).toLocaleTimeString()} • {ev.category}</div>
                <div style={{ color: 'var(--text-main)', fontSize: '0.95rem', lineHeight: 1.4 }}>{ev.action_text}</div>
                <div style={{ display: 'flex', gap: '12px', marginTop: '8px', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                  <span>Score: {ev.final_score?.toFixed(2) || (ev.physics_params ? ev.physics_params.final_score?.toFixed(2) : '0')}</span>
                  <span>Effort: {ev.effort_signals?.effort || (ev.physics_params ? ev.physics_params.effort : '0')}</span>
                </div>
              </div>
            ))}
            {events.length === 0 && <div style={{ color: 'var(--text-muted)' }}>No signals detected.</div>}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
