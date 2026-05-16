import React from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const IdentityChart = ({ data }) => {
  // We want to show the final_score over time or the drift. Let's show final_score over time.
  const chartData = data.slice(-20).map((d, i) => ({
    name: i,
    score: d.final_score || (d.physics_params ? d.physics_params.final_score : 0),
    alignment: d.alignment_score || 0
  }));

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="glass-panel" style={{ padding: '12px' }}>
          <p style={{ margin: 0, color: 'var(--text-main)' }}>Impact: {payload[0].value.toFixed(2)}</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="glass-panel" style={{ height: '350px', display: 'flex', flexDirection: 'column' }}>
      <h3 style={{ fontSize: '1rem', color: 'var(--text-main)', marginBottom: '16px' }}>Impact Horizon (Last 20)</h3>
      <div style={{ flex: 1, width: '100%' }}>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="colorScore" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="var(--neon-purple)" stopOpacity={0.8}/>
                <stop offset="95%" stopColor="var(--neon-purple)" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" vertical={false} />
            <XAxis dataKey="name" hide />
            <YAxis stroke="var(--text-muted)" tick={{fill: 'var(--text-muted)', fontSize: 12}} axisLine={false} tickLine={false} />
            <Tooltip content={<CustomTooltip />} />
            <Area type="monotone" dataKey="score" stroke="var(--neon-purple)" strokeWidth={3} fillOpacity={1} fill="url(#colorScore)" />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default IdentityChart;
