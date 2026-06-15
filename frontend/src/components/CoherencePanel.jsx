import React from 'react';

const CoherencePanel = ({ coherence }) => {
  if (!coherence || coherence.score === null) return null;

  const score = coherence.score ?? 0;
  const pct = Math.round(score * 100);
  const statusColor = score >= 0.7
    ? '#10B981'
    : score >= 0.4
    ? '#F59E0B'
    : '#EF4444';

  const bars = [
    { label: 'Constructive', value: coherence.constructive_ratio ?? 0, color: '#10B981' },
    { label: 'Entropic',     value: coherence.entropic_ratio ?? 0,     color: '#EF4444' },
    { label: 'Consistency',  value: coherence.consistency_avg ?? 0,    color: '#06B6D4' },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
      <div style={{
        fontSize: '9px', letterSpacing: '0.4em',
        color: 'rgba(120,100,160,0.45)', textTransform: 'uppercase',
        marginBottom: '2px'
      }}>
        Coherence
      </div>

      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <span style={{
          fontFamily: 'var(--font-display)',
          fontSize: '1.4rem', fontWeight: 700,
          color: statusColor,
          textShadow: `0 0 12px ${statusColor}66`
        }}>
          {pct}%
        </span>
        <span style={{
          fontSize: '9px', letterSpacing: '0.2em',
          color: statusColor, textTransform: 'uppercase',
          border: `1px solid ${statusColor}33`,
          borderRadius: '4px', padding: '2px 8px'
        }}>
          {coherence.status}
        </span>
      </div>

      {bars.map(({ label, value, color }) => (
        <div key={label} style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ fontSize: '9px', color: 'rgba(160,140,200,0.5)', letterSpacing: '0.1em' }}>
              {label.toUpperCase()}
            </span>
            <span style={{ fontSize: '9px', color, fontFamily: 'var(--font-display)' }}>
              {Math.round(value * 100)}%
            </span>
          </div>
          <div style={{
            width: '100%', height: '1px',
            background: 'rgba(255,255,255,0.06)', position: 'relative'
          }}>
            <div style={{
              position: 'absolute', left: 0, top: 0,
              height: '1px', width: `${Math.round(value * 100)}%`,
              background: color,
              boxShadow: `0 0 4px ${color}`,
              transition: 'width 0.8s cubic-bezier(0.16, 1, 0.3, 1)',
              opacity: 0.8
            }} />
          </div>
        </div>
      ))}

      <div style={{ fontSize: '8px', color: 'rgba(120,100,160,0.35)', letterSpacing: '0.1em' }}>
        {coherence.signals_analyzed} signals analyzed
      </div>
    </div>
  );
};

export default CoherencePanel;
