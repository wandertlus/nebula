import React from 'react';

const CapabilitiesPanel = ({ capabilities }) => {
  if (!capabilities?.capabilities) return null;

  const entries = Object.entries(capabilities.capabilities);

  const formatKey = (key) =>
    key.replace(/_capability$/, '').replace(/_/g, ' ').toUpperCase();

  const CapRow = ({ capKey, cap }) => {
    const strength = cap.strength ?? 0;
    const color = cap.exists ? '#10B981' : 'rgba(120,100,160,0.35)';

    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '3px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
            <div style={{
              width: 4, height: 4, borderRadius: '50%',
              background: color,
              boxShadow: cap.exists ? `0 0 6px ${color}` : 'none'
            }} />
            <span style={{ fontSize: '9px', color, letterSpacing: '0.15em' }}>
              {formatKey(capKey)}
            </span>
          </div>
          <span style={{ fontSize: '9px', color, fontFamily: 'var(--font-display)' }}>
            {cap.exists ? `${Math.round(strength * 100)}%` : 'forming'}
          </span>
        </div>
        <div style={{
          width: '100%', height: '1px',
          background: 'rgba(255,255,255,0.04)'
        }}>
          <div style={{
            height: '1px',
            width: `${Math.round(strength * 100)}%`,
            background: color,
            transition: 'width 0.8s cubic-bezier(0.16, 1, 0.3, 1)',
            opacity: cap.exists ? 0.9 : 0.3
          }} />
        </div>
      </div>
    );
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
      <div style={{
        fontSize: '9px', letterSpacing: '0.4em',
        color: 'rgba(120,100,160,0.45)', textTransform: 'uppercase',
        marginBottom: '2px'
      }}>
        Capabilities
      </div>
      {entries.map(([key, cap]) => (
        <CapRow key={key} capKey={key} cap={cap} />
      ))}
    </div>
  );
};

export default CapabilitiesPanel;
