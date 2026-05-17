import React from 'react';

const MetricCard = ({ title, value, delta, color = "var(--text-main)", warning = false }) => {
  return (
    <div className="metric-field">
      <div className="metric-label">{title}</div>
      <div className={`metric-value ${warning ? 'warning' : ''}`} style={{ color }}>
        {value}
      </div>
      {delta && (
        <div className="metric-delta" style={{ color: delta.includes('-') ? 'var(--warning-orange)' : 'var(--success-green)' }}>
          {delta}
        </div>
      )}
    </div>
  );
};

export default MetricCard;
