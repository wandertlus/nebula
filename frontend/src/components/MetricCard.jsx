import React from 'react';

const MetricCard = ({ title, value, delta, color = "var(--text-main)", icon: Icon }) => {
  return (
    <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h3 style={{ fontSize: '0.9rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          {title}
        </h3>
        {Icon && <Icon size={18} color="var(--text-muted)" />}
      </div>
      
      <div style={{ display: 'flex', alignItems: 'baseline', gap: '12px' }}>
        <div className="metric-value" style={{ fontSize: '2rem', color: color }}>
          {value}
        </div>
        {delta && (
          <div style={{ fontSize: '0.85rem', color: delta.startsWith('-') || delta.includes('vs Hist') && delta.startsWith('-') ? 'var(--warning-orange)' : 'var(--success-green)' }}>
            {delta}
          </div>
        )}
      </div>
    </div>
  );
};

export default MetricCard;
