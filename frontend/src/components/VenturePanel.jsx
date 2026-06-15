import React from 'react';

const VenturePanel = ({ ventures }) => {
  if (!ventures?.ventures) return null;

  const ventureList = Object.values(ventures.ventures);
  if (ventureList.length === 0) return null;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
      <div style={{
        fontSize: '9px', letterSpacing: '0.4em',
        color: 'rgba(120,100,160,0.45)', textTransform: 'uppercase',
        marginBottom: '2px'
      }}>
        Ventures
      </div>

      {ventureList.map((venture) => {
        const flow = venture.resource_flow ?? {};
        const netMoney = (flow.money_in ?? 0) - (flow.money_out ?? 0);
        const netColor = netMoney >= 0 ? '#10B981' : '#EF4444';

        return (
          <div key={venture.id} style={{
            display: 'flex', flexDirection: 'column', gap: '8px',
            padding: '8px 0',
            borderTop: '1px solid rgba(255,255,255,0.04)'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{
                fontSize: '10px', letterSpacing: '0.2em',
                color: '#F59E0B', textTransform: 'uppercase', fontWeight: 600
              }}>
                {venture.name}
              </span>
              <span style={{
                fontSize: '8px', color: 'rgba(120,100,160,0.4)',
                letterSpacing: '0.1em', textTransform: 'uppercase'
              }}>
                {venture.type}
              </span>
            </div>

            <div style={{ display: 'flex', gap: '16px' }}>
              {[
                { label: 'Mass',     value: venture.mass?.toFixed(2),     color: '#F59E0B' },
                { label: 'Momentum', value: venture.momentum?.toFixed(3), color: '#06B6D4' },
              ].map(({ label, value, color }) => (
                <div key={label}>
                  <div style={{ fontSize: '8px', color: 'rgba(120,100,160,0.4)', letterSpacing: '0.1em' }}>
                    {label.toUpperCase()}
                  </div>
                  <div style={{
                    fontFamily: 'var(--font-display)',
                    fontSize: '0.9rem', fontWeight: 700, color
                  }}>
                    {value}
                  </div>
                </div>
              ))}
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ fontSize: '9px', color: 'rgba(160,140,200,0.5)', letterSpacing: '0.1em' }}>
                NET FLOW
              </span>
              <span style={{
                fontSize: '9px', fontFamily: 'var(--font-display)',
                color: netColor, fontWeight: 700
              }}>
                {netMoney >= 0 ? '+' : ''}{netMoney.toFixed(0)}
              </span>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ fontSize: '9px', color: 'rgba(160,140,200,0.5)', letterSpacing: '0.1em' }}>
                TIME IN
              </span>
              <span style={{
                fontSize: '9px', fontFamily: 'var(--font-display)',
                color: 'rgba(160,140,200,0.7)'
              }}>
                {(flow.time_in ?? 0).toFixed(0)} min
              </span>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default VenturePanel;
