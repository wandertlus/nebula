import React from 'react';

const getFieldMeta = (fieldKey, index, total) => {
  const defaults = {
    engineering: { label: 'Engineering', color: '#BC13FE', glow: 'rgba(188,19,254,0.4)' },
    fitness:     { label: 'Fitness',     color: '#FF8C00', glow: 'rgba(255,140,0,0.4)'  },
    be_fluent:   { label: 'Be Fluent',   color: '#5ba8e8', glow: 'rgba(91,168,232,0.4)' },
  };

  if (defaults[fieldKey]) return defaults[fieldKey];

  const hue = (index * 137.5) % 360; // Golden ratio color distribution for distinct hues
  const color = `hsl(${hue}, 85%, 65%)`;
  const glow = `hsla(${hue}, 85%, 65%, 0.4)`;
  
  const label = fieldKey
    .split(/[_-]/)
    .map(w => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ');

  return { label, color, glow };
};

const IdentityFields = ({ fieldMasses = {}, dominant }) => {
  const fields = Object.keys(fieldMasses);
  const totalFields = fields.length;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
      <div style={{ fontSize: '9px', letterSpacing: '0.4em', color: 'rgba(120,100,160,0.45)', textTransform: 'uppercase', marginBottom: '4px' }}>
        Identity Fields
      </div>

      {fields.map((field, idx) => {
        const meta = getFieldMeta(field, idx, totalFields);
        const mass = fieldMasses[field] ?? 0;
        const pct = Math.round(mass * 100);
        const isDominant = field === dominant;

        return (
          <div 
            key={field} 
            style={{ 
              display: 'flex', 
              flexDirection: 'column', 
              gap: '6px',
              padding: isDominant ? '4px 0' : '0px',
              transition: 'all 0.4s ease',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: isDominant ? '9px' : '6px', transition: 'all 0.4s ease' }}>
                <div style={{
                  width: isDominant ? 8 : 4, 
                  height: isDominant ? 8 : 4, 
                  borderRadius: '50%',
                  background: meta.color,
                  boxShadow: isDominant ? `0 0 10px ${meta.glow}, 0 0 20px ${meta.glow}` : 'none',
                  animation: isDominant ? 'pulse 2s infinite' : 'none',
                  transition: 'all 0.4s ease',
                }} />
                <span style={{
                  fontSize: isDominant ? '11px' : '9.5px',
                  letterSpacing: isDominant ? '0.25em' : '0.18em',
                  color: isDominant ? meta.color : 'rgba(160,140,200,0.65)',
                  textTransform: 'uppercase',
                  textShadow: isDominant ? `0 0 8px ${meta.glow}` : 'none',
                  fontWeight: isDominant ? '700' : '300',
                  transition: 'all 0.4s ease',
                }}>
                  {meta.label}
                </span>
              </div>
              <span style={{
                fontFamily: 'var(--font-display)',
                fontSize: isDominant ? '1.1rem' : '0.8rem',
                fontWeight: 700,
                color: isDominant ? meta.color : 'rgba(120,100,160,0.6)',
                textShadow: isDominant ? `0 0 8px ${meta.glow}` : 'none',
                transition: 'all 0.4s ease',
              }}>
                {pct}%
              </span>
            </div>

            {/* Mass bar */}
            <div style={{
              width: '100%', height: isDominant ? '2px' : '1px',
              background: 'rgba(255,255,255,0.06)',
              position: 'relative', overflow: 'visible',
              transition: 'all 0.4s ease',
            }}>
              <div 
                className={isDominant ? 'mass-bar-active' : ''}
                style={{
                  position: 'absolute', left: 0, top: 0, 
                  height: isDominant ? '2px' : '1px',
                  width: `${pct}%`,
                  background: meta.color,
                  boxShadow: `0 0 6px ${meta.glow}`,
                  transition: 'width 0.8s cubic-bezier(0.16, 1, 0.3, 1), height 0.4s ease',
                  opacity: isDominant ? 1 : 0.6,
                }} 
              />
            </div>
          </div>
        );
      })}
      <style>{`
        @keyframes breathe {
          0%, 100% { opacity: 0.6; box-shadow: 0 0 4px currentColor; }
          50% { opacity: 1; box-shadow: 0 0 12px currentColor; }
        }
        .mass-bar-active {
          animation: breathe 3s ease-in-out infinite;
        }
      `}</style>
    </div>
  );
};

export default IdentityFields;
